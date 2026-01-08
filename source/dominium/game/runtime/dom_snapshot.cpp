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
#include <vector>

#include "runtime/dom_io_guard.h"
#include "runtime/dom_cosmo_graph.h"
#include "runtime/dom_game_runtime.h"
#include "runtime/dom_game_query.h"
#include "runtime/dom_system_registry.h"
#include "runtime/dom_body_registry.h"
#include "runtime/dom_frames.h"
#include "runtime/dom_surface_topology.h"
#include "runtime/dom_surface_height.h"
#include "runtime/dom_construction_registry.h"
#include "runtime/dom_station_registry.h"
#include "runtime/dom_route_graph.h"
#include "runtime/dom_transfer_scheduler.h"

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

struct StationCollectContext {
    std::vector<dom_station_info> *stations;
};

static void collect_station_info(const dom_station_info *info, void *user) {
    StationCollectContext *ctx = static_cast<StationCollectContext *>(user);
    if (ctx && ctx->stations && info) {
        ctx->stations->push_back(*info);
    }
}

struct RouteCollectContext {
    std::vector<dom_route_info> *routes;
};

static void collect_route_info(const dom_route_info *info, void *user) {
    RouteCollectContext *ctx = static_cast<RouteCollectContext *>(user);
    if (ctx && ctx->routes && info) {
        ctx->routes->push_back(*info);
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

dom_orbit_summary_snapshot *dom_game_runtime_build_orbit_summary_snapshot(const dom_game_runtime *rt) {
    dom_orbit_summary_snapshot *snap;

    if (!rt) {
        return (dom_orbit_summary_snapshot *)0;
    }

    snap = new dom_orbit_summary_snapshot();
    std::memset(snap, 0, sizeof(*snap));
    snap->struct_size = sizeof(*snap);
    snap->struct_version = DOM_ORBIT_SUMMARY_SNAPSHOT_VERSION;
    snap->has_orbit = 0u;
    return snap;
}

void dom_game_runtime_release_orbit_summary_snapshot(dom_orbit_summary_snapshot *snapshot) {
    if (!snapshot) {
        return;
    }
    delete snapshot;
}

dom_surface_view_snapshot *dom_game_runtime_build_surface_view_snapshot(const dom_game_runtime *rt) {
    dom_surface_view_snapshot *snap;
    dom_body_id body_id = 0ull;
    dom_topo_latlong_q16 center;
    q48_16 height = 0;
    const dom_surface_chunks *chunks = 0;
    u32 count = 0u;

    if (!rt) {
        return (dom_surface_view_snapshot *)0;
    }

    center.lat_turns = 0;
    center.lon_turns = 0;
    if (dom_game_runtime_get_surface_focus(rt, &body_id, &center) != DOM_GAME_RUNTIME_OK) {
        body_id = 0ull;
    }
    if (body_id != 0ull) {
        (void)dom_surface_height_sample(body_id, &center, &height);
    }

    snap = new dom_surface_view_snapshot();
    std::memset(snap, 0, sizeof(*snap));
    snap->struct_size = sizeof(*snap);
    snap->struct_version = DOM_SURFACE_VIEW_SNAPSHOT_VERSION;
    snap->body_id = body_id;
    snap->center_latlong = center;
    snap->sampled_height_m = height;

    chunks = static_cast<const dom_surface_chunks *>(dom_game_runtime_surface_chunks(rt));
    if (chunks) {
        if (dom_surface_chunks_list_active(const_cast<dom_surface_chunks *>(chunks),
                                           0,
                                           0u,
                                           &count) == DOM_SURFACE_CHUNKS_OK &&
            count > 0u) {
            snap->chunks = new dom_surface_chunk_view[count];
            if (dom_surface_chunks_list_active(const_cast<dom_surface_chunks *>(chunks),
                                               snap->chunks,
                                               count,
                                               &snap->chunk_count) != DOM_SURFACE_CHUNKS_OK) {
                delete[] snap->chunks;
                snap->chunks = 0;
                snap->chunk_count = 0u;
            }
        }
    }

    return snap;
}

void dom_game_runtime_release_surface_view_snapshot(dom_surface_view_snapshot *snapshot) {
    if (!snapshot) {
        return;
    }
    delete[] snapshot->chunks;
    delete snapshot;
}

dom_local_tangent_frame_snapshot *dom_game_runtime_build_local_tangent_frame_snapshot(const dom_game_runtime *rt) {
    dom_local_tangent_frame_snapshot *snap;
    dom_body_id body_id = 0ull;
    dom_topo_latlong_q16 center;
    dom_topology_binding binding;
    dom_posseg_q16 origin;
    int have_frame = 0;
    int have_origin = 0;

    if (!rt) {
        return (dom_local_tangent_frame_snapshot *)0;
    }

    center.lat_turns = 0;
    center.lon_turns = 0;
    if (dom_game_runtime_get_surface_focus(rt, &body_id, &center) != DOM_GAME_RUNTIME_OK) {
        body_id = 0ull;
    }

    snap = new dom_local_tangent_frame_snapshot();
    std::memset(snap, 0, sizeof(*snap));
    snap->struct_size = sizeof(*snap);
    snap->struct_version = DOM_LOCAL_TANGENT_FRAME_SNAPSHOT_VERSION;
    snap->body_id = body_id;
    snap->center_latlong = center;
    std::memset(&snap->east, 0, sizeof(snap->east));
    std::memset(&snap->north, 0, sizeof(snap->north));
    std::memset(&snap->up, 0, sizeof(snap->up));
    std::memset(&snap->origin_body_fixed, 0, sizeof(snap->origin_body_fixed));

    if (body_id != 0ull) {
        const dom_body_registry *bodies = static_cast<const dom_body_registry *>(
            dom_game_runtime_body_registry(rt));
        if (bodies &&
            dom_surface_topology_select(bodies, body_id, 0u, &binding) == DOM_TOPOLOGY_OK) {
            dom_topo_tangent_frame_q16 frame;
            if (dom_surface_topology_tangent_frame(&binding, &center, &frame) == DOM_TOPOLOGY_OK) {
                snap->east = frame.east;
                snap->north = frame.north;
                snap->up = frame.up;
                have_frame = 1;
            }
            if (dom_surface_topology_pos_from_latlong(&binding, &center, 0, &origin) == DOM_TOPOLOGY_OK) {
                snap->origin_body_fixed = origin;
                have_origin = 1;
            }
        }
    }

    if (!have_frame) {
        snap->east.v[0] = 0;
        snap->east.v[1] = d_q16_16_from_int(1);
        snap->east.v[2] = 0;
        snap->north.v[0] = d_q16_16_from_int(1);
        snap->north.v[1] = 0;
        snap->north.v[2] = 0;
        snap->up.v[0] = 0;
        snap->up.v[1] = 0;
        snap->up.v[2] = d_q16_16_from_int(1);
    }
    if (!have_origin) {
        std::memset(&snap->origin_body_fixed, 0, sizeof(snap->origin_body_fixed));
    }

    return snap;
}

void dom_game_runtime_release_local_tangent_frame_snapshot(dom_local_tangent_frame_snapshot *snapshot) {
    if (!snapshot) {
        return;
    }
    delete snapshot;
}

dom_construction_list_snapshot *dom_game_runtime_build_construction_list_snapshot(const dom_game_runtime *rt) {
    dom_construction_list_snapshot *snap;
    const dom_construction_registry *registry;
    u32 count = 0u;

    if (!rt) {
        return (dom_construction_list_snapshot *)0;
    }
    registry = static_cast<const dom_construction_registry *>(
        dom_game_runtime_construction_registry(rt));
    if (!registry) {
        return (dom_construction_list_snapshot *)0;
    }

    snap = new dom_construction_list_snapshot();
    std::memset(snap, 0, sizeof(*snap));
    snap->struct_size = sizeof(*snap);
    snap->struct_version = DOM_CONSTRUCTION_LIST_SNAPSHOT_VERSION;

    if (dom_construction_list(registry, 0, 0u, &count) == DOM_CONSTRUCTION_OK && count > 0u) {
        dom_construction_instance *tmp = new dom_construction_instance[count];
        u32 filled = 0u;
        if (dom_construction_list(registry, tmp, count, &filled) == DOM_CONSTRUCTION_OK) {
            u32 i;
            snap->constructions = new dom_construction_view[filled];
            snap->construction_count = filled;
            for (i = 0u; i < filled; ++i) {
                dom_construction_view &view = snap->constructions[i];
                view.instance_id = tmp[i].instance_id;
                view.type_id = tmp[i].type_id;
                view.body_id = tmp[i].body_id;
                view.chunk_key = tmp[i].chunk_key;
                view.local_pos_m[0] = tmp[i].local_pos_m[0];
                view.local_pos_m[1] = tmp[i].local_pos_m[1];
                view.local_pos_m[2] = tmp[i].local_pos_m[2];
                view.orientation = tmp[i].orientation;
            }
        }
        delete[] tmp;
        if (!snap->constructions || snap->construction_count == 0u) {
            snap->constructions = 0;
            snap->construction_count = 0u;
        }
    }
    return snap;
}

void dom_game_runtime_release_construction_list_snapshot(dom_construction_list_snapshot *snapshot) {
    if (!snapshot) {
        return;
    }
    delete[] snapshot->constructions;
    delete snapshot;
}

dom_station_list_snapshot *dom_game_runtime_build_station_list_snapshot(const dom_game_runtime *rt) {
    dom_station_list_snapshot *snap;
    const dom_station_registry *registry;
    u32 count = 0u;

    if (!rt) {
        return (dom_station_list_snapshot *)0;
    }
    registry = static_cast<const dom_station_registry *>(
        dom_game_runtime_station_registry(rt));
    if (!registry) {
        return (dom_station_list_snapshot *)0;
    }

    snap = new dom_station_list_snapshot();
    std::memset(snap, 0, sizeof(*snap));
    snap->struct_size = sizeof(*snap);
    snap->struct_version = DOM_STATION_LIST_SNAPSHOT_VERSION;

    count = dom_station_count(registry);
    snap->station_count = count;
    if (count == 0u) {
        return snap;
    }

    {
        std::vector<dom_station_info> stations;
        std::vector<u32> inv_counts;
        StationCollectContext ctx;
        u32 total_inv = 0u;

        stations.reserve(count);
        ctx.stations = &stations;
        (void)dom_station_iterate(registry, collect_station_info, &ctx);

        inv_counts.resize(stations.size());
        for (size_t i = 0u; i < stations.size(); ++i) {
            u32 inv_count = 0u;
            if (dom_station_inventory_list(registry,
                                           stations[i].station_id,
                                           0,
                                           0u,
                                           &inv_count) != DOM_STATION_REGISTRY_OK) {
                inv_count = 0u;
            }
            inv_counts[i] = inv_count;
            if (inv_count > 0u && total_inv > (0xffffffffu - inv_count)) {
                delete snap;
                return (dom_station_list_snapshot *)0;
            }
            total_inv += inv_count;
        }

        snap->stations = new dom_station_view[stations.size()];
        if (total_inv > 0u) {
            snap->inventory = new dom_station_inventory_view[total_inv];
        }
        snap->inventory_count = total_inv;

        u32 inv_offset = 0u;
        for (size_t i = 0u; i < stations.size(); ++i) {
            dom_station_view &view = snap->stations[i];
            u32 inv_count = inv_counts[i];
            u32 filled = 0u;

            view.station_id = stations[i].station_id;
            view.body_id = stations[i].body_id;
            view.frame_id = stations[i].frame_id;
            view.inventory_offset = inv_offset;
            view.inventory_count = 0u;

            if (inv_count > 0u && snap->inventory) {
                std::vector<dom_inventory_entry> inv;
                inv.resize(inv_count);
                if (dom_station_inventory_list(registry,
                                               stations[i].station_id,
                                               &inv[0],
                                               inv_count,
                                               &filled) == DOM_STATION_REGISTRY_OK) {
                    if (filled > inv_count) {
                        filled = inv_count;
                    }
                    for (u32 j = 0u; j < filled; ++j) {
                        dom_station_inventory_view &iview = snap->inventory[inv_offset + j];
                        iview.station_id = stations[i].station_id;
                        iview.resource_id = inv[j].resource_id;
                        iview.quantity = inv[j].quantity;
                    }
                } else {
                    filled = 0u;
                }
            }
            view.inventory_count = filled;
            inv_offset += filled;
        }
    }

    return snap;
}

void dom_game_runtime_release_station_list_snapshot(dom_station_list_snapshot *snapshot) {
    if (!snapshot) {
        return;
    }
    delete[] snapshot->stations;
    delete[] snapshot->inventory;
    delete snapshot;
}

dom_route_list_snapshot *dom_game_runtime_build_route_list_snapshot(const dom_game_runtime *rt) {
    dom_route_list_snapshot *snap;
    const dom_route_graph *graph;
    u32 count = 0u;

    if (!rt) {
        return (dom_route_list_snapshot *)0;
    }
    graph = static_cast<const dom_route_graph *>(dom_game_runtime_route_graph(rt));
    if (!graph) {
        return (dom_route_list_snapshot *)0;
    }

    snap = new dom_route_list_snapshot();
    std::memset(snap, 0, sizeof(*snap));
    snap->struct_size = sizeof(*snap);
    snap->struct_version = DOM_ROUTE_LIST_SNAPSHOT_VERSION;

    count = dom_route_graph_count(graph);
    snap->route_count = count;
    if (count > 0u) {
        std::vector<dom_route_info> routes;
        RouteCollectContext ctx;
        routes.reserve(count);
        ctx.routes = &routes;
        (void)dom_route_graph_iterate(graph, collect_route_info, &ctx);
        snap->routes = new dom_route_view[routes.size()];
        for (size_t i = 0u; i < routes.size(); ++i) {
            dom_route_view &view = snap->routes[i];
            view.route_id = routes[i].route_id;
            view.src_station_id = routes[i].src_station_id;
            view.dst_station_id = routes[i].dst_station_id;
            view.duration_ticks = routes[i].duration_ticks;
            view.capacity_units = routes[i].capacity_units;
        }
    }
    return snap;
}

void dom_game_runtime_release_route_list_snapshot(dom_route_list_snapshot *snapshot) {
    if (!snapshot) {
        return;
    }
    delete[] snapshot->routes;
    delete snapshot;
}

dom_transfer_list_snapshot *dom_game_runtime_build_transfer_list_snapshot(const dom_game_runtime *rt) {
    dom_transfer_list_snapshot *snap;
    const dom_transfer_scheduler *sched;
    u32 count = 0u;

    if (!rt) {
        return (dom_transfer_list_snapshot *)0;
    }
    sched = static_cast<const dom_transfer_scheduler *>(
        dom_game_runtime_transfer_scheduler(rt));
    if (!sched) {
        return (dom_transfer_list_snapshot *)0;
    }

    snap = new dom_transfer_list_snapshot();
    std::memset(snap, 0, sizeof(*snap));
    snap->struct_size = sizeof(*snap);
    snap->struct_version = DOM_TRANSFER_LIST_SNAPSHOT_VERSION;

    if (dom_transfer_list(sched, 0, 0u, &count) != DOM_TRANSFER_OK) {
        return snap;
    }
    snap->transfer_count = count;
    if (count > 0u) {
        std::vector<dom_transfer_info> transfers;
        transfers.resize(count);
        if (dom_transfer_list(sched, &transfers[0], count, &count) == DOM_TRANSFER_OK) {
            snap->transfers = new dom_transfer_view[count];
            for (u32 i = 0u; i < count; ++i) {
                dom_transfer_view &view = snap->transfers[i];
                view.transfer_id = transfers[i].transfer_id;
                view.route_id = transfers[i].route_id;
                view.start_tick = transfers[i].start_tick;
                view.arrival_tick = transfers[i].arrival_tick;
                view.entry_count = transfers[i].entry_count;
                view.total_units = transfers[i].total_units;
            }
        }
    }
    return snap;
}

void dom_game_runtime_release_transfer_list_snapshot(dom_transfer_list_snapshot *snapshot) {
    if (!snapshot) {
        return;
    }
    delete[] snapshot->transfers;
    delete snapshot;
}
