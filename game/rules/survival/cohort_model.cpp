/*
FILE: game/rules/survival/cohort_model.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Game / survival rules
RESPONSIBILITY: Implements cohort registries for CIV0a survival.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Cohort ordering is stable and deterministic.
*/
#include "dominium/rules/survival/cohort_model.h"

#include <string.h>

void survival_cohort_registry_init(survival_cohort_registry* reg,
                                   survival_cohort* storage,
                                   u32 capacity)
{
    if (!reg) {
        return;
    }
    reg->cohorts = storage;
    reg->count = 0u;
    reg->capacity = capacity;
    if (storage && capacity > 0u) {
        memset(storage, 0, sizeof(survival_cohort) * (size_t)capacity);
    }
}

static u32 survival_cohort_find_index(const survival_cohort_registry* reg,
                                      u64 cohort_id,
                                      int* out_found)
{
    u32 i;
    if (out_found) {
        *out_found = 0;
    }
    if (!reg || !reg->cohorts) {
        return 0u;
    }
    for (i = 0u; i < reg->count; ++i) {
        if (reg->cohorts[i].cohort_id == cohort_id) {
            if (out_found) {
                *out_found = 1;
            }
            return i;
        }
        if (reg->cohorts[i].cohort_id > cohort_id) {
            break;
        }
    }
    return i;
}

int survival_cohort_register(survival_cohort_registry* reg,
                             u64 cohort_id,
                             u32 count,
                             u64 location_ref)
{
    int found = 0;
    u32 idx;
    u32 i;
    survival_cohort* entry;

    if (!reg || !reg->cohorts) {
        return -1;
    }
    if (reg->count >= reg->capacity) {
        return -2;
    }
    idx = survival_cohort_find_index(reg, cohort_id, &found);
    if (found) {
        return -3;
    }
    for (i = reg->count; i > idx; --i) {
        reg->cohorts[i] = reg->cohorts[i - 1u];
    }
    entry = &reg->cohorts[idx];
    memset(entry, 0, sizeof(*entry));
    entry->cohort_id = cohort_id;
    entry->count = count;
    entry->location_ref = location_ref;
    entry->age_bucket = 0u;
    entry->health_bucket = 0u;
    entry->next_due_tick = DOM_TIME_ACT_MAX;
    entry->active_action_id = 0u;
    reg->count += 1u;
    return 0;
}

survival_cohort* survival_cohort_find(survival_cohort_registry* reg, u64 cohort_id)
{
    int found = 0;
    u32 idx;
    if (!reg || !reg->cohorts) {
        return 0;
    }
    idx = survival_cohort_find_index(reg, cohort_id, &found);
    if (!found) {
        return 0;
    }
    return &reg->cohorts[idx];
}

int survival_cohort_adjust_count(survival_cohort_registry* reg,
                                 u64 cohort_id,
                                 i32 delta,
                                 u32* out_count)
{
    survival_cohort* cohort = survival_cohort_find(reg, cohort_id);
    i32 next;
    if (!cohort) {
        return -1;
    }
    next = (i32)cohort->count + delta;
    if (next < 0) {
        next = 0;
    }
    cohort->count = (u32)next;
    if (out_count) {
        *out_count = cohort->count;
    }
    if (cohort->count == 0u) {
        cohort->next_due_tick = DOM_TIME_ACT_MAX;
    }
    return 0;
}

int survival_cohort_set_next_due(survival_cohort_registry* reg,
                                 u64 cohort_id,
                                 dom_act_time_t next_due_tick)
{
    survival_cohort* cohort = survival_cohort_find(reg, cohort_id);
    if (!cohort) {
        return -1;
    }
    cohort->next_due_tick = next_due_tick;
    return 0;
}

int survival_cohort_set_active_action(survival_cohort_registry* reg,
                                      u64 cohort_id,
                                      u64 action_id)
{
    survival_cohort* cohort = survival_cohort_find(reg, cohort_id);
    if (!cohort) {
        return -1;
    }
    cohort->active_action_id = action_id;
    return 0;
}
