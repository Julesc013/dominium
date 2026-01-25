/*
FILE: tools/observability/history_viewer.h
MODULE: Dominium
LAYER / SUBSYSTEM: Tools / observability
RESPONSIBILITY: Read-only history browsing, provenance tracing, and causal lookup.
ALLOWED DEPENDENCIES: Engine public headers and tools headers only.
FORBIDDEN DEPENDENCIES: Engine/game internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Deterministic filtering and ordering.
*/
#ifndef DOMINIUM_TOOLS_OBSERVABILITY_HISTORY_VIEWER_H
#define DOMINIUM_TOOLS_OBSERVABILITY_HISTORY_VIEWER_H

#include "domino/core/dom_time_core.h"
#include "domino/core/types.h"
#include "inspect_access.h"
#include "observation_store.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct tool_history_viewer {
    const tool_observation_store* store;
    tool_access_context access;
    u64 agent_id;
    u64 institution_id;
    u32 flags_mask;
    u32 cursor;
} tool_history_viewer;

typedef struct tool_history_explanation {
    tool_observe_event_record event;
    tool_agent_state agent;
    tool_institution_state institution;
    u32 has_event;
    u32 has_agent;
    u32 has_institution;
} tool_history_explanation;

int tool_history_viewer_init(tool_history_viewer* viewer,
                             const tool_observation_store* store,
                             const tool_access_context* access,
                             u64 agent_id,
                             u64 institution_id,
                             u32 flags_mask);
int tool_history_viewer_next(tool_history_viewer* viewer,
                             tool_history_record* out_record);
int tool_history_viewer_collect_range(const tool_observation_store* store,
                                      const tool_access_context* access,
                                      dom_act_time_t start_act,
                                      dom_act_time_t end_act,
                                      tool_history_record* out_records,
                                      u32 max_records,
                                      u32* out_count);
int tool_history_viewer_trace_provenance(const tool_observation_store* store,
                                         const tool_access_context* access,
                                         u64 provenance_id,
                                         tool_history_record* out_records,
                                         u32 max_records,
                                         u32* out_count);
int tool_history_viewer_explain_event(const tool_observation_store* store,
                                      const tool_access_context* access,
                                      u64 event_id,
                                      tool_history_explanation* out_explanation);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_TOOLS_OBSERVABILITY_HISTORY_VIEWER_H */
