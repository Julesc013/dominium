/*
FILE: game/rules/war/resistance_state.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Game / war rules
RESPONSIBILITY: Implements deterministic resistance registries and updates.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Resistance ordering and updates are deterministic.
*/
#include "dominium/rules/war/resistance_state.h"

#include <string.h>

static u32 resistance_bucket_u32(u32 value, u32 bucket)
{
    if (bucket == 0u) {
        return value;
    }
    return (value / bucket) * bucket;
}

void resistance_registry_init(resistance_registry* reg,
                              resistance_state* storage,
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
        memset(storage, 0, sizeof(resistance_state) * (size_t)capacity);
    }
}

static u32 resistance_find_index(const resistance_registry* reg,
                                 u64 resistance_id,
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
        if (reg->states[i].resistance_id == resistance_id) {
            if (out_found) {
                *out_found = 1;
            }
            return i;
        }
        if (reg->states[i].resistance_id > resistance_id) {
            break;
        }
    }
    return i;
}

resistance_state* resistance_find(resistance_registry* reg,
                                  u64 resistance_id)
{
    int found = 0;
    u32 idx;
    if (!reg || !reg->states) {
        return 0;
    }
    idx = resistance_find_index(reg, resistance_id, &found);
    if (!found) {
        return 0;
    }
    return &reg->states[idx];
}

resistance_state* resistance_find_by_territory(resistance_registry* reg,
                                               u64 territory_id)
{
    u32 i;
    resistance_state* best = 0;
    if (!reg || !reg->states || territory_id == 0u) {
        return 0;
    }
    for (i = 0u; i < reg->count; ++i) {
        resistance_state* cur = &reg->states[i];
        if (cur->territory_id != territory_id) {
            continue;
        }
        if (!best || cur->resistance_id < best->resistance_id) {
            best = cur;
        }
    }
    return best;
}

int resistance_register(resistance_registry* reg,
                        const resistance_state* input,
                        u64* out_id)
{
    int found = 0;
    u32 idx;
    u32 i;
    resistance_state* entry;
    u64 resistance_id;
    if (!reg || !reg->states || !input) {
        return -1;
    }
    if (reg->count >= reg->capacity) {
        return -2;
    }
    resistance_id = input->resistance_id;
    if (resistance_id == 0u) {
        resistance_id = reg->next_id++;
        if (resistance_id == 0u) {
            resistance_id = reg->next_id++;
        }
    }
    idx = resistance_find_index(reg, resistance_id, &found);
    if (found) {
        return -3;
    }
    for (i = reg->count; i > idx; --i) {
        reg->states[i] = reg->states[i - 1u];
    }
    entry = &reg->states[idx];
    memset(entry, 0, sizeof(*entry));
    *entry = *input;
    entry->resistance_id = resistance_id;
    if (entry->activation_threshold == 0u) {
        entry->activation_threshold = 400u;
    }
    if (entry->suppression_threshold == 0u) {
        entry->suppression_threshold = 150u;
    }
    if (entry->pressure_decay == 0u) {
        entry->pressure_decay = 25u;
    }
    if (entry->pressure_gain_base == 0u) {
        entry->pressure_gain_base = 25u;
    }
    if (entry->next_due_tick == 0u) {
        entry->next_due_tick = DOM_TIME_ACT_MAX;
    }
    if (entry->provenance_ref == 0u) {
        entry->provenance_ref = resistance_id;
    }
    reg->count += 1u;
    if (out_id) {
        *out_id = resistance_id;
    }
    return 0;
}

int resistance_set_next_due(resistance_registry* reg,
                            u64 resistance_id,
                            dom_act_time_t next_due_tick)
{
    resistance_state* state = resistance_find(reg, resistance_id);
    if (!state) {
        return -1;
    }
    state->next_due_tick = next_due_tick;
    return 0;
}

static u32 resistance_compute_deprivation(const resistance_state* state,
                                          resistance_update_context* ctx)
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
    if (score > RESISTANCE_SCALE) {
        score = RESISTANCE_SCALE;
    }
    return score;
}

int resistance_apply_update(resistance_state* state,
                            const occupation_state* occupation,
                            resistance_update_context* ctx)
{
    u32 pressure;
    u32 add = 0u;
    u32 decay;
    u32 deprivation;
    legitimacy_state* legit = 0;
    if (!state || !ctx) {
        return -1;
    }
    pressure = state->resistance_pressure;
    if (occupation) {
        state->coercion_level = occupation->coercion_level;
    }
    if (ctx->legitimacy && state->legitimacy_id != 0u) {
        legit = legitimacy_find(ctx->legitimacy, state->legitimacy_id);
        if (legit && legit->value < state->legitimacy_min) {
            u32 deficit = state->legitimacy_min - legit->value;
            add += state->pressure_gain_base + (deficit / 10u);
        }
    }
    deprivation = resistance_compute_deprivation(state, ctx);
    if (deprivation > state->deprivation_threshold) {
        add += state->pressure_gain_base + ((deprivation - state->deprivation_threshold) / 10u);
    }
    if (state->coercion_level > state->coercion_threshold) {
        add += (state->coercion_level - state->coercion_threshold) / 10u;
    }
    if (add > 0u) {
        u64 next = (u64)pressure + (u64)add;
        pressure = (next > RESISTANCE_SCALE) ? RESISTANCE_SCALE : (u32)next;
    } else {
        decay = state->pressure_decay;
        if (pressure > decay) {
            pressure -= decay;
        } else {
            pressure = 0u;
        }
    }
    state->resistance_pressure = pressure;
    if (pressure >= state->activation_threshold) {
        state->status = RESISTANCE_STATUS_ACTIVE;
    } else if (pressure <= state->suppression_threshold) {
        state->status = RESISTANCE_STATUS_SUPPRESSED;
    } else {
        state->status = RESISTANCE_STATUS_LATENT;
    }
    if (state->update_interval == 0u) {
        state->next_due_tick = DOM_TIME_ACT_MAX;
    } else {
        state->next_due_tick = ctx->now_act + state->update_interval;
    }
    return 0;
}

int resistance_estimate_from_view(const dom_epistemic_view* view,
                                  const resistance_state* actual,
                                  resistance_estimate* out)
{
    int is_known = 0;
    if (!out || !actual) {
        return -1;
    }
    if (view && view->state == DOM_EPI_KNOWN && !view->is_uncertain) {
        is_known = 1;
    }
    if (is_known) {
        out->pressure = actual->resistance_pressure;
        out->status = actual->status;
        out->uncertainty_q16 = view ? view->uncertainty_q16 : 0u;
        out->is_exact = 1;
        return 0;
    }
    out->pressure = resistance_bucket_u32(actual->resistance_pressure, 50u);
    out->status = actual->status;
    out->uncertainty_q16 = view ? view->uncertainty_q16 : 0xFFFFu;
    out->is_exact = 0;
    return 0;
}
