/*
FILE: include/dominium/rules/scale/scale_logistics_types.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / scale
RESPONSIBILITY: Defines shared logistics types for CIV4 scaling.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C89/C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Shared types are stable and deterministic.
*/
#ifndef DOMINIUM_RULES_SCALE_LOGISTICS_TYPES_H
#define DOMINIUM_RULES_SCALE_LOGISTICS_TYPES_H

#ifdef __cplusplus
extern "C" {
#endif

typedef enum scale_flow_status {
    SCALE_FLOW_PENDING = 0,
    SCALE_FLOW_ARRIVED = 1,
    SCALE_FLOW_BLOCKED = 2
} scale_flow_status;

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_RULES_SCALE_LOGISTICS_TYPES_H */
