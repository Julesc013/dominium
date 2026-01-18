/*
FILE: game/rules/governance/org_governance_binding.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Game / governance
RESPONSIBILITY: Implements organization to jurisdiction bindings.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Binding order is stable and deterministic.
*/
#include "dominium/rules/governance/org_governance_binding.h"

#include <string.h>

void org_governance_registry_init(org_governance_registry* reg,
                                  org_governance_binding* storage,
                                  u32 capacity)
{
    if (!reg) {
        return;
    }
    reg->bindings = storage;
    reg->count = 0u;
    reg->capacity = capacity;
    if (storage && capacity > 0u) {
        memset(storage, 0, sizeof(org_governance_binding) * (size_t)capacity);
    }
}

static u32 org_governance_find_index(const org_governance_registry* reg,
                                     u64 org_id,
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
        if (reg->bindings[i].org_id == org_id) {
            if (out_found) {
                *out_found = 1;
            }
            return i;
        }
        if (reg->bindings[i].org_id > org_id) {
            break;
        }
    }
    return i;
}

int org_governance_register(org_governance_registry* reg,
                            u64 org_id,
                            u64 jurisdiction_id,
                            u64 legitimacy_ref,
                            u64 enforcement_ref)
{
    int found = 0;
    u32 idx;
    u32 i;
    org_governance_binding* entry;
    if (!reg || !reg->bindings) {
        return -1;
    }
    if (reg->count >= reg->capacity) {
        return -2;
    }
    idx = org_governance_find_index(reg, org_id, &found);
    if (found) {
        return -3;
    }
    for (i = reg->count; i > idx; --i) {
        reg->bindings[i] = reg->bindings[i - 1u];
    }
    entry = &reg->bindings[idx];
    memset(entry, 0, sizeof(*entry));
    entry->org_id = org_id;
    entry->jurisdiction_id = jurisdiction_id;
    entry->legitimacy_ref = legitimacy_ref;
    entry->enforcement_capacity_ref = enforcement_ref;
    reg->count += 1u;
    return 0;
}

org_governance_binding* org_governance_find(org_governance_registry* reg,
                                            u64 org_id)
{
    int found = 0;
    u32 idx;
    if (!reg || !reg->bindings) {
        return 0;
    }
    idx = org_governance_find_index(reg, org_id, &found);
    if (!found) {
        return 0;
    }
    return &reg->bindings[idx];
}
