/*
FILE: include/dominium/physical/physical_process.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / physical
RESPONSIBILITY: Shared types for physical process execution (capability/authority gating).
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C89/C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Process gating is deterministic for identical inputs.
*/
#ifndef DOMINIUM_PHYSICAL_PHYSICAL_PROCESS_H
#define DOMINIUM_PHYSICAL_PHYSICAL_PROCESS_H

#include "domino/core/dom_time_core.h"
#include "domino/core/types.h"
#include "dominium/physical/physical_audit.h"

#ifdef __cplusplus
extern "C" {
#endif

enum {
    DOM_PHYS_CAP_TERRAIN = 1u << 0,
    DOM_PHYS_CAP_EXTRACTION = 1u << 1,
    DOM_PHYS_CAP_CONSTRUCTION = 1u << 2,
    DOM_PHYS_CAP_NETWORK = 1u << 3,
    DOM_PHYS_CAP_MACHINE = 1u << 4
};

enum {
    DOM_PHYS_AUTH_TERRAIN = 1u << 0,
    DOM_PHYS_AUTH_EXTRACTION = 1u << 1,
    DOM_PHYS_AUTH_CONSTRUCTION = 1u << 2,
    DOM_PHYS_AUTH_NETWORK = 1u << 3,
    DOM_PHYS_AUTH_MAINTENANCE = 1u << 4
};

enum {
    DOM_PHYS_FAIL_NONE = 0,
    DOM_PHYS_FAIL_NO_CAPABILITY = 1,
    DOM_PHYS_FAIL_NO_AUTHORITY = 2,
    DOM_PHYS_FAIL_CONSTRAINT = 3,
    DOM_PHYS_FAIL_RESOURCE_EMPTY = 4,
    DOM_PHYS_FAIL_CAPACITY = 5,
    DOM_PHYS_FAIL_UNSUPPORTED = 6
};

typedef struct dom_physical_process_context {
    u64 actor_id;
    u32 capability_mask;
    u32 authority_mask;
    dom_act_time_t now_act;
    dom_physical_audit_log* audit;
} dom_physical_process_context;

typedef struct dom_physical_process_result {
    int ok;
    u32 failure_mode_id;
    u32 cost_units;
} dom_physical_process_result;

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_PHYSICAL_PHYSICAL_PROCESS_H */
