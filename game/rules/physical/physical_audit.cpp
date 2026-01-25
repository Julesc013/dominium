/*
FILE: game/rules/physical/physical_audit.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Game / physical
RESPONSIBILITY: Implements deterministic audit logging for physicalization events.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Event ordering is deterministic under identical inputs.
*/
#include "dominium/physical/physical_audit.h"

#include <string.h>

void dom_physical_audit_init(dom_physical_audit_log* log,
                             dom_physical_event* storage,
                             u32 capacity,
                             u64 start_id)
{
    if (!log) {
        return;
    }
    log->entries = storage;
    log->count = 0u;
    log->capacity = capacity;
    log->next_event_id = start_id ? start_id : 1u;
    log->current_act = 0u;
    log->provenance_id = 0u;
    if (storage && capacity > 0u) {
        memset(storage, 0, sizeof(dom_physical_event) * (size_t)capacity);
    }
}

void dom_physical_audit_set_context(dom_physical_audit_log* log,
                                    dom_act_time_t act_time,
                                    dom_provenance_id provenance_id)
{
    if (!log) {
        return;
    }
    log->current_act = act_time;
    log->provenance_id = provenance_id;
}

int dom_physical_audit_record(dom_physical_audit_log* log,
                              u64 actor_id,
                              u32 kind,
                              u64 subject_id,
                              u64 related_id,
                              i64 amount)
{
    dom_physical_event* entry;
    if (!log || !log->entries) {
        return -1;
    }
    if (log->count >= log->capacity) {
        return -2;
    }
    entry = &log->entries[log->count++];
    memset(entry, 0, sizeof(*entry));
    entry->event_id = log->next_event_id++;
    entry->actor_id = actor_id;
    entry->act_time = log->current_act;
    entry->provenance_id = log->provenance_id;
    entry->kind = kind;
    entry->subject_id = subject_id;
    entry->related_id = related_id;
    entry->amount = amount;
    entry->flags = 0u;
    return 0;
}
