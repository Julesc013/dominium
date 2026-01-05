/*
FILE: source/dominium/game/runtime/dom_snapshot.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / game/runtime/dom_snapshot
RESPONSIBILITY: Implements immutable snapshot creation for UI/render.
ALLOWED DEPENDENCIES: `include/dominium/**`, `source/dominium/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: Dependency inversions that violate `docs/OVERVIEW_ARCHITECTURE.md` layering.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: Snapshot creation must not mutate authoritative state.
VERSIONING / ABI / DATA FORMAT NOTES: Internal structs versioned for forward evolution.
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include "runtime/dom_snapshot.h"

#include <cstring>

#include "runtime/dom_io_guard.h"
#include "runtime/dom_game_runtime.h"
#include "runtime/dom_game_query.h"

extern "C" {
}

dom_game_snapshot *dom_game_runtime_build_snapshot(const dom_game_runtime *rt, u32 flags) {
    dom_game_snapshot *snap;
    dom_game_counts counts;
    (void)flags;

    if (!rt) {
        return (dom_game_snapshot *)0;
    }

    snap = new dom_game_snapshot();
    std::memset(snap, 0, sizeof(*snap));

    snap->struct_size = sizeof(*snap);
    snap->struct_version = DOM_GAME_SNAPSHOT_VERSION;

    snap->runtime.struct_size = sizeof(snap->runtime);
    snap->runtime.struct_version = DOM_RUNTIME_SUMMARY_SNAPSHOT_VERSION;
    snap->runtime.tick_index = dom_game_runtime_get_tick(rt);
    snap->runtime.ups = dom_game_runtime_get_ups(rt);
    snap->runtime.sim_hash = dom_game_runtime_get_hash(rt);
    snap->runtime.entity_count = 0u;
    snap->runtime.vessel_count = 0u;
    snap->runtime.construction_count = 0u;
    snap->runtime.io_violation_count = dom_io_guard_violation_count();
    snap->runtime.stall_count = dom_io_guard_stall_count();
    snap->runtime.last_frame_ms = dom_io_guard_last_frame_ms();

    std::memset(&counts, 0, sizeof(counts));
    if (dom_game_runtime_get_counts(rt, &counts) == DOM_GAME_RUNTIME_OK) {
        snap->runtime.entity_count = counts.entity_count;
        snap->runtime.construction_count = counts.construction_count;
    }

    snap->view.struct_size = sizeof(snap->view);
    snap->view.struct_version = DOM_VIEW_STATE_SNAPSHOT_VERSION;
    snap->view.camera_x = 0.0f;
    snap->view.camera_y = 0.0f;
    snap->view.camera_zoom = 1.0f;
    snap->view.selected_struct_id = 0u;

    return snap;
}

void dom_game_runtime_release_snapshot(dom_game_snapshot *snapshot) {
    if (!snapshot) {
        return;
    }
    delete snapshot;
}
