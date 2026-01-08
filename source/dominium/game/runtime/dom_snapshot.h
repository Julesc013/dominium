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

#include "domino/core/fixed.h"
#include "domino/core/types.h"
#include "runtime/dom_cosmo_transit.h"
#include "runtime/dom_surface_chunks.h"

#ifdef __cplusplus
extern "C" {
#endif

enum {
    DOM_RUNTIME_SUMMARY_SNAPSHOT_VERSION = 2u,
    DOM_VIEW_STATE_SNAPSHOT_VERSION = 1u,
    DOM_GAME_SNAPSHOT_VERSION = 1u,
    DOM_COSMO_MAP_SNAPSHOT_VERSION = 1u,
    DOM_COSMO_TRANSIT_SNAPSHOT_VERSION = 1u,
    DOM_SYSTEM_LIST_SNAPSHOT_VERSION = 1u,
    DOM_BODY_LIST_SNAPSHOT_VERSION = 1u,
    DOM_FRAME_TREE_SNAPSHOT_VERSION = 1u,
    DOM_BODY_TOPOLOGY_SNAPSHOT_VERSION = 1u,
    DOM_ORBIT_SUMMARY_SNAPSHOT_VERSION = 1u,
    DOM_SURFACE_VIEW_SNAPSHOT_VERSION = 1u,
    DOM_LOCAL_TANGENT_FRAME_SNAPSHOT_VERSION = 1u,
    DOM_CONSTRUCTION_LIST_SNAPSHOT_VERSION = 1u,
    DOM_STATION_LIST_SNAPSHOT_VERSION = 1u,
    DOM_ROUTE_LIST_SNAPSHOT_VERSION = 1u,
    DOM_TRANSFER_LIST_SNAPSHOT_VERSION = 1u
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

typedef struct dom_cosmo_entity_view {
    u64 id;
    u64 parent_id;
    u32 kind;
} dom_cosmo_entity_view;

typedef struct dom_cosmo_edge_view {
    u64 id;
    u64 src_id;
    u64 dst_id;
    u64 duration_ticks;
    u32 cost;
} dom_cosmo_edge_view;

typedef struct dom_cosmo_map_snapshot {
    u32 struct_size;
    u32 struct_version;
    u32 entity_count;
    u32 edge_count;
    dom_cosmo_entity_view *entities;
    dom_cosmo_edge_view *edges;
    dom_cosmo_transit_state transit;
    int transit_active;
} dom_cosmo_map_snapshot;

typedef struct dom_cosmo_transit_snapshot {
    u32 struct_size;
    u32 struct_version;
    dom_cosmo_transit_state transit;
    int transit_active;
    u64 last_arrival_tick;
} dom_cosmo_transit_snapshot;

typedef struct dom_system_view {
    u64 id;
    u64 parent_id;
} dom_system_view;

typedef struct dom_body_view {
    u64 id;
    u64 system_id;
    u32 kind;
    q48_16 radius_m;
    u64 mu_m3_s2;
    u64 rotation_period_ticks;
} dom_body_view;

typedef struct dom_frame_view {
    u64 id;
    u64 parent_id;
    u32 kind;
    u64 body_id;
} dom_frame_view;

typedef struct dom_body_topology_view {
    u64 body_id;
    u32 topology_kind;
    q48_16 param_a_m;
    q48_16 param_b_m;
    q48_16 param_c_m;
} dom_body_topology_view;

typedef struct dom_system_list_snapshot {
    u32 struct_size;
    u32 struct_version;
    u32 system_count;
    dom_system_view *systems;
} dom_system_list_snapshot;

typedef struct dom_body_list_snapshot {
    u32 struct_size;
    u32 struct_version;
    u32 body_count;
    dom_body_view *bodies;
} dom_body_list_snapshot;

typedef struct dom_frame_tree_snapshot {
    u32 struct_size;
    u32 struct_version;
    u32 frame_count;
    dom_frame_view *frames;
} dom_frame_tree_snapshot;

typedef struct dom_body_topology_snapshot {
    u32 struct_size;
    u32 struct_version;
    u32 body_count;
    dom_body_topology_view *bodies;
} dom_body_topology_snapshot;

typedef struct dom_orbit_summary_snapshot {
    u32 struct_size;
    u32 struct_version;
    u64 vessel_id;
    u64 primary_body_id;
    q48_16 altitude_m;
    q48_16 apoapsis_m;
    q48_16 periapsis_m;
    u64 period_ticks;
    u32 next_event_kind;
    u64 next_event_tick;
    u32 has_orbit;
} dom_orbit_summary_snapshot;

typedef struct dom_surface_chunk_view {
    dom_surface_chunk_key key;
    u32 state;
} dom_surface_chunk_view;

typedef struct dom_surface_view_snapshot {
    u32 struct_size;
    u32 struct_version;
    u64 body_id;
    dom_topo_latlong_q16 center_latlong;
    q48_16 sampled_height_m;
    u32 chunk_count;
    dom_surface_chunk_view *chunks;
} dom_surface_view_snapshot;

typedef struct dom_local_tangent_frame_snapshot {
    u32 struct_size;
    u32 struct_version;
    u64 body_id;
    dom_topo_latlong_q16 center_latlong;
    dom_topo_vec3_q16 east;
    dom_topo_vec3_q16 north;
    dom_topo_vec3_q16 up;
    dom_posseg_q16 origin_body_fixed;
} dom_local_tangent_frame_snapshot;

typedef struct dom_construction_view {
    u64 instance_id;
    u32 type_id;
    u64 body_id;
    dom_surface_chunk_key chunk_key;
    q48_16 local_pos_m[3];
    u32 orientation;
} dom_construction_view;

typedef struct dom_construction_list_snapshot {
    u32 struct_size;
    u32 struct_version;
    u32 construction_count;
    dom_construction_view *constructions;
} dom_construction_list_snapshot;

typedef struct dom_station_view {
    u64 station_id;
    u64 body_id;
    u64 frame_id;
    u32 inventory_count;
    u32 inventory_offset;
} dom_station_view;

typedef struct dom_station_inventory_view {
    u64 station_id;
    u64 resource_id;
    i64 quantity;
} dom_station_inventory_view;

typedef struct dom_station_list_snapshot {
    u32 struct_size;
    u32 struct_version;
    u32 station_count;
    u32 inventory_count;
    dom_station_view *stations;
    dom_station_inventory_view *inventory;
} dom_station_list_snapshot;

typedef struct dom_route_view {
    u64 route_id;
    u64 src_station_id;
    u64 dst_station_id;
    u64 duration_ticks;
    u64 capacity_units;
} dom_route_view;

typedef struct dom_route_list_snapshot {
    u32 struct_size;
    u32 struct_version;
    u32 route_count;
    dom_route_view *routes;
} dom_route_list_snapshot;

typedef struct dom_transfer_view {
    u64 transfer_id;
    u64 route_id;
    u64 start_tick;
    u64 arrival_tick;
    u32 entry_count;
    u64 total_units;
} dom_transfer_view;

typedef struct dom_transfer_list_snapshot {
    u32 struct_size;
    u32 struct_version;
    u32 transfer_count;
    dom_transfer_view *transfers;
} dom_transfer_list_snapshot;

struct dom_game_runtime;

dom_game_snapshot *dom_game_runtime_build_snapshot(const struct dom_game_runtime *rt, u32 flags);
void dom_game_runtime_release_snapshot(dom_game_snapshot *snapshot);
dom_cosmo_map_snapshot *dom_game_runtime_build_cosmo_map_snapshot(const struct dom_game_runtime *rt);
void dom_game_runtime_release_cosmo_map_snapshot(dom_cosmo_map_snapshot *snapshot);
dom_cosmo_transit_snapshot *dom_game_runtime_build_cosmo_transit_snapshot(const struct dom_game_runtime *rt);
void dom_game_runtime_release_cosmo_transit_snapshot(dom_cosmo_transit_snapshot *snapshot);
dom_system_list_snapshot *dom_game_runtime_build_system_list_snapshot(const struct dom_game_runtime *rt);
void dom_game_runtime_release_system_list_snapshot(dom_system_list_snapshot *snapshot);
dom_body_list_snapshot *dom_game_runtime_build_body_list_snapshot(const struct dom_game_runtime *rt);
void dom_game_runtime_release_body_list_snapshot(dom_body_list_snapshot *snapshot);
dom_frame_tree_snapshot *dom_game_runtime_build_frame_tree_snapshot(const struct dom_game_runtime *rt);
void dom_game_runtime_release_frame_tree_snapshot(dom_frame_tree_snapshot *snapshot);
dom_body_topology_snapshot *dom_game_runtime_build_body_topology_snapshot(const struct dom_game_runtime *rt);
void dom_game_runtime_release_body_topology_snapshot(dom_body_topology_snapshot *snapshot);
dom_orbit_summary_snapshot *dom_game_runtime_build_orbit_summary_snapshot(const struct dom_game_runtime *rt);
void dom_game_runtime_release_orbit_summary_snapshot(dom_orbit_summary_snapshot *snapshot);
dom_surface_view_snapshot *dom_game_runtime_build_surface_view_snapshot(const struct dom_game_runtime *rt);
void dom_game_runtime_release_surface_view_snapshot(dom_surface_view_snapshot *snapshot);
dom_local_tangent_frame_snapshot *dom_game_runtime_build_local_tangent_frame_snapshot(const struct dom_game_runtime *rt);
void dom_game_runtime_release_local_tangent_frame_snapshot(dom_local_tangent_frame_snapshot *snapshot);
dom_construction_list_snapshot *dom_game_runtime_build_construction_list_snapshot(const struct dom_game_runtime *rt);
void dom_game_runtime_release_construction_list_snapshot(dom_construction_list_snapshot *snapshot);
dom_station_list_snapshot *dom_game_runtime_build_station_list_snapshot(const struct dom_game_runtime *rt);
void dom_game_runtime_release_station_list_snapshot(dom_station_list_snapshot *snapshot);
dom_route_list_snapshot *dom_game_runtime_build_route_list_snapshot(const struct dom_game_runtime *rt);
void dom_game_runtime_release_route_list_snapshot(dom_route_list_snapshot *snapshot);
dom_transfer_list_snapshot *dom_game_runtime_build_transfer_list_snapshot(const struct dom_game_runtime *rt);
void dom_game_runtime_release_transfer_list_snapshot(dom_transfer_list_snapshot *snapshot);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOM_SNAPSHOT_H */
