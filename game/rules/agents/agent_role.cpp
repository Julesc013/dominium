/*
FILE: game/agents/agent_role.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Game / agents
RESPONSIBILITY: Implements agent role registry logic.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Role ordering is deterministic by role_id.
*/
#include "dominium/agents/agent_role.h"

#include <string.h>

void agent_role_registry_init(agent_role_registry* reg,
                              agent_role* storage,
                              u32 capacity)
{
    if (!reg) {
        return;
    }
    reg->roles = storage;
    reg->count = 0u;
    reg->capacity = capacity;
    if (storage && capacity > 0u) {
        memset(storage, 0, sizeof(agent_role) * (size_t)capacity);
    }
}

static u32 agent_role_find_index(const agent_role_registry* reg,
                                 u64 role_id,
                                 int* out_found)
{
    u32 i;
    if (out_found) {
        *out_found = 0;
    }
    if (!reg || !reg->roles) {
        return 0u;
    }
    for (i = 0u; i < reg->count; ++i) {
        if (reg->roles[i].role_id == role_id) {
            if (out_found) {
                *out_found = 1;
            }
            return i;
        }
        if (reg->roles[i].role_id > role_id) {
            break;
        }
    }
    return i;
}

agent_role* agent_role_find(agent_role_registry* reg,
                            u64 role_id)
{
    int found = 0;
    u32 idx;
    if (!reg || !reg->roles) {
        return 0;
    }
    idx = agent_role_find_index(reg, role_id, &found);
    if (!found) {
        return 0;
    }
    return &reg->roles[idx];
}

int agent_role_register(agent_role_registry* reg,
                        u64 role_id,
                        u64 default_doctrine_ref,
                        u32 authority_requirements,
                        u32 capability_requirements)
{
    int found = 0;
    u32 idx;
    u32 i;
    agent_role* entry;
    if (!reg || !reg->roles || role_id == 0u) {
        return -1;
    }
    if (reg->count >= reg->capacity) {
        return -2;
    }
    idx = agent_role_find_index(reg, role_id, &found);
    if (found) {
        return -3;
    }
    for (i = reg->count; i > idx; --i) {
        reg->roles[i] = reg->roles[i - 1u];
    }
    entry = &reg->roles[idx];
    memset(entry, 0, sizeof(*entry));
    entry->role_id = role_id;
    entry->default_doctrine_ref = default_doctrine_ref;
    entry->authority_requirements = authority_requirements;
    entry->capability_requirements = capability_requirements;
    reg->count += 1u;
    return 0;
}

int agent_role_requirements_ok(const agent_role* role,
                               u32 authority_mask,
                               u32 capability_mask)
{
    if (!role) {
        return 0;
    }
    if ((authority_mask & role->authority_requirements) != role->authority_requirements) {
        return 0;
    }
    if ((capability_mask & role->capability_requirements) != role->capability_requirements) {
        return 0;
    }
    return 1;
}
