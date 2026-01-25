/*
FILE: tools/observability/determinism_tools.h
MODULE: Dominium
LAYER / SUBSYSTEM: Tools / observability
RESPONSIBILITY: Determinism and regression comparison helpers (read-only).
ALLOWED DEPENDENCIES: Engine public headers and tools headers only.
FORBIDDEN DEPENDENCIES: Engine/game internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Deterministic hashing and comparison.
*/
#ifndef DOMINIUM_TOOLS_OBSERVABILITY_DETERMINISM_TOOLS_H
#define DOMINIUM_TOOLS_OBSERVABILITY_DETERMINISM_TOOLS_H

#include "domino/core/types.h"
#include "observation_store.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef enum tool_determinism_diff_kind {
    TOOL_DET_DIFF_NONE = 0,
    TOOL_DET_DIFF_COUNT = 1,
    TOOL_DET_DIFF_EVENT_ID = 2,
    TOOL_DET_DIFF_EVENT_ACT = 3,
    TOOL_DET_DIFF_EVENT_KIND = 4,
    TOOL_DET_DIFF_EVENT_FLAGS = 5,
    TOOL_DET_DIFF_EVENT_AGENT = 6,
    TOOL_DET_DIFF_SNAPSHOT_META = 7,
    TOOL_DET_DIFF_SNAPSHOT_PAYLOAD = 8
} tool_determinism_diff_kind;

typedef struct tool_determinism_diff {
    u32 diverged;
    u32 index;
    u32 kind;
    u64 left_id;
    u64 right_id;
} tool_determinism_diff;

u64 tool_determinism_hash_events(const tool_observe_event_record* events,
                                 u32 event_count);
u64 tool_determinism_hash_snapshots(const tool_snapshot_record* snapshots,
                                    u32 snapshot_count);

int tool_determinism_compare_replays(const tool_observe_replay* left,
                                     const tool_observe_replay* right,
                                     tool_determinism_diff* out_diff);
int tool_determinism_compare_events(const tool_observe_event_record* left,
                                    u32 left_count,
                                    const tool_observe_event_record* right,
                                    u32 right_count,
                                    tool_determinism_diff* out_diff);
int tool_determinism_compare_snapshots(const tool_snapshot_record* left,
                                       u32 left_count,
                                       const tool_snapshot_record* right,
                                       u32 right_count,
                                       tool_determinism_diff* out_diff);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_TOOLS_OBSERVABILITY_DETERMINISM_TOOLS_H */
