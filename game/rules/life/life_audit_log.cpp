/*
FILE: game/core/life/life_audit_log.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Game / life
RESPONSIBILITY: Implements append-only audit log for LIFE events.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Log ordering is deterministic.
*/
#include "dominium/life/life_audit_log.h"

#include <string.h>

void life_audit_log_init(life_audit_log* log,
                         life_audit_entry* storage,
                         u32 capacity,
                         u64 start_id)
{
    if (!log) {
        return;
    }
    log->entries = storage;
    log->count = 0u;
    log->capacity = capacity;
    log->next_id = start_id ? start_id : 1u;
    if (storage && capacity > 0u) {
        memset(storage, 0, sizeof(life_audit_entry) * (size_t)capacity);
    }
}

int life_audit_log_append(life_audit_log* log, const life_audit_entry* entry)
{
    life_audit_entry* slot;
    if (!log || !entry || !log->entries) {
        return -1;
    }
    if (log->count >= log->capacity) {
        return -2;
    }
    slot = &log->entries[log->count++];
    *slot = *entry;
    slot->audit_id = log->next_id++;
    return 0;
}
