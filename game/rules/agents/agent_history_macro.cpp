/*
FILE: game/agents/agent_history_macro.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Game / agents
RESPONSIBILITY: Aggregates macro-history records from audit logs.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Output order is stable and reproducible.
*/
#include "dominium/agents/agent_history_macro.h"

#include <string.h>

void agent_history_buffer_init(agent_history_buffer* buffer,
                               agent_history_record* storage,
                               u32 capacity,
                               u64 start_id)
{
    if (!buffer) {
        return;
    }
    buffer->entries = storage;
    buffer->count = 0u;
    buffer->capacity = capacity;
    buffer->next_id = start_id ? start_id : 1u;
    if (storage && capacity > 0u) {
        memset(storage, 0, sizeof(agent_history_record) * (size_t)capacity);
    }
}

void agent_history_buffer_reset(agent_history_buffer* buffer)
{
    if (!buffer) {
        return;
    }
    buffer->count = 0u;
}

static int agent_history_append(agent_history_buffer* buffer,
                                const dom_agent_audit_entry* entry,
                                u64 narrative_id,
                                u32 flags)
{
    agent_history_record* out;
    if (!buffer || !buffer->entries || !entry) {
        return -1;
    }
    if (buffer->count >= buffer->capacity) {
        return -2;
    }
    out = &buffer->entries[buffer->count++];
    memset(out, 0, sizeof(*out));
    out->history_id = buffer->next_id++;
    out->source_event_id = entry->event_id;
    out->narrative_id = narrative_id;
    out->agent_id = entry->agent_id;
    out->institution_id = entry->related_id;
    out->subject_id = entry->subject_id;
    out->act_time = entry->act_time;
    out->kind = entry->kind;
    out->flags = flags;
    out->amount = entry->amount;
    return 0;
}

u32 agent_history_aggregate(const dom_agent_audit_log* audit,
                            const agent_history_policy* policy,
                            agent_history_buffer* out_history)
{
    u32 i;
    u32 written = 0u;
    u32 include_objective = 1u;
    if (!audit || !audit->entries || !out_history) {
        return 0u;
    }
    if (policy) {
        include_objective = policy->include_objective ? 1u : 0u;
    }
    for (i = 0u; i < audit->count; ++i) {
        const dom_agent_audit_entry* entry = &audit->entries[i];
        if (include_objective) {
            if (agent_history_append(out_history, entry, 0u, AGENT_HISTORY_FLAG_NONE) == 0) {
                written += 1u;
            }
        }
        if (policy && policy->narrative_ids && policy->narrative_count > 0u) {
            u32 n;
            for (n = 0u; n < policy->narrative_count; ++n) {
                u64 narrative_id = policy->narrative_ids[n];
                u32 flags = AGENT_HISTORY_FLAG_PROPAGANDA;
                if (entry->amount < 0) {
                    flags |= AGENT_HISTORY_FLAG_LOST;
                }
                if (agent_history_append(out_history, entry, narrative_id, flags) == 0) {
                    written += 1u;
                }
            }
        }
    }
    return written;
}
