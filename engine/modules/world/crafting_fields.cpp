/*
FILE: source/domino/world/crafting_fields.cpp
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / world/crafting_fields
RESPONSIBILITY: Deterministic, atomic crafting and disassembly processes over explicit inventories.
ALLOWED DEPENDENCIES: `include/domino/**` and C89/C++98 headers only.
FORBIDDEN DEPENDENCIES: Engine private headers outside world.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: Fixed-point only; deterministic ordering and math.
*/
#include "domino/world/crafting_fields.h"

#include "domino/core/fixed_math.h"
#include "domino/core/rng_model.h"

#include <string.h>

static q16_16 dom_craft_clamp_q16_16(q16_16 v, q16_16 lo, q16_16 hi)
{
    if (v < lo) {
        return lo;
    }
    if (v > hi) {
        return hi;
    }
    return v;
}

static d_bool dom_craft_domain_is_active(const dom_craft_domain* domain)
{
    if (!domain) {
        return D_FALSE;
    }
    if (domain->existence_state == DOM_DOMAIN_EXISTENCE_NONEXISTENT ||
        domain->existence_state == DOM_DOMAIN_EXISTENCE_DECLARED) {
        return D_FALSE;
    }
    return D_TRUE;
}

static void dom_craft_result_init(dom_craft_result* result)
{
    if (!result) {
        return;
    }
    memset(result, 0, sizeof(*result));
    result->ok = 0u;
    result->refusal_reason = DOM_DOMAIN_REFUSE_NONE;
}

static q16_16 dom_craft_apply_loss(q16_16 quantity, q16_16 loss)
{
    q16_16 one = d_q16_16_from_int(1);
    q16_16 loss_clamped = dom_craft_clamp_q16_16(loss, 0, one);
    q16_16 keep = d_q16_16_sub(one, loss_clamped);
    return d_q16_16_mul(quantity, keep);
}

static int dom_craft_inventory_find(const dom_craft_domain* domain,
                                    u32 item_id,
                                    u32 kind,
                                    q16_16 min_quantity)
{
    if (!domain) {
        return -1;
    }
    for (u32 i = 0u; i < domain->inventory_count; ++i) {
        const dom_craft_item_stack* stack = &domain->inventory[i];
        if (stack->item_id != item_id || stack->kind != kind) {
            continue;
        }
        if (stack->quantity >= min_quantity) {
            return (int)i;
        }
    }
    return -1;
}

static int dom_craft_inventory_find_merge(const dom_craft_domain* domain,
                                          u32 item_id,
                                          u32 kind,
                                          q16_16 integrity)
{
    if (!domain) {
        return -1;
    }
    for (u32 i = 0u; i < domain->inventory_count; ++i) {
        const dom_craft_item_stack* stack = &domain->inventory[i];
        if (stack->item_id != item_id || stack->kind != kind) {
            continue;
        }
        if (kind == DOM_CRAFT_ITEM_ASSEMBLY || kind == DOM_CRAFT_ITEM_TOOL) {
            if (stack->integrity != integrity) {
                continue;
            }
        }
        return (int)i;
    }
    return -1;
}

static void dom_craft_inventory_remove_at(dom_craft_domain* domain, u32 index)
{
    if (!domain || index >= domain->inventory_count) {
        return;
    }
    for (u32 i = index + 1u; i < domain->inventory_count; ++i) {
        domain->inventory[i - 1u] = domain->inventory[i];
    }
    domain->inventory_count -= 1u;
}

static int dom_craft_inventory_add(dom_craft_domain* domain,
                                   u32 item_id,
                                   u32 kind,
                                   q16_16 quantity,
                                   q16_16 integrity,
                                   u32 flags)
{
    int merge_index;
    dom_craft_item_stack* stack;
    if (!domain) {
        return 0;
    }
    if (quantity <= 0) {
        return 1;
    }
    if (kind == DOM_CRAFT_ITEM_MATERIAL || kind == DOM_CRAFT_ITEM_PART) {
        integrity = 0;
    }
    merge_index = dom_craft_inventory_find_merge(domain, item_id, kind, integrity);
    if (merge_index >= 0) {
        stack = &domain->inventory[(u32)merge_index];
        stack->quantity = d_q16_16_add(stack->quantity, quantity);
        return 1;
    }
    if (domain->inventory_count >= domain->surface.inventory_capacity ||
        domain->inventory_count >= DOM_CRAFT_MAX_INVENTORY) {
        return 0;
    }
    stack = &domain->inventory[domain->inventory_count++];
    memset(stack, 0, sizeof(*stack));
    stack->item_id = item_id;
    stack->kind = kind;
    stack->quantity = quantity;
    stack->integrity = integrity;
    stack->flags = flags;
    return 1;
}

static int dom_craft_tool_find(const dom_craft_domain* domain, u32 tool_id, q16_16 min_integrity)
{
    if (!domain) {
        return -1;
    }
    for (u32 i = 0u; i < domain->tool_count; ++i) {
        const dom_craft_tool_instance* tool = &domain->tools[i];
        if (tool->tool_id != tool_id) {
            continue;
        }
        if (tool->integrity >= min_integrity) {
            return (int)i;
        }
    }
    return -1;
}

static int dom_craft_conditions_ok(const dom_craft_recipe_spec* recipe,
                                   const dom_craft_conditions* conditions)
{
    if (!recipe) {
        return 0;
    }
    if (recipe->flags & (DOM_CRAFT_RECIPE_REQUIRE_TEMP |
                         DOM_CRAFT_RECIPE_REQUIRE_HUMIDITY |
                         DOM_CRAFT_RECIPE_REQUIRE_ENVIRONMENT)) {
        if (!conditions) {
            return 0;
        }
    }
    if ((recipe->flags & DOM_CRAFT_RECIPE_REQUIRE_TEMP) && conditions) {
        if (conditions->temperature < recipe->temperature.min ||
            conditions->temperature > recipe->temperature.max) {
            return 0;
        }
    }
    if ((recipe->flags & DOM_CRAFT_RECIPE_REQUIRE_HUMIDITY) && conditions) {
        if (conditions->humidity < recipe->humidity.min ||
            conditions->humidity > recipe->humidity.max) {
            return 0;
        }
    }
    if ((recipe->flags & DOM_CRAFT_RECIPE_REQUIRE_ENVIRONMENT) && conditions) {
        if (conditions->environment_id != recipe->environment_id) {
            return 0;
        }
    }
    return 1;
}

static u32 dom_craft_cost_for_recipe(const dom_craft_surface_desc* surface,
                                     const dom_craft_recipe_spec* recipe)
{
    u32 cost = 0u;
    if (!surface || !recipe) {
        return 0u;
    }
    cost = surface->craft_cost_base;
    cost += recipe->input_count * surface->craft_cost_per_input;
    cost += recipe->output_count * surface->craft_cost_per_output;
    cost += recipe->tool_count * surface->craft_cost_per_tool;
    return cost;
}

void dom_craft_surface_desc_init(dom_craft_surface_desc* desc)
{
    if (!desc) {
        return;
    }
    memset(desc, 0, sizeof(*desc));
    desc->domain_id = 1u;
    desc->world_seed = 1u;
    desc->craft_cost_base = 10u;
    desc->craft_cost_per_input = 2u;
    desc->craft_cost_per_output = 3u;
    desc->craft_cost_per_tool = 1u;
    desc->inventory_capacity = 64u;
    desc->tool_capacity = 16u;
    desc->law_allow_crafting = 1u;
    desc->metalaw_allow_crafting = 1u;
    desc->recipe_count = 0u;
}

void dom_craft_domain_init(dom_craft_domain* domain,
                           const dom_craft_surface_desc* desc)
{
    if (!domain || !desc) {
        return;
    }
    memset(domain, 0, sizeof(*domain));
    domain->surface = *desc;
    dom_domain_policy_init(&domain->policy);
    domain->existence_state = DOM_DOMAIN_EXISTENCE_REALIZED;
    domain->archival_state = DOM_DOMAIN_ARCHIVAL_LIVE;
    domain->authoring_version = 1u;
    domain->inventory_count = 0u;
    domain->tool_count = 0u;
}

void dom_craft_domain_free(dom_craft_domain* domain)
{
    if (!domain) {
        return;
    }
    domain->inventory_count = 0u;
    domain->tool_count = 0u;
}

void dom_craft_domain_set_state(dom_craft_domain* domain,
                                u32 existence_state,
                                u32 archival_state)
{
    if (!domain) {
        return;
    }
    domain->existence_state = existence_state;
    domain->archival_state = archival_state;
}

void dom_craft_domain_set_policy(dom_craft_domain* domain,
                                 const dom_domain_policy* policy)
{
    if (!domain || !policy) {
        return;
    }
    domain->policy = *policy;
}

int dom_craft_execute(dom_craft_domain* domain,
                      u32 recipe_index,
                      const dom_craft_conditions* conditions,
                      u64 tick,
                      dom_domain_budget* budget,
                      dom_craft_result* out_result)
{
    dom_craft_recipe_spec* recipe;
    u32 process_id;
    u32 event_id;
    d_bool conditions_ok;
    d_bool tools_ok = D_TRUE;
    d_bool allow_failure = D_FALSE;
    if (out_result) {
        dom_craft_result_init(out_result);
    }
    if (!domain || recipe_index >= domain->surface.recipe_count) {
        if (out_result) {
            out_result->refusal_reason = DOM_DOMAIN_REFUSE_INTERNAL;
        }
        return -1;
    }
    if (!dom_craft_domain_is_active(domain)) {
        if (out_result) {
            out_result->refusal_reason = DOM_DOMAIN_REFUSE_DOMAIN_INACTIVE;
        }
        return 0;
    }
    if (!domain->surface.law_allow_crafting) {
        if (out_result) {
            out_result->flags |= DOM_CRAFT_RESULT_LAW_BLOCK;
            out_result->refusal_reason = DOM_DOMAIN_REFUSE_POLICY;
        }
        return 0;
    }
    if (!domain->surface.metalaw_allow_crafting) {
        if (out_result) {
            out_result->flags |= DOM_CRAFT_RESULT_METALAW_BLOCK;
            out_result->refusal_reason = DOM_DOMAIN_REFUSE_POLICY;
        }
        return 0;
    }

    recipe = &domain->surface.recipes[recipe_index];
    conditions_ok = dom_craft_conditions_ok(recipe, conditions);
    for (u32 i = 0u; i < recipe->tool_count; ++i) {
        const dom_craft_tool_requirement* req = &recipe->tools[i];
        if (dom_craft_tool_find(domain, req->tool_id, req->min_integrity) < 0) {
            tools_ok = D_FALSE;
            break;
        }
    }
    if (!conditions_ok || !tools_ok) {
        if (recipe->failure_mode == DOM_CRAFT_FAILURE_REFUSE) {
            if (out_result) {
                out_result->refusal_reason = DOM_DOMAIN_REFUSE_POLICY;
            }
            return 0;
        }
        allow_failure = D_TRUE;
    }

    for (u32 i = 0u; i < recipe->input_count; ++i) {
        const dom_craft_item_req* req = &recipe->inputs[i];
        if (dom_craft_inventory_find(domain, req->item_id, req->kind, req->quantity) < 0) {
            if (out_result) {
                out_result->refusal_reason = DOM_DOMAIN_REFUSE_POLICY;
            }
            return 0;
        }
    }

    if (budget) {
        u32 cost = dom_craft_cost_for_recipe(&domain->surface, recipe);
        if (!dom_domain_budget_consume(budget, cost)) {
            if (out_result) {
                out_result->refusal_reason = DOM_DOMAIN_REFUSE_BUDGET;
            }
            return 0;
        }
    }

    process_id = d_rng_hash_str32("process.craft.execute");
    event_id = d_rng_hash_str32((recipe->flags & DOM_CRAFT_RECIPE_DISASSEMBLY)
                                ? "event.craft.disassemble"
                                : "event.craft.execute");

    for (u32 i = 0u; i < recipe->input_count; ++i) {
        const dom_craft_item_req* req = &recipe->inputs[i];
        int idx = dom_craft_inventory_find(domain, req->item_id, req->kind, req->quantity);
        if (idx < 0) {
            if (out_result) {
                out_result->refusal_reason = DOM_DOMAIN_REFUSE_INTERNAL;
            }
            return 0;
        }
        {
            dom_craft_item_stack* stack = &domain->inventory[(u32)idx];
            stack->quantity = d_q16_16_sub(stack->quantity, req->quantity);
            if (stack->quantity <= 0) {
                dom_craft_inventory_remove_at(domain, (u32)idx);
            }
        }
        if (out_result) {
            out_result->inputs_consumed += 1u;
        }
    }

    if (allow_failure) {
        if (out_result) {
            out_result->flags |= DOM_CRAFT_RESULT_FAILURE;
            if (recipe->failure_mode == DOM_CRAFT_FAILURE_WASTE ||
                recipe->failure_mode == DOM_CRAFT_FAILURE_DAMAGE) {
                out_result->flags |= DOM_CRAFT_RESULT_WASTE;
            }
        }
    }

    if (!allow_failure) {
        for (u32 i = 0u; i < recipe->output_count; ++i) {
            const dom_craft_item_req* out = &recipe->outputs[i];
            q16_16 quantity = out->quantity;
            q16_16 integrity = recipe->output_integrity;
            if (recipe->flags & DOM_CRAFT_RECIPE_DISASSEMBLY) {
                quantity = dom_craft_apply_loss(quantity, recipe->recycle_loss);
            }
            if (quantity > 0) {
                if (!dom_craft_inventory_add(domain,
                                             out->item_id,
                                             out->kind,
                                             quantity,
                                             integrity,
                                             (out->kind == DOM_CRAFT_ITEM_ASSEMBLY || out->kind == DOM_CRAFT_ITEM_TOOL)
                                                 ? DOM_CRAFT_ITEM_DAMAGEABLE
                                                 : 0u)) {
                    if (out_result) {
                        out_result->refusal_reason = DOM_DOMAIN_REFUSE_INTERNAL;
                    }
                    return 0;
                }
                if (out_result) {
                    out_result->outputs_produced += 1u;
                }
            }
        }
    }

    if (recipe->byproduct_count > 0u) {
        for (u32 i = 0u; i < recipe->byproduct_count; ++i) {
            const dom_craft_item_req* byp = &recipe->byproducts[i];
            if (byp->quantity > 0) {
                if (!dom_craft_inventory_add(domain,
                                             byp->item_id,
                                             byp->kind,
                                             byp->quantity,
                                             0,
                                             0u)) {
                    if (out_result) {
                        out_result->refusal_reason = DOM_DOMAIN_REFUSE_INTERNAL;
                    }
                    return 0;
                }
                if (out_result) {
                    out_result->byproducts_produced += 1u;
                }
            }
        }
    }

    if (!allow_failure || recipe->failure_mode == DOM_CRAFT_FAILURE_DAMAGE) {
        for (u32 i = 0u; i < recipe->tool_count; ++i) {
            dom_craft_tool_requirement* req = &recipe->tools[i];
            int tindex = dom_craft_tool_find(domain, req->tool_id, req->min_integrity);
            if (tindex >= 0) {
                dom_craft_tool_instance* tool = &domain->tools[(u32)tindex];
                if (recipe->tool_wear > 0) {
                    tool->integrity = d_q16_16_sub(tool->integrity, recipe->tool_wear);
                    if (tool->integrity < 0) {
                        tool->integrity = 0;
                    }
                    if (out_result) {
                        out_result->tool_damage += 1u;
                        out_result->flags |= DOM_CRAFT_RESULT_TOOL_DAMAGE;
                    }
                }
            }
        }
    }

    if (out_result) {
        out_result->ok = 1u;
        out_result->recipe_id = recipe->recipe_id;
        out_result->inventory_count = domain->inventory_count;
        out_result->tool_count = domain->tool_count;
        out_result->process_id = process_id;
        out_result->event_id = event_id;
        if (recipe->flags & DOM_CRAFT_RECIPE_DISASSEMBLY) {
            out_result->flags |= DOM_CRAFT_RESULT_DISASSEMBLY;
        }
    }
    (void)tick;
    return 0;
}

u32 dom_craft_inventory_count(const dom_craft_domain* domain)
{
    return domain ? domain->inventory_count : 0u;
}

const dom_craft_item_stack* dom_craft_inventory_at(const dom_craft_domain* domain, u32 index)
{
    if (!domain || index >= domain->inventory_count) {
        return (const dom_craft_item_stack*)0;
    }
    return &domain->inventory[index];
}

u32 dom_craft_tool_count(const dom_craft_domain* domain)
{
    return domain ? domain->tool_count : 0u;
}

const dom_craft_tool_instance* dom_craft_tool_at(const dom_craft_domain* domain, u32 index)
{
    if (!domain || index >= domain->tool_count) {
        return (const dom_craft_tool_instance*)0;
    }
    return &domain->tools[index];
}
