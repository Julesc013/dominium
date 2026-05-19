/*
FILE: game/agents/agent_authority.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Game / agents
RESPONSIBILITY: Implements authority grant registries and resolution.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Grants ordered by grant_id.
*/
#include "dominium/agents/agent_authority.h"

#include <string.h>

void agent_authority_registry_init(agent_authority_registry* reg,
                                   agent_authority_grant* storage,
                                   u32 capacity)
{
    if (!reg) {
        return;
    }
    reg->entries = storage;
    reg->count = 0u;
    reg->capacity = capacity;
    if (storage && capacity > 0u) {
        memset(storage, 0, sizeof(agent_authority_grant) * (size_t)capacity);
    }
}

static u32 agent_authority_find_index(const agent_authority_registry* reg,
                                      u64 grant_id,
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
        if (reg->entries[i].grant_id == grant_id) {
            if (out_found) {
                *out_found = 1;
            }
            return i;
        }
        if (reg->entries[i].grant_id > grant_id) {
            break;
        }
    }
    return i;
}

agent_authority_grant* agent_authority_find(agent_authority_registry* reg,
                                            u64 grant_id)
{
    int found = 0;
    u32 idx;
    if (!reg || !reg->entries) {
        return 0;
    }
    idx = agent_authority_find_index(reg, grant_id, &found);
    if (!found) {
        return 0;
    }
    return &reg->entries[idx];
}

int agent_authority_grant_register(agent_authority_registry* reg,
                                   u64 grant_id,
                                   u64 granter_id,
                                   u64 grantee_id,
                                   u32 authority_mask,
                                   dom_act_time_t expiry_act,
                                   dom_provenance_id provenance_id)
{
    int found = 0;
    u32 idx;
    u32 i;
    agent_authority_grant* entry;
    if (!reg || !reg->entries || grant_id == 0u || grantee_id == 0u) {
        return -1;
    }
    if (reg->count >= reg->capacity) {
        return -2;
    }
    idx = agent_authority_find_index(reg, grant_id, &found);
    if (found) {
        return -3;
    }
    for (i = reg->count; i > idx; --i) {
        reg->entries[i] = reg->entries[i - 1u];
    }
    entry = &reg->entries[idx];
    memset(entry, 0, sizeof(*entry));
    entry->grant_id = grant_id;
    entry->granter_id = granter_id;
    entry->grantee_id = grantee_id;
    entry->authority_mask = authority_mask;
    entry->expiry_act = expiry_act;
    entry->revoked = 0u;
    entry->provenance_id = provenance_id ? provenance_id : grant_id;
    reg->count += 1u;
    return 0;
}

int agent_authority_grant_revoke(agent_authority_registry* reg,
                                 u64 grant_id)
{
    agent_authority_grant* entry = agent_authority_find(reg, grant_id);
    if (!entry) {
        return -1;
    }
    entry->revoked = 1u;
    return 0;
}

u32 agent_authority_effective_mask(const agent_authority_registry* reg,
                                   u64 grantee_id,
                                   u32 base_mask,
                                   dom_act_time_t now_act)
{
    u32 mask = base_mask;
    u32 i;
    if (!reg || !reg->entries || grantee_id == 0u) {
        return mask;
    }
    for (i = 0u; i < reg->count; ++i) {
        const agent_authority_grant* grant = &reg->entries[i];
        if (grant->grantee_id != grantee_id) {
            continue;
        }
        if (grant->revoked) {
            continue;
        }
        if (grant->expiry_act != 0u && grant->expiry_act <= now_act) {
            continue;
        }
        mask |= grant->authority_mask;
    }
    return mask;
}
