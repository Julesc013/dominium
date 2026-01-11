/*
FILE: include/domino/core/dom_time_core.h
MODULE: Domino
RESPONSIBILITY: Authoritative engine time core (ACT storage + advancement).
NOTES: Pure C90 header; no platform headers, no calendars.
*/
#ifndef DOMINO_CORE_DOM_TIME_CORE_H
#define DOMINO_CORE_DOM_TIME_CORE_H

#include "domino/core/types.h"

#ifdef __cplusplus
extern "C" {
#endif

enum {
    DOM_TIME_OK = 0,
    DOM_TIME_ERR = -1,
    DOM_TIME_INVALID = -2,
    DOM_TIME_OVERFLOW = -3,
    DOM_TIME_BACKWARDS = -4,
    DOM_TIME_EMPTY = -5,
    DOM_TIME_FULL = -6,
    DOM_TIME_NOT_FOUND = -7,
    DOM_TIME_NO_DATA = -8
};

typedef i64 dom_act_time_t;   /* ACT seconds, monotonic. */
typedef i64 dom_time_delta_t; /* Signed delta in ACT seconds. */

typedef enum dom_time_frame_id {
    DOM_TIME_FRAME_ACT = 0,
    DOM_TIME_FRAME_BST = 1,
    DOM_TIME_FRAME_GCT = 2,
    DOM_TIME_FRAME_CPT = 3
} dom_time_frame_id;

typedef u64 dom_time_event_id;

typedef struct dom_time_core {
    dom_act_time_t current_act;
} dom_time_core;

#define DOM_TIME_ACT_MAX ((dom_act_time_t)0x7fffffffffffffffLL)
#define DOM_TIME_ACT_MIN ((dom_act_time_t)(-0x7fffffffffffffffLL - 1LL))

/* Initializes time core to a start ACT value. */
int dom_time_core_init(dom_time_core *core, dom_act_time_t start_act);

/* Returns current ACT; out_act required. */
int dom_time_get_act(const dom_time_core *core, dom_act_time_t *out_act);

/* Advances ACT by delta seconds; refuses negative deltas. */
int dom_time_advance(dom_time_core *core, dom_time_delta_t delta);

/* Advances ACT to target (must be >= current). */
int dom_time_advance_to(dom_time_core *core, dom_act_time_t target_act);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINO_CORE_DOM_TIME_CORE_H */
