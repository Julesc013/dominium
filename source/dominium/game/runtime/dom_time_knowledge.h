/*
FILE: source/dominium/game/runtime/dom_time_knowledge.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / game/runtime/time_knowledge
RESPONSIBILITY: Epistemic time knowledge state and accessors (no clocks yet).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/dominium/**`, C++98 STL.
FORBIDDEN DEPENDENCIES: OS headers; locale/timezone libraries.
*/
#ifndef DOM_TIME_KNOWLEDGE_H
#define DOM_TIME_KNOWLEDGE_H

#include "domino/core/dom_time_core.h"
#include "runtime/dom_calendar.h"

#ifdef __cplusplus
extern "C" {
#endif

enum {
    DOM_TIME_KNOWLEDGE_OK = 0,
    DOM_TIME_KNOWLEDGE_ERR = -1,
    DOM_TIME_KNOWLEDGE_INVALID_ARGUMENT = -2,
    DOM_TIME_KNOWLEDGE_DUPLICATE_ID = -3,
    DOM_TIME_KNOWLEDGE_NOT_FOUND = -4,
    DOM_TIME_KNOWLEDGE_OVERFLOW = -5,
    DOM_TIME_KNOWLEDGE_UNKNOWN = -6,
    DOM_TIME_KNOWLEDGE_NOT_IMPLEMENTED = -7,
    DOM_TIME_KNOWLEDGE_BACKWARDS = -8
};

typedef u64 dom_time_actor_id;

typedef struct dom_time_knowledge dom_time_knowledge;

dom_time_knowledge *dom_time_knowledge_create(dom_time_actor_id actor_id);
void dom_time_knowledge_destroy(dom_time_knowledge *knowledge);
int dom_time_knowledge_init(dom_time_knowledge *knowledge, dom_time_actor_id actor_id);

int dom_time_knowledge_add_frame(dom_time_knowledge *knowledge, dom_time_frame_id frame);
int dom_time_knowledge_has_frame(const dom_time_knowledge *knowledge,
                                 dom_time_frame_id frame,
                                 d_bool *out_known);

int dom_time_knowledge_add_calendar(dom_time_knowledge *knowledge, dom_calendar_id id);
int dom_time_knowledge_has_calendar(const dom_time_knowledge *knowledge,
                                    dom_calendar_id id,
                                    d_bool *out_known);
int dom_time_knowledge_list_calendars(const dom_time_knowledge *knowledge,
                                      dom_calendar_id *out_ids,
                                      u32 max_ids,
                                      u32 *out_count);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOM_TIME_KNOWLEDGE_H */
