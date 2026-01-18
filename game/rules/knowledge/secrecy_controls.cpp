/*
FILE: game/rules/knowledge/secrecy_controls.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Game / knowledge
RESPONSIBILITY: Implements secrecy policies for knowledge diffusion.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Secrecy decisions are deterministic.
*/
#include "dominium/rules/knowledge/secrecy_controls.h"

#include <string.h>

void knowledge_secrecy_registry_init(knowledge_secrecy_registry* reg,
                                     knowledge_secrecy_policy* storage,
                                     u32 capacity)
{
    if (!reg) {
        return;
    }
    reg->policies = storage;
    reg->count = 0u;
    reg->capacity = capacity;
    if (storage && capacity > 0u) {
        memset(storage, 0, sizeof(knowledge_secrecy_policy) * (size_t)capacity);
    }
}

static u32 knowledge_secrecy_find_index(const knowledge_secrecy_registry* reg,
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

int knowledge_secrecy_register(knowledge_secrecy_registry* reg,
                               u64 policy_id,
                               u32 allow_diffusion,
                               u32 min_fidelity)
{
    int found = 0;
    u32 idx;
    u32 i;
    knowledge_secrecy_policy* entry;
    if (!reg || !reg->policies) {
        return -1;
    }
    if (reg->count >= reg->capacity) {
        return -2;
    }
    idx = knowledge_secrecy_find_index(reg, policy_id, &found);
    if (found) {
        return -3;
    }
    for (i = reg->count; i > idx; --i) {
        reg->policies[i] = reg->policies[i - 1u];
    }
    entry = &reg->policies[idx];
    memset(entry, 0, sizeof(*entry));
    entry->policy_id = policy_id;
    entry->allow_diffusion = allow_diffusion;
    entry->min_fidelity = min_fidelity;
    reg->count += 1u;
    return 0;
}

knowledge_secrecy_policy* knowledge_secrecy_find(knowledge_secrecy_registry* reg,
                                                 u64 policy_id)
{
    int found = 0;
    u32 idx;
    if (!reg || !reg->policies) {
        return 0;
    }
    idx = knowledge_secrecy_find_index(reg, policy_id, &found);
    if (!found) {
        return 0;
    }
    return &reg->policies[idx];
}

int knowledge_secrecy_allows(const knowledge_secrecy_policy* policy,
                             u32 fidelity)
{
    if (!policy) {
        return 1;
    }
    if (!policy->allow_diffusion) {
        return 0;
    }
    if (fidelity < policy->min_fidelity) {
        return 0;
    }
    return 1;
}
