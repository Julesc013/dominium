/*
FILE: tools/observability/observability_api.h
MODULE: Dominium
LAYER / SUBSYSTEM: Tools / observability
RESPONSIBILITY: Read-only tool interfaces for snapshots, events, history, replay, packs, and capabilities.
ALLOWED DEPENDENCIES: Engine public headers and tools headers only.
FORBIDDEN DEPENDENCIES: Engine/game internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: All queries are deterministic and side-effect free.
*/
#ifndef DOMINIUM_TOOLS_OBSERVABILITY_API_H
#define DOMINIUM_TOOLS_OBSERVABILITY_API_H

#include "domino/core/dom_time_core.h"
#include "domino/core/types.h"
#include "domino/snapshot.h"
#include "inspect_access.h"
#include "observation_store.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct tool_snapshot_request {
    u64 snapshot_id;
    u32 kind; /* dom_snapshot_kind */
    u32 kind_set;
    u32 lod_tag;
    u32 budget_units;
    u32 scope_mask;
} tool_snapshot_request;

typedef struct tool_snapshot_view {
    tool_snapshot_record record;
} tool_snapshot_view;

typedef struct tool_event_stream_request {
    u64 agent_id;
    u32 required_knowledge;
} tool_event_stream_request;

typedef struct tool_event_stream {
    const tool_observation_store* store;
    tool_event_stream_request request;
    tool_access_context access;
    u32 cursor;
} tool_event_stream;

typedef struct tool_history_query {
    u64 agent_id;
    u64 institution_id;
    u32 required_knowledge;
    u32 flags_mask;
} tool_history_query;

typedef struct tool_history_view {
    const tool_observation_store* store;
    tool_history_query request;
    tool_access_context access;
    u32 cursor;
} tool_history_view;

typedef enum tool_replay_command_kind {
    TOOL_REPLAY_CMD_LOAD = 1,
    TOOL_REPLAY_CMD_SEEK = 2,
    TOOL_REPLAY_CMD_STEP = 3,
    TOOL_REPLAY_CMD_RESET = 4
} tool_replay_command_kind;

typedef struct tool_replay_command {
    u32 kind;
    dom_act_time_t act;
    const tool_observe_replay* replay;
} tool_replay_command;

typedef struct tool_replay_state {
    u32 cursor;
    tool_observe_replay_event current;
    u32 has_current;
} tool_replay_state;

typedef struct tool_replay_controller {
    const tool_observe_replay* replay;
    u32 cursor;
} tool_replay_controller;

typedef struct tool_pack_query {
    u32 include_disabled;
} tool_pack_query;

typedef struct tool_pack_view {
    const tool_observation_store* store;
    tool_pack_query request;
    u32 cursor;
} tool_pack_view;

typedef struct tool_capability_query {
    u32 provider_kind;
} tool_capability_query;

typedef struct tool_capability_view {
    const tool_observation_store* store;
    tool_capability_query request;
    u32 cursor;
} tool_capability_view;

int tool_snapshot_query(const tool_observation_store* store,
                        const tool_snapshot_request* request,
                        const tool_access_context* access,
                        tool_snapshot_view* out_view);
int tool_event_stream_subscribe(const tool_observation_store* store,
                                const tool_event_stream_request* request,
                                const tool_access_context* access,
                                tool_event_stream* out_stream);
int tool_event_stream_next(tool_event_stream* stream,
                           tool_observe_event_record* out_event);
int tool_history_query(const tool_observation_store* store,
                       const tool_history_query* request,
                       const tool_access_context* access,
                       tool_history_view* out_view);
int tool_history_view_next(tool_history_view* view,
                           tool_history_record* out_record);
int tool_replay_control(tool_replay_controller* controller,
                        const tool_replay_command* command,
                        tool_replay_state* out_state);
int tool_pack_manifest_query(const tool_observation_store* store,
                             const tool_pack_query* request,
                             tool_pack_view* out_view);
int tool_pack_view_next(tool_pack_view* view,
                        tool_pack_record* out_record);
int tool_capability_query(const tool_observation_store* store,
                          const tool_capability_query* request,
                          tool_capability_view* out_view);
int tool_capability_view_next(tool_capability_view* view,
                              tool_capability_record* out_record);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_TOOLS_OBSERVABILITY_API_H */
