/*
FILE: game/rules/survival/needs_model.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Game / survival rules
RESPONSIBILITY: Implements deterministic needs state registries.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Needs updates are deterministic.
*/
#include "dominium/rules/survival/needs_model.h"

#include <string.h>

void survival_needs_registry_init(survival_needs_registry* reg,
                                  survival_needs_entry* storage,
                                  u32 capacity)
{
    if (!reg) {
        return;
    }
    reg->entries = storage;
    reg->count = 0u;
    reg->capacity = capacity;
    if (storage && capacity > 0u) {
        memset(storage, 0, sizeof(survival_needs_entry) * (size_t)capacity);
    }
}

int survival_needs_register(survival_needs_registry* reg,
                            u64 cohort_id,
                            const survival_needs_state* initial)
{
    survival_needs_entry* entry;
    u32 i;
    if (!reg || !reg->entries) {
        return -1;
    }
    if (reg->count >= reg->capacity) {
        return -2;
    }
    for (i = 0u; i < reg->count; ++i) {
        if (reg->entries[i].cohort_id == cohort_id) {
            return -3;
        }
    }
    entry = &reg->entries[reg->count++];
    memset(entry, 0, sizeof(*entry));
    entry->cohort_id = cohort_id;
    if (initial) {
        entry->state = *initial;
    } else {
        entry->state.food_store = 0u;
        entry->state.water_store = 0u;
        entry->state.shelter_level = 0u;
        entry->state.hunger_level = 0u;
        entry->state.thirst_level = 0u;
        entry->state.last_consumption_tick = 0;
        entry->state.next_consumption_tick = DOM_TIME_ACT_MAX;
        entry->state.last_production_provenance = 0u;
    }
    return 0;
}

survival_needs_state* survival_needs_get(survival_needs_registry* reg,
                                         u64 cohort_id)
{
    u32 i;
    if (!reg || !reg->entries) {
        return 0;
    }
    for (i = 0u; i < reg->count; ++i) {
        if (reg->entries[i].cohort_id == cohort_id) {
            return &reg->entries[i].state;
        }
    }
    return 0;
}

void survival_needs_params_default(survival_needs_params* params)
{
    if (!params) {
        return;
    }
    params->food_per_person = 1u;
    params->water_per_person = 1u;
    params->hunger_max = 10u;
    params->thirst_max = 6u;
    params->shelter_min = 1u;
    params->shelter_max = 5u;
    params->consumption_interval = 10;
}

int survival_needs_resources_sufficient(const survival_needs_state* state,
                                        const survival_needs_params* params,
                                        u32 cohort_count)
{
    u64 food_need;
    u64 water_need;
    if (!state || !params) {
        return 0;
    }
    food_need = (u64)params->food_per_person * (u64)cohort_count;
    water_need = (u64)params->water_per_person * (u64)cohort_count;
    if (state->food_store < food_need) {
        return 0;
    }
    if (state->water_store < water_need) {
        return 0;
    }
    if (state->shelter_level < params->shelter_min) {
        return 0;
    }
    return 1;
}
