/*
FILE: game/rules/war/blockade.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Game / war rules
RESPONSIBILITY: Implements deterministic blockade registries and logistics effects.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Blockade updates and effects are deterministic.
*/
#include "dominium/rules/war/blockade.h"

#include <string.h>

const char* blockade_refusal_to_string(blockade_refusal_code code)
{
    switch (code) {
        case BLOCKADE_REFUSAL_NONE: return "none";
        case BLOCKADE_REFUSAL_INSUFFICIENT_FORCES: return "insufficient_forces";
        case BLOCKADE_REFUSAL_BLOCKADE_ALREADY_ACTIVE: return "blockade_already_active";
        case BLOCKADE_REFUSAL_OUT_OF_AUTHORITY: return "out_of_authority";
        case BLOCKADE_REFUSAL_INSUFFICIENT_LOGISTICS: return "insufficient_logistics";
        default: return "unknown";
    }
}

static u32 blockade_bucket_u32(u32 value, u32 bucket)
{
    if (bucket == 0u) {
        return value;
    }
    return (value / bucket) * bucket;
}

void blockade_registry_init(blockade_registry* reg,
                            blockade_state* storage,
                            u32 capacity,
                            u64 start_id)
{
    if (!reg) {
        return;
    }
    reg->states = storage;
    reg->count = 0u;
    reg->capacity = capacity;
    reg->next_id = start_id ? start_id : 1u;
    if (storage && capacity > 0u) {
        memset(storage, 0, sizeof(blockade_state) * (size_t)capacity);
    }
}

static u32 blockade_find_index(const blockade_registry* reg,
                               u64 blockade_id,
                               int* out_found)
{
    u32 i;
    if (out_found) {
        *out_found = 0;
    }
    if (!reg || !reg->states) {
        return 0u;
    }
    for (i = 0u; i < reg->count; ++i) {
        if (reg->states[i].blockade_id == blockade_id) {
            if (out_found) {
                *out_found = 1;
            }
            return i;
        }
        if (reg->states[i].blockade_id > blockade_id) {
            break;
        }
    }
    return i;
}

blockade_state* blockade_find(blockade_registry* reg,
                              u64 blockade_id)
{
    int found = 0;
    u32 idx;
    if (!reg || !reg->states) {
        return 0;
    }
    idx = blockade_find_index(reg, blockade_id, &found);
    if (!found) {
        return 0;
    }
    return &reg->states[idx];
}

blockade_state* blockade_find_active(blockade_registry* reg,
                                     u64 domain_ref)
{
    u32 i;
    blockade_state* best = 0;
    if (!reg || !reg->states || domain_ref == 0u) {
        return 0;
    }
    for (i = 0u; i < reg->count; ++i) {
        blockade_state* cur = &reg->states[i];
        if (cur->domain_ref != domain_ref) {
            continue;
        }
        if (cur->status != BLOCKADE_STATUS_ACTIVE) {
            continue;
        }
        if (!best || cur->blockade_id < best->blockade_id) {
            best = cur;
        }
    }
    return best;
}

int blockade_register(blockade_registry* reg,
                      const blockade_state* input,
                      u64* out_id,
                      blockade_refusal_code* out_refusal)
{
    int found = 0;
    u32 idx;
    u32 i;
    u64 blockade_id;
    blockade_state* entry;
    if (out_refusal) {
        *out_refusal = BLOCKADE_REFUSAL_NONE;
    }
    if (!reg || !reg->states || !input) {
        return -1;
    }
    if (reg->count >= reg->capacity) {
        return -2;
    }
    if (input->domain_ref != 0u && blockade_find_active(reg, input->domain_ref)) {
        if (out_refusal) {
            *out_refusal = BLOCKADE_REFUSAL_BLOCKADE_ALREADY_ACTIVE;
        }
        return -3;
    }
    blockade_id = input->blockade_id;
    if (blockade_id == 0u) {
        blockade_id = reg->next_id++;
        if (blockade_id == 0u) {
            blockade_id = reg->next_id++;
        }
    }
    idx = blockade_find_index(reg, blockade_id, &found);
    if (found) {
        return -4;
    }
    for (i = reg->count; i > idx; --i) {
        reg->states[i] = reg->states[i - 1u];
    }
    entry = &reg->states[idx];
    memset(entry, 0, sizeof(*entry));
    *entry = *input;
    entry->blockade_id = blockade_id;
    if (entry->control_strength > BLOCKADE_CONTROL_SCALE) {
        entry->control_strength = BLOCKADE_CONTROL_SCALE;
    }
    if (entry->throttle_limit_pct == 0u) {
        entry->throttle_limit_pct = 500u;
    }
    if (entry->status == 0u) {
        entry->status = BLOCKADE_STATUS_ACTIVE;
    }
    if (entry->provenance_ref == 0u) {
        entry->provenance_ref = blockade_id;
    }
    reg->count += 1u;
    if (out_id) {
        *out_id = blockade_id;
    }
    return 0;
}

static int blockade_supply_available(const blockade_state* state,
                                     infra_store_registry* stores)
{
    u32 total = 0u;
    u32 i;
    if (!state) {
        return 0;
    }
    if (state->supply_asset_id == 0u || state->supply_qty == 0u) {
        return 1;
    }
    if (!stores) {
        return 0;
    }
    for (i = 0u; i < state->supply_ref_count; ++i) {
        u32 qty = 0u;
        if (infra_store_get_qty(stores,
                                state->supply_store_refs[i],
                                state->supply_asset_id,
                                &qty) == 0) {
            total += qty;
        }
    }
    return (total >= state->supply_qty) ? 1 : 0;
}

static void blockade_consume_supply(const blockade_state* state,
                                    infra_store_registry* stores)
{
    u32 remaining;
    u32 i;
    if (!state || !stores || state->supply_asset_id == 0u || state->supply_qty == 0u) {
        return;
    }
    remaining = state->supply_qty;
    for (i = 0u; i < state->supply_ref_count && remaining > 0u; ++i) {
        u32 available = 0u;
        u32 take;
        if (infra_store_get_qty(stores,
                                state->supply_store_refs[i],
                                state->supply_asset_id,
                                &available) != 0) {
            continue;
        }
        if (available == 0u) {
            continue;
        }
        take = (available > remaining) ? remaining : available;
        if (take > 0u) {
            (void)infra_store_consume(stores, state->supply_store_refs[i],
                                      state->supply_asset_id, take);
            remaining -= take;
        }
    }
}

int blockade_apply_maintenance(blockade_state* state,
                               blockade_update_context* ctx,
                               blockade_refusal_code* out_refusal)
{
    legitimacy_state* legit;
    if (out_refusal) {
        *out_refusal = BLOCKADE_REFUSAL_NONE;
    }
    if (!state || !ctx) {
        return -1;
    }
    if (state->status != BLOCKADE_STATUS_ACTIVE) {
        return 0;
    }
    if (state->blockading_force_count == 0u) {
        if (out_refusal) {
            *out_refusal = BLOCKADE_REFUSAL_INSUFFICIENT_FORCES;
        }
        state->status = BLOCKADE_STATUS_ENDED;
        state->next_due_tick = DOM_TIME_ACT_MAX;
        return -2;
    }
    if (!blockade_supply_available(state, ctx->stores)) {
        if (out_refusal) {
            *out_refusal = BLOCKADE_REFUSAL_INSUFFICIENT_LOGISTICS;
        }
        state->status = BLOCKADE_STATUS_ENDED;
        state->next_due_tick = DOM_TIME_ACT_MAX;
        return -3;
    }
    blockade_consume_supply(state, ctx->stores);
    if (ctx->legitimacy && state->legitimacy_id != 0u && state->legitimacy_delta != 0) {
        legit = legitimacy_find(ctx->legitimacy, state->legitimacy_id);
        if (legit) {
            (void)legitimacy_apply_delta(legit, state->legitimacy_delta);
        }
    }
    if (state->maintenance_interval == 0u) {
        state->next_due_tick = DOM_TIME_ACT_MAX;
    } else {
        state->next_due_tick = ctx->now_act + state->maintenance_interval;
    }
    return 0;
}

int blockade_apply_to_flow(const blockade_state* state,
                           u64 domain_ref,
                           const logistics_flow_input* input,
                           blockade_flow_effect* out_effect,
                           blockade_refusal_code* out_refusal)
{
    u32 strength;
    u32 adjusted_qty;
    dom_act_time_t arrival_act;
    u32 delay = 0u;
    if (out_refusal) {
        *out_refusal = BLOCKADE_REFUSAL_NONE;
    }
    if (!out_effect || !input) {
        return -1;
    }
    memset(out_effect, 0, sizeof(*out_effect));
    if (!state || state->status != BLOCKADE_STATUS_ACTIVE) {
        out_effect->adjusted_qty = input->qty;
        out_effect->adjusted_arrival_act = input->arrival_act;
        return 0;
    }
    if (state->domain_ref != 0u && domain_ref != 0u &&
        state->domain_ref != domain_ref) {
        out_effect->adjusted_qty = input->qty;
        out_effect->adjusted_arrival_act = input->arrival_act;
        return 0;
    }
    strength = state->control_strength;
    adjusted_qty = input->qty;
    arrival_act = input->arrival_act;
    if (state->policy == BLOCKADE_POLICY_DENY && strength >= 300u) {
        out_effect->deny = 1;
        out_effect->adjusted_qty = 0u;
        out_effect->adjusted_arrival_act = input->arrival_act;
        return 0;
    }
    if (state->policy == BLOCKADE_POLICY_THROTTLE) {
        u32 limit_pct = (state->throttle_limit_pct > 1000u) ? 1000u : state->throttle_limit_pct;
        u32 effective_pct = limit_pct;
        if (strength > 0u) {
            u32 strength_penalty = strength / 5u;
            if (strength_penalty < effective_pct) {
                effective_pct -= strength_penalty;
            } else {
                effective_pct = 0u;
            }
        }
        adjusted_qty = (u32)(((u64)input->qty * (u64)effective_pct) / 1000u);
        if (adjusted_qty == 0u && input->qty > 0u) {
            adjusted_qty = 1u;
        }
    }
    if (state->policy == BLOCKADE_POLICY_INSPECT) {
        delay = state->inspect_delay_ticks;
        if (delay == 0u) {
            delay = 1u + (strength / 200u);
        }
        arrival_act += delay;
    }
    out_effect->adjusted_qty = adjusted_qty;
    out_effect->delay_ticks = delay;
    out_effect->adjusted_arrival_act = arrival_act;
    return 0;
}

int blockade_estimate_from_view(const dom_epistemic_view* view,
                                const blockade_state* actual,
                                blockade_estimate* out)
{
    int is_known = 0;
    if (!out || !actual) {
        return -1;
    }
    if (view && view->state == DOM_EPI_KNOWN && !view->is_uncertain) {
        is_known = 1;
    }
    if (is_known) {
        out->domain_ref = actual->domain_ref;
        out->policy = actual->policy;
        out->control_strength = actual->control_strength;
        out->uncertainty_q16 = view ? view->uncertainty_q16 : 0u;
        out->is_exact = 1;
        return 0;
    }
    out->domain_ref = 0u;
    out->policy = actual->policy;
    out->control_strength = blockade_bucket_u32(actual->control_strength, 100u);
    out->uncertainty_q16 = view ? view->uncertainty_q16 : 0xFFFFu;
    out->is_exact = 0;
    return 0;
}
