/*
FILE: game/rules/population/household_model.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Game / population rules
RESPONSIBILITY: Implements bounded household membership and deterministic ordering.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Member ordering is deterministic.
*/
#include "dominium/rules/population/household_model.h"

#include <string.h>

void population_household_registry_init(population_household_registry* reg,
                                        population_household* storage,
                                        u32 capacity)
{
    if (!reg) {
        return;
    }
    reg->households = storage;
    reg->count = 0u;
    reg->capacity = capacity;
    if (storage && capacity > 0u) {
        memset(storage, 0, sizeof(population_household) * (size_t)capacity);
    }
}

static u32 population_household_find_index(const population_household_registry* reg,
                                           u64 household_id,
                                           int* out_found)
{
    u32 i;
    if (out_found) {
        *out_found = 0;
    }
    if (!reg || !reg->households) {
        return 0u;
    }
    for (i = 0u; i < reg->count; ++i) {
        if (reg->households[i].household_id == household_id) {
            if (out_found) {
                *out_found = 1;
            }
            return i;
        }
        if (reg->households[i].household_id > household_id) {
            break;
        }
    }
    return i;
}

int population_household_register(population_household_registry* reg,
                                  u64 household_id,
                                  u64 residence_ref,
                                  u64 resource_pool_ref)
{
    int found = 0;
    u32 idx;
    u32 i;
    population_household* entry;

    if (!reg || !reg->households) {
        return -1;
    }
    if (reg->count >= reg->capacity) {
        return -2;
    }
    idx = population_household_find_index(reg, household_id, &found);
    if (found) {
        return -3;
    }
    for (i = reg->count; i > idx; --i) {
        reg->households[i] = reg->households[i - 1u];
    }
    entry = &reg->households[idx];
    memset(entry, 0, sizeof(*entry));
    entry->household_id = household_id;
    entry->residence_ref = residence_ref;
    entry->resource_pool_ref = resource_pool_ref;
    entry->member_count = 0u;
    entry->next_due_tick = DOM_TIME_ACT_MAX;
    reg->count += 1u;
    return 0;
}

population_household* population_household_find(population_household_registry* reg,
                                                u64 household_id)
{
    int found = 0;
    u32 idx;
    if (!reg || !reg->households) {
        return 0;
    }
    idx = population_household_find_index(reg, household_id, &found);
    if (!found) {
        return 0;
    }
    return &reg->households[idx];
}

int population_household_add_member(population_household_registry* reg,
                                    u64 household_id,
                                    u64 person_id,
                                    population_refusal_code* out_refusal)
{
    population_household* household;
    u32 i;
    if (out_refusal) {
        *out_refusal = POP_REFUSAL_NONE;
    }
    household = population_household_find(reg, household_id);
    if (!household) {
        if (out_refusal) {
            *out_refusal = POP_REFUSAL_COHORT_NOT_FOUND;
        }
        return -1;
    }
    if (household->member_count >= POPULATION_HOUSEHOLD_MAX_MEMBERS) {
        if (out_refusal) {
            *out_refusal = POP_REFUSAL_HOUSEHOLD_TOO_LARGE;
        }
        return -2;
    }
    for (i = 0u; i < household->member_count; ++i) {
        if (household->members[i] == person_id) {
            return 0;
        }
        if (household->members[i] > person_id) {
            break;
        }
    }
    if (i < household->member_count) {
        u32 j;
        for (j = household->member_count; j > i; --j) {
            household->members[j] = household->members[j - 1u];
        }
    }
    household->members[i] = person_id;
    household->member_count += 1u;
    return 0;
}

int population_household_remove_member(population_household_registry* reg,
                                       u64 household_id,
                                       u64 person_id)
{
    population_household* household;
    u32 i;
    if (!reg) {
        return -1;
    }
    household = population_household_find(reg, household_id);
    if (!household) {
        return -2;
    }
    for (i = 0u; i < household->member_count; ++i) {
        if (household->members[i] == person_id) {
            u32 j;
            for (j = i + 1u; j < household->member_count; ++j) {
                household->members[j - 1u] = household->members[j];
            }
            household->members[household->member_count - 1u] = 0u;
            household->member_count -= 1u;
            return 0;
        }
    }
    return 1;
}

int population_household_has_member(const population_household* household,
                                    u64 person_id)
{
    u32 i;
    if (!household) {
        return 0;
    }
    for (i = 0u; i < household->member_count; ++i) {
        if (household->members[i] == person_id) {
            return 1;
        }
        if (household->members[i] > person_id) {
            break;
        }
    }
    return 0;
}
