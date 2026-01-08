/*
FILE: source/dominium/game/runtime/dom_game_runtime.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / game/runtime/dom_game_runtime
RESPONSIBILITY: Implements the internal runtime kernel; does NOT define a public API (see `include/**`).
ALLOWED DEPENDENCIES: `include/dominium/**`, `source/dominium/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: Dependency inversions that violate `docs/OVERVIEW_ARCHITECTURE.md` layering.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: Internal struct versioned for forward evolution.
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include "runtime/dom_game_runtime.h"

#include <cstring>
#include <vector>
#include <cstdio>
#include <climits>

#include "dom_game_net.h"
#include "dom_instance.h"
#include "dom_session.h"
#include "runtime/dom_cosmo_graph.h"
#include "runtime/dom_cosmo_transit.h"
#include "runtime/dom_system_registry.h"
#include "runtime/dom_body_registry.h"
#include "runtime/dom_frames.h"
#include "runtime/dom_lane_scheduler.h"
#include "runtime/dom_surface_chunks.h"
#include "runtime/dom_surface_height.h"
#include "runtime/dom_construction_registry.h"
#include "runtime/dom_station_registry.h"
#include "runtime/dom_route_graph.h"
#include "runtime/dom_transfer_scheduler.h"
#include "runtime/dom_production.h"
#include "runtime/dom_macro_economy.h"
#include "runtime/dom_macro_events.h"
#include "runtime/dom_game_hash.h"
#include "runtime/dom_game_replay.h"
#include "domino/core/spacetime.h"

extern "C" {
#include "ai/d_agent.h"
#include "net/d_net_apply.h"
#include "net/d_net_cmd.h"
#include "net/d_net_schema.h"
#include "net/d_net_transport.h"
#include "struct/d_struct.h"
#include "domino/core/d_tlv_kv.h"
}

struct dom_game_runtime {
    void *session;
    void *net;
    const void *instance;
    u32 ups;
    u32 warp_factor;
    u32 pending_warp_factor;
    u64 pending_warp_tick;
    int pending_warp_valid;
    double dt_s;
    u64 wall_accum_us;
    void *replay_play;
    u32 replay_last_tick;
    int replay_last_tick_valid;
    u64 run_id;
    std::vector<unsigned char> manifest_hash_bytes;
    dom_system_registry *system_registry;
    dom_body_registry *body_registry;
    dom_frames *frames;
    dom_lane_scheduler *lane_sched;
    dom_surface_chunks *surface_chunks;
    dom_construction_registry *construction_registry;
    dom_station_registry *station_registry;
    dom_route_graph *route_graph;
    dom_transfer_scheduler *transfer_scheduler;
    dom_production *production;
    dom_macro_economy *macro_economy;
    dom_macro_events *macro_events;
    dom_body_id surface_body_id;
    dom_topo_latlong_q16 surface_focus;
    int surface_focus_valid;
    dom::dom_cosmo_graph cosmo_graph;
    dom_cosmo_transit_state cosmo_transit;
    u64 cosmo_last_arrival_tick;
};

namespace {

static const u32 DEFAULT_UPS = 60u;
static const u32 DEFAULT_WARP_FACTOR = 1u;
static const u32 MAX_WARP_FACTOR = 1024u;

static dom::DomSession *session_of(dom_game_runtime *rt) {
    return rt ? static_cast<dom::DomSession *>(rt->session) : 0;
}

static dom::DomSession *session_of(const dom_game_runtime *rt) {
    return rt ? static_cast<dom::DomSession *>(rt->session) : 0;
}

static dom::DomGameNet *net_of(dom_game_runtime *rt) {
    return rt ? static_cast<dom::DomGameNet *>(rt->net) : 0;
}

static const dom::InstanceInfo *inst_of(const dom_game_runtime *rt) {
    return rt ? static_cast<const dom::InstanceInfo *>(rt->instance) : 0;
}

static u64 compute_seed(dom::DomSession *session, const dom::InstanceInfo *inst) {
    const d_world *w = session ? session->world() : 0;
    if (w) {
        return w->meta.seed;
    }
    return inst ? (u64)inst->world_seed : 0ull;
}

static int parse_warp_payload(const dom_game_command *cmd, u32 *out_factor) {
    d_tlv_blob blob;
    u32 offset = 0u;
    u32 tag = 0u;
    d_tlv_blob payload;
    if (!cmd || !out_factor) {
        return DOM_GAME_RUNTIME_ERR;
    }
    if (!cmd->payload || cmd->payload_size == 0u) {
        return DOM_GAME_RUNTIME_ERR;
    }
    blob.ptr = (unsigned char *)cmd->payload;
    blob.len = cmd->payload_size;
    while (d_tlv_kv_next(&blob, &offset, &tag, &payload) == 0) {
        if (tag == D_NET_TLV_WARP_FACTOR) {
            if (d_tlv_kv_read_u32(&payload, out_factor) != 0) {
                return DOM_GAME_RUNTIME_ERR;
            }
            return DOM_GAME_RUNTIME_OK;
        }
    }
    return DOM_GAME_RUNTIME_ERR;
}

static void zero_posseg(dom_posseg_q16 *pos) {
    u32 i;
    for (i = 0u; i < 3u; ++i) {
        pos->seg[i] = 0;
        pos->loc[i] = 0;
    }
}

static q48_16 posseg_axis_to_q48(i32 seg, q16_16 loc) {
    q48_16 seg_m = d_q48_16_from_int((i64)seg * (i64)DOM_TOPOLOGY_POSSEG_SIZE_M);
    q48_16 loc_m = d_q48_16_from_q16_16(loc);
    return d_q48_16_add(seg_m, loc_m);
}

static void posseg_to_q48(const dom_posseg_q16 *pos, q48_16 out[3]) {
    out[0] = posseg_axis_to_q48(pos->seg[0], pos->loc[0]);
    out[1] = posseg_axis_to_q48(pos->seg[1], pos->loc[1]);
    out[2] = posseg_axis_to_q48(pos->seg[2], pos->loc[2]);
}

static i32 clamp_i64_to_i32(i64 v) {
    if (v > (i64)INT_MAX) {
        return INT_MAX;
    }
    if (v < (i64)INT_MIN) {
        return INT_MIN;
    }
    return (i32)v;
}

static q16_16 mul_q16_i32_clamp(i32 a, i32 b) {
    i64 v = (i64)a * (i64)b;
    return (q16_16)clamp_i64_to_i32(v);
}

static q48_16 dot_q48_q16(const q48_16 v[3], const dom_topo_vec3_q16 *axis) {
    q48_16 sum = 0;
    sum = d_q48_16_add(sum, d_q48_16_mul(v[0], d_q48_16_from_q16_16(axis->v[0])));
    sum = d_q48_16_add(sum, d_q48_16_mul(v[1], d_q48_16_from_q16_16(axis->v[1])));
    sum = d_q48_16_add(sum, d_q48_16_mul(v[2], d_q48_16_from_q16_16(axis->v[2])));
    return sum;
}

static u64 square_u64(i64 v) {
    u64 a = (v < 0) ? (u64)(-v) : (u64)v;
    return a * a;
}

static int build_baseline_frames(dom_frames *frames, const dom_body_registry *bodies) {
    dom_frame_desc desc;
    dom_body_info earth_info;
    dom_frame_id sol_frame = 0ull;
    dom_frame_id earth_centered = 0ull;
    dom_frame_id earth_fixed = 0ull;
    dom_body_id earth_id = 0ull;
    int rc;

    if (!frames) {
        return DOM_FRAMES_INVALID_ARGUMENT;
    }

    (void)dom_id_hash64("SOL_BARYCENTRIC_INERTIAL", 24u, &sol_frame);
    (void)dom_id_hash64("EARTH_CENTERED_INERTIAL", 23u, &earth_centered);
    (void)dom_id_hash64("EARTH_FIXED_ROTATING", 20u, &earth_fixed);
    (void)dom_id_hash64("earth", 5u, &earth_id);

    std::memset(&desc, 0, sizeof(desc));
    desc.id = sol_frame;
    desc.parent_id = 0ull;
    desc.kind = DOM_FRAME_KIND_INERTIAL_BARYCENTRIC;
    desc.body_id = 0ull;
    zero_posseg(&desc.origin_offset);
    desc.rotation_period_ticks = 0ull;
    desc.rotation_epoch_tick = 0ull;
    desc.rotation_phase_turns = 0;
    rc = dom_frames_register(frames, &desc);
    if (rc != DOM_FRAMES_OK) {
        return rc;
    }

    std::memset(&desc, 0, sizeof(desc));
    desc.id = earth_centered;
    desc.parent_id = sol_frame;
    desc.kind = DOM_FRAME_KIND_BODY_CENTERED_INERTIAL;
    desc.body_id = earth_id;
    zero_posseg(&desc.origin_offset);
    desc.rotation_period_ticks = 0ull;
    desc.rotation_epoch_tick = 0ull;
    desc.rotation_phase_turns = 0;
    rc = dom_frames_register(frames, &desc);
    if (rc != DOM_FRAMES_OK) {
        return rc;
    }

    std::memset(&desc, 0, sizeof(desc));
    desc.id = earth_fixed;
    desc.parent_id = earth_centered;
    desc.kind = DOM_FRAME_KIND_BODY_FIXED;
    desc.body_id = earth_id;
    zero_posseg(&desc.origin_offset);
    desc.rotation_period_ticks = 0ull;
    desc.rotation_epoch_tick = 0ull;
    desc.rotation_phase_turns = 0;
    if (bodies && dom_body_registry_get(bodies, earth_id, &earth_info) == DOM_BODY_REGISTRY_OK) {
        desc.rotation_period_ticks = earth_info.rotation_period_ticks;
        desc.rotation_epoch_tick = earth_info.rotation_epoch_tick;
    }
    rc = dom_frames_register(frames, &desc);
    if (rc != DOM_FRAMES_OK) {
        return rc;
    }

    return dom_frames_validate(frames);
}

static void register_macro_system(const dom_system_info *info, void *user) {
    dom_macro_economy *econ = static_cast<dom_macro_economy *>(user);
    if (!econ || !info) {
        return;
    }
    (void)dom_macro_economy_register_system(econ, info->id);
}

static void register_macro_galaxy(const dom::dom_cosmo_entity *ent, void *user) {
    dom_macro_economy *econ = static_cast<dom_macro_economy *>(user);
    if (!econ || !ent) {
        return;
    }
    (void)dom_macro_economy_register_galaxy(econ, ent->id);
}

struct DomConstructionPlaceCmd {
    u32 type_id;
    dom_body_id body_id;
    dom_topo_latlong_q16 latlong;
    u32 orientation;
    int have_type;
    int have_body;
    int have_lat;
    int have_lon;
    int have_orient;
};

struct DomConstructionRemoveCmd {
    dom_construction_instance_id instance_id;
    int have_id;
};

struct DomStationCreateCmd {
    dom_station_id station_id;
    dom_body_id body_id;
    dom_frame_id frame_id;
    int have_station;
    int have_body;
    int have_frame;
};

struct DomRouteCreateCmd {
    dom_route_id route_id;
    dom_station_id src_station_id;
    dom_station_id dst_station_id;
    u64 duration_ticks;
    u64 capacity_units;
    int have_route;
    int have_src;
    int have_dst;
    int have_duration;
    int have_capacity;
};

struct DomTransferScheduleCmd {
    dom_route_id route_id;
    u32 item_count;
    const unsigned char *items;
    u32 items_len;
    int have_route;
    int have_count;
    int have_items;
};

static int tlv_read_u64(const d_tlv_blob *payload, u64 *out) {
    if (!payload || !out || !payload->ptr) {
        return -1;
    }
    if (payload->len != 8u) {
        return -1;
    }
    std::memcpy(out, payload->ptr, 8u);
    return 0;
}


static int parse_construction_place(const d_net_cmd *cmd, DomConstructionPlaceCmd *out) {
    d_tlv_blob blob;
    u32 offset = 0u;
    u32 tag = 0u;
    d_tlv_blob payload;
    if (!cmd || !out) {
        return DOM_GAME_RUNTIME_ERR;
    }
    std::memset(out, 0, sizeof(*out));
    blob = cmd->payload;
    while (d_tlv_kv_next(&blob, &offset, &tag, &payload) == 0) {
        if (tag == D_NET_TLV_CONSTRUCTION_TYPE_ID) {
            if (d_tlv_kv_read_u32(&payload, &out->type_id) == 0) {
                out->have_type = 1;
            }
        } else if (tag == D_NET_TLV_CONSTRUCTION_BODY_ID) {
            u64 body = 0ull;
            if (tlv_read_u64(&payload, &body) == 0) {
                out->body_id = body;
                out->have_body = 1;
            }
        } else if (tag == D_NET_TLV_CONSTRUCTION_LAT_TURNS) {
            if (d_tlv_kv_read_q16_16(&payload, &out->latlong.lat_turns) == 0) {
                out->have_lat = 1;
            }
        } else if (tag == D_NET_TLV_CONSTRUCTION_LON_TURNS) {
            if (d_tlv_kv_read_q16_16(&payload, &out->latlong.lon_turns) == 0) {
                out->have_lon = 1;
            }
        } else if (tag == D_NET_TLV_CONSTRUCTION_ORIENT) {
            if (d_tlv_kv_read_u32(&payload, &out->orientation) == 0) {
                out->have_orient = 1;
            }
        }
    }
    if (!out->have_type || !out->have_body || !out->have_lat ||
        !out->have_lon || !out->have_orient) {
        return DOM_GAME_RUNTIME_ERR;
    }
    return DOM_GAME_RUNTIME_OK;
}

static int parse_construction_remove(const d_net_cmd *cmd, DomConstructionRemoveCmd *out) {
    d_tlv_blob blob;
    u32 offset = 0u;
    u32 tag = 0u;
    d_tlv_blob payload;
    if (!cmd || !out) {
        return DOM_GAME_RUNTIME_ERR;
    }
    std::memset(out, 0, sizeof(*out));
    blob = cmd->payload;
    while (d_tlv_kv_next(&blob, &offset, &tag, &payload) == 0) {
        if (tag == D_NET_TLV_CONSTRUCTION_INSTANCE_ID) {
            u64 id = 0ull;
            if (tlv_read_u64(&payload, &id) == 0) {
                out->instance_id = id;
                out->have_id = 1;
            }
        }
    }
    return out->have_id ? DOM_GAME_RUNTIME_OK : DOM_GAME_RUNTIME_ERR;
}

static int parse_station_create(const d_net_cmd *cmd, DomStationCreateCmd *out) {
    d_tlv_blob blob;
    u32 offset = 0u;
    u32 tag = 0u;
    d_tlv_blob payload;
    if (!cmd || !out) {
        return DOM_GAME_RUNTIME_ERR;
    }
    std::memset(out, 0, sizeof(*out));
    blob = cmd->payload;
    while (d_tlv_kv_next(&blob, &offset, &tag, &payload) == 0) {
        if (tag == D_NET_TLV_STATION_ID) {
            u64 id = 0ull;
            if (tlv_read_u64(&payload, &id) == 0) {
                out->station_id = id;
                out->have_station = 1;
            }
        } else if (tag == D_NET_TLV_STATION_BODY_ID) {
            u64 body = 0ull;
            if (tlv_read_u64(&payload, &body) == 0) {
                out->body_id = body;
                out->have_body = 1;
            }
        } else if (tag == D_NET_TLV_STATION_FRAME_ID) {
            u64 frame = 0ull;
            if (tlv_read_u64(&payload, &frame) == 0) {
                out->frame_id = frame;
                out->have_frame = 1;
            }
        }
    }
    if (!out->have_station || !out->have_body || !out->have_frame) {
        return DOM_GAME_RUNTIME_ERR;
    }
    return DOM_GAME_RUNTIME_OK;
}

static int parse_route_create(const d_net_cmd *cmd, DomRouteCreateCmd *out) {
    d_tlv_blob blob;
    u32 offset = 0u;
    u32 tag = 0u;
    d_tlv_blob payload;
    if (!cmd || !out) {
        return DOM_GAME_RUNTIME_ERR;
    }
    std::memset(out, 0, sizeof(*out));
    blob = cmd->payload;
    while (d_tlv_kv_next(&blob, &offset, &tag, &payload) == 0) {
        if (tag == D_NET_TLV_ROUTE_ID) {
            u64 id = 0ull;
            if (tlv_read_u64(&payload, &id) == 0) {
                out->route_id = id;
                out->have_route = 1;
            }
        } else if (tag == D_NET_TLV_ROUTE_SRC_STATION_ID) {
            u64 id = 0ull;
            if (tlv_read_u64(&payload, &id) == 0) {
                out->src_station_id = id;
                out->have_src = 1;
            }
        } else if (tag == D_NET_TLV_ROUTE_DST_STATION_ID) {
            u64 id = 0ull;
            if (tlv_read_u64(&payload, &id) == 0) {
                out->dst_station_id = id;
                out->have_dst = 1;
            }
        } else if (tag == D_NET_TLV_ROUTE_DURATION_TICKS) {
            u64 duration = 0ull;
            if (tlv_read_u64(&payload, &duration) == 0) {
                out->duration_ticks = duration;
                out->have_duration = 1;
            }
        } else if (tag == D_NET_TLV_ROUTE_CAPACITY_UNITS) {
            u64 cap = 0ull;
            if (tlv_read_u64(&payload, &cap) == 0) {
                out->capacity_units = cap;
                out->have_capacity = 1;
            }
        }
    }
    if (!out->have_route || !out->have_src || !out->have_dst ||
        !out->have_duration || !out->have_capacity) {
        return DOM_GAME_RUNTIME_ERR;
    }
    return DOM_GAME_RUNTIME_OK;
}

static int parse_transfer_schedule(const d_net_cmd *cmd, DomTransferScheduleCmd *out) {
    d_tlv_blob blob;
    u32 offset = 0u;
    u32 tag = 0u;
    d_tlv_blob payload;
    if (!cmd || !out) {
        return DOM_GAME_RUNTIME_ERR;
    }
    std::memset(out, 0, sizeof(*out));
    blob = cmd->payload;
    while (d_tlv_kv_next(&blob, &offset, &tag, &payload) == 0) {
        if (tag == D_NET_TLV_TRANSFER_ROUTE_ID) {
            u64 id = 0ull;
            if (tlv_read_u64(&payload, &id) == 0) {
                out->route_id = id;
                out->have_route = 1;
            }
        } else if (tag == D_NET_TLV_TRANSFER_ITEM_COUNT) {
            if (d_tlv_kv_read_u32(&payload, &out->item_count) == 0) {
                out->have_count = 1;
            }
        } else if (tag == D_NET_TLV_TRANSFER_ITEMS) {
            out->items = payload.ptr;
            out->items_len = payload.len;
            out->have_items = 1;
        }
    }
    if (!out->have_route || !out->have_count || !out->have_items) {
        return DOM_GAME_RUNTIME_ERR;
    }
    if (out->item_count == 0u) {
        return DOM_GAME_RUNTIME_ERR;
    }
    if (out->items_len != (out->item_count * 16u)) {
        return DOM_GAME_RUNTIME_ERR;
    }
    return DOM_GAME_RUNTIME_OK;
}

static int construction_type_valid(u32 type_id) {
    return type_id == DOM_CONSTRUCTION_TYPE_HABITAT ||
           type_id == DOM_CONSTRUCTION_TYPE_STORAGE ||
           type_id == DOM_CONSTRUCTION_TYPE_GENERIC_PLATFORM;
}

static int apply_construction_place(dom_game_runtime *rt, const d_net_cmd *cmd) {
    DomConstructionPlaceCmd parsed;
    dom_activation_bubble bubble;
    dom_body_id bubble_body = 0ull;
    dom_topo_latlong_q16 bubble_center;
    int bubble_active = 0;
    dom_topology_binding binding;
    dom_posseg_q16 pos;
    dom_posseg_q16 center_pos;
    dom_posseg_q16 origin_pos;
    q48_16 height = 0;
    q48_16 center_height = 0;
    q48_16 origin_height = 0;
    q48_16 pos_q48[3];
    q48_16 center_q48[3];
    q48_16 origin_q48[3];
    q48_16 delta[3];
    dom_surface_chunk_key key;
    dom_topo_latlong_q16 origin_latlong;
    dom_topo_tangent_frame_q16 frame;
    dom_construction_instance inst;
    dom_construction_instance_id new_id = 0ull;
    i64 dx;
    i64 dy;
    i64 dz;
    u64 dist2;
    i64 radius_i;
    u64 radius2;
    int rc;

    if (!rt || !cmd || !rt->construction_registry || !rt->lane_sched ||
        !rt->body_registry || !rt->surface_chunks) {
        return DOM_GAME_RUNTIME_ERR;
    }
    if (parse_construction_place(cmd, &parsed) != DOM_GAME_RUNTIME_OK) {
        return DOM_GAME_RUNTIME_ERR;
    }
    if (!construction_type_valid(parsed.type_id)) {
        return DOM_GAME_RUNTIME_ERR;
    }
    if (parsed.orientation > 3u) {
        return DOM_GAME_RUNTIME_ERR;
    }
    if (dom_lane_scheduler_get_bubble(rt->lane_sched,
                                      &bubble,
                                      &bubble_active,
                                      &bubble_body,
                                      &bubble_center) != DOM_LANE_OK ||
        !bubble_active) {
        return DOM_GAME_RUNTIME_ERR;
    }
    if (bubble_body == 0ull || parsed.body_id != bubble_body) {
        return DOM_GAME_RUNTIME_ERR;
    }
    if (dom_surface_topology_select(rt->body_registry, parsed.body_id, 0u, &binding) != DOM_TOPOLOGY_OK) {
        return DOM_GAME_RUNTIME_ERR;
    }
    if (dom_surface_height_sample(parsed.body_id, &parsed.latlong, &height) != DOM_SURFACE_HEIGHT_OK) {
        return DOM_GAME_RUNTIME_ERR;
    }
    if (dom_surface_height_sample(parsed.body_id, &bubble_center, &center_height) != DOM_SURFACE_HEIGHT_OK) {
        center_height = 0;
    }
    if (dom_surface_topology_pos_from_latlong(&binding, &parsed.latlong, height, &pos) != DOM_TOPOLOGY_OK) {
        return DOM_GAME_RUNTIME_ERR;
    }
    if (dom_surface_topology_pos_from_latlong(&binding, &bubble_center, center_height, &center_pos) != DOM_TOPOLOGY_OK) {
        return DOM_GAME_RUNTIME_ERR;
    }
    posseg_to_q48(&pos, pos_q48);
    posseg_to_q48(&center_pos, center_q48);
    dx = d_q48_16_to_int(d_q48_16_sub(pos_q48[0], center_q48[0]));
    dy = d_q48_16_to_int(d_q48_16_sub(pos_q48[1], center_q48[1]));
    dz = d_q48_16_to_int(d_q48_16_sub(pos_q48[2], center_q48[2]));
    dist2 = square_u64(dx) + square_u64(dy) + square_u64(dz);
    radius_i = d_q48_16_to_int(bubble.radius_m);
    if (radius_i < 0) {
        radius_i = -radius_i;
    }
    radius2 = square_u64(radius_i);
    if (dist2 > radius2) {
        return DOM_GAME_RUNTIME_ERR;
    }

    rc = dom_surface_chunks_build_key(rt->surface_chunks,
                                      rt->body_registry,
                                      parsed.body_id,
                                      &parsed.latlong,
                                      &key);
    if (rc != DOM_SURFACE_CHUNKS_OK) {
        return DOM_GAME_RUNTIME_ERR;
    }

    origin_latlong.lat_turns = mul_q16_i32_clamp(key.lat_index, key.step_turns_q16);
    origin_latlong.lon_turns = mul_q16_i32_clamp(key.lon_index, key.step_turns_q16);

    if (dom_surface_height_sample(parsed.body_id, &origin_latlong, &origin_height) != DOM_SURFACE_HEIGHT_OK) {
        origin_height = 0;
    }
    if (dom_surface_topology_pos_from_latlong(&binding, &origin_latlong, origin_height, &origin_pos) != DOM_TOPOLOGY_OK) {
        return DOM_GAME_RUNTIME_ERR;
    }
    if (dom_surface_topology_tangent_frame(&binding, &origin_latlong, &frame) != DOM_TOPOLOGY_OK) {
        return DOM_GAME_RUNTIME_ERR;
    }

    posseg_to_q48(&origin_pos, origin_q48);
    delta[0] = d_q48_16_sub(pos_q48[0], origin_q48[0]);
    delta[1] = d_q48_16_sub(pos_q48[1], origin_q48[1]);
    delta[2] = d_q48_16_sub(pos_q48[2], origin_q48[2]);

    std::memset(&inst, 0, sizeof(inst));
    inst.instance_id = 0ull;
    inst.type_id = parsed.type_id;
    inst.body_id = parsed.body_id;
    inst.chunk_key = key;
    inst.local_pos_m[0] = dot_q48_q16(delta, &frame.east);
    inst.local_pos_m[1] = dot_q48_q16(delta, &frame.north);
    inst.local_pos_m[2] = dot_q48_q16(delta, &frame.up);
    inst.orientation = parsed.orientation;
    inst.cell_x = clamp_i64_to_i32(d_q48_16_to_int(inst.local_pos_m[0]));
    inst.cell_y = clamp_i64_to_i32(d_q48_16_to_int(inst.local_pos_m[1]));

    rc = dom_construction_register_instance(rt->construction_registry, &inst, &new_id);
    if (rc != DOM_CONSTRUCTION_OK) {
        return DOM_GAME_RUNTIME_ERR;
    }

    (void)new_id;
    return DOM_GAME_RUNTIME_OK;
}

static int apply_construction_remove(dom_game_runtime *rt, const d_net_cmd *cmd) {
    DomConstructionRemoveCmd parsed;
    if (!rt || !cmd || !rt->construction_registry) {
        return DOM_GAME_RUNTIME_ERR;
    }
    if (parse_construction_remove(cmd, &parsed) != DOM_GAME_RUNTIME_OK) {
        return DOM_GAME_RUNTIME_ERR;
    }
    if (dom_construction_remove_instance(rt->construction_registry, parsed.instance_id) != DOM_CONSTRUCTION_OK) {
        return DOM_GAME_RUNTIME_ERR;
    }
    return DOM_GAME_RUNTIME_OK;
}

static int apply_station_create(dom_game_runtime *rt, const d_net_cmd *cmd) {
    DomStationCreateCmd parsed;
    dom_station_desc desc;
    if (!rt || !cmd || !rt->station_registry) {
        return DOM_GAME_RUNTIME_ERR;
    }
    if (parse_station_create(cmd, &parsed) != DOM_GAME_RUNTIME_OK) {
        return DOM_GAME_RUNTIME_ERR;
    }
    std::memset(&desc, 0, sizeof(desc));
    desc.station_id = parsed.station_id;
    desc.body_id = parsed.body_id;
    desc.frame_id = parsed.frame_id;
    if (dom_station_register(rt->station_registry, &desc) != DOM_STATION_REGISTRY_OK) {
        return DOM_GAME_RUNTIME_ERR;
    }
    return DOM_GAME_RUNTIME_OK;
}

static int apply_route_create(dom_game_runtime *rt, const d_net_cmd *cmd) {
    DomRouteCreateCmd parsed;
    dom_route_desc desc;
    dom_station_info station;
    if (!rt || !cmd || !rt->route_graph || !rt->station_registry) {
        return DOM_GAME_RUNTIME_ERR;
    }
    if (parse_route_create(cmd, &parsed) != DOM_GAME_RUNTIME_OK) {
        return DOM_GAME_RUNTIME_ERR;
    }
    if (dom_station_get(rt->station_registry, parsed.src_station_id, &station) != DOM_STATION_REGISTRY_OK) {
        return DOM_GAME_RUNTIME_ERR;
    }
    if (dom_station_get(rt->station_registry, parsed.dst_station_id, &station) != DOM_STATION_REGISTRY_OK) {
        return DOM_GAME_RUNTIME_ERR;
    }
    std::memset(&desc, 0, sizeof(desc));
    desc.route_id = parsed.route_id;
    desc.src_station_id = parsed.src_station_id;
    desc.dst_station_id = parsed.dst_station_id;
    desc.duration_ticks = parsed.duration_ticks;
    desc.capacity_units = parsed.capacity_units;
    if (dom_route_graph_register(rt->route_graph, &desc) != DOM_ROUTE_GRAPH_OK) {
        return DOM_GAME_RUNTIME_ERR;
    }
    return DOM_GAME_RUNTIME_OK;
}

static int apply_transfer_schedule(dom_game_runtime *rt, const d_net_cmd *cmd, u64 tick) {
    DomTransferScheduleCmd parsed;
    std::vector<dom_transfer_entry> entries;
    dom_transfer_id new_id = 0ull;
    if (!rt || !cmd || !rt->transfer_scheduler || !rt->route_graph || !rt->station_registry) {
        return DOM_GAME_RUNTIME_ERR;
    }
    if (parse_transfer_schedule(cmd, &parsed) != DOM_GAME_RUNTIME_OK) {
        return DOM_GAME_RUNTIME_ERR;
    }
    entries.resize(parsed.item_count);
    for (u32 i = 0u; i < parsed.item_count; ++i) {
        const unsigned char *ptr = parsed.items + (i * 16u);
        u64 resource_id = 0ull;
        i64 quantity = 0;
        std::memcpy(&resource_id, ptr, 8u);
        std::memcpy(&quantity, ptr + 8u, 8u);
        entries[i].resource_id = resource_id;
        entries[i].quantity = quantity;
    }
    if (dom_transfer_schedule(rt->transfer_scheduler,
                              rt->route_graph,
                              rt->station_registry,
                              parsed.route_id,
                              entries.empty() ? (const dom_transfer_entry *)0 : &entries[0],
                              (u32)entries.size(),
                              tick,
                              &new_id) != DOM_TRANSFER_OK) {
        return DOM_GAME_RUNTIME_ERR;
    }
    (void)new_id;
    return DOM_GAME_RUNTIME_OK;
}

static void dom_game_runtime_tick_observer(void *user,
                                           d_world *w,
                                           u32 tick,
                                           const d_net_cmd *cmds,
                                           u32 cmd_count) {
    dom_game_runtime *rt = static_cast<dom_game_runtime *>(user);
    u32 i;
    (void)w;
    (void)tick;
    if (!rt || !cmds || cmd_count == 0u) {
        return;
    }
    for (i = 0u; i < cmd_count; ++i) {
        const d_net_cmd *cmd = &cmds[i];
        if (!cmd) {
            continue;
        }
        if (cmd->schema_id == (u32)D_NET_SCHEMA_CMD_CONSTRUCTION_PLACE_V1) {
            if (apply_construction_place(rt, cmd) != DOM_GAME_RUNTIME_OK) {
                std::fprintf(stderr, "construction: place refused at tick %u\n",
                             (unsigned)tick);
            }
        } else if (cmd->schema_id == (u32)D_NET_SCHEMA_CMD_CONSTRUCTION_REMOVE_V1) {
            if (apply_construction_remove(rt, cmd) != DOM_GAME_RUNTIME_OK) {
                std::fprintf(stderr, "construction: remove refused at tick %u\n",
                             (unsigned)tick);
            }
        } else if (cmd->schema_id == (u32)D_NET_SCHEMA_CMD_STATION_CREATE_V1) {
            if (apply_station_create(rt, cmd) != DOM_GAME_RUNTIME_OK) {
                std::fprintf(stderr, "logistics: station create refused at tick %u\n",
                             (unsigned)tick);
            }
        } else if (cmd->schema_id == (u32)D_NET_SCHEMA_CMD_ROUTE_CREATE_V1) {
            if (apply_route_create(rt, cmd) != DOM_GAME_RUNTIME_OK) {
                std::fprintf(stderr, "logistics: route create refused at tick %u\n",
                             (unsigned)tick);
            }
        } else if (cmd->schema_id == (u32)D_NET_SCHEMA_CMD_TRANSFER_SCHEDULE_V1) {
            if (apply_transfer_schedule(rt, cmd, (u64)tick) != DOM_GAME_RUNTIME_OK) {
                std::fprintf(stderr, "logistics: transfer schedule refused at tick %u\n",
                             (unsigned)tick);
            }
        }
    }
}

static int inject_replay(dom_game_runtime *rt, d_sim_context *sim) {
    const dom_game_replay_packet *packets = (const dom_game_replay_packet *)0;
    u32 count = 0u;
    const u64 next_tick = (u64)sim->tick_index + 1ull;
    int rc;
    u32 i;

    if (!rt || !sim) {
        return DOM_GAME_RUNTIME_ERR;
    }
    if (!rt->replay_play) {
        return DOM_GAME_RUNTIME_OK;
    }

    rc = dom_game_replay_play_next_for_tick((dom_game_replay_play *)rt->replay_play,
                                            next_tick,
                                            &packets,
                                            &count);
    if (rc == DOM_GAME_REPLAY_END) {
        return DOM_GAME_RUNTIME_REPLAY_END;
    }
    if (rc != DOM_GAME_REPLAY_OK) {
        return DOM_GAME_RUNTIME_ERR;
    }

    for (i = 0u; i < count; ++i) {
        (void)d_net_receive_packet(0u, 0u, packets[i].payload, packets[i].size);
    }

    if (count == 0u && rt->replay_last_tick_valid && next_tick > (u64)rt->replay_last_tick) {
        return DOM_GAME_RUNTIME_REPLAY_END;
    }

    return DOM_GAME_RUNTIME_OK;
}

} // namespace

dom_game_runtime *dom_game_runtime_create(const dom_game_runtime_init_desc *desc) {
    dom_game_runtime *rt;
    if (!desc || desc->struct_size != sizeof(dom_game_runtime_init_desc) ||
        desc->struct_version != DOM_GAME_RUNTIME_INIT_DESC_VERSION) {
        return 0;
    }
    if (!desc->session || !desc->net) {
        return 0;
    }

    rt = new dom_game_runtime();
    rt->session = desc->session;
    rt->net = desc->net;
    rt->instance = desc->instance;
    rt->ups = desc->ups ? desc->ups : DEFAULT_UPS;
    rt->warp_factor = DEFAULT_WARP_FACTOR;
    rt->pending_warp_factor = DEFAULT_WARP_FACTOR;
    rt->pending_warp_tick = 0u;
    rt->pending_warp_valid = 0;
    rt->dt_s = (rt->ups > 0u) ? (1.0 / (double)rt->ups) : (1.0 / 60.0);
    rt->wall_accum_us = 0u;
    rt->replay_play = 0;
    rt->replay_last_tick = 0u;
    rt->replay_last_tick_valid = 0;
    rt->run_id = desc->run_id;
    rt->system_registry = 0;
    rt->body_registry = 0;
    rt->frames = 0;
    rt->lane_sched = 0;
    rt->surface_chunks = 0;
    rt->construction_registry = 0;
    rt->station_registry = 0;
    rt->route_graph = 0;
    rt->transfer_scheduler = 0;
    rt->production = 0;
    rt->macro_economy = 0;
    rt->macro_events = 0;
    rt->surface_body_id = 0ull;
    rt->surface_focus.lat_turns = 0;
    rt->surface_focus.lon_turns = 0;
    rt->surface_focus_valid = 0;
    (void)dom::dom_cosmo_graph_init(&rt->cosmo_graph,
                                    compute_seed(session_of(rt), inst_of(rt)),
                                    0);
    dom_cosmo_transit_reset(&rt->cosmo_transit);
    rt->cosmo_last_arrival_tick = 0ull;
    rt->system_registry = dom_system_registry_create();
    rt->body_registry = dom_body_registry_create();
    rt->frames = dom_frames_create();
    rt->lane_sched = dom_lane_scheduler_create();
    rt->construction_registry = dom_construction_registry_create();
    rt->station_registry = dom_station_registry_create();
    rt->route_graph = dom_route_graph_create();
    rt->transfer_scheduler = dom_transfer_scheduler_create();
    rt->production = dom_production_create();
    rt->macro_economy = dom_macro_economy_create();
    rt->macro_events = dom_macro_events_create();
    {
        dom_surface_chunks_desc sdesc;
        std::memset(&sdesc, 0, sizeof(sdesc));
        sdesc.struct_size = sizeof(sdesc);
        sdesc.struct_version = DOM_SURFACE_CHUNKS_DESC_VERSION;
        sdesc.max_chunks = 256u;
        sdesc.chunk_size_m = 2048u;
    rt->surface_chunks = dom_surface_chunks_create(&sdesc);
    }
    if (!rt->system_registry || !rt->body_registry || !rt->frames ||
        !rt->lane_sched || !rt->surface_chunks || !rt->construction_registry ||
        !rt->station_registry || !rt->route_graph ||
        !rt->transfer_scheduler || !rt->production ||
        !rt->macro_economy || !rt->macro_events) {
        dom_game_runtime_destroy(rt);
        return 0;
    }
    if (dom_system_registry_add_baseline(rt->system_registry) != DOM_SYSTEM_REGISTRY_OK) {
        dom_game_runtime_destroy(rt);
        return 0;
    }
    if (dom_body_registry_add_baseline(rt->body_registry) != DOM_BODY_REGISTRY_OK) {
        dom_game_runtime_destroy(rt);
        return 0;
    }
    if (build_baseline_frames(rt->frames, rt->body_registry) != DOM_FRAMES_OK) {
        dom_game_runtime_destroy(rt);
        return 0;
    }
    if (rt->macro_economy) {
        (void)dom_system_registry_iterate(rt->system_registry,
                                          register_macro_system,
                                          rt->macro_economy);
        (void)dom::dom_cosmo_graph_iterate(&rt->cosmo_graph,
                                           dom::DOM_COSMO_KIND_GALAXY,
                                           register_macro_galaxy,
                                           rt->macro_economy);
    }
    {
        dom_body_id earth_id = 0ull;
        if (dom_id_hash64("earth", 5u, &earth_id) == DOM_SPACETIME_OK &&
            earth_id != 0ull) {
            rt->surface_body_id = earth_id;
            rt->surface_focus.lat_turns = 0;
            rt->surface_focus.lon_turns = 0;
            rt->surface_focus_valid = 1;
        }
    }
    if (desc->instance_manifest_hash_bytes && desc->instance_manifest_hash_len > 0u) {
        rt->manifest_hash_bytes.assign(desc->instance_manifest_hash_bytes,
                                       desc->instance_manifest_hash_bytes +
                                       desc->instance_manifest_hash_len);
    }
    d_net_set_tick_cmds_observer(dom_game_runtime_tick_observer, rt);
    return rt;
}

void dom_game_runtime_destroy(dom_game_runtime *rt) {
    if (!rt) {
        return;
    }
    d_net_set_tick_cmds_observer(0, 0);
    dom_production_destroy(rt->production);
    dom_transfer_scheduler_destroy(rt->transfer_scheduler);
    dom_route_graph_destroy(rt->route_graph);
    dom_station_registry_destroy(rt->station_registry);
    dom_macro_events_destroy(rt->macro_events);
    dom_macro_economy_destroy(rt->macro_economy);
    dom_surface_chunks_destroy(rt->surface_chunks);
    dom_construction_registry_destroy(rt->construction_registry);
    dom_lane_scheduler_destroy(rt->lane_sched);
    dom_frames_destroy(rt->frames);
    dom_body_registry_destroy(rt->body_registry);
    dom_system_registry_destroy(rt->system_registry);
    delete rt;
}

int dom_game_runtime_set_replay_last_tick(dom_game_runtime *rt, u32 last_tick) {
    if (!rt) {
        return DOM_GAME_RUNTIME_ERR;
    }
    rt->replay_last_tick = last_tick;
    rt->replay_last_tick_valid = (last_tick > 0u) ? 1 : 0;
    return DOM_GAME_RUNTIME_OK;
}

int dom_game_runtime_set_replay_playback(dom_game_runtime *rt, void *playback) {
    if (!rt) {
        return DOM_GAME_RUNTIME_ERR;
    }
    rt->replay_play = playback;
    return DOM_GAME_RUNTIME_OK;
}

int dom_game_runtime_cosmo_transit_begin(dom_game_runtime *rt,
                                         u64 src_entity_id,
                                         u64 dst_entity_id,
                                         u64 travel_edge_id,
                                         u64 start_tick,
                                         u64 duration_ticks) {
    if (!rt) {
        return DOM_GAME_RUNTIME_ERR;
    }
    if (dom_cosmo_transit_begin(&rt->cosmo_transit,
                                src_entity_id,
                                dst_entity_id,
                                travel_edge_id,
                                start_tick,
                                duration_ticks) != DOM_COSMO_TRANSIT_OK) {
        return DOM_GAME_RUNTIME_ERR;
    }
    rt->cosmo_last_arrival_tick = 0ull;
    return DOM_GAME_RUNTIME_OK;
}

int dom_game_runtime_cosmo_transit_get(const dom_game_runtime *rt,
                                       dom_cosmo_transit_state *out_state) {
    if (!rt || !out_state) {
        return DOM_GAME_RUNTIME_ERR;
    }
    *out_state = rt->cosmo_transit;
    return DOM_GAME_RUNTIME_OK;
}

u64 dom_game_runtime_cosmo_last_arrival_tick(const dom_game_runtime *rt) {
    return rt ? rt->cosmo_last_arrival_tick : 0ull;
}

int dom_game_runtime_pump(dom_game_runtime *rt) {
    dom::DomSession *session;
    dom::DomGameNet *net;
    const dom::InstanceInfo *inst;
    d_world *w;
    d_sim_context *sim;

    if (!rt) {
        return DOM_GAME_RUNTIME_ERR;
    }

    session = session_of(rt);
    net = net_of(rt);
    inst = inst_of(rt);
    if (!session || !net || !inst) {
        return DOM_GAME_RUNTIME_ERR;
    }
    if (!session->is_initialized()) {
        return DOM_GAME_RUNTIME_OK;
    }
    w = session->world();
    sim = session->sim();
    if (!w || !sim) {
        return DOM_GAME_RUNTIME_ERR;
    }

    net->pump(w, sim, *inst);
    return DOM_GAME_RUNTIME_OK;
}

int dom_game_runtime_step(dom_game_runtime *rt) {
    dom::DomSession *session;
    d_world *w;
    d_sim_context *sim;
    int rc;

    if (!rt) {
        return DOM_GAME_RUNTIME_ERR;
    }

    session = session_of(rt);
    if (!session || !session->is_initialized()) {
        return DOM_GAME_RUNTIME_OK;
    }
    w = session->world();
    sim = session->sim();
    if (!w || !sim) {
        return DOM_GAME_RUNTIME_ERR;
    }

    rc = inject_replay(rt, sim);
    if (rc != DOM_GAME_RUNTIME_OK) {
        return rc;
    }

    if (rt->pending_warp_valid &&
        (u64)sim->tick_index >= rt->pending_warp_tick) {
        u32 factor = rt->pending_warp_factor;
        if (factor < DEFAULT_WARP_FACTOR) {
            factor = DEFAULT_WARP_FACTOR;
        } else if (factor > MAX_WARP_FACTOR) {
            factor = MAX_WARP_FACTOR;
        }
        rt->warp_factor = factor;
        rt->pending_warp_valid = 0;
    }

    if (d_sim_step(sim, 1u) != 0) {
        return DOM_GAME_RUNTIME_ERR;
    }
    {
        int arrived = 0;
        (void)dom_cosmo_transit_tick(&rt->cosmo_transit,
                                     (u64)sim->tick_index,
                                     &arrived);
        if (arrived) {
            rt->cosmo_last_arrival_tick = dom_cosmo_transit_arrival_tick(&rt->cosmo_transit);
        }
    }
    if (rt->lane_sched) {
        int lane_rc = dom_lane_scheduler_update(rt->lane_sched, rt, (dom_tick)sim->tick_index);
        if (lane_rc != DOM_LANE_OK) {
            return DOM_GAME_RUNTIME_ERR;
        }
    }
    if (rt->lane_sched && rt->surface_chunks) {
        dom_activation_bubble bubble;
        dom_body_id body_id = rt->surface_body_id;
        dom_topo_latlong_q16 center = rt->surface_focus;
        int bubble_active = 0;
        if (dom_lane_scheduler_get_bubble(rt->lane_sched,
                                          &bubble,
                                          &bubble_active,
                                          &body_id,
                                          &center) == DOM_LANE_OK &&
            bubble_active) {
            rt->surface_body_id = body_id;
            rt->surface_focus = center;
            rt->surface_focus_valid = 1;
            (void)dom_surface_chunks_set_interest(rt->surface_chunks,
                                                  rt->body_registry,
                                                  body_id,
                                                  &center,
                                                  bubble.radius_m);
        } else {
            (void)dom_surface_chunks_clear_interest(rt->surface_chunks);
        }
    }

    if (rt->transfer_scheduler && rt->route_graph && rt->station_registry) {
        if (dom_transfer_update(rt->transfer_scheduler,
                                rt->route_graph,
                                rt->station_registry,
                                (u64)sim->tick_index) != DOM_TRANSFER_OK) {
            return DOM_GAME_RUNTIME_ERR;
        }
    }
    if (rt->macro_events && rt->macro_economy) {
        if (dom_macro_events_update(rt->macro_events,
                                    rt->macro_economy,
                                    (u64)sim->tick_index) != DOM_MACRO_EVENTS_OK) {
            return DOM_GAME_RUNTIME_ERR;
        }
    }
    if (rt->production && rt->station_registry) {
        if (dom_production_update_with_macro(rt->production,
                                             rt->station_registry,
                                             rt->body_registry,
                                             rt->macro_economy,
                                             (u64)sim->tick_index) != DOM_PRODUCTION_OK) {
            return DOM_GAME_RUNTIME_ERR;
        }
    }

    return DOM_GAME_RUNTIME_OK;
}

int dom_game_runtime_tick_wall(dom_game_runtime *rt, u64 wall_dt_usec, u32 *out_ticks) {
    u64 tick_us = (rt && rt->ups > 0u) ? (1000000ull / (u64)rt->ups) : 0ull;
    if (rt && rt->warp_factor > 1u && tick_us > 0u) {
        tick_us /= (u64)rt->warp_factor;
        if (tick_us == 0u) {
            tick_us = 1u;
        }
    }
    u32 stepped = 0u;
    int rc = DOM_GAME_RUNTIME_OK;

    if (!rt) {
        return DOM_GAME_RUNTIME_ERR;
    }

    if (tick_us == 0ull) {
        rc = dom_game_runtime_step(rt);
        if (rc == DOM_GAME_RUNTIME_OK || rc == DOM_GAME_RUNTIME_REPLAY_END) {
            stepped = 1u;
        }
        if (out_ticks) {
            *out_ticks = stepped;
        }
        return rc;
    }

    rt->wall_accum_us += wall_dt_usec;

    while (rt->wall_accum_us >= tick_us) {
        rc = dom_game_runtime_step(rt);
        if (rc == DOM_GAME_RUNTIME_ERR) {
            break;
        }
        rt->wall_accum_us -= tick_us;
        stepped += 1u;
        if (rc == DOM_GAME_RUNTIME_REPLAY_END) {
            break;
        }
    }

    if (out_ticks) {
        *out_ticks = stepped;
    }
    return rc;
}

int dom_game_runtime_execute(dom_game_runtime *rt, const dom_game_command *cmd, u32 *out_tick) {
    dom::DomGameNet *net;
    d_net_cmd net_cmd;
    u32 tick;
    u32 warp_factor = 0u;
    d_bool is_warp = D_FALSE;

    if (!rt || !cmd) {
        return DOM_GAME_RUNTIME_ERR;
    }
    if (cmd->struct_size != sizeof(dom_game_command) ||
        cmd->struct_version != DOM_GAME_COMMAND_VERSION) {
        return DOM_GAME_RUNTIME_ERR;
    }
    if (cmd->schema_id == 0u || cmd->schema_ver == 0u) {
        return DOM_GAME_RUNTIME_ERR;
    }
    if (cmd->payload_size > 0u && !cmd->payload) {
        return DOM_GAME_RUNTIME_ERR;
    }

    net = net_of(rt);
    if (!net) {
        return DOM_GAME_RUNTIME_ERR;
    }

    tick = cmd->tick ? cmd->tick : dom_game_runtime_next_cmd_tick(rt);
    if (cmd->schema_id == D_NET_SCHEMA_CMD_WARP_V1) {
        if (parse_warp_payload(cmd, &warp_factor) != DOM_GAME_RUNTIME_OK) {
            return DOM_GAME_RUNTIME_ERR;
        }
        if (warp_factor < DEFAULT_WARP_FACTOR || warp_factor > MAX_WARP_FACTOR) {
            return DOM_GAME_RUNTIME_ERR;
        }
        is_warp = D_TRUE;
    }

    std::memset(&net_cmd, 0, sizeof(net_cmd));
    net_cmd.tick = tick;
    net_cmd.schema_id = cmd->schema_id;
    net_cmd.schema_ver = cmd->schema_ver;
    net_cmd.payload.ptr = (unsigned char *)cmd->payload;
    net_cmd.payload.len = cmd->payload_size;

    if (!net->submit_cmd(&net_cmd)) {
        return DOM_GAME_RUNTIME_ERR;
    }
    if (is_warp) {
        rt->pending_warp_tick = (u64)tick;
        rt->pending_warp_factor = warp_factor;
        rt->pending_warp_valid = 1;
    }

    if (out_tick) {
        *out_tick = tick;
    }
    return DOM_GAME_RUNTIME_OK;
}

u64 dom_game_runtime_get_tick(const dom_game_runtime *rt) {
    dom::DomSession *session = session_of(rt);
    const d_sim_context *sim = session ? session->sim() : 0;
    return sim ? (u64)sim->tick_index : 0ull;
}

u64 dom_game_runtime_get_seed(const dom_game_runtime *rt) {
    dom::DomSession *session = session_of(rt);
    const dom::InstanceInfo *inst = inst_of(rt);
    return compute_seed(session, inst);
}

u32 dom_game_runtime_get_ups(const dom_game_runtime *rt) {
    return rt ? rt->ups : 0u;
}

u64 dom_game_runtime_get_hash(const dom_game_runtime *rt) {
    dom::DomSession *session = session_of(rt);
    const d_world *w = session ? session->world() : 0;
    return (u64)dom_game_hash_world(w);
}

u64 dom_game_runtime_get_run_id(const dom_game_runtime *rt) {
    return rt ? rt->run_id : 0ull;
}

u32 dom_game_runtime_get_warp_factor(const dom_game_runtime *rt) {
    return rt ? rt->warp_factor : DEFAULT_WARP_FACTOR;
}

const unsigned char *dom_game_runtime_get_manifest_hash(const dom_game_runtime *rt, u32 *out_len) {
    if (out_len) {
        *out_len = 0u;
    }
    if (!rt || rt->manifest_hash_bytes.empty()) {
        return (const unsigned char *)0;
    }
    if (out_len) {
        *out_len = (u32)rt->manifest_hash_bytes.size();
    }
    return &rt->manifest_hash_bytes[0];
}

int dom_game_runtime_get_counts(const dom_game_runtime *rt, dom_game_counts *out_counts) {
    dom::DomSession *session;
    d_world *w;

    if (!rt || !out_counts) {
        return DOM_GAME_RUNTIME_ERR;
    }

    out_counts->struct_size = sizeof(dom_game_counts);
    out_counts->struct_version = DOM_GAME_QUERY_VERSION;

    session = session_of(rt);
    w = session ? session->world() : 0;
    if (!w) {
        out_counts->entity_count = 0u;
        out_counts->construction_count = 0u;
        return DOM_GAME_RUNTIME_ERR;
    }

    out_counts->entity_count = d_agent_count(w);
    if (rt->construction_registry) {
        out_counts->construction_count = dom_construction_count(rt->construction_registry);
    } else {
        out_counts->construction_count = d_struct_count(w);
    }
    return DOM_GAME_RUNTIME_OK;
}

u32 dom_game_runtime_input_delay(const dom_game_runtime *rt) {
    if (!rt || !rt->net) {
        return 1u;
    }
    return static_cast<const dom::DomGameNet *>(rt->net)->input_delay_ticks();
}

u32 dom_game_runtime_next_cmd_tick(const dom_game_runtime *rt) {
    const u64 now = dom_game_runtime_get_tick(rt);
    u32 delay = dom_game_runtime_input_delay(rt);
    if (delay < 1u) {
        delay = 1u;
    }
    return (u32)now + delay;
}

struct d_world *dom_game_runtime_world(dom_game_runtime *rt) {
    dom::DomSession *session = session_of(rt);
    return session ? session->world() : 0;
}

struct d_sim_context *dom_game_runtime_sim(dom_game_runtime *rt) {
    dom::DomSession *session = session_of(rt);
    return session ? session->sim() : 0;
}

struct d_replay_context *dom_game_runtime_replay(dom_game_runtime *rt) {
    dom::DomSession *session = session_of(rt);
    return session ? session->replay() : 0;
}

const void *dom_game_runtime_session(const dom_game_runtime *rt) {
    return rt ? rt->session : 0;
}

const void *dom_game_runtime_instance(const dom_game_runtime *rt) {
    return rt ? rt->instance : 0;
}

const void *dom_game_runtime_cosmo_graph(const dom_game_runtime *rt) {
    return rt ? static_cast<const void *>(&rt->cosmo_graph) : 0;
}

const void *dom_game_runtime_system_registry(const dom_game_runtime *rt) {
    return rt ? static_cast<const void *>(rt->system_registry) : 0;
}

const void *dom_game_runtime_body_registry(const dom_game_runtime *rt) {
    return rt ? static_cast<const void *>(rt->body_registry) : 0;
}

const void *dom_game_runtime_frames(const dom_game_runtime *rt) {
    return rt ? static_cast<const void *>(rt->frames) : 0;
}

const void *dom_game_runtime_lane_scheduler(const dom_game_runtime *rt) {
    return rt ? static_cast<const void *>(rt->lane_sched) : 0;
}

const void *dom_game_runtime_surface_chunks(const dom_game_runtime *rt) {
    return rt ? static_cast<const void *>(rt->surface_chunks) : 0;
}

const void *dom_game_runtime_construction_registry(const dom_game_runtime *rt) {
    return rt ? static_cast<const void *>(rt->construction_registry) : 0;
}

const void *dom_game_runtime_station_registry(const dom_game_runtime *rt) {
    return rt ? static_cast<const void *>(rt->station_registry) : 0;
}

const void *dom_game_runtime_route_graph(const dom_game_runtime *rt) {
    return rt ? static_cast<const void *>(rt->route_graph) : 0;
}

const void *dom_game_runtime_transfer_scheduler(const dom_game_runtime *rt) {
    return rt ? static_cast<const void *>(rt->transfer_scheduler) : 0;
}

const void *dom_game_runtime_production(const dom_game_runtime *rt) {
    return rt ? static_cast<const void *>(rt->production) : 0;
}

const void *dom_game_runtime_macro_economy(const dom_game_runtime *rt) {
    return rt ? static_cast<const void *>(rt->macro_economy) : 0;
}

const void *dom_game_runtime_macro_events(const dom_game_runtime *rt) {
    return rt ? static_cast<const void *>(rt->macro_events) : 0;
}

int dom_game_runtime_set_surface_focus(dom_game_runtime *rt,
                                       dom_body_id body_id,
                                       const dom_topo_latlong_q16 *latlong) {
    if (!rt || !latlong || body_id == 0ull) {
        return DOM_GAME_RUNTIME_ERR;
    }
    rt->surface_body_id = body_id;
    rt->surface_focus = *latlong;
    rt->surface_focus_valid = 1;
    return DOM_GAME_RUNTIME_OK;
}

int dom_game_runtime_get_surface_focus(const dom_game_runtime *rt,
                                       dom_body_id *out_body_id,
                                       dom_topo_latlong_q16 *out_latlong) {
    if (!rt || !out_body_id || !out_latlong || !rt->surface_focus_valid) {
        return DOM_GAME_RUNTIME_ERR;
    }
    *out_body_id = rt->surface_body_id;
    *out_latlong = rt->surface_focus;
    return DOM_GAME_RUNTIME_OK;
}

int dom_game_runtime_pump_surface_chunks(dom_game_runtime *rt,
                                         u32 max_ms,
                                         u64 max_io_bytes,
                                         u32 max_jobs) {
    if (!rt || !rt->surface_chunks) {
        return DOM_GAME_RUNTIME_ERR;
    }
    return (dom_surface_chunk_pump_jobs(rt->surface_chunks,
                                        max_ms,
                                        max_io_bytes,
                                        max_jobs) == DOM_SURFACE_CHUNKS_OK)
               ? DOM_GAME_RUNTIME_OK
               : DOM_GAME_RUNTIME_ERR;
}

int dom_game_runtime_surface_has_pending(const dom_game_runtime *rt) {
    if (!rt || !rt->surface_chunks) {
        return 0;
    }
    return dom_surface_chunks_has_pending(rt->surface_chunks) ? 1 : 0;
}
