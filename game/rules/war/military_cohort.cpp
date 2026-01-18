/*
FILE: game/rules/war/military_cohort.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Game / war rules
RESPONSIBILITY: Implements military cohort registries and count updates.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Cohort ordering and updates are deterministic.
*/
#include "dominium/rules/war/military_cohort.h"

#include <string.h>

void military_cohort_registry_init(military_cohort_registry* reg,
                                   military_cohort* storage,
                                   u32 capacity)
{
    if (!reg) {
        return;
    }
    reg->cohorts = storage;
    reg->count = 0u;
    reg->capacity = capacity;
    if (storage && capacity > 0u) {
        memset(storage, 0, sizeof(military_cohort) * (size_t)capacity);
    }
}

static u32 military_cohort_find_index(const military_cohort_registry* reg,
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

military_cohort* military_cohort_find(military_cohort_registry* reg,
                                      u64 cohort_id)
{
    int found = 0;
    u32 idx;
    if (!reg || !reg->cohorts) {
        return 0;
    }
    idx = military_cohort_find_index(reg, cohort_id, &found);
    if (!found) {
        return 0;
    }
    return &reg->cohorts[idx];
}

int military_cohort_register(military_cohort_registry* reg,
                             u64 cohort_id,
                             u64 assigned_force_id,
                             u32 count,
                             u32 role,
                             u64 casualty_tracking_ref)
{
    int found = 0;
    u32 idx;
    u32 i;
    military_cohort* entry;
    if (!reg || !reg->cohorts || cohort_id == 0u) {
        return -1;
    }
    if (reg->count >= reg->capacity) {
        return -2;
    }
    idx = military_cohort_find_index(reg, cohort_id, &found);
    if (found) {
        return -3;
    }
    for (i = reg->count; i > idx; --i) {
        reg->cohorts[i] = reg->cohorts[i - 1u];
    }
    entry = &reg->cohorts[idx];
    memset(entry, 0, sizeof(*entry));
    entry->cohort_id = cohort_id;
    entry->assigned_force_id = assigned_force_id;
    entry->count = count;
    entry->role = role;
    entry->casualty_tracking_ref = casualty_tracking_ref ? casualty_tracking_ref : cohort_id;
    reg->count += 1u;
    return 0;
}

int military_cohort_adjust_count(military_cohort_registry* reg,
                                 u64 cohort_id,
                                 i32 delta,
                                 u32* out_count)
{
    military_cohort* cohort = military_cohort_find(reg, cohort_id);
    if (!cohort) {
        return -1;
    }
    if (delta < 0) {
        u32 remove = (u32)(-delta);
        if (remove > cohort->count) {
            return -2;
        }
        cohort->count -= remove;
    } else {
        cohort->count += (u32)delta;
    }
    if (out_count) {
        *out_count = cohort->count;
    }
    return 0;
}

int military_cohort_release(military_cohort_registry* reg,
                            u64 cohort_id)
{
    military_cohort* cohort = military_cohort_find(reg, cohort_id);
    if (!cohort) {
        return -1;
    }
    cohort->assigned_force_id = 0u;
    cohort->count = 0u;
    cohort->role = MILITARY_ROLE_INFANTRY;
    return 0;
}
