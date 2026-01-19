/*
FILE: tools/inspect/replay_inspector.h
MODULE: Dominium
LAYER / SUBSYSTEM: Tools / inspect
RESPONSIBILITY: Deterministic replay inspection without state mutation.
ALLOWED DEPENDENCIES: Engine public headers and C89/C++98 standard headers only.
FORBIDDEN DEPENDENCIES: Engine/game internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Deterministic iteration and hashing.
*/
#ifndef DOMINIUM_TOOLS_INSPECT_REPLAY_INSPECTOR_H
#define DOMINIUM_TOOLS_INSPECT_REPLAY_INSPECTOR_H

#include "domino/core/dom_time_core.h"
#include "domino/core/types.h"
#include "inspect_access.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef enum tool_replay_event_kind {
    TOOL_REPLAY_EVENT_REDACTED = 0,
    TOOL_REPLAY_EVENT_COMMAND = 1,
    TOOL_REPLAY_EVENT_OUTCOME = 2,
    TOOL_REPLAY_EVENT_SCHEDULE = 3
} tool_replay_event_kind;

enum {
    TOOL_REPLAY_FLAG_REFUSED = 1u << 0,
    TOOL_REPLAY_FLAG_CANCELLED = 1u << 1
};

typedef struct tool_replay_event {
    u64 event_id;
    dom_act_time_t act;
    u32 kind;
    u32 required_knowledge;
    u32 flags;
} tool_replay_event;

typedef struct tool_replay {
    const tool_replay_event* events;
    u32 event_count;
} tool_replay;

typedef struct tool_replay_view_event {
    u64 event_id;
    dom_act_time_t act;
    u32 kind;
    u32 flags;
    u32 visible;
} tool_replay_view_event;

typedef struct tool_replay_inspector {
    const tool_replay* replay;
    tool_access_context access;
    u32 cursor;
} tool_replay_inspector;

u64 tool_replay_hash(const tool_replay* replay);

int tool_replay_inspector_init(tool_replay_inspector* insp,
                               const tool_replay* replay,
                               const tool_access_context* access);
int tool_replay_inspector_seek(tool_replay_inspector* insp,
                               dom_act_time_t act);
int tool_replay_inspector_next(tool_replay_inspector* insp,
                               tool_replay_view_event* out_event);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_TOOLS_INSPECT_REPLAY_INSPECTOR_H */
