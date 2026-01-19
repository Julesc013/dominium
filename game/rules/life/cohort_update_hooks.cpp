/*
FILE: game/core/life/cohort_update_hooks.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Game / life
RESPONSIBILITY: Implements cohort aggregation hooks for macro fidelity.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Cohort ordering and counts are deterministic.
*/
#include "dominium/life/cohort_update_hooks.h"

#include <string.h>

void life_cohort_registry_init(life_cohort_registry* reg,
                               life_cohort_entry* storage,
                               u32 capacity)
{
    if (!reg) {
        return;
    }
    reg->entries = storage;
    reg->count = 0u;
    reg->capacity = capacity;
    if (storage && capacity > 0u) {
        memset(storage, 0, sizeof(life_cohort_entry) * (size_t)capacity);
    }
}

static u32 life_cohort_find_index(const life_cohort_registry* reg,
                                  u64 cohort_id,
                                  int* out_found)
{
    u32 i;
    if (out_found) {
        *out_found = 0;
    }
    if (!reg || !reg->entries) {
        return 0u;
    }
    for (i = 0u; i < reg->count; ++i) {
        if (reg->entries[i].cohort_id == cohort_id) {
            if (out_found) {
                *out_found = 1;
            }
            return i;
        }
        if (reg->entries[i].cohort_id > cohort_id) {
            break;
        }
    }
    return i;
}

int life_cohort_add_birth(life_cohort_registry* reg,
                          u64 cohort_id,
                          u64 count)
{
    int found = 0;
    u32 idx;
    u32 i;
    if (!reg || !reg->entries || cohort_id == 0u) {
        return -1;
    }
    idx = life_cohort_find_index(reg, cohort_id, &found);
    if (found) {
        reg->entries[idx].population_count += count;
        return 0;
    }
    if (reg->count >= reg->capacity) {
        return -2;
    }
    for (i = reg->count; i > idx; --i) {
        reg->entries[i] = reg->entries[i - 1u];
    }
    reg->entries[idx].cohort_id = cohort_id;
    reg->entries[idx].population_count = count;
    reg->count += 1u;
    return 0;
}

int life_cohort_get_count(const life_cohort_registry* reg,
                          u64 cohort_id,
                          u64* out_count)
{
    int found = 0;
    u32 idx;
    if (out_count) {
        *out_count = 0u;
    }
    if (!reg || !reg->entries) {
        return 0;
    }
    idx = life_cohort_find_index(reg, cohort_id, &found);
    if (!found) {
        return 0;
    }
    if (out_count) {
        *out_count = reg->entries[idx].population_count;
    }
    return 1;
}
