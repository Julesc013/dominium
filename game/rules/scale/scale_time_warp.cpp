/*
FILE: game/rules/scale/scale_time_warp.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Game / scale
RESPONSIBILITY: Implements deterministic scale-aware time warp policies.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Warp resolution is deterministic and integer-based.
*/
#include "dominium/rules/scale/scale_time_warp.h"

#include <string.h>

void scale_time_warp_registry_init(scale_time_warp_registry* reg,
                                   scale_time_warp_policy* storage,
                                   u32 capacity)
{
    if (!reg) {
        return;
    }
    reg->policies = storage;
    reg->count = 0u;
    reg->capacity = capacity;
    if (storage && capacity > 0u) {
        memset(storage, 0, sizeof(scale_time_warp_policy) * (size_t)capacity);
    }
}

static u32 scale_time_warp_find_index(const scale_time_warp_registry* reg,
                                      u64 policy_id,
                                      int* out_found)
{
    u32 i;
    if (out_found) {
        *out_found = 0;
    }
    if (!reg || !reg->policies) {
        return 0u;
    }
    for (i = 0u; i < reg->count; ++i) {
        if (reg->policies[i].policy_id == policy_id) {
            if (out_found) {
                *out_found = 1;
            }
            return i;
        }
        if (reg->policies[i].policy_id > policy_id) {
            break;
        }
    }
    return i;
}

int scale_time_warp_register(scale_time_warp_registry* reg,
                             u64 policy_id,
                             u64 domain_id,
                             u32 min_warp,
                             u32 max_warp,
                             u32 interest_cap)
{
    int found = 0;
    u32 idx;
    u32 i;
    scale_time_warp_policy* entry;
    if (!reg || !reg->policies) {
        return -1;
    }
    if (reg->count >= reg->capacity) {
        return -2;
    }
    idx = scale_time_warp_find_index(reg, policy_id, &found);
    if (found) {
        return -3;
    }
    for (i = reg->count; i > idx; --i) {
        reg->policies[i] = reg->policies[i - 1u];
    }
    entry = &reg->policies[idx];
    memset(entry, 0, sizeof(*entry));
    entry->policy_id = policy_id;
    entry->domain_id = domain_id;
    entry->min_warp = min_warp;
    entry->max_warp = max_warp;
    entry->interest_cap = interest_cap;
    reg->count += 1u;
    return 0;
}

scale_time_warp_policy* scale_time_warp_find(scale_time_warp_registry* reg,
                                             u64 policy_id)
{
    int found = 0;
    u32 idx;
    if (!reg || !reg->policies) {
        return 0;
    }
    idx = scale_time_warp_find_index(reg, policy_id, &found);
    if (!found) {
        return 0;
    }
    return &reg->policies[idx];
}

scale_time_warp_policy* scale_time_warp_find_domain(scale_time_warp_registry* reg,
                                                    u64 domain_id)
{
    u32 i;
    if (!reg || !reg->policies) {
        return 0;
    }
    for (i = 0u; i < reg->count; ++i) {
        if (reg->policies[i].domain_id == domain_id) {
            return &reg->policies[i];
        }
    }
    return 0;
}

static u32 scale_time_warp_clamp(u32 value, u32 min_warp, u32 max_warp)
{
    if (value < min_warp) {
        return min_warp;
    }
    if (value > max_warp) {
        return max_warp;
    }
    return value;
}

u32 scale_time_warp_resolve(const scale_time_warp_policy* policy,
                            u32 requested_warp,
                            int has_interest)
{
    u32 min_warp;
    u32 max_warp;
    u32 cap;
    if (!policy) {
        if (requested_warp == 0u) {
            return 1u;
        }
        return requested_warp;
    }
    min_warp = policy->min_warp ? policy->min_warp : 1u;
    max_warp = policy->max_warp ? policy->max_warp : min_warp;
    cap = policy->interest_cap ? policy->interest_cap : max_warp;
    if (requested_warp == 0u) {
        requested_warp = 1u;
    }
    if (has_interest) {
        max_warp = scale_time_warp_clamp(cap, min_warp, max_warp);
    }
    return scale_time_warp_clamp(requested_warp, min_warp, max_warp);
}
