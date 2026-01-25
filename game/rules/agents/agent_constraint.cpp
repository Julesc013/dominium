/*
FILE: game/agents/agent_constraint.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Game / agents
RESPONSIBILITY: Implements deterministic constraint evaluation.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Constraints are processed in stable order.
*/
#include "dominium/agents/agent_constraint.h"
#include "dominium/agents/agent_planner.h"

#include <string.h>

void agent_constraint_registry_init(agent_constraint_registry* reg,
                                    agent_constraint* storage,
                                    u32 capacity)
{
    if (!reg) {
        return;
    }
    reg->entries = storage;
    reg->count = 0u;
    reg->capacity = capacity;
    if (storage && capacity > 0u) {
        memset(storage, 0, sizeof(agent_constraint) * (size_t)capacity);
    }
}

static u32 agent_constraint_find_index(const agent_constraint_registry* reg,
                                       u64 constraint_id,
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
        if (reg->entries[i].constraint_id == constraint_id) {
            if (out_found) {
                *out_found = 1;
            }
            return i;
        }
        if (reg->entries[i].constraint_id > constraint_id) {
            break;
        }
    }
    return i;
}

agent_constraint* agent_constraint_find(agent_constraint_registry* reg,
                                        u64 constraint_id)
{
    int found = 0;
    u32 idx;
    if (!reg || !reg->entries) {
        return 0;
    }
    idx = agent_constraint_find_index(reg, constraint_id, &found);
    if (!found) {
        return 0;
    }
    return &reg->entries[idx];
}

int agent_constraint_register(agent_constraint_registry* reg,
                              u64 constraint_id,
                              u64 institution_id,
                              u64 target_agent_id,
                              u32 process_kind_mask,
                              u32 mode,
                              dom_act_time_t expiry_act,
                              dom_provenance_id provenance_id)
{
    int found = 0;
    u32 idx;
    u32 i;
    agent_constraint* entry;
    if (!reg || !reg->entries || constraint_id == 0u) {
        return -1;
    }
    if (reg->count >= reg->capacity) {
        return -2;
    }
    idx = agent_constraint_find_index(reg, constraint_id, &found);
    if (found) {
        return -3;
    }
    for (i = reg->count; i > idx; --i) {
        reg->entries[i] = reg->entries[i - 1u];
    }
    entry = &reg->entries[idx];
    memset(entry, 0, sizeof(*entry));
    entry->constraint_id = constraint_id;
    entry->institution_id = institution_id;
    entry->target_agent_id = target_agent_id;
    entry->process_kind_mask = process_kind_mask;
    entry->mode = mode;
    entry->expiry_act = expiry_act;
    entry->provenance_id = provenance_id ? provenance_id : constraint_id;
    entry->revoked = 0u;
    reg->count += 1u;
    return 0;
}

int agent_constraint_revoke(agent_constraint_registry* reg,
                            u64 constraint_id)
{
    agent_constraint* entry = agent_constraint_find(reg, constraint_id);
    if (!entry) {
        return -1;
    }
    entry->revoked = 1u;
    return 0;
}

int agent_constraint_allows_process(const agent_constraint_registry* reg,
                                    u64 agent_id,
                                    u32 process_kind,
                                    dom_act_time_t now_act,
                                    u64* out_institution_id)
{
    u32 i;
    int denied = 0;
    if (out_institution_id) {
        *out_institution_id = 0u;
    }
    if (!reg || !reg->entries || process_kind == 0u) {
        return 1;
    }
    for (i = 0u; i < reg->count; ++i) {
        const agent_constraint* c = &reg->entries[i];
        if (c->revoked) {
            continue;
        }
        if (c->expiry_act != 0u && c->expiry_act <= now_act) {
            continue;
        }
        if (c->target_agent_id != 0u && c->target_agent_id != agent_id) {
            continue;
        }
        if ((c->process_kind_mask & AGENT_PROCESS_KIND_BIT(process_kind)) == 0u) {
            continue;
        }
        if (c->mode == AGENT_CONSTRAINT_DENY) {
            denied = 1;
            if (out_institution_id) {
                *out_institution_id = c->institution_id;
            }
            break;
        }
    }
    return denied ? 0 : 1;
}
