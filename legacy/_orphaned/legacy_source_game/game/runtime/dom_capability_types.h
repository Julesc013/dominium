/*
FILE: source/dominium/game/runtime/dom_capability_types.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / game/runtime/capabilities
RESPONSIBILITY: Defines core capability and resolution enums shared by belief and capability layers.
ALLOWED DEPENDENCIES: `include/domino/**`, `source/dominium/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: OS headers; locale/timezone libraries.
*/
#ifndef DOM_CAPABILITY_TYPES_H
#define DOM_CAPABILITY_TYPES_H

#include "domino/core/types.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef u32 dom_capability_id;

typedef enum dom_resolution_tier {
    DOM_RESOLUTION_UNKNOWN = 0,
    DOM_RESOLUTION_BINARY = 1,
    DOM_RESOLUTION_COARSE = 2,
    DOM_RESOLUTION_BOUNDED = 3,
    DOM_RESOLUTION_EXACT = 4
} dom_resolution_tier;

typedef enum dom_capability_kind {
    DOM_CAP_TIME_READOUT = 1,
    DOM_CAP_CALENDAR_VIEW = 2,
    DOM_CAP_MAP_VIEW = 3,
    DOM_CAP_POSITION_ESTIMATE = 4,
    DOM_CAP_HEALTH_STATUS = 5,
    DOM_CAP_INVENTORY_SUMMARY = 6,
    DOM_CAP_ECONOMIC_ACCOUNT = 7,
    DOM_CAP_MARKET_QUOTES = 8,
    DOM_CAP_COMMUNICATIONS = 9,
    DOM_CAP_COMMAND_STATUS = 10,
    DOM_CAP_ENVIRONMENTAL_STATUS = 11,
    DOM_CAP_LEGAL_STATUS = 12
} dom_capability_kind;

typedef enum dom_capability_subject_kind {
    DOM_CAP_SUBJECT_NONE = 0,
    DOM_CAP_SUBJECT_ACTOR = 1,
    DOM_CAP_SUBJECT_ENTITY = 2,
    DOM_CAP_SUBJECT_LOCATION = 3,
    DOM_CAP_SUBJECT_CONTRACT = 4,
    DOM_CAP_SUBJECT_RESOURCE = 5,
    DOM_CAP_SUBJECT_COMMAND = 6,
    DOM_CAP_SUBJECT_MARKET = 7,
    DOM_CAP_SUBJECT_ENV = 8,
    DOM_CAP_SUBJECT_LEGAL = 9,
    DOM_CAP_SUBJECT_CALENDAR = 10,
    DOM_CAP_SUBJECT_CLOCK = 11
} dom_capability_subject_kind;

typedef struct dom_capability_subject {
    u32 kind;
    u64 id;
} dom_capability_subject;

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOM_CAPABILITY_TYPES_H */
