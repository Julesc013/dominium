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
#include "runtime/dom_cosmo_graph.h"
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

dom_cosmo_map_snapshot *dom_game_runtime_build_cosmo_map_snapshot(const dom_game_runtime *rt) {
    dom_cosmo_map_snapshot *snap;
    const dom::dom_cosmo_graph *graph;
    size_t i;

    if (!rt) {
        return (dom_cosmo_map_snapshot *)0;
    }

    snap = new dom_cosmo_map_snapshot();
    std::memset(snap, 0, sizeof(*snap));
    snap->struct_size = sizeof(*snap);
    snap->struct_version = DOM_COSMO_MAP_SNAPSHOT_VERSION;

    graph = static_cast<const dom::dom_cosmo_graph *>(dom_game_runtime_cosmo_graph(rt));
    if (graph) {
        if (graph->entities.size() > 0xffffffffu || graph->edges.size() > 0xffffffffu) {
            delete snap;
            return (dom_cosmo_map_snapshot *)0;
        }
        snap->entity_count = (u32)graph->entities.size();
        snap->edge_count = (u32)graph->edges.size();
        if (snap->entity_count > 0u) {
            snap->entities = new dom_cosmo_entity_view[snap->entity_count];
            for (i = 0u; i < graph->entities.size(); ++i) {
                const dom::dom_cosmo_entity &ent = graph->entities[i];
                snap->entities[i].id = ent.id;
                snap->entities[i].parent_id = ent.parent_id;
                snap->entities[i].kind = ent.kind;
            }
        }
        if (snap->edge_count > 0u) {
            snap->edges = new dom_cosmo_edge_view[snap->edge_count];
            for (i = 0u; i < graph->edges.size(); ++i) {
                const dom::dom_cosmo_edge &edge = graph->edges[i];
                snap->edges[i].id = edge.id;
                snap->edges[i].src_id = edge.src_id;
                snap->edges[i].dst_id = edge.dst_id;
                snap->edges[i].duration_ticks = edge.duration_ticks;
                snap->edges[i].cost = edge.cost;
            }
        }
    }

    if (dom_game_runtime_cosmo_transit_get(rt, &snap->transit) == DOM_GAME_RUNTIME_OK) {
        snap->transit_active = snap->transit.active ? 1 : 0;
    }

    return snap;
}

void dom_game_runtime_release_cosmo_map_snapshot(dom_cosmo_map_snapshot *snapshot) {
    if (!snapshot) {
        return;
    }
    delete[] snapshot->entities;
    delete[] snapshot->edges;
    delete snapshot;
}

dom_cosmo_transit_snapshot *dom_game_runtime_build_cosmo_transit_snapshot(const dom_game_runtime *rt) {
    dom_cosmo_transit_snapshot *snap;

    if (!rt) {
        return (dom_cosmo_transit_snapshot *)0;
    }

    snap = new dom_cosmo_transit_snapshot();
    std::memset(snap, 0, sizeof(*snap));
    snap->struct_size = sizeof(*snap);
    snap->struct_version = DOM_COSMO_TRANSIT_SNAPSHOT_VERSION;
    if (dom_game_runtime_cosmo_transit_get(rt, &snap->transit) == DOM_GAME_RUNTIME_OK) {
        snap->transit_active = snap->transit.active ? 1 : 0;
    }
    snap->last_arrival_tick = dom_game_runtime_cosmo_last_arrival_tick(rt);
    return snap;
}

void dom_game_runtime_release_cosmo_transit_snapshot(dom_cosmo_transit_snapshot *snapshot) {
    if (!snapshot) {
        return;
    }
    delete snapshot;
}
