/*
FILE: game/rules/war/occupation_state.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Game / war rules
RESPONSIBILITY: Implements deterministic occupation registries and maintenance updates.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Occupation ordering and updates are deterministic.
*/
#include "dominium/rules/war/occupation_state.h"

#include <string.h>

const char* occupation_refusal_to_string(occupation_refusal_code code)
{
    switch (code) {
        case OCCUPATION_REFUSAL_NONE: return "none";
        case OCCUPATION_REFUSAL_INSUFFICIENT_ENFORCEMENT: return "insufficient_enforcement";
        case OCCUPATION_REFUSAL_INSUFFICIENT_SUPPLY: return "insufficient_supply";
        case OCCUPATION_REFUSAL_POLICY_NOT_ALLOWED: return "policy_not_allowed";
        case OCCUPATION_REFUSAL_TERRITORY_NOT_CONTROLLED: return "territory_not_controlled";
        case OCCUPATION_REFUSAL_UNKNOWN_TERRITORY: return "unknown_territory";
        default: return "unknown";
    }
}

void occupation_registry_init(occupation_registry* reg,
                              occupation_state* storage,
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
        memset(storage, 0, sizeof(occupation_state) * (size_t)capacity);
    }
}

static u32 occupation_find_index(const occupation_registry* reg,
                                 u64 occupation_id,
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
        if (reg->states[i].occupation_id == occupation_id) {
            if (out_found) {
                *out_found = 1;
            }
            return i;
        }
        if (reg->states[i].occupation_id > occupation_id) {
            break;
        }
    }
    return i;
}

occupation_state* occupation_find(occupation_registry* reg,
                                  u64 occupation_id)
{
    int found = 0;
    u32 idx;
    if (!reg || !reg->states) {
        return 0;
    }
    idx = occupation_find_index(reg, occupation_id, &found);
    if (!found) {
        return 0;
    }
    return &reg->states[idx];
}

occupation_state* occupation_find_by_territory(occupation_registry* reg,
                                               u64 territory_id)
{
    u32 i;
    occupation_state* best = 0;
    if (!reg || !reg->states || territory_id == 0u) {
        return 0;
    }
    for (i = 0u; i < reg->count; ++i) {
        occupation_state* cur = &reg->states[i];
        if (cur->territory_id != territory_id) {
            continue;
        }
        if (cur->status != OCCUPATION_STATUS_ACTIVE) {
            continue;
        }
        if (!best || cur->occupation_id < best->occupation_id) {
            best = cur;
        }
    }
    return best;
}

int occupation_register(occupation_registry* reg,
                        const occupation_state* input,
                        u64* out_id)
{
    int found = 0;
    u32 idx;
    u32 i;
    occupation_state* entry;
    u64 occupation_id;
    if (!reg || !reg->states || !input) {
        return -1;
    }
    if (reg->count >= reg->capacity) {
        return -2;
    }
    occupation_id = input->occupation_id;
    if (occupation_id == 0u) {
        occupation_id = reg->next_id++;
        if (occupation_id == 0u) {
            occupation_id = reg->next_id++;
        }
    }
    idx = occupation_find_index(reg, occupation_id, &found);
    if (found) {
        return -3;
    }
    for (i = reg->count; i > idx; --i) {
        reg->states[i] = reg->states[i - 1u];
    }
    entry = &reg->states[idx];
    memset(entry, 0, sizeof(*entry));
    *entry = *input;
    entry->occupation_id = occupation_id;
    if (entry->control_gain == 0u) {
        entry->control_gain = 10u;
    }
    if (entry->control_loss == 0u) {
        entry->control_loss = 20u;
    }
    if (entry->status == 0u) {
        entry->status = OCCUPATION_STATUS_ACTIVE;
    }
    if (entry->next_due_tick == 0u) {
        entry->next_due_tick = DOM_TIME_ACT_MAX;
    }
    if (entry->provenance_ref == 0u) {
        entry->provenance_ref = occupation_id;
    }
    reg->count += 1u;
    if (out_id) {
        *out_id = occupation_id;
    }
    return 0;
}

int occupation_set_next_due(occupation_registry* reg,
                            u64 occupation_id,
                            dom_act_time_t next_due_tick)
{
    occupation_state* state = occupation_find(reg, occupation_id);
    if (!state) {
        return -1;
    }
    state->next_due_tick = next_due_tick;
    return 0;
}

static int occupation_supply_available(const occupation_state* state,
                                       infra_store_registry* stores,
                                       u32* out_available)
{
    u32 total = 0u;
    u32 i;
    if (out_available) {
        *out_available = 0u;
    }
    if (!state || !stores || state->supply_asset_id == 0u || state->supply_qty == 0u) {
        return 0;
    }
    for (i = 0u; i < state->supply_ref_count; ++i) {
        u32 qty = 0u;
        if (infra_store_get_qty(stores,
                                state->supply_refs[i],
                                state->supply_asset_id,
                                &qty) == 0) {
            total += qty;
        }
    }
    if (out_available) {
        *out_available = total;
    }
    return (total >= state->supply_qty) ? 1 : 0;
}

static void occupation_consume_supply(const occupation_state* state,
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
                                state->supply_refs[i],
                                state->supply_asset_id,
                                &available) != 0) {
            continue;
        }
        if (available == 0u) {
            continue;
        }
        take = (available > remaining) ? remaining : available;
        if (take > 0u) {
            (void)infra_store_consume(stores, state->supply_refs[i],
                                      state->supply_asset_id, take);
            remaining -= take;
        }
    }
}

int occupation_apply_maintenance(occupation_state* state,
                                 occupation_update_context* ctx,
                                 occupation_refusal_code* out_refusal)
{
    territory_control* territory;
    legitimacy_state* legit;
    enforcement_capacity* enforcement;
    int supply_ok = 1;
    if (out_refusal) {
        *out_refusal = OCCUPATION_REFUSAL_NONE;
    }
    if (!state || !ctx) {
        return -1;
    }
    if (state->status != OCCUPATION_STATUS_ACTIVE) {
        return 0;
    }
    if (!ctx->territory) {
        return -2;
    }
    territory = territory_control_find(ctx->territory, state->territory_id);
    if (!territory) {
        if (out_refusal) {
            *out_refusal = OCCUPATION_REFUSAL_UNKNOWN_TERRITORY;
        }
        state->status = OCCUPATION_STATUS_FAILED;
        state->next_due_tick = DOM_TIME_ACT_MAX;
        return -3;
    }
    if (state->occupier_org_id != 0u &&
        territory->current_controller != state->occupier_org_id) {
        if (out_refusal) {
            *out_refusal = OCCUPATION_REFUSAL_TERRITORY_NOT_CONTROLLED;
        }
        state->status = OCCUPATION_STATUS_FAILED;
        state->next_due_tick = DOM_TIME_ACT_MAX;
        return -4;
    }
    enforcement = 0;
    if (ctx->enforcement && state->enforcement_capacity_id != 0u) {
        enforcement = enforcement_capacity_find(ctx->enforcement,
                                                 state->enforcement_capacity_id);
    }
    if (!enforcement || enforcement->available_enforcers < state->enforcement_min) {
        if (out_refusal) {
            *out_refusal = OCCUPATION_REFUSAL_INSUFFICIENT_ENFORCEMENT;
        }
        state->status = OCCUPATION_STATUS_FAILED;
        (void)territory_control_apply_delta(ctx->territory,
                                            state->territory_id,
                                            -(i32)state->control_loss);
        state->next_due_tick = DOM_TIME_ACT_MAX;
        return -5;
    }
    if (state->supply_asset_id != 0u && state->supply_qty > 0u) {
        supply_ok = occupation_supply_available(state, ctx->stores, 0);
    }
    if (!supply_ok) {
        if (out_refusal) {
            *out_refusal = OCCUPATION_REFUSAL_INSUFFICIENT_SUPPLY;
        }
        state->status = OCCUPATION_STATUS_FAILED;
        (void)territory_control_apply_delta(ctx->territory,
                                            state->territory_id,
                                            -(i32)state->control_loss);
        state->next_due_tick = DOM_TIME_ACT_MAX;
        return -6;
    }
    if (state->supply_asset_id != 0u && state->supply_qty > 0u) {
        occupation_consume_supply(state, ctx->stores);
    }
    (void)territory_control_apply_delta(ctx->territory,
                                        state->territory_id,
                                        (i32)state->control_gain);
    if (ctx->legitimacy && state->legitimacy_id != 0u) {
        legit = legitimacy_find(ctx->legitimacy, state->legitimacy_id);
        if (legit && legit->value < state->legitimacy_min) {
            if (state->legitimacy_decay != 0) {
                (void)legitimacy_apply_delta(legit, state->legitimacy_decay);
            }
            (void)territory_control_apply_delta(ctx->territory,
                                                state->territory_id,
                                                -(i32)state->control_loss);
            territory->contested_flag = 1u;
        }
    }
    if (state->maintenance_interval == 0u) {
        state->next_due_tick = DOM_TIME_ACT_MAX;
    } else {
        state->next_due_tick = ctx->now_act + state->maintenance_interval;
    }
    return 0;
}
