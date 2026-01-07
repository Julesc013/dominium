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
    DOM_BODY_TOPOLOGY_SNAPSHOT_VERSION = 1u
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

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOM_SNAPSHOT_H */
