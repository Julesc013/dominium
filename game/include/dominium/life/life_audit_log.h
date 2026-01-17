/*
FILE: include/dominium/life/life_audit_log.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / life
RESPONSIBILITY: Defines append-only audit log for LIFE events.
ALLOWED DEPENDENCIES: `game/include/**`, `engine/include/**` public headers, and C89/C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; product-layer runtime code.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Log ordering is deterministic.
*/
#ifndef DOMINIUM_LIFE_AUDIT_LOG_H
#define DOMINIUM_LIFE_AUDIT_LOG_H

#include "domino/core/dom_time_core.h"
#include "domino/core/types.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef enum life_audit_kind {
    LIFE_AUDIT_DEATH = 1,
    LIFE_AUDIT_ESTATE = 2,
    LIFE_AUDIT_INHERITANCE = 3,
    LIFE_AUDIT_REFUSAL = 4
} life_audit_kind;

typedef struct life_audit_entry {
    u64 audit_id;
    u32 kind;
    u64 subject_id;
    u64 related_id;
    u32 code;
    dom_act_time_t act_tick;
} life_audit_entry;

typedef struct life_audit_log {
    life_audit_entry* entries;
    u32 count;
    u32 capacity;
    u64 next_id;
} life_audit_log;

void life_audit_log_init(life_audit_log* log,
                         life_audit_entry* storage,
                         u32 capacity,
                         u64 start_id);
int life_audit_log_append(life_audit_log* log, const life_audit_entry* entry);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_LIFE_AUDIT_LOG_H */
