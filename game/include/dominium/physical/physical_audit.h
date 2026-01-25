/*
FILE: include/dominium/physical/physical_audit.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / physical
RESPONSIBILITY: Defines deterministic audit logging for physicalization events.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C89/C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Event ordering is deterministic under identical inputs.
*/
#ifndef DOMINIUM_PHYSICAL_PHYSICAL_AUDIT_H
#define DOMINIUM_PHYSICAL_PHYSICAL_AUDIT_H

#include "domino/core/dom_time_core.h"
#include "domino/core/types.h"
#include "domino/provenance.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef enum dom_physical_event_kind {
    DOM_PHYS_EVENT_TERRAIN_MODIFY = 1,
    DOM_PHYS_EVENT_RESOURCE_SURVEY = 2,
    DOM_PHYS_EVENT_RESOURCE_EXTRACT = 3,
    DOM_PHYS_EVENT_RESOURCE_REFINE = 4,
    DOM_PHYS_EVENT_RESOURCE_TAILINGS = 5,
    DOM_PHYS_EVENT_STRUCTURE_BUILD = 6,
    DOM_PHYS_EVENT_STRUCTURE_FAIL = 7,
    DOM_PHYS_EVENT_VOLUME_CONFLICT = 8,
    DOM_PHYS_EVENT_NETWORK_CONNECT = 9,
    DOM_PHYS_EVENT_NETWORK_OVERLOAD = 10,
    DOM_PHYS_EVENT_NETWORK_FAIL = 11,
    DOM_PHYS_EVENT_MACHINE_WEAR = 12,
    DOM_PHYS_EVENT_MACHINE_FAIL = 13,
    DOM_PHYS_EVENT_MAINTENANCE = 14
} dom_physical_event_kind;

typedef struct dom_physical_event {
    u64 event_id;
    u64 actor_id;
    dom_act_time_t act_time;
    dom_provenance_id provenance_id;
    u32 kind;
    u64 subject_id;
    u64 related_id;
    i64 amount;
    u32 flags;
} dom_physical_event;

typedef struct dom_physical_audit_log {
    dom_physical_event* entries;
    u32 count;
    u32 capacity;
    u64 next_event_id;
    dom_act_time_t current_act;
    dom_provenance_id provenance_id;
} dom_physical_audit_log;

void dom_physical_audit_init(dom_physical_audit_log* log,
                             dom_physical_event* storage,
                             u32 capacity,
                             u64 start_id);
void dom_physical_audit_set_context(dom_physical_audit_log* log,
                                    dom_act_time_t act_time,
                                    dom_provenance_id provenance_id);
int dom_physical_audit_record(dom_physical_audit_log* log,
                              u64 actor_id,
                              u32 kind,
                              u64 subject_id,
                              u64 related_id,
                              i64 amount);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_PHYSICAL_PHYSICAL_AUDIT_H */
