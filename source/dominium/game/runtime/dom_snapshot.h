/*
FILE: source/dominium/game/runtime/dom_snapshot.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / game/runtime/dom_snapshot
RESPONSIBILITY: Defines immutable snapshot structs for UI/render consumption.
ALLOWED DEPENDENCIES: `include/dominium/**`, `source/dominium/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: Dependency inversions that violate `docs/OVERVIEW_ARCHITECTURE.md` layering.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: Snapshot creation must not mutate authoritative state.
VERSIONING / ABI / DATA FORMAT NOTES: Internal structs versioned for forward evolution.
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOM_SNAPSHOT_H
#define DOM_SNAPSHOT_H

#include "domino/core/types.h"

#ifdef __cplusplus
extern "C" {
#endif

enum {
    DOM_RUNTIME_SUMMARY_SNAPSHOT_VERSION = 2u,
    DOM_VIEW_STATE_SNAPSHOT_VERSION = 1u,
    DOM_GAME_SNAPSHOT_VERSION = 1u
};

enum {
    DOM_GAME_SNAPSHOT_FLAG_RUNTIME = 1u,
    DOM_GAME_SNAPSHOT_FLAG_VIEW = 2u
};

typedef struct dom_runtime_summary_snapshot {
    u32 struct_size;
    u32 struct_version;
    u64 tick_index;
    u32 ups;
    u64 sim_hash;
    u32 entity_count;
    u32 vessel_count;
    u32 construction_count;
    u32 io_violation_count;
    u32 stall_count;
    u32 last_frame_ms;
} dom_runtime_summary_snapshot;

typedef struct dom_view_state_snapshot {
    u32 struct_size;
    u32 struct_version;
    float camera_x;
    float camera_y;
    float camera_zoom;
    u32 selected_struct_id;
} dom_view_state_snapshot;

typedef struct dom_game_snapshot {
    u32 struct_size;
    u32 struct_version;
    dom_runtime_summary_snapshot runtime;
    dom_view_state_snapshot view;
} dom_game_snapshot;

struct dom_game_runtime;

dom_game_snapshot *dom_game_runtime_build_snapshot(const struct dom_game_runtime *rt, u32 flags);
void dom_game_runtime_release_snapshot(dom_game_snapshot *snapshot);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOM_SNAPSHOT_H */
