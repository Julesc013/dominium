/*
FILE: game/rules/logistics/transport_capacity.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Game / logistics
RESPONSIBILITY: Implements deterministic transport capacity records.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Capacity updates are deterministic.
*/
#include "dominium/rules/logistics/transport_capacity.h"

#include <string.h>

void transport_capacity_registry_init(transport_capacity_registry* reg,
                                      transport_capacity* storage,
                                      u32 capacity)
{
    if (!reg) {
        return;
    }
    reg->capacities = storage;
    reg->count = 0u;
    reg->capacity = capacity;
    if (storage && capacity > 0u) {
        memset(storage, 0, sizeof(transport_capacity) * (size_t)capacity);
    }
}

static u32 transport_capacity_find_index(const transport_capacity_registry* reg,
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

int transport_capacity_register(transport_capacity_registry* reg,
                                u64 capacity_id,
                                u32 max_qty)
{
    int found = 0;
    u32 idx;
    u32 i;
    transport_capacity* entry;
    if (!reg || !reg->capacities) {
        return -1;
    }
    if (reg->count >= reg->capacity) {
        return -2;
    }
    idx = transport_capacity_find_index(reg, capacity_id, &found);
    if (found) {
        return -3;
    }
    for (i = reg->count; i > idx; --i) {
        reg->capacities[i] = reg->capacities[i - 1u];
    }
    entry = &reg->capacities[idx];
    memset(entry, 0, sizeof(*entry));
    entry->capacity_id = capacity_id;
    entry->max_qty = max_qty;
    entry->available_qty = max_qty;
    reg->count += 1u;
    return 0;
}

transport_capacity* transport_capacity_find(transport_capacity_registry* reg,
                                            u64 capacity_id)
{
    int found = 0;
    u32 idx;
    if (!reg || !reg->capacities) {
        return 0;
    }
    idx = transport_capacity_find_index(reg, capacity_id, &found);
    if (!found) {
        return 0;
    }
    return &reg->capacities[idx];
}

int transport_capacity_reserve(transport_capacity_registry* reg,
                               u64 capacity_id,
                               u32 qty)
{
    transport_capacity* cap = transport_capacity_find(reg, capacity_id);
    if (!cap) {
        return -1;
    }
    if (qty > cap->available_qty) {
        return -2;
    }
    cap->available_qty -= qty;
    return 0;
}

int transport_capacity_release(transport_capacity_registry* reg,
                               u64 capacity_id,
                               u32 qty)
{
    transport_capacity* cap = transport_capacity_find(reg, capacity_id);
    u32 next;
    if (!cap) {
        return -1;
    }
    next = cap->available_qty + qty;
    if (next > cap->max_qty) {
        next = cap->max_qty;
    }
    cap->available_qty = next;
    return 0;
}
