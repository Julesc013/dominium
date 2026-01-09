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
#include <climits>

#include "runtime/dom_io_guard.h"
#include "runtime/dom_cosmo_graph.h"
#include "runtime/dom_game_runtime.h"
#include "runtime/dom_game_query.h"
#include "runtime/dom_system_registry.h"
#include "runtime/dom_body_registry.h"
#include "runtime/dom_frames.h"
#include "runtime/dom_lane_scheduler.h"
#include "runtime/dom_media_provider.h"
#include "runtime/dom_weather_provider.h"
#include "runtime/dom_surface_topology.h"
#include "runtime/dom_surface_height.h"
#include "runtime/dom_construction_registry.h"
#include "runtime/dom_station_registry.h"
#include "runtime/dom_route_graph.h"
#include "runtime/dom_transfer_scheduler.h"
#include "runtime/dom_macro_economy.h"
#include "runtime/dom_macro_events.h"
#include "runtime/dom_faction_registry.h"
#include "runtime/dom_ai_scheduler.h"

extern "C" {
#include "domino/core/dom_deterministic_math.h"
}

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

struct FactionCollectContext {
    std::vector<dom_faction_info> *factions;
};

static void collect_faction_info(const dom_faction_info *info, void *user) {
    FactionCollectContext *ctx = static_cast<FactionCollectContext *>(user);
    if (ctx && ctx->factions && info) {
        ctx->factions->push_back(*info);
    }
}

static u64 abs_i64_u64(i64 v) {
    return v < 0 ? (u64)(-v) : (u64)v;
}

static u64 square_u64_clamp(u64 v) {
    if (v != 0u && v > (UINT64_MAX / v)) {
        return UINT64_MAX;
    }
    return v * v;
}

static u64 add_u64_clamp(u64 a, u64 b) {
    u64 sum = a + b;
    if (sum < a) {
        return UINT64_MAX;
    }
    return sum;
}

static u64 spacepos_length_u64(const SpacePos *pos) {
    u64 x2;
    u64 y2;
    u64 z2;
    u64 sum;
    if (!pos) {
        return 0u;
    }
    x2 = square_u64_clamp(abs_i64_u64(d_q48_16_to_int(pos->x)));
    y2 = square_u64_clamp(abs_i64_u64(d_q48_16_to_int(pos->y)));
    z2 = square_u64_clamp(abs_i64_u64(d_q48_16_to_int(pos->z)));
    sum = add_u64_clamp(x2, y2);
    sum = add_u64_clamp(sum, z2);
    return dom_sqrt_u64(sum);
}

static bool compute_altitude_from_pos(const dom_body_registry *bodies,
                                      dom_body_id body_id,
                                      const SpacePos *pos,
                                      q48_16 *out_altitude) {
    dom_body_info info;
    if (!bodies || !pos || !out_altitude || body_id == 0ull) {
        return false;
    }
    if (dom_body_registry_get(bodies, body_id, &info) != DOM_BODY_REGISTRY_OK) {
        return false;
    }
    *out_altitude = d_q48_16_sub(d_q48_16_from_int((i64)spacepos_length_u64(pos)),
                                 info.radius_m);
    return true;
}

static void zero_media_sample(dom_media_sample *sample) {
    if (!sample) {
        return;
    }
    std::memset(sample, 0, sizeof(*sample));
}

static void apply_weather_mods(dom_media_sample *sample,
                               const dom_weather_mods *mods) {
    if (!sample || !mods) {
        return;
    }
    sample->density_q16 = d_q16_16_add(sample->density_q16, mods->density_delta_q16);
    if (sample->density_q16 < 0) {
        sample->density_q16 = 0;
    }
    sample->pressure_q16 = d_q16_16_add(sample->pressure_q16, mods->pressure_delta_q16);
    if (sample->pressure_q16 < 0) {
        sample->pressure_q16 = 0;
    }
    sample->temperature_q16 = d_q16_16_add(sample->temperature_q16, mods->temperature_delta_q16);
    if (sample->temperature_q16 < 0) {
        sample->temperature_q16 = 0;
    }
    if (mods->has_wind || sample->has_wind) {
        sample->wind_body_q16.v[0] =
            d_q16_16_add(sample->wind_body_q16.v[0], mods->wind_delta_q16.v[0]);
        sample->wind_body_q16.v[1] =
            d_q16_16_add(sample->wind_body_q16.v[1], mods->wind_delta_q16.v[1]);
        sample->wind_body_q16.v[2] =
            d_q16_16_add(sample->wind_body_q16.v[2], mods->wind_delta_q16.v[2]);
        sample->has_wind = 1u;
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

dom_atmos_sample_snapshot *dom_game_runtime_build_atmos_sample_snapshot(const dom_game_runtime *rt) {
    dom_atmos_sample_snapshot *snap;
    const dom_lane_scheduler *sched;
    dom_activation_bubble bubble;
    int bubble_active = 0;
    dom_body_id body_id = 0ull;
    SpacePos pos;
    dom_lane_type lane = DOM_LANE_ORBITAL;
    q48_16 altitude = 0;
    dom_media_sample sample;
    dom_weather_mods mods;
    const dom_media_registry *media;
    const dom_weather_registry *weather;
    const dom_body_registry *bodies;

    if (!rt) {
        return (dom_atmos_sample_snapshot *)0;
    }

    snap = new dom_atmos_sample_snapshot();
    std::memset(snap, 0, sizeof(*snap));
    snap->struct_size = sizeof(*snap);
    snap->struct_version = DOM_ATMOS_SAMPLE_SNAPSHOT_VERSION;
    snap->has_sample = 0u;

    sched = static_cast<const dom_lane_scheduler *>(dom_game_runtime_lane_scheduler(rt));
    if (!sched) {
        return snap;
    }
    if (dom_lane_scheduler_get_bubble(sched, &bubble, &bubble_active, &body_id, 0) != DOM_LANE_OK ||
        !bubble_active || body_id == 0ull) {
        return snap;
    }
    if (dom_lane_scheduler_get_local_state(sched, bubble.center_vessel_id, &pos, 0, &lane) != DOM_LANE_OK) {
        return snap;
    }
    if (lane != DOM_LANE_LOCAL_KINEMATIC && lane != DOM_LANE_DOCKED_LANDED) {
        return snap;
    }

    bodies = static_cast<const dom_body_registry *>(dom_game_runtime_body_registry(rt));
    if (!compute_altitude_from_pos(bodies, body_id, &pos, &altitude)) {
        altitude = 0;
    }

    zero_media_sample(&sample);
    media = static_cast<const dom_media_registry *>(dom_game_runtime_media_registry(rt));
    if (media) {
        int rc = dom_media_sample(media,
                                  body_id,
                                  DOM_MEDIA_KIND_ATMOSPHERE,
                                  0,
                                  altitude,
                                  dom_game_runtime_get_tick(rt),
                                  &sample);
        if (rc != DOM_MEDIA_OK) {
            zero_media_sample(&sample);
        }
    }
    weather = static_cast<const dom_weather_registry *>(dom_game_runtime_weather_registry(rt));
    if (weather) {
        std::memset(&mods, 0, sizeof(mods));
        if (dom_weather_sample_modifiers(weather,
                                         body_id,
                                         0,
                                         altitude,
                                         dom_game_runtime_get_tick(rt),
                                         &mods) == DOM_WEATHER_OK) {
            apply_weather_mods(&sample, &mods);
        }
    }

    snap->body_id = body_id;
    snap->altitude_m = altitude;
    snap->density_q16 = sample.density_q16;
    snap->pressure_q16 = sample.pressure_q16;
    snap->temperature_q16 = sample.temperature_q16;
    snap->has_sample = 1u;
    return snap;
}

void dom_game_runtime_release_atmos_sample_snapshot(dom_atmos_sample_snapshot *snapshot) {
    if (!snapshot) {
        return;
    }
    delete snapshot;
}

dom_reentry_status_snapshot *dom_game_runtime_build_reentry_status_snapshot(const dom_game_runtime *rt) {
    dom_reentry_status_snapshot *snap;
    const dom_lane_scheduler *sched;
    dom_activation_bubble bubble;
    int bubble_active = 0;
    dom_lane_type lane = DOM_LANE_ORBITAL;
    dom_vehicle_aero_state aero;
    u64 vessel_id = 0ull;
    int rc;

    if (!rt) {
        return (dom_reentry_status_snapshot *)0;
    }

    snap = new dom_reentry_status_snapshot();
    std::memset(snap, 0, sizeof(*snap));
    snap->struct_size = sizeof(*snap);
    snap->struct_version = DOM_REENTRY_STATUS_SNAPSHOT_VERSION;
    snap->max_warp_factor = 1u;
    snap->has_data = 0u;

    sched = static_cast<const dom_lane_scheduler *>(dom_game_runtime_lane_scheduler(rt));
    if (!sched) {
        return snap;
    }
    snap->max_warp_factor = dom_lane_scheduler_max_warp(sched);
    if (dom_lane_scheduler_get_bubble(sched, &bubble, &bubble_active, 0, 0) != DOM_LANE_OK ||
        !bubble_active) {
        return snap;
    }
    vessel_id = bubble.center_vessel_id;
    if (dom_lane_scheduler_get_local_state(sched, vessel_id, 0, 0, &lane) != DOM_LANE_OK) {
        return snap;
    }
    if (lane != DOM_LANE_LOCAL_KINEMATIC && lane != DOM_LANE_DOCKED_LANDED) {
        return snap;
    }

    rc = dom_lane_scheduler_get_aero_state(sched, vessel_id, &aero);
    if (rc != DOM_LANE_OK) {
        return snap;
    }

    snap->vessel_id = vessel_id;
    snap->drag_accel_q16 = aero.last_drag_accel_q16;
    snap->heating_rate_q16 = aero.last_heating_rate_q16;
    snap->heat_accum_q16 = aero.heat_accum_q16;
    snap->has_data = 1u;
    return snap;
}

void dom_game_runtime_release_reentry_status_snapshot(dom_reentry_status_snapshot *snapshot) {
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

dom_macro_economy_snapshot *dom_game_runtime_build_macro_economy_snapshot(const dom_game_runtime *rt) {
    dom_macro_economy_snapshot *snap;
    const dom_macro_economy *econ;
    u32 sys_count = 0u;
    u32 gal_count = 0u;
    u32 scope_count = 0u;
    u32 total_prod = 0u;
    u32 total_demand = 0u;
    u32 total_stock = 0u;

    if (!rt) {
        return (dom_macro_economy_snapshot *)0;
    }
    econ = static_cast<const dom_macro_economy *>(dom_game_runtime_macro_economy(rt));
    if (!econ) {
        return (dom_macro_economy_snapshot *)0;
    }
    if (dom_macro_economy_list_scopes(econ, DOM_MACRO_SCOPE_SYSTEM, 0, 0u, &sys_count) != DOM_MACRO_ECONOMY_OK ||
        dom_macro_economy_list_scopes(econ, DOM_MACRO_SCOPE_GALAXY, 0, 0u, &gal_count) != DOM_MACRO_ECONOMY_OK) {
        return (dom_macro_economy_snapshot *)0;
    }
    scope_count = sys_count + gal_count;

    snap = new dom_macro_economy_snapshot();
    if (!snap) {
        return (dom_macro_economy_snapshot *)0;
    }
    std::memset(snap, 0, sizeof(*snap));
    snap->struct_size = sizeof(*snap);
    snap->struct_version = DOM_MACRO_ECONOMY_SNAPSHOT_VERSION;
    snap->scope_count = scope_count;

    if (scope_count > 0u) {
        std::vector<dom_macro_scope_info> scopes;
        scopes.resize(scope_count);
        if (sys_count > 0u) {
            u32 out_count = sys_count;
            if (dom_macro_economy_list_scopes(econ,
                                              DOM_MACRO_SCOPE_SYSTEM,
                                              &scopes[0],
                                              sys_count,
                                              &out_count) != DOM_MACRO_ECONOMY_OK) {
                delete snap;
                return (dom_macro_economy_snapshot *)0;
            }
            sys_count = out_count;
        }
        if (gal_count > 0u) {
            u32 out_count = gal_count;
            if (dom_macro_economy_list_scopes(econ,
                                              DOM_MACRO_SCOPE_GALAXY,
                                              &scopes[sys_count],
                                              gal_count,
                                              &out_count) != DOM_MACRO_ECONOMY_OK) {
                delete snap;
                return (dom_macro_economy_snapshot *)0;
            }
            gal_count = out_count;
        }
        scope_count = sys_count + gal_count;
        snap->scope_count = scope_count;

        for (u32 i = 0u; i < scope_count; ++i) {
            total_prod += scopes[i].production_count;
            total_demand += scopes[i].demand_count;
            total_stock += scopes[i].stockpile_count;
        }

        snap->production_count = total_prod;
        snap->demand_count = total_demand;
        snap->stockpile_count = total_stock;

        snap->scopes = new dom_macro_scope_view[scope_count];
        if (!snap->scopes) {
            delete snap;
            return (dom_macro_economy_snapshot *)0;
        }
        if (total_prod > 0u) {
            snap->production = new dom_macro_rate_view[total_prod];
            if (!snap->production) {
                dom_game_runtime_release_macro_economy_snapshot(snap);
                return (dom_macro_economy_snapshot *)0;
            }
        }
        if (total_demand > 0u) {
            snap->demand = new dom_macro_rate_view[total_demand];
            if (!snap->demand) {
                dom_game_runtime_release_macro_economy_snapshot(snap);
                return (dom_macro_economy_snapshot *)0;
            }
        }
        if (total_stock > 0u) {
            snap->stockpile = new dom_macro_stock_view[total_stock];
            if (!snap->stockpile) {
                dom_game_runtime_release_macro_economy_snapshot(snap);
                return (dom_macro_economy_snapshot *)0;
            }
        }

        u32 prod_offset = 0u;
        u32 demand_offset = 0u;
        u32 stock_offset = 0u;
        for (u32 i = 0u; i < scope_count; ++i) {
            const dom_macro_scope_info &info = scopes[i];
            dom_macro_scope_view &view = snap->scopes[i];
            view.scope_kind = info.scope_kind;
            view.scope_id = info.scope_id;
            view.flags = info.flags;
            view.production_count = info.production_count;
            view.production_offset = prod_offset;
            view.demand_count = info.demand_count;
            view.demand_offset = demand_offset;
            view.stockpile_count = info.stockpile_count;
            view.stockpile_offset = stock_offset;

            if (info.production_count > 0u) {
                std::vector<dom_macro_rate_entry> entries;
                entries.resize(info.production_count);
                u32 count = info.production_count;
                if (dom_macro_economy_list_production(econ,
                                                      info.scope_kind,
                                                      info.scope_id,
                                                      &entries[0],
                                                      count,
                                                      &count) != DOM_MACRO_ECONOMY_OK) {
                    dom_game_runtime_release_macro_economy_snapshot(snap);
                    return (dom_macro_economy_snapshot *)0;
                }
                for (u32 j = 0u; j < count; ++j) {
                    dom_macro_rate_view &rview = snap->production[prod_offset + j];
                    rview.resource_id = entries[j].resource_id;
                    rview.rate_per_tick = entries[j].rate_per_tick;
                }
                prod_offset += count;
            }

            if (info.demand_count > 0u) {
                std::vector<dom_macro_rate_entry> entries;
                entries.resize(info.demand_count);
                u32 count = info.demand_count;
                if (dom_macro_economy_list_demand(econ,
                                                  info.scope_kind,
                                                  info.scope_id,
                                                  &entries[0],
                                                  count,
                                                  &count) != DOM_MACRO_ECONOMY_OK) {
                    dom_game_runtime_release_macro_economy_snapshot(snap);
                    return (dom_macro_economy_snapshot *)0;
                }
                for (u32 j = 0u; j < count; ++j) {
                    dom_macro_rate_view &rview = snap->demand[demand_offset + j];
                    rview.resource_id = entries[j].resource_id;
                    rview.rate_per_tick = entries[j].rate_per_tick;
                }
                demand_offset += count;
            }

            if (info.stockpile_count > 0u) {
                std::vector<dom_macro_stock_entry> entries;
                entries.resize(info.stockpile_count);
                u32 count = info.stockpile_count;
                if (dom_macro_economy_list_stockpile(econ,
                                                     info.scope_kind,
                                                     info.scope_id,
                                                     &entries[0],
                                                     count,
                                                     &count) != DOM_MACRO_ECONOMY_OK) {
                    dom_game_runtime_release_macro_economy_snapshot(snap);
                    return (dom_macro_economy_snapshot *)0;
                }
                for (u32 j = 0u; j < count; ++j) {
                    dom_macro_stock_view &sview = snap->stockpile[stock_offset + j];
                    sview.resource_id = entries[j].resource_id;
                    sview.quantity = entries[j].quantity;
                }
                stock_offset += count;
            }
        }
    }

    return snap;
}

void dom_game_runtime_release_macro_economy_snapshot(dom_macro_economy_snapshot *snapshot) {
    if (!snapshot) {
        return;
    }
    delete[] snapshot->scopes;
    delete[] snapshot->production;
    delete[] snapshot->demand;
    delete[] snapshot->stockpile;
    delete snapshot;
}

dom_macro_event_list_snapshot *dom_game_runtime_build_macro_event_list_snapshot(const dom_game_runtime *rt) {
    dom_macro_event_list_snapshot *snap;
    const dom_macro_events *events;
    u32 event_count = 0u;
    u32 effect_count = 0u;

    if (!rt) {
        return (dom_macro_event_list_snapshot *)0;
    }
    events = static_cast<const dom_macro_events *>(dom_game_runtime_macro_events(rt));
    if (!events) {
        return (dom_macro_event_list_snapshot *)0;
    }
    if (dom_macro_events_list(events, 0, 0u, &event_count) != DOM_MACRO_EVENTS_OK) {
        return (dom_macro_event_list_snapshot *)0;
    }

    snap = new dom_macro_event_list_snapshot();
    if (!snap) {
        return (dom_macro_event_list_snapshot *)0;
    }
    std::memset(snap, 0, sizeof(*snap));
    snap->struct_size = sizeof(*snap);
    snap->struct_version = DOM_MACRO_EVENT_LIST_SNAPSHOT_VERSION;
    snap->event_count = event_count;

    if (event_count > 0u) {
        std::vector<dom_macro_event_info> infos;
        infos.resize(event_count);
        if (dom_macro_events_list(events, &infos[0], event_count, &event_count) != DOM_MACRO_EVENTS_OK) {
            delete snap;
            return (dom_macro_event_list_snapshot *)0;
        }
        snap->event_count = event_count;
        for (u32 i = 0u; i < event_count; ++i) {
            effect_count += infos[i].effect_count;
        }

        snap->effect_count = effect_count;
        snap->events = new dom_macro_event_view[event_count];
        if (!snap->events) {
            delete snap;
            return (dom_macro_event_list_snapshot *)0;
        }
        if (effect_count > 0u) {
            snap->effects = new dom_macro_event_effect_view[effect_count];
            if (!snap->effects) {
                dom_game_runtime_release_macro_event_list_snapshot(snap);
                return (dom_macro_event_list_snapshot *)0;
            }
        }

        u32 effect_offset = 0u;
        for (u32 i = 0u; i < event_count; ++i) {
            const dom_macro_event_info &info = infos[i];
            dom_macro_event_view &view = snap->events[i];
            view.event_id = info.event_id;
            view.scope_kind = info.scope_kind;
            view.scope_id = info.scope_id;
            view.trigger_tick = info.trigger_tick;
            view.effect_count = info.effect_count;
            view.effect_offset = effect_offset;

            if (info.effect_count > 0u) {
                std::vector<dom_macro_event_effect> effects;
                effects.resize(info.effect_count);
                u32 count = info.effect_count;
                if (dom_macro_events_list_effects(events,
                                                  info.event_id,
                                                  &effects[0],
                                                  count,
                                                  &count) != DOM_MACRO_EVENTS_OK) {
                    dom_game_runtime_release_macro_event_list_snapshot(snap);
                    return (dom_macro_event_list_snapshot *)0;
                }
                for (u32 j = 0u; j < count; ++j) {
                    dom_macro_event_effect_view &eview = snap->effects[effect_offset + j];
                    eview.resource_id = effects[j].resource_id;
                    eview.production_delta = effects[j].production_delta;
                    eview.demand_delta = effects[j].demand_delta;
                    eview.flags_set = effects[j].flags_set;
                    eview.flags_clear = effects[j].flags_clear;
                }
                effect_offset += count;
            }
        }
    }

    return snap;
}

void dom_game_runtime_release_macro_event_list_snapshot(dom_macro_event_list_snapshot *snapshot) {
    if (!snapshot) {
        return;
    }
    delete[] snapshot->events;
    delete[] snapshot->effects;
    delete snapshot;
}

dom_faction_list_snapshot *dom_game_runtime_build_faction_list_snapshot(const dom_game_runtime *rt) {
    dom_faction_list_snapshot *snap;
    const dom_faction_registry *registry;
    u32 count = 0u;

    if (!rt) {
        return (dom_faction_list_snapshot *)0;
    }
    registry = static_cast<const dom_faction_registry *>(dom_game_runtime_faction_registry(rt));
    if (!registry) {
        return (dom_faction_list_snapshot *)0;
    }

    snap = new dom_faction_list_snapshot();
    std::memset(snap, 0, sizeof(*snap));
    snap->struct_size = sizeof(*snap);
    snap->struct_version = DOM_FACTION_LIST_SNAPSHOT_VERSION;

    count = dom_faction_count(registry);
    snap->faction_count = count;
    if (count == 0u) {
        return snap;
    }

    {
        std::vector<dom_faction_info> list;
        FactionCollectContext ctx;
        list.reserve(count);
        ctx.factions = &list;
        (void)dom_faction_iterate(registry, collect_faction_info, &ctx);
        snap->faction_count = (u32)list.size();
        if (!list.empty()) {
            snap->factions = new dom_faction_view[list.size()];
            for (size_t i = 0u; i < list.size(); ++i) {
                dom_faction_view &view = snap->factions[i];
                view.faction_id = list[i].faction_id;
                view.home_scope_kind = list[i].home_scope_kind;
                view.home_scope_id = list[i].home_scope_id;
                view.policy_kind = list[i].policy_kind;
                view.policy_flags = list[i].policy_flags;
                view.ai_seed = list[i].ai_seed;
            }
        }
    }

    return snap;
}

void dom_game_runtime_release_faction_list_snapshot(dom_faction_list_snapshot *snapshot) {
    if (!snapshot) {
        return;
    }
    delete[] snapshot->factions;
    delete snapshot;
}

dom_faction_summary_snapshot *dom_game_runtime_build_faction_summary_snapshot(const dom_game_runtime *rt) {
    dom_faction_summary_snapshot *snap;
    const dom_faction_registry *registry;
    u32 count = 0u;
    u32 total_resources = 0u;
    u32 total_nodes = 0u;

    if (!rt) {
        return (dom_faction_summary_snapshot *)0;
    }
    registry = static_cast<const dom_faction_registry *>(dom_game_runtime_faction_registry(rt));
    if (!registry) {
        return (dom_faction_summary_snapshot *)0;
    }

    snap = new dom_faction_summary_snapshot();
    std::memset(snap, 0, sizeof(*snap));
    snap->struct_size = sizeof(*snap);
    snap->struct_version = DOM_FACTION_SUMMARY_SNAPSHOT_VERSION;

    count = dom_faction_count(registry);
    snap->faction_count = count;
    if (count == 0u) {
        return snap;
    }

    {
        std::vector<dom_faction_info> list;
        FactionCollectContext ctx;
        list.reserve(count);
        ctx.factions = &list;
        (void)dom_faction_iterate(registry, collect_faction_info, &ctx);
        snap->faction_count = (u32)list.size();

        for (size_t i = 0u; i < list.size(); ++i) {
            u32 res_count = 0u;
            u32 node_count = 0u;
            if (dom_faction_resource_list(registry,
                                          list[i].faction_id,
                                          0,
                                          0u,
                                          &res_count) != DOM_FACTION_OK) {
                res_count = 0u;
            }
            if (dom_faction_list_known_nodes(registry,
                                             list[i].faction_id,
                                             0,
                                             0u,
                                             &node_count) != DOM_FACTION_OK) {
                node_count = 0u;
            }
            if (res_count > 0u && total_resources > (0xffffffffu - res_count)) {
                delete snap;
                return (dom_faction_summary_snapshot *)0;
            }
            if (node_count > 0u && total_nodes > (0xffffffffu - node_count)) {
                delete snap;
                return (dom_faction_summary_snapshot *)0;
            }
            total_resources += res_count;
            total_nodes += node_count;
        }

        snap->resource_count = total_resources;
        snap->known_node_count = total_nodes;
        if (!list.empty()) {
            snap->factions = new dom_faction_summary_view[list.size()];
        }
        if (total_resources > 0u) {
            snap->resources = new dom_faction_resource_view[total_resources];
        }
        if (total_nodes > 0u) {
            snap->known_nodes = new dom_faction_known_node_view[total_nodes];
        }

        u32 res_offset = 0u;
        u32 node_offset = 0u;
        for (size_t i = 0u; i < list.size(); ++i) {
            dom_faction_summary_view &view = snap->factions[i];
            u32 res_count = 0u;
            u32 node_count = 0u;
            u32 res_filled = 0u;
            u32 node_filled = 0u;

            view.faction_id = list[i].faction_id;
            view.home_scope_kind = list[i].home_scope_kind;
            view.home_scope_id = list[i].home_scope_id;
            view.policy_kind = list[i].policy_kind;
            view.policy_flags = list[i].policy_flags;
            view.ai_seed = list[i].ai_seed;

            if (dom_faction_resource_list(registry,
                                          list[i].faction_id,
                                          0,
                                          0u,
                                          &res_count) != DOM_FACTION_OK) {
                res_count = 0u;
            }
            if (dom_faction_list_known_nodes(registry,
                                             list[i].faction_id,
                                             0,
                                             0u,
                                             &node_count) != DOM_FACTION_OK) {
                node_count = 0u;
            }

            view.resource_offset = res_offset;
            view.resource_count = res_count;
            view.known_node_offset = node_offset;
            view.known_node_count = node_count;

            if (res_count > 0u && snap->resources) {
                std::vector<dom_faction_resource_entry> entries;
                entries.resize(res_count);
                if (dom_faction_resource_list(registry,
                                              list[i].faction_id,
                                              &entries[0],
                                              res_count,
                                              &res_filled) == DOM_FACTION_OK) {
                    if (res_filled > res_count) {
                        res_filled = res_count;
                    }
                    for (u32 j = 0u; j < res_filled; ++j) {
                        dom_faction_resource_view &rview = snap->resources[res_offset + j];
                        rview.faction_id = list[i].faction_id;
                        rview.resource_id = entries[j].resource_id;
                        rview.quantity = entries[j].quantity;
                    }
                } else {
                    res_filled = 0u;
                }
            }

            if (node_count > 0u && snap->known_nodes) {
                std::vector<u64> nodes;
                nodes.resize(node_count);
                if (dom_faction_list_known_nodes(registry,
                                                 list[i].faction_id,
                                                 &nodes[0],
                                                 node_count,
                                                 &node_filled) == DOM_FACTION_OK) {
                    if (node_filled > node_count) {
                        node_filled = node_count;
                    }
                    for (u32 j = 0u; j < node_filled; ++j) {
                        dom_faction_known_node_view &nview = snap->known_nodes[node_offset + j];
                        nview.faction_id = list[i].faction_id;
                        nview.node_id = nodes[j];
                    }
                } else {
                    node_filled = 0u;
                }
            }

            view.resource_count = res_filled;
            view.known_node_count = node_filled;
            res_offset += res_filled;
            node_offset += node_filled;
        }

        snap->resource_count = res_offset;
        snap->known_node_count = node_offset;
    }

    return snap;
}

void dom_game_runtime_release_faction_summary_snapshot(dom_faction_summary_snapshot *snapshot) {
    if (!snapshot) {
        return;
    }
    delete[] snapshot->factions;
    delete[] snapshot->resources;
    delete[] snapshot->known_nodes;
    delete snapshot;
}

dom_ai_decision_summary_snapshot *dom_game_runtime_build_ai_decision_summary_snapshot(const dom_game_runtime *rt) {
    dom_ai_decision_summary_snapshot *snap;
    const dom_ai_scheduler *sched;
    u32 count = 0u;

    if (!rt) {
        return (dom_ai_decision_summary_snapshot *)0;
    }
    sched = static_cast<const dom_ai_scheduler *>(dom_game_runtime_ai_scheduler(rt));
    if (!sched) {
        return (dom_ai_decision_summary_snapshot *)0;
    }
    if (dom_ai_scheduler_list_states(sched, 0, 0u, &count) != DOM_AI_SCHEDULER_OK) {
        return (dom_ai_decision_summary_snapshot *)0;
    }

    snap = new dom_ai_decision_summary_snapshot();
    std::memset(snap, 0, sizeof(*snap));
    snap->struct_size = sizeof(*snap);
    snap->struct_version = DOM_AI_DECISION_SUMMARY_SNAPSHOT_VERSION;
    snap->entry_count = count;

    if (count > 0u) {
        std::vector<dom_ai_faction_state> states;
        states.resize(count);
        if (dom_ai_scheduler_list_states(sched, &states[0], count, &count) != DOM_AI_SCHEDULER_OK) {
            delete snap;
            return (dom_ai_decision_summary_snapshot *)0;
        }
        snap->entry_count = count;
        if (count > 0u) {
            snap->entries = new dom_ai_decision_view[count];
            for (u32 i = 0u; i < count; ++i) {
                dom_ai_decision_view &view = snap->entries[i];
                view.faction_id = states[i].faction_id;
                view.next_decision_tick = states[i].next_decision_tick;
                view.last_plan_id = states[i].last_plan_id;
                view.last_output_count = states[i].last_output_count;
                view.last_reason_code = states[i].last_reason_code;
                view.last_budget_hit = states[i].last_budget_hit;
            }
        }
    }

    return snap;
}

void dom_game_runtime_release_ai_decision_summary_snapshot(dom_ai_decision_summary_snapshot *snapshot) {
    if (!snapshot) {
        return;
    }
    delete[] snapshot->entries;
    delete snapshot;
}
