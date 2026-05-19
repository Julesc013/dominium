/*
FILE: game/agents/agent_conflict.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Game / agents
RESPONSIBILITY: Implements conflict registries and resolution.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Conflicts ordered by conflict_id.
*/
#include "dominium/agents/agent_conflict.h"

#include <string.h>

void agent_conflict_registry_init(agent_conflict_registry* reg,
                                  agent_conflict* storage,
                                  u32 capacity)
{
    if (!reg) {
        return;
    }
    reg->entries = storage;
    reg->count = 0u;
    reg->capacity = capacity;
    if (storage && capacity > 0u) {
        memset(storage, 0, sizeof(agent_conflict) * (size_t)capacity);
    }
}

static u32 agent_conflict_find_index(const agent_conflict_registry* reg,
                                     u64 conflict_id,
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
        if (reg->entries[i].conflict_id == conflict_id) {
            if (out_found) {
                *out_found = 1;
            }
            return i;
        }
        if (reg->entries[i].conflict_id > conflict_id) {
            break;
        }
    }
    return i;
}

agent_conflict* agent_conflict_find(agent_conflict_registry* reg,
                                    u64 conflict_id)
{
    int found = 0;
    u32 idx;
    if (!reg || !reg->entries) {
        return 0;
    }
    idx = agent_conflict_find_index(reg, conflict_id, &found);
    if (!found) {
        return 0;
    }
    return &reg->entries[idx];
}

int agent_conflict_register(agent_conflict_registry* reg,
                            u64 conflict_id,
                            u64 party_a_id,
                            u64 party_b_id,
                            u64 subject_id,
                            dom_act_time_t started_act,
                            dom_provenance_id provenance_id)
{
    int found = 0;
    u32 idx;
    u32 i;
    agent_conflict* entry;
    if (!reg || !reg->entries || conflict_id == 0u) {
        return -1;
    }
    if (reg->count >= reg->capacity) {
        return -2;
    }
    idx = agent_conflict_find_index(reg, conflict_id, &found);
    if (found) {
        return -3;
    }
    for (i = reg->count; i > idx; --i) {
        reg->entries[i] = reg->entries[i - 1u];
    }
    entry = &reg->entries[idx];
    memset(entry, 0, sizeof(*entry));
    entry->conflict_id = conflict_id;
    entry->party_a_id = party_a_id;
    entry->party_b_id = party_b_id;
    entry->subject_id = subject_id;
    entry->status = AGENT_CONFLICT_ACTIVE;
    entry->started_act = started_act;
    entry->resolved_act = 0u;
    entry->provenance_id = provenance_id ? provenance_id : conflict_id;
    entry->flags = 0u;
    reg->count += 1u;
    return 0;
}

int agent_conflict_resolve(agent_conflict* conflict,
                           dom_act_time_t resolved_act)
{
    if (!conflict) {
        return -1;
    }
    conflict->status = AGENT_CONFLICT_RESOLVED;
    conflict->resolved_act = resolved_act;
    return 0;
}
