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
#include "runtime/dom_system_registry.h"
#include "runtime/dom_body_registry.h"
#include "runtime/dom_frames.h"
#include "runtime/dom_surface_topology.h"

extern "C" {
}

namespace {

struct SystemFillContext {
    dom_system_view *systems;
    u32 index;
};

static void fill_system_view(const dom_system_info *info, void *user) {
    SystemFillContext *ctx = static_cast<SystemFillContext *>(user);
    dom_system_view *view = &ctx->systems[ctx->index++];
    view->id = info->id;
    view->parent_id = info->parent_id;
}

struct BodyFillContext {
    dom_body_view *bodies;
    u32 index;
};

static void fill_body_view(const dom_body_info *info, void *user) {
    BodyFillContext *ctx = static_cast<BodyFillContext *>(user);
    dom_body_view *view = &ctx->bodies[ctx->index++];
    view->id = info->id;
    view->system_id = info->system_id;
    view->kind = info->kind;
    view->radius_m = info->radius_m;
    view->mu_m3_s2 = info->mu_m3_s2;
    view->rotation_period_ticks = info->rotation_period_ticks;
}

struct FrameFillContext {
    dom_frame_view *frames;
    u32 index;
};

static void fill_frame_view(const dom_frame_info *info, void *user) {
    FrameFillContext *ctx = static_cast<FrameFillContext *>(user);
    dom_frame_view *view = &ctx->frames[ctx->index++];
    view->id = info->id;
    view->parent_id = info->parent_id;
    view->kind = info->kind;
    view->body_id = info->body_id;
}

struct TopologyFillContext {
    const dom_body_registry *bodies;
    dom_body_topology_view *views;
    u32 index;
};

static void fill_topology_view(const dom_body_info *info, void *user) {
    TopologyFillContext *ctx = static_cast<TopologyFillContext *>(user);
    dom_body_topology_view *view = &ctx->views[ctx->index++];
    dom_topology_binding binding;
    int rc;

    view->body_id = info->id;
    view->topology_kind = 0u;
    view->param_a_m = 0;
    view->param_b_m = 0;
    view->param_c_m = 0;

    rc = dom_surface_topology_select(ctx->bodies, info->id, 0u, &binding);
    if (rc == DOM_TOPOLOGY_OK) {
        view->topology_kind = binding.kind;
        view->param_a_m = binding.param_a_m;
        view->param_b_m = binding.param_b_m;
        view->param_c_m = binding.param_c_m;
    }
}

} // namespace

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

dom_system_list_snapshot *dom_game_runtime_build_system_list_snapshot(const dom_game_runtime *rt) {
    dom_system_list_snapshot *snap;
    const dom_system_registry *registry;
    u32 count;
    SystemFillContext ctx;

    if (!rt) {
        return (dom_system_list_snapshot *)0;
    }
    registry = static_cast<const dom_system_registry *>(dom_game_runtime_system_registry(rt));
    if (!registry) {
        return (dom_system_list_snapshot *)0;
    }

    snap = new dom_system_list_snapshot();
    std::memset(snap, 0, sizeof(*snap));
    snap->struct_size = sizeof(*snap);
    snap->struct_version = DOM_SYSTEM_LIST_SNAPSHOT_VERSION;

    count = dom_system_registry_count(registry);
    snap->system_count = count;
    if (count > 0u) {
        snap->systems = new dom_system_view[count];
        ctx.systems = snap->systems;
        ctx.index = 0u;
        (void)dom_system_registry_iterate(registry, fill_system_view, &ctx);
    }
    return snap;
}

void dom_game_runtime_release_system_list_snapshot(dom_system_list_snapshot *snapshot) {
    if (!snapshot) {
        return;
    }
    delete[] snapshot->systems;
    delete snapshot;
}

dom_body_list_snapshot *dom_game_runtime_build_body_list_snapshot(const dom_game_runtime *rt) {
    dom_body_list_snapshot *snap;
    const dom_body_registry *registry;
    u32 count;
    BodyFillContext ctx;

    if (!rt) {
        return (dom_body_list_snapshot *)0;
    }
    registry = static_cast<const dom_body_registry *>(dom_game_runtime_body_registry(rt));
    if (!registry) {
        return (dom_body_list_snapshot *)0;
    }

    snap = new dom_body_list_snapshot();
    std::memset(snap, 0, sizeof(*snap));
    snap->struct_size = sizeof(*snap);
    snap->struct_version = DOM_BODY_LIST_SNAPSHOT_VERSION;

    count = dom_body_registry_count(registry);
    snap->body_count = count;
    if (count > 0u) {
        snap->bodies = new dom_body_view[count];
        ctx.bodies = snap->bodies;
        ctx.index = 0u;
        (void)dom_body_registry_iterate(registry, fill_body_view, &ctx);
    }
    return snap;
}

void dom_game_runtime_release_body_list_snapshot(dom_body_list_snapshot *snapshot) {
    if (!snapshot) {
        return;
    }
    delete[] snapshot->bodies;
    delete snapshot;
}

dom_frame_tree_snapshot *dom_game_runtime_build_frame_tree_snapshot(const dom_game_runtime *rt) {
    dom_frame_tree_snapshot *snap;
    const dom_frames *frames;
    u32 count;
    FrameFillContext ctx;

    if (!rt) {
        return (dom_frame_tree_snapshot *)0;
    }
    frames = static_cast<const dom_frames *>(dom_game_runtime_frames(rt));
    if (!frames) {
        return (dom_frame_tree_snapshot *)0;
    }

    snap = new dom_frame_tree_snapshot();
    std::memset(snap, 0, sizeof(*snap));
    snap->struct_size = sizeof(*snap);
    snap->struct_version = DOM_FRAME_TREE_SNAPSHOT_VERSION;

    count = dom_frames_count(frames);
    snap->frame_count = count;
    if (count > 0u) {
        snap->frames = new dom_frame_view[count];
        ctx.frames = snap->frames;
        ctx.index = 0u;
        (void)dom_frames_iterate(frames, fill_frame_view, &ctx);
    }
    return snap;
}

void dom_game_runtime_release_frame_tree_snapshot(dom_frame_tree_snapshot *snapshot) {
    if (!snapshot) {
        return;
    }
    delete[] snapshot->frames;
    delete snapshot;
}

dom_body_topology_snapshot *dom_game_runtime_build_body_topology_snapshot(const dom_game_runtime *rt) {
    dom_body_topology_snapshot *snap;
    const dom_body_registry *registry;
    u32 count;
    TopologyFillContext ctx;

    if (!rt) {
        return (dom_body_topology_snapshot *)0;
    }
    registry = static_cast<const dom_body_registry *>(dom_game_runtime_body_registry(rt));
    if (!registry) {
        return (dom_body_topology_snapshot *)0;
    }

    snap = new dom_body_topology_snapshot();
    std::memset(snap, 0, sizeof(*snap));
    snap->struct_size = sizeof(*snap);
    snap->struct_version = DOM_BODY_TOPOLOGY_SNAPSHOT_VERSION;

    count = dom_body_registry_count(registry);
    snap->body_count = count;
    if (count > 0u) {
        snap->bodies = new dom_body_topology_view[count];
        ctx.bodies = registry;
        ctx.views = snap->bodies;
        ctx.index = 0u;
        (void)dom_body_registry_iterate(registry, fill_topology_view, &ctx);
    }
    return snap;
}

void dom_game_runtime_release_body_topology_snapshot(dom_body_topology_snapshot *snapshot) {
    if (!snapshot) {
        return;
    }
    delete[] snapshot->bodies;
    delete snapshot;
}
