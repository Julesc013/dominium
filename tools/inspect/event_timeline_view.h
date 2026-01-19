/*
FILE: tools/inspect/event_timeline_view.h
MODULE: Dominium
LAYER / SUBSYSTEM: Tools / inspect
RESPONSIBILITY: Event timeline inspection helpers for scheduled event debugging.
ALLOWED DEPENDENCIES: Engine public headers and C89/C++98 standard headers only.
FORBIDDEN DEPENDENCIES: Engine/game internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Deterministic ordering and filtering.
*/
#ifndef DOMINIUM_TOOLS_INSPECT_EVENT_TIMELINE_VIEW_H
#define DOMINIUM_TOOLS_INSPECT_EVENT_TIMELINE_VIEW_H

#include "domino/core/dom_time_core.h"
#include "domino/core/types.h"
#include "inspect_access.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef enum tool_event_state {
    TOOL_EVENT_PENDING = 0,
    TOOL_EVENT_FIRED = 1,
    TOOL_EVENT_CANCELED = 2,
    TOOL_EVENT_REFUSED = 3
} tool_event_state;

typedef struct tool_event_record {
    u64 event_id;
    dom_act_time_t act;
    u32 state;
    u32 kind;
    u32 required_knowledge;
} tool_event_record;

typedef struct tool_event_timeline {
    const tool_event_record* events;
    u32 event_count;
} tool_event_timeline;

int tool_event_timeline_next_due(const tool_event_timeline* timeline,
                                 const tool_access_context* access,
                                 dom_act_time_t now_act,
                                 dom_act_time_t* out_next_act);

int tool_event_timeline_collect(const tool_event_timeline* timeline,
                                const tool_access_context* access,
                                dom_act_time_t start_act,
                                dom_act_time_t end_act,
                                tool_event_record* out_events,
                                u32 max_events,
                                u32* out_count);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_TOOLS_INSPECT_EVENT_TIMELINE_VIEW_H */
