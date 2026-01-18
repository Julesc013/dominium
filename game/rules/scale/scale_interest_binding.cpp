/*
FILE: game/rules/scale/scale_interest_binding.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Game / scale
RESPONSIBILITY: Implements deterministic interest bindings across scale domains.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Interest ordering and checks are deterministic.
*/
#include "dominium/rules/scale/scale_interest_binding.h"

#include <string.h>

void scale_interest_registry_init(scale_interest_registry* reg,
                                  scale_interest_binding* storage,
                                  u32 capacity)
{
    if (!reg) {
        return;
    }
    reg->bindings = storage;
    reg->count = 0u;
    reg->capacity = capacity;
    if (storage && capacity > 0u) {
        memset(storage, 0, sizeof(scale_interest_binding) * (size_t)capacity);
    }
}

static u32 scale_interest_find_index(const scale_interest_registry* reg,
                                     u64 binding_id,
                                     int* out_found)
{
    u32 i;
    if (out_found) {
        *out_found = 0;
    }
    if (!reg || !reg->bindings) {
        return 0u;
    }
    for (i = 0u; i < reg->count; ++i) {
        if (reg->bindings[i].binding_id == binding_id) {
            if (out_found) {
                *out_found = 1;
            }
            return i;
        }
        if (reg->bindings[i].binding_id > binding_id) {
            break;
        }
    }
    return i;
}

int scale_interest_register(scale_interest_registry* reg,
                            u64 binding_id,
                            u64 domain_id,
                            u64 object_id,
                            u32 strength,
                            u32 pinned)
{
    int found = 0;
    u32 idx;
    u32 i;
    scale_interest_binding* entry;
    if (!reg || !reg->bindings) {
        return -1;
    }
    if (reg->count >= reg->capacity) {
        return -2;
    }
    idx = scale_interest_find_index(reg, binding_id, &found);
    if (found) {
        return -3;
    }
    for (i = reg->count; i > idx; --i) {
        reg->bindings[i] = reg->bindings[i - 1u];
    }
    entry = &reg->bindings[idx];
    memset(entry, 0, sizeof(*entry));
    entry->binding_id = binding_id;
    entry->domain_id = domain_id;
    entry->object_id = object_id;
    entry->strength = strength;
    entry->pinned = pinned;
    reg->count += 1u;
    return 0;
}

scale_interest_binding* scale_interest_find(scale_interest_registry* reg,
                                            u64 binding_id)
{
    int found = 0;
    u32 idx;
    if (!reg || !reg->bindings) {
        return 0;
    }
    idx = scale_interest_find_index(reg, binding_id, &found);
    if (!found) {
        return 0;
    }
    return &reg->bindings[idx];
}

int scale_interest_set_strength(scale_interest_registry* reg,
                                u64 binding_id,
                                u32 strength)
{
    scale_interest_binding* binding = scale_interest_find(reg, binding_id);
    if (!binding) {
        return -1;
    }
    binding->strength = strength;
    return 0;
}

int scale_interest_set_pinned(scale_interest_registry* reg,
                              u64 binding_id,
                              u32 pinned)
{
    scale_interest_binding* binding = scale_interest_find(reg, binding_id);
    if (!binding) {
        return -1;
    }
    binding->pinned = pinned;
    return 0;
}

int scale_interest_domain_active(const scale_interest_registry* reg,
                                 u64 domain_id,
                                 u32 threshold)
{
    u32 i;
    if (!reg || !reg->bindings) {
        return 0;
    }
    for (i = 0u; i < reg->count; ++i) {
        if (reg->bindings[i].domain_id != domain_id) {
            continue;
        }
        if (reg->bindings[i].strength >= threshold) {
            return 1;
        }
        if (reg->bindings[i].pinned) {
            return 1;
        }
    }
    return 0;
}

int scale_interest_should_refine(const scale_interest_registry* reg,
                                 u64 domain_id,
                                 u32 threshold)
{
    if (!reg) {
        return 0;
    }
    return scale_interest_domain_active(reg, domain_id, threshold);
}
