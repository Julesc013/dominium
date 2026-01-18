/*
FILE: game/rules/governance/enforcement_capacity.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Game / governance
RESPONSIBILITY: Implements enforcement capacity records and registries.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Capacity ordering is stable and deterministic.
*/
#include "dominium/rules/governance/enforcement_capacity.h"

#include <string.h>

void enforcement_capacity_registry_init(enforcement_capacity_registry* reg,
                                        enforcement_capacity* storage,
                                        u32 capacity)
{
    if (!reg) {
        return;
    }
    reg->capacities = storage;
    reg->count = 0u;
    reg->capacity = capacity;
    if (storage && capacity > 0u) {
        memset(storage, 0, sizeof(enforcement_capacity) * (size_t)capacity);
    }
}

static u32 enforcement_capacity_find_index(const enforcement_capacity_registry* reg,
                                           u64 capacity_id,
                                           int* out_found)
{
    u32 i;
    if (out_found) {
        *out_found = 0;
    }
    if (!reg || !reg->capacities) {
        return 0u;
    }
    for (i = 0u; i < reg->count; ++i) {
        if (reg->capacities[i].capacity_id == capacity_id) {
            if (out_found) {
                *out_found = 1;
            }
            return i;
        }
        if (reg->capacities[i].capacity_id > capacity_id) {
            break;
        }
    }
    return i;
}

int enforcement_capacity_register(enforcement_capacity_registry* reg,
                                  u64 capacity_id,
                                  u32 enforcers,
                                  u32 coverage_area,
                                  dom_act_time_t response_time,
                                  u64 cost_ref)
{
    int found = 0;
    u32 idx;
    u32 i;
    enforcement_capacity* entry;
    if (!reg || !reg->capacities) {
        return -1;
    }
    if (reg->count >= reg->capacity) {
        return -2;
    }
    idx = enforcement_capacity_find_index(reg, capacity_id, &found);
    if (found) {
        return -3;
    }
    for (i = reg->count; i > idx; --i) {
        reg->capacities[i] = reg->capacities[i - 1u];
    }
    entry = &reg->capacities[idx];
    memset(entry, 0, sizeof(*entry));
    entry->capacity_id = capacity_id;
    entry->available_enforcers = enforcers;
    entry->coverage_area = coverage_area;
    entry->response_time = response_time;
    entry->cost_ref = cost_ref;
    reg->count += 1u;
    return 0;
}

enforcement_capacity* enforcement_capacity_find(enforcement_capacity_registry* reg,
                                                u64 capacity_id)
{
    int found = 0;
    u32 idx;
    if (!reg || !reg->capacities) {
        return 0;
    }
    idx = enforcement_capacity_find_index(reg, capacity_id, &found);
    if (!found) {
        return 0;
    }
    return &reg->capacities[idx];
}
