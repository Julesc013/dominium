/*
FILE: game/rules/war/siege_effects.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Game / war rules
RESPONSIBILITY: Implements deterministic siege updates.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Siege updates are deterministic and event-driven.
*/
#include "dominium/rules/war/siege_effects.h"

#include <string.h>

void siege_registry_init(siege_registry* reg,
                         siege_state* storage,
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
        memset(storage, 0, sizeof(siege_state) * (size_t)capacity);
    }
}

static u32 siege_find_index(const siege_registry* reg,
                            u64 siege_id,
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
        if (reg->states[i].siege_id == siege_id) {
            if (out_found) {
                *out_found = 1;
            }
            return i;
        }
        if (reg->states[i].siege_id > siege_id) {
            break;
        }
    }
    return i;
}

siege_state* siege_find(siege_registry* reg,
                        u64 siege_id)
{
    int found = 0;
    u32 idx;
    if (!reg || !reg->states) {
        return 0;
    }
    idx = siege_find_index(reg, siege_id, &found);
    if (!found) {
        return 0;
    }
    return &reg->states[idx];
}

int siege_register(siege_registry* reg,
                   const siege_state* input,
                   u64* out_id)
{
    int found = 0;
    u32 idx;
    u32 i;
    u64 siege_id;
    siege_state* entry;
    if (!reg || !reg->states || !input) {
        return -1;
    }
    if (reg->count >= reg->capacity) {
        return -2;
    }
    siege_id = input->siege_id;
    if (siege_id == 0u) {
        siege_id = reg->next_id++;
        if (siege_id == 0u) {
            siege_id = reg->next_id++;
        }
    }
    idx = siege_find_index(reg, siege_id, &found);
    if (found) {
        return -3;
    }
    for (i = reg->count; i > idx; --i) {
        reg->states[i] = reg->states[i - 1u];
    }
    entry = &reg->states[idx];
    memset(entry, 0, sizeof(*entry));
    *entry = *input;
    entry->siege_id = siege_id;
    if (entry->deprivation_threshold == 0u) {
        entry->deprivation_threshold = 300u;
    }
    if (entry->pressure_gain_base == 0u) {
        entry->pressure_gain_base = 20u;
    }
    if (entry->pressure_decay == 0u) {
        entry->pressure_decay = 10u;
    }
    if (entry->status == 0u) {
        entry->status = SIEGE_STATUS_ACTIVE;
    }
    if (entry->next_due_tick == 0u) {
        entry->next_due_tick = DOM_TIME_ACT_MAX;
    }
    if (entry->provenance_ref == 0u) {
        entry->provenance_ref = siege_id;
    }
    reg->count += 1u;
    if (out_id) {
        *out_id = siege_id;
    }
    return 0;
}

static u32 siege_compute_deprivation(const siege_state* state,
                                     siege_update_context* ctx)
{
    survival_cohort* cohort;
    survival_needs_state* needs;
    u32 score = 0u;
    if (!state || !ctx || !ctx->needs || !ctx->cohorts) {
        return 0u;
    }
    cohort = survival_cohort_find(ctx->cohorts, state->population_cohort_id);
    needs = survival_needs_get(ctx->needs, state->population_cohort_id);
    if (!cohort || !needs) {
        return 0u;
    }
    if (survival_needs_resources_sufficient(needs, &ctx->needs_params, cohort->count)) {
        return 0u;
    }
    score = 300u;
    score += needs->hunger_level * 20u;
    score += needs->thirst_level * 25u;
    if (needs->shelter_level < ctx->needs_params.shelter_min) {
        score += 100u;
    }
    if (score > SIEGE_PRESSURE_SCALE) {
        score = SIEGE_PRESSURE_SCALE;
    }
    return score;
}

int siege_apply_update(siege_state* state,
                       siege_update_context* ctx)
{
    legitimacy_state* legit;
    u32 pressure;
    u32 deprivation;
    u32 add = 0u;
    if (!state || !ctx) {
        return -1;
    }
    if (state->status != SIEGE_STATUS_ACTIVE) {
        return 0;
    }
    pressure = state->deprivation_pressure;
    deprivation = siege_compute_deprivation(state, ctx);
    if (deprivation > state->deprivation_threshold) {
        add = state->pressure_gain_base + ((deprivation - state->deprivation_threshold) / 10u);
    }
    if (add > 0u) {
        u64 next = (u64)pressure + (u64)add;
        pressure = (next > SIEGE_PRESSURE_SCALE) ? SIEGE_PRESSURE_SCALE : (u32)next;
    } else {
        if (pressure > state->pressure_decay) {
            pressure -= state->pressure_decay;
        } else {
            pressure = 0u;
        }
    }
    state->deprivation_pressure = pressure;
    if (ctx->legitimacy && state->legitimacy_id != 0u && state->legitimacy_delta != 0) {
        if (pressure >= state->deprivation_threshold) {
            legit = legitimacy_find(ctx->legitimacy, state->legitimacy_id);
            if (legit) {
                (void)legitimacy_apply_delta(legit, state->legitimacy_delta);
            }
        }
    }
    if (state->update_interval == 0u) {
        state->next_due_tick = DOM_TIME_ACT_MAX;
    } else {
        state->next_due_tick = ctx->now_act + state->update_interval;
    }
    return 0;
}
