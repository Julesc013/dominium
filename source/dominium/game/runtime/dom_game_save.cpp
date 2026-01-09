/*
FILE: source/dominium/game/runtime/dom_game_save.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / game/runtime/dom_game_save
RESPONSIBILITY: Implements DMSG save/load helpers for the runtime kernel; does NOT define a public API (see `include/**`).
ALLOWED DEPENDENCIES: `include/dominium/**`, `source/dominium/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: Dependency inversions that violate `docs/OVERVIEW_ARCHITECTURE.md` layering.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: Determinism-sensitive (hash comparisons across save/load); see `docs/SPEC_DETERMINISM.md`.
VERSIONING / ABI / DATA FORMAT NOTES: DMSG v4 container; see `source/dominium/game/SPEC_SAVE.md`.
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include "runtime/dom_game_save.h"

#include <vector>
#include <cstdio>
#include <cstring>
#include <cstdlib>
#include <climits>

#include "runtime/dom_game_runtime.h"
#include "runtime/dom_game_content_id.h"
#include "runtime/dom_body_registry.h"
#include "runtime/dom_media_provider.h"
#include "runtime/dom_weather_provider.h"
#include "runtime/dom_lane_scheduler.h"
#include "runtime/dom_construction_registry.h"
#include "runtime/dom_station_registry.h"
#include "runtime/dom_route_graph.h"
#include "runtime/dom_transfer_scheduler.h"
#include "runtime/dom_production.h"
#include "runtime/dom_macro_economy.h"
#include "runtime/dom_macro_events.h"
#include "runtime/dom_faction_registry.h"
#include "runtime/dom_ai_scheduler.h"
#include "../dom_game_save.h"
#include "dom_instance.h"
#include "dom_session.h"
#include "dominium/core_tlv.h"
#include "dom_feature_epoch.h"
#include "runtime/dom_io_guard.h"

extern "C" {
#include "domino/sys.h"
#include "net/d_net_cmd.h"
}

namespace {

enum {
    DMSG_VERSION = 6u,
    DMSG_ENDIAN = 0x0000FFFEu,
    DMSG_CORE_VERSION = 1u,
    DMSG_ORBIT_VERSION = 1u,
    DMSG_SURFACE_VERSION = 1u,
    DMSG_MEDIA_BINDINGS_VERSION = 1u,
    DMSG_WEATHER_BINDINGS_VERSION = 1u,
    DMSG_AERO_PROPS_VERSION = 1u,
    DMSG_AERO_STATE_VERSION = 1u,
    DMSG_CONSTRUCTION_VERSION = 1u,
    DMSG_STATIONS_VERSION = 1u,
    DMSG_ROUTES_VERSION = 1u,
    DMSG_TRANSFERS_VERSION = 1u,
    DMSG_PRODUCTION_VERSION = 1u,
    DMSG_MACRO_ECONOMY_VERSION = 1u,
    DMSG_MACRO_EVENTS_VERSION = 1u,
    DMSG_FACTIONS_VERSION = 1u,
    DMSG_AI_SCHED_VERSION = 1u,
    DMSG_RNG_VERSION = 1u,
    DMSG_IDENTITY_VERSION = 1u
};

enum {
    DMSG_IDENTITY_TAG_INSTANCE_ID = 2u,
    DMSG_IDENTITY_TAG_RUN_ID = 3u,
    DMSG_IDENTITY_TAG_MANIFEST_HASH = 4u,
    DMSG_IDENTITY_TAG_CONTENT_HASH = 5u
};

enum {
    DMSG_MEDIA_BINDINGS_SCHEMA_VERSION = 1u,
    DMSG_MEDIA_BINDINGS_TAG_BINDING = 0x0100u,
    DMSG_MEDIA_BINDINGS_TAG_BODY_ID = 0x0101u,
    DMSG_MEDIA_BINDINGS_TAG_KIND = 0x0102u,
    DMSG_MEDIA_BINDINGS_TAG_PROVIDER_ID = 0x0103u,
    DMSG_MEDIA_BINDINGS_TAG_PARAMS = 0x0104u
};

enum {
    DMSG_WEATHER_BINDINGS_SCHEMA_VERSION = 1u,
    DMSG_WEATHER_BINDINGS_TAG_BINDING = 0x0200u,
    DMSG_WEATHER_BINDINGS_TAG_BODY_ID = 0x0201u,
    DMSG_WEATHER_BINDINGS_TAG_PROVIDER_ID = 0x0202u,
    DMSG_WEATHER_BINDINGS_TAG_PARAMS = 0x0203u
};

static u32 read_u32_le(const unsigned char *p) {
    return (u32)p[0] |
           ((u32)p[1] << 8) |
           ((u32)p[2] << 16) |
           ((u32)p[3] << 24);
}

static u64 read_u64_le(const unsigned char *p) {
    return (u64)read_u32_le(p) | ((u64)read_u32_le(p + 4u) << 32u);
}

static i32 read_i32_le(const unsigned char *p) {
    return (i32)read_u32_le(p);
}

static i64 read_i64_le(const unsigned char *p) {
    return (i64)read_u64_le(p);
}

static void write_u32_le(unsigned char out[4], u32 v) {
    out[0] = (unsigned char)(v & 0xffu);
    out[1] = (unsigned char)((v >> 8u) & 0xffu);
    out[2] = (unsigned char)((v >> 16u) & 0xffu);
    out[3] = (unsigned char)((v >> 24u) & 0xffu);
}

static void write_u64_le(unsigned char out[8], u64 v) {
    write_u32_le(out, (u32)(v & 0xffffffffull));
    write_u32_le(out + 4u, (u32)((v >> 32u) & 0xffffffffull));
}

static void append_bytes(std::vector<unsigned char> &out, const void *data, size_t len) {
    const size_t base = out.size();
    out.resize(base + len);
    if (len > 0u && data) {
        std::memcpy(&out[base], data, len);
    }
}

static void append_u32_le(std::vector<unsigned char> &out, u32 v) {
    unsigned char buf[4];
    write_u32_le(buf, v);
    append_bytes(out, buf, 4u);
}

static void append_u64_le(std::vector<unsigned char> &out, u64 v) {
    unsigned char buf[8];
    write_u64_le(buf, v);
    append_bytes(out, buf, 8u);
}

static void append_i32_le(std::vector<unsigned char> &out, i32 v) {
    append_u32_le(out, (u32)v);
}

static void append_i64_le(std::vector<unsigned char> &out, i64 v) {
    append_u64_le(out, (u64)v);
}

static bool write_file(const char *path, const unsigned char *data, size_t len) {
    void *fh;
    size_t wrote;
    if (!path || !path[0]) {
        return false;
    }
    if (!dom_io_guard_io_allowed()) {
        dom_io_guard_note_violation("save_write", path);
        return false;
    }
    fh = dsys_file_open(path, "wb");
    if (!fh) {
        return false;
    }
    wrote = dsys_file_write(fh, data, len);
    dsys_file_close(fh);
    return wrote == len;
}

static bool read_file_alloc(const char *path, unsigned char **out_data, size_t *out_len) {
    void *fh;
    long size;
    size_t read_len;
    unsigned char *buf;

    if (!path || !path[0] || !out_data || !out_len) {
        return false;
    }
    if (!dom_io_guard_io_allowed()) {
        dom_io_guard_note_violation("save_read", path);
        return false;
    }

    fh = dsys_file_open(path, "rb");
    if (!fh) {
        return false;
    }
    if (dsys_file_seek(fh, 0L, SEEK_END) != 0) {
        dsys_file_close(fh);
        return false;
    }
    size = dsys_file_tell(fh);
    if (size <= 0L) {
        dsys_file_close(fh);
        return false;
    }
    if (dsys_file_seek(fh, 0L, SEEK_SET) != 0) {
        dsys_file_close(fh);
        return false;
    }

    buf = (unsigned char *)std::malloc((size_t)size);
    if (!buf) {
        dsys_file_close(fh);
        return false;
    }
    read_len = dsys_file_read(fh, buf, (size_t)size);
    dsys_file_close(fh);
    if (read_len != (size_t)size) {
        std::free(buf);
        return false;
    }

    *out_data = buf;
    *out_len = (size_t)size;
    return true;
}

static bool build_identity_tlv(const dom_game_runtime *rt,
                               const unsigned char *content_tlv,
                               size_t content_len,
                               std::vector<unsigned char> &out) {
    dom::core_tlv::TlvWriter w;
    const dom::InstanceInfo *inst = (const dom::InstanceInfo *)dom_game_runtime_instance(rt);
    u32 manifest_len = 0u;
    const unsigned char *manifest = dom_game_runtime_get_manifest_hash(rt, &manifest_len);
    const u64 run_id = dom_game_runtime_get_run_id(rt);
    const u64 content_hash = dom::core_tlv::tlv_fnv1a64(content_tlv, content_len);
    const std::string inst_id = inst ? inst->id : std::string();
    const unsigned char *manifest_ptr = manifest;
    u32 manifest_size = manifest_len;

    if (!manifest_ptr) {
        manifest_size = 0u;
    }

    w.add_u32(dom::core_tlv::CORE_TLV_TAG_SCHEMA_VERSION, DMSG_IDENTITY_VERSION);
    w.add_string(DMSG_IDENTITY_TAG_INSTANCE_ID, inst_id);
    w.add_u64(DMSG_IDENTITY_TAG_RUN_ID, run_id);
    w.add_bytes(DMSG_IDENTITY_TAG_MANIFEST_HASH, manifest_ptr, manifest_size);
    w.add_u64(DMSG_IDENTITY_TAG_CONTENT_HASH, content_hash);

    out = w.bytes();
    return true;
}

struct BodyIdCollectCtx {
    std::vector<dom_body_id> *ids;
};

static void collect_body_id(const dom_body_info *info, void *user) {
    BodyIdCollectCtx *ctx = static_cast<BodyIdCollectCtx *>(user);
    if (ctx && ctx->ids && info && info->id != 0ull) {
        ctx->ids->push_back(info->id);
    }
}

static bool build_media_bindings_blob(const dom_game_runtime *rt,
                                      std::vector<unsigned char> &out) {
    const dom_body_registry *bodies;
    const dom_media_registry *media;
    dom::core_tlv::TlvWriter writer;
    static const u32 kinds[] = {
        DOM_MEDIA_KIND_VACUUM,
        DOM_MEDIA_KIND_ATMOSPHERE,
        DOM_MEDIA_KIND_OCEAN
    };

    writer.add_u32(dom::core_tlv::CORE_TLV_TAG_SCHEMA_VERSION,
                   DMSG_MEDIA_BINDINGS_SCHEMA_VERSION);
    bodies = rt ? (const dom_body_registry *)dom_game_runtime_body_registry(rt) : 0;
    media = rt ? (const dom_media_registry *)dom_game_runtime_media_registry(rt) : 0;
    if (!bodies || !media) {
        out = writer.bytes();
        return true;
    }

    {
        std::vector<dom_body_id> body_ids;
        BodyIdCollectCtx ctx;
        ctx.ids = &body_ids;
        if (dom_body_registry_iterate(bodies, collect_body_id, &ctx) != DOM_BODY_REGISTRY_OK) {
            return false;
        }
        for (size_t i = 0u; i < body_ids.size(); ++i) {
            for (size_t k = 0u; k < (sizeof(kinds) / sizeof(kinds[0])); ++k) {
                dom_media_binding binding;
                std::memset(&binding, 0, sizeof(binding));
                if (dom_media_registry_get_binding(media, body_ids[i], kinds[k], &binding)
                    != DOM_MEDIA_OK) {
                    continue;
                }
                if (binding.provider_id_len == 0u ||
                    binding.provider_id_len >= DOM_MEDIA_PROVIDER_ID_MAX) {
                    return false;
                }
                {
                    dom::core_tlv::TlvWriter entry;
                    entry.add_u64(DMSG_MEDIA_BINDINGS_TAG_BODY_ID, binding.body_id);
                    entry.add_u32(DMSG_MEDIA_BINDINGS_TAG_KIND, binding.kind);
                    entry.add_bytes(DMSG_MEDIA_BINDINGS_TAG_PROVIDER_ID,
                                    (const unsigned char *)binding.provider_id,
                                    binding.provider_id_len);
                    entry.add_bytes(DMSG_MEDIA_BINDINGS_TAG_PARAMS,
                                    binding.params,
                                    binding.params_len);
                    writer.add_container(DMSG_MEDIA_BINDINGS_TAG_BINDING, entry.bytes());
                }
            }
        }
    }

    out = writer.bytes();
    return true;
}

static bool build_weather_bindings_blob(const dom_game_runtime *rt,
                                        std::vector<unsigned char> &out) {
    const dom_body_registry *bodies;
    const dom_weather_registry *weather;
    dom::core_tlv::TlvWriter writer;

    writer.add_u32(dom::core_tlv::CORE_TLV_TAG_SCHEMA_VERSION,
                   DMSG_WEATHER_BINDINGS_SCHEMA_VERSION);
    bodies = rt ? (const dom_body_registry *)dom_game_runtime_body_registry(rt) : 0;
    weather = rt ? (const dom_weather_registry *)dom_game_runtime_weather_registry(rt) : 0;
    if (!bodies || !weather) {
        out = writer.bytes();
        return true;
    }

    {
        std::vector<dom_body_id> body_ids;
        BodyIdCollectCtx ctx;
        ctx.ids = &body_ids;
        if (dom_body_registry_iterate(bodies, collect_body_id, &ctx) != DOM_BODY_REGISTRY_OK) {
            return false;
        }
        for (size_t i = 0u; i < body_ids.size(); ++i) {
            dom_weather_binding binding;
            std::memset(&binding, 0, sizeof(binding));
            if (dom_weather_registry_get_binding(weather, body_ids[i], &binding)
                != DOM_WEATHER_OK) {
                continue;
            }
            if (binding.provider_id_len == 0u ||
                binding.provider_id_len >= DOM_WEATHER_PROVIDER_ID_MAX) {
                return false;
            }
            {
                dom::core_tlv::TlvWriter entry;
                entry.add_u64(DMSG_WEATHER_BINDINGS_TAG_BODY_ID, binding.body_id);
                entry.add_bytes(DMSG_WEATHER_BINDINGS_TAG_PROVIDER_ID,
                                (const unsigned char *)binding.provider_id,
                                binding.provider_id_len);
                entry.add_bytes(DMSG_WEATHER_BINDINGS_TAG_PARAMS,
                                binding.params,
                                binding.params_len);
                writer.add_container(DMSG_WEATHER_BINDINGS_TAG_BINDING, entry.bytes());
            }
        }
    }

    out = writer.bytes();
    return true;
}

static bool build_aero_props_blob(const dom_game_runtime *rt,
                                  std::vector<unsigned char> &out) {
    const dom_lane_scheduler *sched;
    u32 count = 0u;
    std::vector<dom_lane_vessel_aero> list;
    std::vector<dom_lane_vessel_aero> filtered;

    out.clear();
    sched = rt ? (const dom_lane_scheduler *)dom_game_runtime_lane_scheduler(rt) : 0;
    if (!sched) {
        append_u32_le(out, 0u);
        return true;
    }
    if (dom_lane_scheduler_list_aero(sched, 0, 0u, &count) != DOM_LANE_OK) {
        return false;
    }
    if (count == 0u) {
        append_u32_le(out, 0u);
        return true;
    }
    list.resize(count);
    if (dom_lane_scheduler_list_aero(sched, &list[0], count, &count) != DOM_LANE_OK) {
        return false;
    }
    filtered.reserve(count);
    for (u32 i = 0u; i < count; ++i) {
        if (list[i].has_aero_props) {
            filtered.push_back(list[i]);
        }
    }

    append_u32_le(out, (u32)filtered.size());
    for (size_t i = 0u; i < filtered.size(); ++i) {
        const dom_vehicle_aero_props &props = filtered[i].aero_props;
        append_u64_le(out, filtered[i].vessel_id);
        append_i32_le(out, props.mass_kg_q16);
        append_i32_le(out, props.drag_area_cda_q16);
        append_i32_le(out, props.heat_coeff_q16);
        append_i32_le(out, props.max_heat_q16);
        append_u32_le(out, props.has_max_heat ? 1u : 0u);
    }
    return true;
}

static bool build_aero_state_blob(const dom_game_runtime *rt,
                                  std::vector<unsigned char> &out) {
    const dom_lane_scheduler *sched;
    u32 count = 0u;
    std::vector<dom_lane_vessel_aero> list;
    std::vector<dom_lane_vessel_aero> filtered;

    out.clear();
    sched = rt ? (const dom_lane_scheduler *)dom_game_runtime_lane_scheduler(rt) : 0;
    if (!sched) {
        append_u32_le(out, 0u);
        return true;
    }
    if (dom_lane_scheduler_list_aero(sched, 0, 0u, &count) != DOM_LANE_OK) {
        return false;
    }
    if (count == 0u) {
        append_u32_le(out, 0u);
        return true;
    }
    list.resize(count);
    if (dom_lane_scheduler_list_aero(sched, &list[0], count, &count) != DOM_LANE_OK) {
        return false;
    }
    filtered.reserve(count);
    for (u32 i = 0u; i < count; ++i) {
        if (list[i].has_aero_props) {
            filtered.push_back(list[i]);
        }
    }

    append_u32_le(out, (u32)filtered.size());
    for (size_t i = 0u; i < filtered.size(); ++i) {
        const dom_vehicle_aero_state &state = filtered[i].aero_state;
        append_u64_le(out, filtered[i].vessel_id);
        append_i32_le(out, state.heat_accum_q16);
        append_i32_le(out, state.last_heating_rate_q16);
        append_i32_le(out, state.last_drag_accel_q16);
    }
    return true;
}

static bool construction_type_valid(u32 type_id) {
    return type_id == DOM_CONSTRUCTION_TYPE_HABITAT ||
           type_id == DOM_CONSTRUCTION_TYPE_STORAGE ||
           type_id == DOM_CONSTRUCTION_TYPE_GENERIC_PLATFORM;
}

struct StationCollectCtx {
    std::vector<dom_station_info> *stations;
};

static void collect_station_info(const dom_station_info *info, void *user) {
    StationCollectCtx *ctx = static_cast<StationCollectCtx *>(user);
    if (ctx && ctx->stations && info) {
        ctx->stations->push_back(*info);
    }
}

struct RouteCollectCtx {
    std::vector<dom_route_info> *routes;
};

static void collect_route_info(const dom_route_info *info, void *user) {
    RouteCollectCtx *ctx = static_cast<RouteCollectCtx *>(user);
    if (ctx && ctx->routes && info) {
        ctx->routes->push_back(*info);
    }
}

struct ProductionCollectCtx {
    std::vector<dom_production_rule_info> *rules;
};

static void collect_production_rule_info(const dom_production_rule_info *info, void *user) {
    ProductionCollectCtx *ctx = static_cast<ProductionCollectCtx *>(user);
    if (ctx && ctx->rules && info) {
        ctx->rules->push_back(*info);
    }
}

struct FactionCollectCtx {
    std::vector<dom_faction_info> *factions;
};

static void collect_faction_info(const dom_faction_info *info, void *user) {
    FactionCollectCtx *ctx = static_cast<FactionCollectCtx *>(user);
    if (ctx && ctx->factions && info) {
        ctx->factions->push_back(*info);
    }
}

enum {
    DMSG_CONSTRUCTION_RECORD_SIZE = 68u
};

enum {
    DMSG_AERO_PROPS_RECORD_SIZE = 28u,
    DMSG_AERO_STATE_RECORD_SIZE = 20u
};

enum {
    DMSG_ROUTE_RECORD_SIZE = 40u,
    DMSG_PRODUCTION_RECORD_SIZE = 40u
};

static bool build_construction_blob(const dom_game_runtime *rt,
                                    std::vector<unsigned char> &out) {
    const dom_construction_registry *registry;
    u32 count = 0u;
    int rc;

    out.clear();
    registry = rt ? (const dom_construction_registry *)dom_game_runtime_construction_registry(rt) : 0;
    if (!registry) {
        append_u32_le(out, 0u);
        return true;
    }
    rc = dom_construction_list(registry, 0, 0u, &count);
    if (rc != DOM_CONSTRUCTION_OK) {
        return false;
    }
    append_u32_le(out, count);
    if (count == 0u) {
        return true;
    }
    {
        std::vector<dom_construction_instance> list;
        list.resize(count);
        rc = dom_construction_list(registry, &list[0], count, &count);
        if (rc != DOM_CONSTRUCTION_OK) {
            return false;
        }
        if (list.size() != count) {
            list.resize(count);
        }
        for (u32 i = 0u; i < count; ++i) {
            const dom_construction_instance &inst = list[i];
            append_u64_le(out, inst.instance_id);
            append_u32_le(out, inst.type_id);
            append_u32_le(out, inst.orientation);
            append_u64_le(out, inst.body_id);
            append_i32_le(out, inst.chunk_key.step_turns_q16);
            append_i32_le(out, inst.chunk_key.lat_index);
            append_i32_le(out, inst.chunk_key.lon_index);
            append_i64_le(out, (i64)inst.local_pos_m[0]);
            append_i64_le(out, (i64)inst.local_pos_m[1]);
            append_i64_le(out, (i64)inst.local_pos_m[2]);
            append_i32_le(out, inst.cell_x);
            append_i32_le(out, inst.cell_y);
        }
    }
    return true;
}

static bool build_station_blob(const dom_game_runtime *rt,
                               std::vector<unsigned char> &out) {
    const dom_station_registry *registry;
    std::vector<dom_station_info> stations;
    StationCollectCtx ctx;
    u32 count = 0u;

    out.clear();
    registry = rt ? (const dom_station_registry *)dom_game_runtime_station_registry(rt) : 0;
    if (!registry) {
        append_u32_le(out, 0u);
        return true;
    }

    count = dom_station_count(registry);
    append_u32_le(out, count);
    if (count == 0u) {
        return true;
    }

    stations.reserve(count);
    ctx.stations = &stations;
    if (dom_station_iterate(registry, collect_station_info, &ctx) != DOM_STATION_REGISTRY_OK) {
        return false;
    }
    if (stations.size() != count) {
        count = (u32)stations.size();
    }

    for (u32 i = 0u; i < count; ++i) {
        const dom_station_info &info = stations[i];
        u32 inv_count = 0u;
        append_u64_le(out, info.station_id);
        append_u64_le(out, info.body_id);
        append_u64_le(out, info.frame_id);

        if (dom_station_inventory_list(registry, info.station_id, 0, 0u, &inv_count) != DOM_STATION_REGISTRY_OK) {
            return false;
        }
        append_u32_le(out, inv_count);
        if (inv_count > 0u) {
            std::vector<dom_inventory_entry> inv;
            inv.resize(inv_count);
            if (dom_station_inventory_list(registry, info.station_id, &inv[0], inv_count, &inv_count)
                != DOM_STATION_REGISTRY_OK) {
                return false;
            }
            for (u32 j = 0u; j < inv_count; ++j) {
                append_u64_le(out, inv[j].resource_id);
                append_i64_le(out, inv[j].quantity);
            }
        }
    }
    return true;
}

static bool build_route_blob(const dom_game_runtime *rt,
                             std::vector<unsigned char> &out) {
    const dom_route_graph *graph;
    std::vector<dom_route_info> routes;
    RouteCollectCtx ctx;
    u32 count = 0u;

    out.clear();
    graph = rt ? (const dom_route_graph *)dom_game_runtime_route_graph(rt) : 0;
    if (!graph) {
        append_u32_le(out, 0u);
        return true;
    }

    count = dom_route_graph_count(graph);
    append_u32_le(out, count);
    if (count == 0u) {
        return true;
    }
    routes.reserve(count);
    ctx.routes = &routes;
    if (dom_route_graph_iterate(graph, collect_route_info, &ctx) != DOM_ROUTE_GRAPH_OK) {
        return false;
    }
    if (routes.size() != count) {
        count = (u32)routes.size();
    }

    for (u32 i = 0u; i < count; ++i) {
        const dom_route_info &info = routes[i];
        append_u64_le(out, info.route_id);
        append_u64_le(out, info.src_station_id);
        append_u64_le(out, info.dst_station_id);
        append_u64_le(out, info.duration_ticks);
        append_u64_le(out, info.capacity_units);
    }
    return true;
}

static bool build_transfer_blob(const dom_game_runtime *rt,
                                std::vector<unsigned char> &out) {
    const dom_transfer_scheduler *sched;
    u32 count = 0u;
    std::vector<dom_transfer_info> transfers;

    out.clear();
    sched = rt ? (const dom_transfer_scheduler *)dom_game_runtime_transfer_scheduler(rt) : 0;
    if (!sched) {
        append_u32_le(out, 0u);
        return true;
    }

    if (dom_transfer_list(sched, 0, 0u, &count) != DOM_TRANSFER_OK) {
        return false;
    }
    append_u32_le(out, count);
    if (count == 0u) {
        return true;
    }
    transfers.resize(count);
    if (dom_transfer_list(sched, &transfers[0], count, &count) != DOM_TRANSFER_OK) {
        return false;
    }
    if (transfers.size() != count) {
        transfers.resize(count);
    }

    for (u32 i = 0u; i < count; ++i) {
        const dom_transfer_info &info = transfers[i];
        std::vector<dom_transfer_entry> entries;
        u32 entry_count = info.entry_count;

        append_u64_le(out, info.transfer_id);
        append_u64_le(out, info.route_id);
        append_u64_le(out, info.start_tick);
        append_u64_le(out, info.arrival_tick);
        append_u32_le(out, entry_count);

        if (entry_count > 0u) {
            entries.resize(entry_count);
            if (dom_transfer_get_entries(sched,
                                         info.transfer_id,
                                         &entries[0],
                                         entry_count,
                                         &entry_count) != DOM_TRANSFER_OK) {
                return false;
            }
            for (u32 j = 0u; j < entry_count; ++j) {
                append_u64_le(out, entries[j].resource_id);
                append_i64_le(out, entries[j].quantity);
            }
        }
    }
    return true;
}

static bool build_production_blob(const dom_game_runtime *rt,
                                  std::vector<unsigned char> &out) {
    const dom_production *prod;
    std::vector<dom_production_rule_info> rules;
    ProductionCollectCtx ctx;
    u32 count = 0u;

    out.clear();
    prod = rt ? (const dom_production *)dom_game_runtime_production(rt) : 0;
    if (!prod) {
        append_u32_le(out, 0u);
        return true;
    }
    count = dom_production_count(prod);
    append_u32_le(out, count);
    if (count == 0u) {
        return true;
    }
    rules.reserve(count);
    ctx.rules = &rules;
    if (dom_production_iterate(prod, collect_production_rule_info, &ctx) != DOM_PRODUCTION_OK) {
        return false;
    }
    if (rules.size() != count) {
        count = (u32)rules.size();
    }
    for (u32 i = 0u; i < count; ++i) {
        const dom_production_rule_info &info = rules[i];
        append_u64_le(out, info.rule_id);
        append_u64_le(out, info.station_id);
        append_u64_le(out, info.resource_id);
        append_i64_le(out, info.delta_per_period);
        append_u64_le(out, info.period_ticks);
    }
    return true;
}

static bool append_macro_scope_entries(const dom_macro_economy *econ,
                                       u32 scope_kind,
                                       std::vector<unsigned char> &out) {
    u32 scope_count = 0u;
    if (!econ) {
        append_u32_le(out, 0u);
        return true;
    }
    if (dom_macro_economy_list_scopes(econ, scope_kind, 0, 0u, &scope_count)
        != DOM_MACRO_ECONOMY_OK) {
        return false;
    }
    append_u32_le(out, scope_count);
    if (scope_count == 0u) {
        return true;
    }
    {
        std::vector<dom_macro_scope_info> scopes;
        scopes.resize(scope_count);
        if (dom_macro_economy_list_scopes(econ,
                                          scope_kind,
                                          &scopes[0],
                                          scope_count,
                                          &scope_count) != DOM_MACRO_ECONOMY_OK) {
            return false;
        }
        if (scopes.size() != scope_count) {
            scopes.resize(scope_count);
        }
        for (u32 i = 0u; i < scope_count; ++i) {
            const dom_macro_scope_info &info = scopes[i];
            u32 prod_count = 0u;
            u32 demand_count = 0u;
            u32 stock_count = 0u;

            if (info.scope_id == 0ull) {
                return false;
            }
            if (dom_macro_economy_list_production(econ,
                                                  scope_kind,
                                                  info.scope_id,
                                                  0,
                                                  0u,
                                                  &prod_count) != DOM_MACRO_ECONOMY_OK) {
                return false;
            }
            if (dom_macro_economy_list_demand(econ,
                                              scope_kind,
                                              info.scope_id,
                                              0,
                                              0u,
                                              &demand_count) != DOM_MACRO_ECONOMY_OK) {
                return false;
            }
            if (dom_macro_economy_list_stockpile(econ,
                                                 scope_kind,
                                                 info.scope_id,
                                                 0,
                                                 0u,
                                                 &stock_count) != DOM_MACRO_ECONOMY_OK) {
                return false;
            }

            append_u64_le(out, info.scope_id);
            append_u32_le(out, info.flags);
            append_u32_le(out, prod_count);
            append_u32_le(out, demand_count);
            append_u32_le(out, stock_count);

            if (prod_count > 0u) {
                std::vector<dom_macro_rate_entry> prod;
                u32 actual = prod_count;
                prod.resize(prod_count);
                if (dom_macro_economy_list_production(econ,
                                                      scope_kind,
                                                      info.scope_id,
                                                      &prod[0],
                                                      prod_count,
                                                      &actual) != DOM_MACRO_ECONOMY_OK) {
                    return false;
                }
                if (actual != prod_count) {
                    return false;
                }
                for (u32 j = 0u; j < prod_count; ++j) {
                    append_u64_le(out, prod[j].resource_id);
                    append_i64_le(out, prod[j].rate_per_tick);
                }
            }

            if (demand_count > 0u) {
                std::vector<dom_macro_rate_entry> demand;
                u32 actual = demand_count;
                demand.resize(demand_count);
                if (dom_macro_economy_list_demand(econ,
                                                  scope_kind,
                                                  info.scope_id,
                                                  &demand[0],
                                                  demand_count,
                                                  &actual) != DOM_MACRO_ECONOMY_OK) {
                    return false;
                }
                if (actual != demand_count) {
                    return false;
                }
                for (u32 j = 0u; j < demand_count; ++j) {
                    append_u64_le(out, demand[j].resource_id);
                    append_i64_le(out, demand[j].rate_per_tick);
                }
            }

            if (stock_count > 0u) {
                std::vector<dom_macro_stock_entry> stock;
                u32 actual = stock_count;
                stock.resize(stock_count);
                if (dom_macro_economy_list_stockpile(econ,
                                                     scope_kind,
                                                     info.scope_id,
                                                     &stock[0],
                                                     stock_count,
                                                     &actual) != DOM_MACRO_ECONOMY_OK) {
                    return false;
                }
                if (actual != stock_count) {
                    return false;
                }
                for (u32 j = 0u; j < stock_count; ++j) {
                    append_u64_le(out, stock[j].resource_id);
                    append_i64_le(out, stock[j].quantity);
                }
            }
        }
    }
    return true;
}

static bool build_macro_economy_blob(const dom_game_runtime *rt,
                                     std::vector<unsigned char> &out) {
    const dom_macro_economy *econ;
    out.clear();
    econ = rt ? (const dom_macro_economy *)dom_game_runtime_macro_economy(rt) : 0;
    if (!append_macro_scope_entries(econ, DOM_MACRO_SCOPE_SYSTEM, out)) {
        return false;
    }
    if (!append_macro_scope_entries(econ, DOM_MACRO_SCOPE_GALAXY, out)) {
        return false;
    }
    return true;
}

static bool build_macro_events_blob(const dom_game_runtime *rt,
                                    std::vector<unsigned char> &out) {
    const dom_macro_events *events;
    u32 count = 0u;

    out.clear();
    events = rt ? (const dom_macro_events *)dom_game_runtime_macro_events(rt) : 0;
    if (!events) {
        append_u32_le(out, 0u);
        return true;
    }
    if (dom_macro_events_list(events, 0, 0u, &count) != DOM_MACRO_EVENTS_OK) {
        return false;
    }
    append_u32_le(out, count);
    if (count == 0u) {
        return true;
    }
    {
        std::vector<dom_macro_event_info> infos;
        infos.resize(count);
        if (dom_macro_events_list(events, &infos[0], count, &count) != DOM_MACRO_EVENTS_OK) {
            return false;
        }
        if (infos.size() != count) {
            infos.resize(count);
        }
        for (u32 i = 0u; i < count; ++i) {
            const dom_macro_event_info &info = infos[i];
            append_u64_le(out, info.event_id);
            append_u32_le(out, info.scope_kind);
            append_u64_le(out, info.scope_id);
            append_u64_le(out, info.trigger_tick);
            append_u32_le(out, info.effect_count);

            if (info.effect_count > 0u) {
                std::vector<dom_macro_event_effect> effects;
                u32 actual = info.effect_count;
                effects.resize(info.effect_count);
                if (dom_macro_events_list_effects(events,
                                                  info.event_id,
                                                  &effects[0],
                                                  info.effect_count,
                                                  &actual) != DOM_MACRO_EVENTS_OK) {
                    return false;
                }
                if (actual != info.effect_count) {
                    return false;
                }
                for (u32 j = 0u; j < info.effect_count; ++j) {
                    append_u64_le(out, effects[j].resource_id);
                    append_i64_le(out, effects[j].production_delta);
                    append_i64_le(out, effects[j].demand_delta);
                    append_u32_le(out, effects[j].flags_set);
                    append_u32_le(out, effects[j].flags_clear);
                }
            }
        }
    }
    return true;
}

static bool build_factions_blob(const dom_game_runtime *rt,
                                std::vector<unsigned char> &out) {
    const dom_faction_registry *registry;
    std::vector<dom_faction_info> factions;
    FactionCollectCtx ctx;
    u32 count = 0u;

    out.clear();
    registry = rt ? (const dom_faction_registry *)dom_game_runtime_faction_registry(rt) : 0;
    if (!registry) {
        append_u32_le(out, 0u);
        return true;
    }
    count = dom_faction_count(registry);
    append_u32_le(out, count);
    if (count == 0u) {
        return true;
    }

    factions.reserve(count);
    ctx.factions = &factions;
    if (dom_faction_iterate(registry, collect_faction_info, &ctx) != DOM_FACTION_OK) {
        return false;
    }
    if (factions.size() != count) {
        count = (u32)factions.size();
    }

    for (u32 i = 0u; i < count; ++i) {
        const dom_faction_info &info = factions[i];
        u32 known_count = 0u;
        u32 resource_count = 0u;
        append_u64_le(out, info.faction_id);
        append_u32_le(out, info.home_scope_kind);
        append_u64_le(out, info.home_scope_id);
        append_u32_le(out, info.policy_kind);
        append_u32_le(out, info.policy_flags);
        append_u64_le(out, info.ai_seed);

        if (dom_faction_list_known_nodes(registry,
                                         info.faction_id,
                                         0,
                                         0u,
                                         &known_count) != DOM_FACTION_OK) {
            return false;
        }
        if (dom_faction_resource_list(registry,
                                      info.faction_id,
                                      0,
                                      0u,
                                      &resource_count) != DOM_FACTION_OK) {
            return false;
        }
        append_u32_le(out, known_count);
        append_u32_le(out, resource_count);

        if (known_count > 0u) {
            std::vector<u64> nodes;
            u32 actual = known_count;
            nodes.resize(known_count);
            if (dom_faction_list_known_nodes(registry,
                                             info.faction_id,
                                             &nodes[0],
                                             known_count,
                                             &actual) != DOM_FACTION_OK) {
                return false;
            }
            if (actual != known_count) {
                return false;
            }
            for (u32 n = 0u; n < known_count; ++n) {
                append_u64_le(out, nodes[n]);
            }
        }

        if (resource_count > 0u) {
            std::vector<dom_faction_resource_entry> resources;
            u32 actual = resource_count;
            resources.resize(resource_count);
            if (dom_faction_resource_list(registry,
                                          info.faction_id,
                                          &resources[0],
                                          resource_count,
                                          &actual) != DOM_FACTION_OK) {
                return false;
            }
            if (actual != resource_count) {
                return false;
            }
            for (u32 r = 0u; r < resource_count; ++r) {
                append_u64_le(out, resources[r].resource_id);
                append_i64_le(out, resources[r].quantity);
            }
        }
    }

    return true;
}

static bool build_ai_sched_blob(const dom_game_runtime *rt,
                                std::vector<unsigned char> &out) {
    const dom_ai_scheduler *sched;
    dom_ai_scheduler_config cfg;
    u32 count = 0u;

    out.clear();
    sched = rt ? (const dom_ai_scheduler *)dom_game_runtime_ai_scheduler(rt) : 0;
    if (!sched) {
        return false;
    }
    std::memset(&cfg, 0, sizeof(cfg));
    cfg.struct_size = (u32)sizeof(cfg);
    cfg.struct_version = DOM_AI_SCHEDULER_CONFIG_VERSION;
    if (dom_ai_scheduler_get_config(sched, &cfg) != DOM_AI_SCHEDULER_OK) {
        return false;
    }
    if (dom_ai_scheduler_list_states(sched, 0, 0u, &count) != DOM_AI_SCHEDULER_OK) {
        return false;
    }

    append_u32_le(out, cfg.period_ticks);
    append_u32_le(out, cfg.max_ops_per_tick);
    append_u32_le(out, cfg.max_factions_per_tick);
    append_u32_le(out, cfg.enable_traces ? 1u : 0u);
    append_u32_le(out, count);

    if (count > 0u) {
        std::vector<dom_ai_faction_state> states;
        u32 actual = count;
        states.resize(count);
        if (dom_ai_scheduler_list_states(sched, &states[0], count, &actual) != DOM_AI_SCHEDULER_OK) {
            return false;
        }
        if (actual != count) {
            return false;
        }
        for (u32 i = 0u; i < count; ++i) {
            append_u64_le(out, states[i].faction_id);
            append_u64_le(out, states[i].next_decision_tick);
            append_u64_le(out, states[i].last_plan_id);
            append_u32_le(out, states[i].last_output_count);
            append_u32_le(out, states[i].last_reason_code);
            append_u32_le(out, states[i].last_budget_hit);
        }
    }

    return true;
}

static int apply_construction_blob(dom_game_runtime *rt,
                                   const unsigned char *blob,
                                   u32 len) {
    dom_construction_registry *registry;
    u32 count = 0u;
    size_t offset = 0u;
    u64 last_id = 0ull;

    if (!rt) {
        return DOM_GAME_SAVE_ERR;
    }
    registry = (dom_construction_registry *)dom_game_runtime_construction_registry(rt);
    if (!registry) {
        return DOM_GAME_SAVE_ERR;
    }
    if (!blob || len < 4u) {
        return DOM_GAME_SAVE_ERR_FORMAT;
    }
    count = read_u32_le(blob);
    if (count > 0u) {
        const size_t remaining = len - 4u;
        if ((remaining / DMSG_CONSTRUCTION_RECORD_SIZE) < count) {
            return DOM_GAME_SAVE_ERR_FORMAT;
        }
    }
    if (len != 4u + ((size_t)count * (size_t)DMSG_CONSTRUCTION_RECORD_SIZE)) {
        return DOM_GAME_SAVE_ERR_FORMAT;
    }
    if (dom_construction_registry_init(registry) != DOM_CONSTRUCTION_OK) {
        return DOM_GAME_SAVE_ERR;
    }

    offset = 4u;
    for (u32 i = 0u; i < count; ++i) {
        dom_construction_instance inst;
        u64 instance_id = read_u64_le(blob + offset);
        u32 type_id = read_u32_le(blob + offset + 8u);
        u32 orientation = read_u32_le(blob + offset + 12u);
        u64 body_id = read_u64_le(blob + offset + 16u);
        i32 step_turns = read_i32_le(blob + offset + 24u);
        i32 lat_index = read_i32_le(blob + offset + 28u);
        i32 lon_index = read_i32_le(blob + offset + 32u);
        i64 local_e = read_i64_le(blob + offset + 36u);
        i64 local_n = read_i64_le(blob + offset + 44u);
        i64 local_u = read_i64_le(blob + offset + 52u);
        i32 cell_x = read_i32_le(blob + offset + 60u);
        i32 cell_y = read_i32_le(blob + offset + 64u);

        if (instance_id == 0ull || body_id == 0ull || !construction_type_valid(type_id)) {
            return DOM_GAME_SAVE_ERR_FORMAT;
        }
        if (orientation > 3u) {
            return DOM_GAME_SAVE_ERR_FORMAT;
        }
        if (instance_id <= last_id) {
            return DOM_GAME_SAVE_ERR_FORMAT;
        }

        std::memset(&inst, 0, sizeof(inst));
        inst.instance_id = instance_id;
        inst.type_id = type_id;
        inst.body_id = body_id;
        inst.chunk_key.body_id = body_id;
        inst.chunk_key.step_turns_q16 = step_turns;
        inst.chunk_key.lat_index = lat_index;
        inst.chunk_key.lon_index = lon_index;
        inst.local_pos_m[0] = (q48_16)local_e;
        inst.local_pos_m[1] = (q48_16)local_n;
        inst.local_pos_m[2] = (q48_16)local_u;
        inst.orientation = orientation;
        inst.cell_x = cell_x;
        inst.cell_y = cell_y;

        if (dom_construction_register_instance(registry, &inst, 0) != DOM_CONSTRUCTION_OK) {
            return DOM_GAME_SAVE_ERR_FORMAT;
        }
        last_id = instance_id;
        offset += DMSG_CONSTRUCTION_RECORD_SIZE;
    }

    return DOM_GAME_SAVE_OK;
}

static int apply_station_blob(dom_game_runtime *rt,
                              const unsigned char *blob,
                              u32 len) {
    dom_station_registry *registry;
    u32 count = 0u;
    size_t offset = 0u;
    u64 last_id = 0ull;

    if (!rt) {
        return DOM_GAME_SAVE_ERR;
    }
    registry = (dom_station_registry *)dom_game_runtime_station_registry(rt);
    if (!registry) {
        return DOM_GAME_SAVE_ERR;
    }
    if (!blob || len < 4u) {
        return DOM_GAME_SAVE_ERR_FORMAT;
    }

    count = read_u32_le(blob);
    offset = 4u;
    if (dom_station_registry_init(registry) != DOM_STATION_REGISTRY_OK) {
        return DOM_GAME_SAVE_ERR;
    }

    for (u32 i = 0u; i < count; ++i) {
        dom_station_desc desc;
        u32 inv_count = 0u;
        if (offset + 28u > len) {
            return DOM_GAME_SAVE_ERR_FORMAT;
        }
        desc.station_id = read_u64_le(blob + offset + 0u);
        desc.body_id = read_u64_le(blob + offset + 8u);
        desc.frame_id = read_u64_le(blob + offset + 16u);
        inv_count = read_u32_le(blob + offset + 24u);
        offset += 28u;

        if (desc.station_id == 0ull || desc.body_id == 0ull) {
            return DOM_GAME_SAVE_ERR_FORMAT;
        }
        if (desc.station_id <= last_id) {
            return DOM_GAME_SAVE_ERR_FORMAT;
        }
        if (dom_station_register(registry, &desc) != DOM_STATION_REGISTRY_OK) {
            return DOM_GAME_SAVE_ERR_FORMAT;
        }

        if (inv_count > 0u) {
            const size_t entries_bytes = (size_t)inv_count * 16u;
            if (entries_bytes > (len - offset)) {
                return DOM_GAME_SAVE_ERR_FORMAT;
            }
            for (u32 j = 0u; j < inv_count; ++j) {
                const size_t base = offset + (size_t)j * 16u;
                dom_resource_id res_id = read_u64_le(blob + base);
                i64 qty = read_i64_le(blob + base + 8u);
                if (res_id == 0ull || qty <= 0) {
                    return DOM_GAME_SAVE_ERR_FORMAT;
                }
                if (dom_station_inventory_add(registry,
                                              desc.station_id,
                                              res_id,
                                              qty) != DOM_STATION_REGISTRY_OK) {
                    return DOM_GAME_SAVE_ERR_FORMAT;
                }
            }
            offset += entries_bytes;
        }

        last_id = desc.station_id;
    }
    if (offset != len) {
        return DOM_GAME_SAVE_ERR_FORMAT;
    }
    return DOM_GAME_SAVE_OK;
}

static int apply_route_blob(dom_game_runtime *rt,
                            const unsigned char *blob,
                            u32 len) {
    dom_route_graph *graph;
    u32 count = 0u;
    size_t offset = 0u;
    u64 last_id = 0ull;

    if (!rt) {
        return DOM_GAME_SAVE_ERR;
    }
    graph = (dom_route_graph *)dom_game_runtime_route_graph(rt);
    if (!graph) {
        return DOM_GAME_SAVE_ERR;
    }
    if (!blob || len < 4u) {
        return DOM_GAME_SAVE_ERR_FORMAT;
    }
    count = read_u32_le(blob);
    if (len != 4u + ((size_t)count * (size_t)DMSG_ROUTE_RECORD_SIZE)) {
        return DOM_GAME_SAVE_ERR_FORMAT;
    }
    if (dom_route_graph_init(graph) != DOM_ROUTE_GRAPH_OK) {
        return DOM_GAME_SAVE_ERR;
    }
    offset = 4u;
    for (u32 i = 0u; i < count; ++i) {
        dom_route_desc desc;
        desc.route_id = read_u64_le(blob + offset + 0u);
        desc.src_station_id = read_u64_le(blob + offset + 8u);
        desc.dst_station_id = read_u64_le(blob + offset + 16u);
        desc.duration_ticks = read_u64_le(blob + offset + 24u);
        desc.capacity_units = read_u64_le(blob + offset + 32u);

        if (desc.route_id == 0ull || desc.src_station_id == 0ull || desc.dst_station_id == 0ull) {
            return DOM_GAME_SAVE_ERR_FORMAT;
        }
        if (desc.route_id <= last_id) {
            return DOM_GAME_SAVE_ERR_FORMAT;
        }
        if (dom_route_graph_register(graph, &desc) != DOM_ROUTE_GRAPH_OK) {
            return DOM_GAME_SAVE_ERR_FORMAT;
        }
        last_id = desc.route_id;
        offset += DMSG_ROUTE_RECORD_SIZE;
    }
    return DOM_GAME_SAVE_OK;
}

static int apply_transfer_blob(dom_game_runtime *rt,
                               const unsigned char *blob,
                               u32 len,
                               u64 current_tick) {
    dom_transfer_scheduler *sched;
    dom_route_graph *graph;
    u32 count = 0u;
    size_t offset = 0u;
    u64 last_id = 0ull;

    if (!rt) {
        return DOM_GAME_SAVE_ERR;
    }
    sched = (dom_transfer_scheduler *)dom_game_runtime_transfer_scheduler(rt);
    graph = (dom_route_graph *)dom_game_runtime_route_graph(rt);
    if (!sched || !graph) {
        return DOM_GAME_SAVE_ERR;
    }
    if (!blob || len < 4u) {
        return DOM_GAME_SAVE_ERR_FORMAT;
    }
    count = read_u32_le(blob);
    offset = 4u;
    if (dom_transfer_scheduler_init(sched) != DOM_TRANSFER_OK) {
        return DOM_GAME_SAVE_ERR;
    }

    for (u32 i = 0u; i < count; ++i) {
        dom_transfer_id transfer_id;
        dom_route_id route_id;
        u64 start_tick;
        u64 arrival_tick;
        u32 entry_count;
        u64 total_units = 0ull;
        std::vector<dom_transfer_entry> entries;

        if (offset + 36u > len) {
            return DOM_GAME_SAVE_ERR_FORMAT;
        }
        transfer_id = read_u64_le(blob + offset + 0u);
        route_id = read_u64_le(blob + offset + 8u);
        start_tick = read_u64_le(blob + offset + 16u);
        arrival_tick = read_u64_le(blob + offset + 24u);
        entry_count = read_u32_le(blob + offset + 32u);
        offset += 36u;

        if (transfer_id == 0ull || route_id == 0ull || entry_count == 0u) {
            return DOM_GAME_SAVE_ERR_FORMAT;
        }
        if (transfer_id <= last_id) {
            return DOM_GAME_SAVE_ERR_FORMAT;
        }
        if (arrival_tick <= current_tick) {
            return DOM_GAME_SAVE_ERR_FORMAT;
        }

        {
            const size_t entry_bytes = (size_t)entry_count * 16u;
            if (entry_bytes > (len - offset)) {
                return DOM_GAME_SAVE_ERR_FORMAT;
            }
            entries.resize(entry_count);
            for (u32 j = 0u; j < entry_count; ++j) {
                const size_t base = offset + (size_t)j * 16u;
                dom_resource_id res_id = read_u64_le(blob + base);
                i64 qty = read_i64_le(blob + base + 8u);
                if (res_id == 0ull || qty <= 0) {
                    return DOM_GAME_SAVE_ERR_FORMAT;
                }
                entries[j].resource_id = res_id;
                entries[j].quantity = qty;
                if (total_units > (ULLONG_MAX - (u64)qty)) {
                    return DOM_GAME_SAVE_ERR_FORMAT;
                }
                total_units += (u64)qty;
            }
            offset += entry_bytes;
        }

        if (dom_transfer_add_loaded(sched,
                                    graph,
                                    route_id,
                                    transfer_id,
                                    start_tick,
                                    arrival_tick,
                                    entries.empty() ? (const dom_transfer_entry *)0 : &entries[0],
                                    entry_count,
                                    total_units) != DOM_TRANSFER_OK) {
            return DOM_GAME_SAVE_ERR_FORMAT;
        }
        last_id = transfer_id;
    }
    if (offset != len) {
        return DOM_GAME_SAVE_ERR_FORMAT;
    }
    return DOM_GAME_SAVE_OK;
}

static int apply_production_blob(dom_game_runtime *rt,
                                 const unsigned char *blob,
                                 u32 len) {
    dom_production *prod;
    u32 count = 0u;
    size_t offset = 0u;
    u64 last_id = 0ull;

    if (!rt) {
        return DOM_GAME_SAVE_ERR;
    }
    prod = (dom_production *)dom_game_runtime_production(rt);
    if (!prod) {
        return DOM_GAME_SAVE_ERR;
    }
    if (!blob || len < 4u) {
        return DOM_GAME_SAVE_ERR_FORMAT;
    }
    count = read_u32_le(blob);
    if (len != 4u + ((size_t)count * (size_t)DMSG_PRODUCTION_RECORD_SIZE)) {
        return DOM_GAME_SAVE_ERR_FORMAT;
    }
    if (dom_production_init(prod) != DOM_PRODUCTION_OK) {
        return DOM_GAME_SAVE_ERR;
    }
    offset = 4u;
    for (u32 i = 0u; i < count; ++i) {
        dom_production_rule_desc desc;
        desc.rule_id = read_u64_le(blob + offset + 0u);
        desc.station_id = read_u64_le(blob + offset + 8u);
        desc.resource_id = read_u64_le(blob + offset + 16u);
        desc.delta_per_period = read_i64_le(blob + offset + 24u);
        desc.period_ticks = read_u64_le(blob + offset + 32u);

        if (desc.rule_id == 0ull || desc.station_id == 0ull || desc.resource_id == 0ull) {
            return DOM_GAME_SAVE_ERR_FORMAT;
        }
        if (desc.rule_id <= last_id) {
            return DOM_GAME_SAVE_ERR_FORMAT;
        }
        if (dom_production_register(prod, &desc) != DOM_PRODUCTION_OK) {
            return DOM_GAME_SAVE_ERR_FORMAT;
        }
        last_id = desc.rule_id;
        offset += DMSG_PRODUCTION_RECORD_SIZE;
    }
    return DOM_GAME_SAVE_OK;
}

static int apply_macro_economy_scopes(dom_macro_economy *econ,
                                      u32 scope_kind,
                                      u32 count,
                                      const unsigned char *blob,
                                      u32 len,
                                      size_t *offset) {
    u64 last_scope_id = 0ull;
    if (!econ || !blob || !offset) {
        return DOM_GAME_SAVE_ERR;
    }
    for (u32 i = 0u; i < count; ++i) {
        u64 scope_id;
        u32 flags;
        u32 prod_count;
        u32 demand_count;
        u32 stock_count;
        u64 last_resource = 0ull;
        int rc;

        if (*offset + 24u > len) {
            return DOM_GAME_SAVE_ERR_FORMAT;
        }
        scope_id = read_u64_le(blob + *offset + 0u);
        flags = read_u32_le(blob + *offset + 8u);
        prod_count = read_u32_le(blob + *offset + 12u);
        demand_count = read_u32_le(blob + *offset + 16u);
        stock_count = read_u32_le(blob + *offset + 20u);
        *offset += 24u;

        if (scope_id == 0ull || scope_id <= last_scope_id) {
            return DOM_GAME_SAVE_ERR_FORMAT;
        }
        if (scope_kind == DOM_MACRO_SCOPE_SYSTEM) {
            rc = dom_macro_economy_register_system(econ, scope_id);
        } else if (scope_kind == DOM_MACRO_SCOPE_GALAXY) {
            rc = dom_macro_economy_register_galaxy(econ, scope_id);
        } else {
            return DOM_GAME_SAVE_ERR_FORMAT;
        }
        if (rc != DOM_MACRO_ECONOMY_OK) {
            return DOM_GAME_SAVE_ERR_FORMAT;
        }
        if (flags != 0u) {
            if (dom_macro_economy_flags_apply(econ, scope_kind, scope_id, flags, 0u)
                != DOM_MACRO_ECONOMY_OK) {
                return DOM_GAME_SAVE_ERR_FORMAT;
            }
        }

        last_resource = 0ull;
        for (u32 j = 0u; j < prod_count; ++j) {
            u64 resource_id;
            i64 rate;
            if (*offset + 16u > len) {
                return DOM_GAME_SAVE_ERR_FORMAT;
            }
            resource_id = read_u64_le(blob + *offset + 0u);
            rate = read_i64_le(blob + *offset + 8u);
            *offset += 16u;
            if (resource_id == 0ull || resource_id <= last_resource) {
                return DOM_GAME_SAVE_ERR_FORMAT;
            }
            last_resource = resource_id;
            if (dom_macro_economy_rate_set(econ,
                                           scope_kind,
                                           scope_id,
                                           resource_id,
                                           rate,
                                           0) != DOM_MACRO_ECONOMY_OK) {
                return DOM_GAME_SAVE_ERR_FORMAT;
            }
        }

        last_resource = 0ull;
        for (u32 j = 0u; j < demand_count; ++j) {
            u64 resource_id;
            i64 rate;
            i64 prod_rate = 0;
            i64 dem_rate = 0;
            if (*offset + 16u > len) {
                return DOM_GAME_SAVE_ERR_FORMAT;
            }
            resource_id = read_u64_le(blob + *offset + 0u);
            rate = read_i64_le(blob + *offset + 8u);
            *offset += 16u;
            if (resource_id == 0ull || resource_id <= last_resource) {
                return DOM_GAME_SAVE_ERR_FORMAT;
            }
            last_resource = resource_id;
            rc = dom_macro_economy_rate_get(econ,
                                            scope_kind,
                                            scope_id,
                                            resource_id,
                                            &prod_rate,
                                            &dem_rate);
            if (rc == DOM_MACRO_ECONOMY_NOT_FOUND) {
                prod_rate = 0;
            } else if (rc != DOM_MACRO_ECONOMY_OK) {
                return DOM_GAME_SAVE_ERR_FORMAT;
            }
            if (dom_macro_economy_rate_set(econ,
                                           scope_kind,
                                           scope_id,
                                           resource_id,
                                           prod_rate,
                                           rate) != DOM_MACRO_ECONOMY_OK) {
                return DOM_GAME_SAVE_ERR_FORMAT;
            }
        }

        last_resource = 0ull;
        for (u32 j = 0u; j < stock_count; ++j) {
            u64 resource_id;
            i64 quantity;
            if (*offset + 16u > len) {
                return DOM_GAME_SAVE_ERR_FORMAT;
            }
            resource_id = read_u64_le(blob + *offset + 0u);
            quantity = read_i64_le(blob + *offset + 8u);
            *offset += 16u;
            if (resource_id == 0ull || resource_id <= last_resource) {
                return DOM_GAME_SAVE_ERR_FORMAT;
            }
            last_resource = resource_id;
            if (dom_macro_economy_stockpile_set(econ,
                                                scope_kind,
                                                scope_id,
                                                resource_id,
                                                quantity) != DOM_MACRO_ECONOMY_OK) {
                return DOM_GAME_SAVE_ERR_FORMAT;
            }
        }

        last_scope_id = scope_id;
    }
    return DOM_GAME_SAVE_OK;
}

static int apply_macro_economy_blob(dom_game_runtime *rt,
                                    const unsigned char *blob,
                                    u32 len) {
    dom_macro_economy *econ;
    size_t offset = 0u;
    u32 system_count = 0u;
    u32 galaxy_count = 0u;
    int rc;

    if (!rt) {
        return DOM_GAME_SAVE_ERR;
    }
    econ = (dom_macro_economy *)dom_game_runtime_macro_economy(rt);
    if (!econ) {
        return DOM_GAME_SAVE_ERR;
    }
    if (!blob || len < 8u) {
        return DOM_GAME_SAVE_ERR_FORMAT;
    }
    if (dom_macro_economy_init(econ) != DOM_MACRO_ECONOMY_OK) {
        return DOM_GAME_SAVE_ERR;
    }
    system_count = read_u32_le(blob + offset);
    offset += 4u;
    rc = apply_macro_economy_scopes(econ,
                                    DOM_MACRO_SCOPE_SYSTEM,
                                    system_count,
                                    blob,
                                    len,
                                    &offset);
    if (rc != DOM_GAME_SAVE_OK) {
        return rc;
    }
    if (offset + 4u > len) {
        return DOM_GAME_SAVE_ERR_FORMAT;
    }
    galaxy_count = read_u32_le(blob + offset);
    offset += 4u;
    rc = apply_macro_economy_scopes(econ,
                                    DOM_MACRO_SCOPE_GALAXY,
                                    galaxy_count,
                                    blob,
                                    len,
                                    &offset);
    if (rc != DOM_GAME_SAVE_OK) {
        return rc;
    }
    if (offset != len) {
        return DOM_GAME_SAVE_ERR_FORMAT;
    }
    return DOM_GAME_SAVE_OK;
}

static int apply_macro_events_blob(dom_game_runtime *rt,
                                   const unsigned char *blob,
                                   u32 len,
                                   u64 current_tick) {
    dom_macro_events *events;
    size_t offset = 0u;
    u32 count = 0u;
    u64 last_tick = 0ull;
    u64 last_event_id = 0ull;
    int has_prev = 0;

    if (!rt) {
        return DOM_GAME_SAVE_ERR;
    }
    events = (dom_macro_events *)dom_game_runtime_macro_events(rt);
    if (!events) {
        return DOM_GAME_SAVE_ERR;
    }
    if (!blob || len < 4u) {
        return DOM_GAME_SAVE_ERR_FORMAT;
    }
    if (dom_macro_events_init(events) != DOM_MACRO_EVENTS_OK) {
        return DOM_GAME_SAVE_ERR;
    }
    count = read_u32_le(blob);
    offset = 4u;
    for (u32 i = 0u; i < count; ++i) {
        dom_macro_event_desc desc;
        std::vector<dom_macro_event_effect> effects;
        u64 event_id;
        u32 scope_kind;
        u64 scope_id;
        u64 trigger_tick;
        u32 effect_count;

        if (offset + 32u > len) {
            return DOM_GAME_SAVE_ERR_FORMAT;
        }
        event_id = read_u64_le(blob + offset + 0u);
        scope_kind = read_u32_le(blob + offset + 8u);
        scope_id = read_u64_le(blob + offset + 12u);
        trigger_tick = read_u64_le(blob + offset + 20u);
        effect_count = read_u32_le(blob + offset + 28u);
        offset += 32u;

        if (event_id == 0ull || scope_id == 0ull) {
            return DOM_GAME_SAVE_ERR_FORMAT;
        }
        if (scope_kind != DOM_MACRO_SCOPE_SYSTEM &&
            scope_kind != DOM_MACRO_SCOPE_GALAXY) {
            return DOM_GAME_SAVE_ERR_FORMAT;
        }
        if (has_prev) {
            if (trigger_tick < last_tick) {
                return DOM_GAME_SAVE_ERR_FORMAT;
            }
            if (trigger_tick == last_tick && event_id <= last_event_id) {
                return DOM_GAME_SAVE_ERR_FORMAT;
            }
        }

        if (effect_count > 0u) {
            effects.resize(effect_count);
            for (u32 j = 0u; j < effect_count; ++j) {
                dom_macro_event_effect effect;
                if (offset + 32u > len) {
                    return DOM_GAME_SAVE_ERR_FORMAT;
                }
                effect.resource_id = read_u64_le(blob + offset + 0u);
                effect.production_delta = read_i64_le(blob + offset + 8u);
                effect.demand_delta = read_i64_le(blob + offset + 16u);
                effect.flags_set = read_u32_le(blob + offset + 24u);
                effect.flags_clear = read_u32_le(blob + offset + 28u);
                offset += 32u;
                if (effect.resource_id == 0ull) {
                    return DOM_GAME_SAVE_ERR_FORMAT;
                }
                effects[j] = effect;
            }
        }

        std::memset(&desc, 0, sizeof(desc));
        desc.event_id = event_id;
        desc.scope_kind = scope_kind;
        desc.scope_id = scope_id;
        desc.trigger_tick = trigger_tick;
        desc.effect_count = effect_count;
        desc.effects = (effect_count > 0u) ? &effects[0] : (const dom_macro_event_effect *)0;
        if (dom_macro_events_schedule(events, &desc) != DOM_MACRO_EVENTS_OK) {
            return DOM_GAME_SAVE_ERR_FORMAT;
        }

        last_tick = trigger_tick;
        last_event_id = event_id;
        has_prev = 1;
    }
    if (offset != len) {
        return DOM_GAME_SAVE_ERR_FORMAT;
    }
    if (dom_macro_events_seek(events, current_tick) != DOM_MACRO_EVENTS_OK) {
        return DOM_GAME_SAVE_ERR;
    }
    return DOM_GAME_SAVE_OK;
}

static int apply_factions_blob(dom_game_runtime *rt,
                               const unsigned char *blob,
                               u32 len) {
    dom_faction_registry *registry;
    size_t offset = 0u;
    u32 count = 0u;
    u64 last_faction_id = 0ull;

    if (!rt) {
        return DOM_GAME_SAVE_ERR;
    }
    registry = (dom_faction_registry *)dom_game_runtime_faction_registry(rt);
    if (!registry) {
        return DOM_GAME_SAVE_ERR;
    }
    if (!blob || len < 4u) {
        return DOM_GAME_SAVE_ERR_FORMAT;
    }
    if (dom_faction_registry_init(registry) != DOM_FACTION_OK) {
        return DOM_GAME_SAVE_ERR;
    }

    count = read_u32_le(blob + offset);
    offset += 4u;
    for (u32 i = 0u; i < count; ++i) {
        dom_faction_desc desc;
        std::vector<u64> nodes;
        std::vector<dom_faction_resource_delta> deltas;
        u32 known_count;
        u32 resource_count;
        u64 last_node = 0ull;
        u64 last_resource = 0ull;

        if (offset + 44u > len) {
            return DOM_GAME_SAVE_ERR_FORMAT;
        }
        desc.faction_id = read_u64_le(blob + offset + 0u);
        desc.home_scope_kind = read_u32_le(blob + offset + 8u);
        desc.home_scope_id = read_u64_le(blob + offset + 12u);
        desc.policy_kind = read_u32_le(blob + offset + 20u);
        desc.policy_flags = read_u32_le(blob + offset + 24u);
        desc.ai_seed = read_u64_le(blob + offset + 28u);
        known_count = read_u32_le(blob + offset + 36u);
        resource_count = read_u32_le(blob + offset + 40u);
        offset += 44u;

        if (desc.faction_id == 0ull || desc.home_scope_id == 0ull || desc.ai_seed == 0ull) {
            return DOM_GAME_SAVE_ERR_FORMAT;
        }
        if (desc.faction_id <= last_faction_id) {
            return DOM_GAME_SAVE_ERR_FORMAT;
        }
        last_faction_id = desc.faction_id;

        if (known_count > 0u) {
            if (offset + (size_t)known_count * 8u > len) {
                return DOM_GAME_SAVE_ERR_FORMAT;
            }
            nodes.resize(known_count);
            for (u32 n = 0u; n < known_count; ++n) {
                u64 node_id = read_u64_le(blob + offset);
                offset += 8u;
                if (node_id == 0ull || node_id <= last_node) {
                    return DOM_GAME_SAVE_ERR_FORMAT;
                }
                last_node = node_id;
                nodes[n] = node_id;
            }
        }

        if (resource_count > 0u) {
            if (offset + (size_t)resource_count * 16u > len) {
                return DOM_GAME_SAVE_ERR_FORMAT;
            }
            deltas.resize(resource_count);
            for (u32 r = 0u; r < resource_count; ++r) {
                dom_faction_resource_delta delta;
                delta.resource_id = read_u64_le(blob + offset + 0u);
                delta.delta = read_i64_le(blob + offset + 8u);
                offset += 16u;
                if (delta.resource_id == 0ull || delta.resource_id <= last_resource) {
                    return DOM_GAME_SAVE_ERR_FORMAT;
                }
                if (delta.delta < 0) {
                    return DOM_GAME_SAVE_ERR_FORMAT;
                }
                last_resource = delta.resource_id;
                deltas[r] = delta;
            }
        }

        desc.known_nodes = nodes.empty() ? 0 : &nodes[0];
        desc.known_node_count = (u32)nodes.size();
        if (dom_faction_register(registry, &desc) != DOM_FACTION_OK) {
            return DOM_GAME_SAVE_ERR_FORMAT;
        }
        if (!deltas.empty()) {
            if (dom_faction_update_resources(registry,
                                             desc.faction_id,
                                             &deltas[0],
                                             (u32)deltas.size()) != DOM_FACTION_OK) {
                return DOM_GAME_SAVE_ERR_FORMAT;
            }
        }
    }

    if (offset != len) {
        return DOM_GAME_SAVE_ERR_FORMAT;
    }
    return DOM_GAME_SAVE_OK;
}

static int apply_ai_sched_blob(dom_game_runtime *rt,
                               const unsigned char *blob,
                               u32 len) {
    dom_ai_scheduler *sched;
    dom_ai_scheduler_config cfg;
    size_t offset = 0u;
    u32 state_count = 0u;
    u64 last_faction_id = 0ull;

    if (!rt) {
        return DOM_GAME_SAVE_ERR;
    }
    sched = (dom_ai_scheduler *)dom_game_runtime_ai_scheduler(rt);
    if (!sched) {
        return DOM_GAME_SAVE_ERR;
    }
    if (!blob || len < 20u) {
        return DOM_GAME_SAVE_ERR_FORMAT;
    }

    std::memset(&cfg, 0, sizeof(cfg));
    cfg.struct_size = (u32)sizeof(cfg);
    cfg.struct_version = DOM_AI_SCHEDULER_CONFIG_VERSION;
    cfg.period_ticks = read_u32_le(blob + offset);
    cfg.max_ops_per_tick = read_u32_le(blob + offset + 4u);
    cfg.max_factions_per_tick = read_u32_le(blob + offset + 8u);
    cfg.enable_traces = read_u32_le(blob + offset + 12u);
    state_count = read_u32_le(blob + offset + 16u);
    offset += 20u;

    if (cfg.period_ticks == 0u || cfg.max_ops_per_tick == 0u ||
        cfg.max_factions_per_tick == 0u) {
        return DOM_GAME_SAVE_ERR_FORMAT;
    }
    if (offset + (size_t)state_count * 36u > len) {
        return DOM_GAME_SAVE_ERR_FORMAT;
    }

    if (dom_ai_scheduler_init(sched, &cfg) != DOM_AI_SCHEDULER_OK) {
        return DOM_GAME_SAVE_ERR;
    }

    if (state_count > 0u) {
        std::vector<dom_ai_faction_state> states;
        states.resize(state_count);
        for (u32 i = 0u; i < state_count; ++i) {
            dom_ai_faction_state state;
            state.faction_id = read_u64_le(blob + offset + 0u);
            state.next_decision_tick = read_u64_le(blob + offset + 8u);
            state.last_plan_id = read_u64_le(blob + offset + 16u);
            state.last_output_count = read_u32_le(blob + offset + 24u);
            state.last_reason_code = read_u32_le(blob + offset + 28u);
            state.last_budget_hit = read_u32_le(blob + offset + 32u);
            offset += 36u;

            if (state.faction_id == 0ull || state.faction_id <= last_faction_id) {
                return DOM_GAME_SAVE_ERR_FORMAT;
            }
            last_faction_id = state.faction_id;
            states[i] = state;
        }
        if (dom_ai_scheduler_load_states(sched, &states[0], state_count) != DOM_AI_SCHEDULER_OK) {
            return DOM_GAME_SAVE_ERR_FORMAT;
        }
    }

    if (offset != len) {
        return DOM_GAME_SAVE_ERR_FORMAT;
    }
    return DOM_GAME_SAVE_OK;
}

static int apply_media_bindings_blob(dom_game_runtime *rt,
                                     const unsigned char *blob,
                                     u32 len) {
    dom_media_registry *registry;
    dom::core_tlv::TlvReader reader(blob, (size_t)len);
    dom::core_tlv::TlvRecord rec;
    u32 schema_version = 0u;

    if (!rt) {
        return DOM_GAME_SAVE_ERR;
    }
    registry = (dom_media_registry *)dom_game_runtime_media_registry(rt);
    if (!registry) {
        return DOM_GAME_SAVE_ERR;
    }
    if (!blob || len == 0u) {
        return DOM_GAME_SAVE_OK;
    }

    while (reader.next(rec)) {
        if (rec.tag == dom::core_tlv::CORE_TLV_TAG_SCHEMA_VERSION) {
            (void)dom::core_tlv::tlv_read_u32_le(rec.payload, rec.len, schema_version);
            continue;
        }
        if (rec.tag != DMSG_MEDIA_BINDINGS_TAG_BINDING) {
            continue;
        }
        {
            dom::core_tlv::TlvReader br(rec.payload, (size_t)rec.len);
            dom::core_tlv::TlvRecord brec;
            dom_body_id body_id = 0ull;
            u32 kind = 0u;
            const unsigned char *provider = 0;
            u32 provider_len = 0u;
            const unsigned char *params = 0;
            u32 params_len = 0u;
            int have_body = 0;
            int have_kind = 0;
            int have_provider = 0;

            while (br.next(brec)) {
                switch (brec.tag) {
                case DMSG_MEDIA_BINDINGS_TAG_BODY_ID:
                    if (brec.len == 8u) {
                        body_id = dtlv_le_read_u64(brec.payload);
                        have_body = 1;
                    }
                    break;
                case DMSG_MEDIA_BINDINGS_TAG_KIND:
                    if (brec.len == 4u) {
                        kind = dtlv_le_read_u32(brec.payload);
                        have_kind = 1;
                    }
                    break;
                case DMSG_MEDIA_BINDINGS_TAG_PROVIDER_ID:
                    provider = brec.payload;
                    provider_len = brec.len;
                    have_provider = 1;
                    break;
                case DMSG_MEDIA_BINDINGS_TAG_PARAMS:
                    params = brec.payload;
                    params_len = brec.len;
                    break;
                default:
                    break;
                }
            }

            if (!have_body || !have_kind || !have_provider || body_id == 0ull) {
                return DOM_GAME_SAVE_ERR_FORMAT;
            }
            if (provider_len == 0u || provider_len >= DOM_MEDIA_PROVIDER_ID_MAX) {
                return DOM_GAME_SAVE_ERR_FORMAT;
            }

            dom_media_binding binding;
            std::memset(&binding, 0, sizeof(binding));
            binding.body_id = body_id;
            binding.kind = kind;
            std::memcpy(binding.provider_id, provider, provider_len);
            binding.provider_id_len = provider_len;
            binding.params = params;
            binding.params_len = params_len;
            if (dom_media_registry_set_binding(registry, &binding) != DOM_MEDIA_OK) {
                return DOM_GAME_SAVE_ERR_FORMAT;
            }
        }
    }

    if (schema_version != DMSG_MEDIA_BINDINGS_SCHEMA_VERSION) {
        return DOM_GAME_SAVE_ERR_FORMAT;
    }
    return DOM_GAME_SAVE_OK;
}

static int apply_weather_bindings_blob(dom_game_runtime *rt,
                                       const unsigned char *blob,
                                       u32 len) {
    dom_weather_registry *registry;
    dom::core_tlv::TlvReader reader(blob, (size_t)len);
    dom::core_tlv::TlvRecord rec;
    u32 schema_version = 0u;

    if (!rt) {
        return DOM_GAME_SAVE_ERR;
    }
    registry = (dom_weather_registry *)dom_game_runtime_weather_registry(rt);
    if (!registry) {
        return DOM_GAME_SAVE_ERR;
    }
    if (!blob || len == 0u) {
        return DOM_GAME_SAVE_OK;
    }

    while (reader.next(rec)) {
        if (rec.tag == dom::core_tlv::CORE_TLV_TAG_SCHEMA_VERSION) {
            (void)dom::core_tlv::tlv_read_u32_le(rec.payload, rec.len, schema_version);
            continue;
        }
        if (rec.tag != DMSG_WEATHER_BINDINGS_TAG_BINDING) {
            continue;
        }
        {
            dom::core_tlv::TlvReader br(rec.payload, (size_t)rec.len);
            dom::core_tlv::TlvRecord brec;
            dom_body_id body_id = 0ull;
            const unsigned char *provider = 0;
            u32 provider_len = 0u;
            const unsigned char *params = 0;
            u32 params_len = 0u;
            int have_body = 0;
            int have_provider = 0;

            while (br.next(brec)) {
                switch (brec.tag) {
                case DMSG_WEATHER_BINDINGS_TAG_BODY_ID:
                    if (brec.len == 8u) {
                        body_id = dtlv_le_read_u64(brec.payload);
                        have_body = 1;
                    }
                    break;
                case DMSG_WEATHER_BINDINGS_TAG_PROVIDER_ID:
                    provider = brec.payload;
                    provider_len = brec.len;
                    have_provider = 1;
                    break;
                case DMSG_WEATHER_BINDINGS_TAG_PARAMS:
                    params = brec.payload;
                    params_len = brec.len;
                    break;
                default:
                    break;
                }
            }

            if (!have_body || !have_provider || body_id == 0ull) {
                return DOM_GAME_SAVE_ERR_FORMAT;
            }
            if (provider_len == 0u || provider_len >= DOM_WEATHER_PROVIDER_ID_MAX) {
                return DOM_GAME_SAVE_ERR_FORMAT;
            }

            dom_weather_binding binding;
            std::memset(&binding, 0, sizeof(binding));
            binding.body_id = body_id;
            std::memcpy(binding.provider_id, provider, provider_len);
            binding.provider_id_len = provider_len;
            binding.params = params;
            binding.params_len = params_len;
            if (dom_weather_registry_set_binding(registry, &binding) != DOM_WEATHER_OK) {
                return DOM_GAME_SAVE_ERR_FORMAT;
            }
        }
    }

    if (schema_version != DMSG_WEATHER_BINDINGS_SCHEMA_VERSION) {
        return DOM_GAME_SAVE_ERR_FORMAT;
    }
    return DOM_GAME_SAVE_OK;
}

static int apply_aero_props_blob(dom_game_runtime *rt,
                                 const unsigned char *blob,
                                 u32 len) {
    dom_lane_scheduler *sched;
    u32 count;
    size_t offset;

    if (!rt) {
        return DOM_GAME_SAVE_ERR;
    }
    sched = (dom_lane_scheduler *)dom_game_runtime_lane_scheduler(rt);
    if (!sched) {
        return DOM_GAME_SAVE_ERR;
    }
    if (!blob || len < 4u) {
        return DOM_GAME_SAVE_ERR_FORMAT;
    }
    count = read_u32_le(blob);
    if (len != 4u + ((size_t)count * (size_t)DMSG_AERO_PROPS_RECORD_SIZE)) {
        return DOM_GAME_SAVE_ERR_FORMAT;
    }
    offset = 4u;
    for (u32 i = 0u; i < count; ++i) {
        dom_vehicle_aero_props props;
        u64 vessel_id = read_u64_le(blob + offset + 0u);
        if (vessel_id == 0ull) {
            return DOM_GAME_SAVE_ERR_FORMAT;
        }
        props.mass_kg_q16 = read_i32_le(blob + offset + 8u);
        props.drag_area_cda_q16 = read_i32_le(blob + offset + 12u);
        props.heat_coeff_q16 = read_i32_le(blob + offset + 16u);
        props.max_heat_q16 = read_i32_le(blob + offset + 20u);
        props.has_max_heat = read_u32_le(blob + offset + 24u) ? 1u : 0u;

        if (dom_vehicle_aero_props_validate(&props) != DOM_VEHICLE_AERO_OK) {
            return DOM_GAME_SAVE_ERR_FORMAT;
        }
        if (dom_lane_scheduler_set_aero_props(sched, vessel_id, &props) != DOM_LANE_OK) {
            return DOM_GAME_SAVE_ERR_FORMAT;
        }
        offset += DMSG_AERO_PROPS_RECORD_SIZE;
    }
    return DOM_GAME_SAVE_OK;
}

static int apply_aero_state_blob(dom_game_runtime *rt,
                                 const unsigned char *blob,
                                 u32 len) {
    dom_lane_scheduler *sched;
    u32 count;
    size_t offset;

    if (!rt) {
        return DOM_GAME_SAVE_ERR;
    }
    sched = (dom_lane_scheduler *)dom_game_runtime_lane_scheduler(rt);
    if (!sched) {
        return DOM_GAME_SAVE_ERR;
    }
    if (!blob || len < 4u) {
        return DOM_GAME_SAVE_ERR_FORMAT;
    }
    count = read_u32_le(blob);
    if (len != 4u + ((size_t)count * (size_t)DMSG_AERO_STATE_RECORD_SIZE)) {
        return DOM_GAME_SAVE_ERR_FORMAT;
    }
    offset = 4u;
    for (u32 i = 0u; i < count; ++i) {
        dom_vehicle_aero_state state;
        u64 vessel_id = read_u64_le(blob + offset + 0u);
        if (vessel_id == 0ull) {
            return DOM_GAME_SAVE_ERR_FORMAT;
        }
        state.heat_accum_q16 = read_i32_le(blob + offset + 8u);
        state.last_heating_rate_q16 = read_i32_le(blob + offset + 12u);
        state.last_drag_accel_q16 = read_i32_le(blob + offset + 16u);

        if (dom_lane_scheduler_set_aero_state(sched, vessel_id, &state) != DOM_LANE_OK) {
            return DOM_GAME_SAVE_ERR_FORMAT;
        }
        offset += DMSG_AERO_STATE_RECORD_SIZE;
    }
    return DOM_GAME_SAVE_OK;
}

static int parse_dmsg(const unsigned char *data, size_t len, dom_game_save_desc *out_desc) {
    u32 version;
    u32 endian;
    u32 ups;
    u64 tick_index;
    u64 seed;
    u32 feature_epoch;
    u32 content_len;
    size_t offset;
    size_t content_offset;

    const unsigned char *core_ptr = (const unsigned char *)0;
    u32 core_len = 0u;
    u32 core_version = 0u;
    const unsigned char *orbit_ptr = (const unsigned char *)0;
    u32 orbit_len = 0u;
    u32 orbit_version = 0u;
    int has_orbit = 0;

    const unsigned char *surface_ptr = (const unsigned char *)0;
    u32 surface_len = 0u;
    u32 surface_version = 0u;
    int has_surface = 0;

    const unsigned char *media_bindings_ptr = (const unsigned char *)0;
    u32 media_bindings_len = 0u;
    u32 media_bindings_version = 0u;
    int has_media_bindings = 0;

    const unsigned char *weather_bindings_ptr = (const unsigned char *)0;
    u32 weather_bindings_len = 0u;
    u32 weather_bindings_version = 0u;
    int has_weather_bindings = 0;

    const unsigned char *aero_props_ptr = (const unsigned char *)0;
    u32 aero_props_len = 0u;
    u32 aero_props_version = 0u;
    int has_aero_props = 0;

    const unsigned char *aero_state_ptr = (const unsigned char *)0;
    u32 aero_state_len = 0u;
    u32 aero_state_version = 0u;
    int has_aero_state = 0;

    const unsigned char *construction_ptr = (const unsigned char *)0;
    u32 construction_len = 0u;
    u32 construction_version = 0u;
    int has_construction = 0;

    const unsigned char *stations_ptr = (const unsigned char *)0;
    u32 stations_len = 0u;
    u32 stations_version = 0u;
    int has_stations = 0;

    const unsigned char *routes_ptr = (const unsigned char *)0;
    u32 routes_len = 0u;
    u32 routes_version = 0u;
    int has_routes = 0;

    const unsigned char *transfers_ptr = (const unsigned char *)0;
    u32 transfers_len = 0u;
    u32 transfers_version = 0u;
    int has_transfers = 0;

    const unsigned char *production_ptr = (const unsigned char *)0;
    u32 production_len = 0u;
    u32 production_version = 0u;
    int has_production = 0;

    const unsigned char *macro_economy_ptr = (const unsigned char *)0;
    u32 macro_economy_len = 0u;
    u32 macro_economy_version = 0u;
    int has_macro_economy = 0;

    const unsigned char *macro_events_ptr = (const unsigned char *)0;
    u32 macro_events_len = 0u;
    u32 macro_events_version = 0u;
    int has_macro_events = 0;

    const unsigned char *factions_ptr = (const unsigned char *)0;
    u32 factions_len = 0u;
    u32 factions_version = 0u;
    int has_factions = 0;

    const unsigned char *ai_sched_ptr = (const unsigned char *)0;
    u32 ai_sched_len = 0u;
    u32 ai_sched_version = 0u;
    int has_ai_sched = 0;

    const char *instance_id = (const char *)0;
    u32 instance_id_len = 0u;
    u64 run_id_val = 0ull;
    const unsigned char *manifest_hash = (const unsigned char *)0;
    u32 manifest_hash_len = 0u;
    u64 content_hash = 0ull;
    int has_content_hash = 0;
    int has_identity = 0;

    u32 rng_state = 0u;
    u32 rng_version = 0u;
    int has_rng = 0;

    if (!data || !out_desc) {
        return DOM_GAME_SAVE_ERR;
    }
    if (len < 36u) {
        return DOM_GAME_SAVE_ERR_FORMAT;
    }
    if (std::memcmp(data, "DMSG", 4u) != 0) {
        return DOM_GAME_SAVE_ERR_FORMAT;
    }

    version = read_u32_le(data + 4u);
    if (version != DMSG_VERSION) {
        return DOM_GAME_SAVE_ERR_MIGRATION;
    }
    endian = read_u32_le(data + 8u);
    if (endian != DMSG_ENDIAN) {
        return DOM_GAME_SAVE_ERR_FORMAT;
    }

    ups = read_u32_le(data + 12u);
    tick_index = read_u64_le(data + 16u);
    seed = read_u64_le(data + 24u);
    feature_epoch = dom::dom_feature_epoch_current();

    if (version >= 3u) {
        if (len < 40u) {
            return DOM_GAME_SAVE_ERR_FORMAT;
        }
        feature_epoch = read_u32_le(data + 32u);
        if (feature_epoch == 0u) {
            return DOM_GAME_SAVE_ERR_FORMAT;
        }
        if (!dom::dom_feature_epoch_supported(feature_epoch)) {
            return DOM_GAME_SAVE_ERR_MIGRATION;
        }
        content_len = read_u32_le(data + 36u);
        content_offset = 40u;
    } else {
        content_len = read_u32_le(data + 32u);
        content_offset = 36u;
    }

    offset = content_offset;
    if ((size_t)content_len > len - offset) {
        return DOM_GAME_SAVE_ERR_FORMAT;
    }
    offset += (size_t)content_len;

    while (offset < len) {
        const unsigned char *tag;
        u32 chunk_version;
        u32 chunk_size;
        if (offset + 12u > len) {
            return DOM_GAME_SAVE_ERR_FORMAT;
        }
        tag = data + offset;
        chunk_version = read_u32_le(data + offset + 4u);
        chunk_size = read_u32_le(data + offset + 8u);
        offset += 12u;
        if ((size_t)chunk_size > len - offset) {
            return DOM_GAME_SAVE_ERR_FORMAT;
        }

        if (std::memcmp(tag, "CORE", 4u) == 0) {
            if (chunk_version > DMSG_CORE_VERSION) {
                return DOM_GAME_SAVE_ERR_MIGRATION;
            }
            if (chunk_version != DMSG_CORE_VERSION || chunk_size == 0u || core_ptr) {
                return DOM_GAME_SAVE_ERR_FORMAT;
            }
            core_ptr = data + offset;
            core_len = chunk_size;
            core_version = chunk_version;
        } else if (std::memcmp(tag, "ORBT", 4u) == 0) {
            if (chunk_version > DMSG_ORBIT_VERSION) {
                return DOM_GAME_SAVE_ERR_MIGRATION;
            }
            if (chunk_version != DMSG_ORBIT_VERSION || has_orbit) {
                return DOM_GAME_SAVE_ERR_FORMAT;
            }
            orbit_ptr = data + offset;
            orbit_len = chunk_size;
            orbit_version = chunk_version;
            has_orbit = 1;
        } else if (std::memcmp(tag, "SOVR", 4u) == 0) {
            if (chunk_version > DMSG_SURFACE_VERSION) {
                return DOM_GAME_SAVE_ERR_MIGRATION;
            }
            if (chunk_version != DMSG_SURFACE_VERSION || has_surface) {
                return DOM_GAME_SAVE_ERR_FORMAT;
            }
            surface_ptr = data + offset;
            surface_len = chunk_size;
            surface_version = chunk_version;
            has_surface = 1;
        } else if (std::memcmp(tag, "MEDI", 4u) == 0) {
            if (chunk_version > DMSG_MEDIA_BINDINGS_VERSION) {
                return DOM_GAME_SAVE_ERR_MIGRATION;
            }
            if (chunk_version != DMSG_MEDIA_BINDINGS_VERSION || has_media_bindings) {
                return DOM_GAME_SAVE_ERR_FORMAT;
            }
            media_bindings_ptr = data + offset;
            media_bindings_len = chunk_size;
            media_bindings_version = chunk_version;
            has_media_bindings = 1;
        } else if (std::memcmp(tag, "WEAT", 4u) == 0) {
            if (chunk_version > DMSG_WEATHER_BINDINGS_VERSION) {
                return DOM_GAME_SAVE_ERR_MIGRATION;
            }
            if (chunk_version != DMSG_WEATHER_BINDINGS_VERSION || has_weather_bindings) {
                return DOM_GAME_SAVE_ERR_FORMAT;
            }
            weather_bindings_ptr = data + offset;
            weather_bindings_len = chunk_size;
            weather_bindings_version = chunk_version;
            has_weather_bindings = 1;
        } else if (std::memcmp(tag, "AERP", 4u) == 0) {
            if (chunk_version > DMSG_AERO_PROPS_VERSION) {
                return DOM_GAME_SAVE_ERR_MIGRATION;
            }
            if (chunk_version != DMSG_AERO_PROPS_VERSION || has_aero_props) {
                return DOM_GAME_SAVE_ERR_FORMAT;
            }
            aero_props_ptr = data + offset;
            aero_props_len = chunk_size;
            aero_props_version = chunk_version;
            has_aero_props = 1;
        } else if (std::memcmp(tag, "AERS", 4u) == 0) {
            if (chunk_version > DMSG_AERO_STATE_VERSION) {
                return DOM_GAME_SAVE_ERR_MIGRATION;
            }
            if (chunk_version != DMSG_AERO_STATE_VERSION || has_aero_state) {
                return DOM_GAME_SAVE_ERR_FORMAT;
            }
            aero_state_ptr = data + offset;
            aero_state_len = chunk_size;
            aero_state_version = chunk_version;
            has_aero_state = 1;
        } else if (std::memcmp(tag, "CNST", 4u) == 0) {
            if (chunk_version > DMSG_CONSTRUCTION_VERSION) {
                return DOM_GAME_SAVE_ERR_MIGRATION;
            }
            if (chunk_version != DMSG_CONSTRUCTION_VERSION || has_construction) {
                return DOM_GAME_SAVE_ERR_FORMAT;
            }
            construction_ptr = data + offset;
            construction_len = chunk_size;
            construction_version = chunk_version;
            has_construction = 1;
        } else if (std::memcmp(tag, "STAT", 4u) == 0) {
            if (chunk_version > DMSG_STATIONS_VERSION) {
                return DOM_GAME_SAVE_ERR_MIGRATION;
            }
            if (chunk_version != DMSG_STATIONS_VERSION || has_stations) {
                return DOM_GAME_SAVE_ERR_FORMAT;
            }
            stations_ptr = data + offset;
            stations_len = chunk_size;
            stations_version = chunk_version;
            has_stations = 1;
        } else if (std::memcmp(tag, "ROUT", 4u) == 0) {
            if (chunk_version > DMSG_ROUTES_VERSION) {
                return DOM_GAME_SAVE_ERR_MIGRATION;
            }
            if (chunk_version != DMSG_ROUTES_VERSION || has_routes) {
                return DOM_GAME_SAVE_ERR_FORMAT;
            }
            routes_ptr = data + offset;
            routes_len = chunk_size;
            routes_version = chunk_version;
            has_routes = 1;
        } else if (std::memcmp(tag, "TRAN", 4u) == 0) {
            if (chunk_version > DMSG_TRANSFERS_VERSION) {
                return DOM_GAME_SAVE_ERR_MIGRATION;
            }
            if (chunk_version != DMSG_TRANSFERS_VERSION || has_transfers) {
                return DOM_GAME_SAVE_ERR_FORMAT;
            }
            transfers_ptr = data + offset;
            transfers_len = chunk_size;
            transfers_version = chunk_version;
            has_transfers = 1;
        } else if (std::memcmp(tag, "PROD", 4u) == 0) {
            if (chunk_version > DMSG_PRODUCTION_VERSION) {
                return DOM_GAME_SAVE_ERR_MIGRATION;
            }
            if (chunk_version != DMSG_PRODUCTION_VERSION || has_production) {
                return DOM_GAME_SAVE_ERR_FORMAT;
            }
            production_ptr = data + offset;
            production_len = chunk_size;
            production_version = chunk_version;
            has_production = 1;
        } else if (std::memcmp(tag, "MECO", 4u) == 0) {
            if (chunk_version > DMSG_MACRO_ECONOMY_VERSION) {
                return DOM_GAME_SAVE_ERR_MIGRATION;
            }
            if (chunk_version != DMSG_MACRO_ECONOMY_VERSION || has_macro_economy) {
                return DOM_GAME_SAVE_ERR_FORMAT;
            }
            macro_economy_ptr = data + offset;
            macro_economy_len = chunk_size;
            macro_economy_version = chunk_version;
            has_macro_economy = 1;
        } else if (std::memcmp(tag, "MEVT", 4u) == 0) {
            if (chunk_version > DMSG_MACRO_EVENTS_VERSION) {
                return DOM_GAME_SAVE_ERR_MIGRATION;
            }
            if (chunk_version != DMSG_MACRO_EVENTS_VERSION || has_macro_events) {
                return DOM_GAME_SAVE_ERR_FORMAT;
            }
            macro_events_ptr = data + offset;
            macro_events_len = chunk_size;
            macro_events_version = chunk_version;
            has_macro_events = 1;
        } else if (std::memcmp(tag, "FACT", 4u) == 0) {
            if (chunk_version > DMSG_FACTIONS_VERSION) {
                return DOM_GAME_SAVE_ERR_MIGRATION;
            }
            if (chunk_version != DMSG_FACTIONS_VERSION || has_factions) {
                return DOM_GAME_SAVE_ERR_FORMAT;
            }
            factions_ptr = data + offset;
            factions_len = chunk_size;
            factions_version = chunk_version;
            has_factions = 1;
        } else if (std::memcmp(tag, "AISC", 4u) == 0) {
            if (chunk_version > DMSG_AI_SCHED_VERSION) {
                return DOM_GAME_SAVE_ERR_MIGRATION;
            }
            if (chunk_version != DMSG_AI_SCHED_VERSION || has_ai_sched) {
                return DOM_GAME_SAVE_ERR_FORMAT;
            }
            ai_sched_ptr = data + offset;
            ai_sched_len = chunk_size;
            ai_sched_version = chunk_version;
            has_ai_sched = 1;
        } else if (std::memcmp(tag, "IDEN", 4u) == 0) {
            dom::core_tlv::TlvReader ir(data + offset, (size_t)chunk_size);
            dom::core_tlv::TlvRecord irec;
            u32 schema_version = 0u;
            if (chunk_version > DMSG_IDENTITY_VERSION) {
                return DOM_GAME_SAVE_ERR_MIGRATION;
            }
            if (chunk_version != DMSG_IDENTITY_VERSION || has_identity) {
                return DOM_GAME_SAVE_ERR_FORMAT;
            }
            while (ir.next(irec)) {
                switch (irec.tag) {
                case dom::core_tlv::CORE_TLV_TAG_SCHEMA_VERSION:
                    (void)dom::core_tlv::tlv_read_u32_le(irec.payload, irec.len, schema_version);
                    break;
                case DMSG_IDENTITY_TAG_INSTANCE_ID:
                    instance_id = (const char *)irec.payload;
                    instance_id_len = irec.len;
                    break;
                case DMSG_IDENTITY_TAG_RUN_ID:
                    (void)dom::core_tlv::tlv_read_u64_le(irec.payload, irec.len, run_id_val);
                    break;
                case DMSG_IDENTITY_TAG_MANIFEST_HASH:
                    manifest_hash = irec.payload;
                    manifest_hash_len = irec.len;
                    break;
                case DMSG_IDENTITY_TAG_CONTENT_HASH:
                    if (dom::core_tlv::tlv_read_u64_le(irec.payload, irec.len, content_hash)) {
                        has_content_hash = 1;
                    }
                    break;
                default:
                    break;
                }
            }
            if (schema_version != DMSG_IDENTITY_VERSION || !has_content_hash) {
                return DOM_GAME_SAVE_ERR_FORMAT;
            }
            has_identity = 1;
        } else if (std::memcmp(tag, "RNG ", 4u) == 0) {
            if (chunk_version > DMSG_RNG_VERSION) {
                return DOM_GAME_SAVE_ERR_MIGRATION;
            }
            if (chunk_version != DMSG_RNG_VERSION || has_rng || chunk_size != 4u) {
                return DOM_GAME_SAVE_ERR_FORMAT;
            }
            rng_state = read_u32_le(data + offset);
            rng_version = chunk_version;
            has_rng = 1;
        }

        offset += (size_t)chunk_size;
    }

    if (!core_ptr || !has_rng || !has_surface || !has_media_bindings ||
        !has_weather_bindings || !has_aero_props || !has_aero_state ||
        !has_construction ||
        !has_stations || !has_routes || !has_transfers || !has_production ||
        !has_macro_economy || !has_macro_events ||
        !has_factions || !has_ai_sched) {
        return DOM_GAME_SAVE_ERR_FORMAT;
    }
    if (version >= 2u && !has_identity) {
        return DOM_GAME_SAVE_ERR_FORMAT;
    }

    std::memset(out_desc, 0, sizeof(*out_desc));
    out_desc->struct_size = (u32)sizeof(*out_desc);
    out_desc->struct_version = DOM_GAME_SAVE_DESC_VERSION;
    out_desc->container_version = version;
    out_desc->ups = ups;
    out_desc->tick_index = tick_index;
    out_desc->seed = seed;
    out_desc->feature_epoch = feature_epoch;
    out_desc->instance_id = instance_id;
    out_desc->instance_id_len = instance_id_len;
    out_desc->run_id = run_id_val;
    out_desc->manifest_hash_bytes = manifest_hash;
    out_desc->manifest_hash_len = manifest_hash_len;
    out_desc->content_hash64 = content_hash;
    out_desc->has_identity = (u32)has_identity;
    out_desc->content_tlv = (content_len > 0u) ? (data + content_offset) : (const unsigned char *)0;
    out_desc->content_tlv_len = content_len;
    out_desc->core_blob = core_ptr;
    out_desc->core_blob_len = core_len;
    out_desc->core_version = core_version;
    out_desc->orbit_blob = orbit_ptr;
    out_desc->orbit_blob_len = orbit_len;
    out_desc->orbit_version = orbit_version;
    out_desc->has_orbit = (u32)has_orbit;
    out_desc->surface_blob = surface_ptr;
    out_desc->surface_blob_len = surface_len;
    out_desc->surface_version = surface_version;
    out_desc->has_surface = (u32)has_surface;
    out_desc->media_bindings_blob = media_bindings_ptr;
    out_desc->media_bindings_blob_len = media_bindings_len;
    out_desc->media_bindings_version = media_bindings_version;
    out_desc->has_media_bindings = (u32)has_media_bindings;
    out_desc->weather_bindings_blob = weather_bindings_ptr;
    out_desc->weather_bindings_blob_len = weather_bindings_len;
    out_desc->weather_bindings_version = weather_bindings_version;
    out_desc->has_weather_bindings = (u32)has_weather_bindings;
    out_desc->aero_props_blob = aero_props_ptr;
    out_desc->aero_props_blob_len = aero_props_len;
    out_desc->aero_props_version = aero_props_version;
    out_desc->has_aero_props = (u32)has_aero_props;
    out_desc->aero_state_blob = aero_state_ptr;
    out_desc->aero_state_blob_len = aero_state_len;
    out_desc->aero_state_version = aero_state_version;
    out_desc->has_aero_state = (u32)has_aero_state;
    out_desc->construction_blob = construction_ptr;
    out_desc->construction_blob_len = construction_len;
    out_desc->construction_version = construction_version;
    out_desc->has_construction = (u32)has_construction;
    out_desc->stations_blob = stations_ptr;
    out_desc->stations_blob_len = stations_len;
    out_desc->stations_version = stations_version;
    out_desc->has_stations = (u32)has_stations;
    out_desc->routes_blob = routes_ptr;
    out_desc->routes_blob_len = routes_len;
    out_desc->routes_version = routes_version;
    out_desc->has_routes = (u32)has_routes;
    out_desc->transfers_blob = transfers_ptr;
    out_desc->transfers_blob_len = transfers_len;
    out_desc->transfers_version = transfers_version;
    out_desc->has_transfers = (u32)has_transfers;
    out_desc->production_blob = production_ptr;
    out_desc->production_blob_len = production_len;
    out_desc->production_version = production_version;
    out_desc->has_production = (u32)has_production;
    out_desc->macro_economy_blob = macro_economy_ptr;
    out_desc->macro_economy_blob_len = macro_economy_len;
    out_desc->macro_economy_version = macro_economy_version;
    out_desc->has_macro_economy = (u32)has_macro_economy;
    out_desc->macro_events_blob = macro_events_ptr;
    out_desc->macro_events_blob_len = macro_events_len;
    out_desc->macro_events_version = macro_events_version;
    out_desc->has_macro_events = (u32)has_macro_events;
    out_desc->factions_blob = factions_ptr;
    out_desc->factions_blob_len = factions_len;
    out_desc->factions_version = factions_version;
    out_desc->has_factions = (u32)has_factions;
    out_desc->ai_sched_blob = ai_sched_ptr;
    out_desc->ai_sched_blob_len = ai_sched_len;
    out_desc->ai_sched_version = ai_sched_version;
    out_desc->has_ai_sched = (u32)has_ai_sched;
    out_desc->rng_state = rng_state;
    out_desc->rng_version = rng_version;
    out_desc->has_rng = (u32)has_rng;
    return DOM_GAME_SAVE_OK;
}

static bool build_save_bytes(const dom_game_runtime *rt, std::vector<unsigned char> &out) {
    d_world *world;
    const dom::DomSession *session;
    std::vector<unsigned char> core_blob;
    std::vector<unsigned char> orbit_blob;
    std::vector<unsigned char> surface_blob;
    std::vector<unsigned char> media_bindings_blob;
    std::vector<unsigned char> weather_bindings_blob;
    std::vector<unsigned char> aero_props_blob;
    std::vector<unsigned char> aero_state_blob;
    std::vector<unsigned char> construction_blob;
    std::vector<unsigned char> stations_blob;
    std::vector<unsigned char> routes_blob;
    std::vector<unsigned char> transfers_blob;
    std::vector<unsigned char> production_blob;
    std::vector<unsigned char> macro_economy_blob;
    std::vector<unsigned char> macro_events_blob;
    std::vector<unsigned char> factions_blob;
    std::vector<unsigned char> ai_sched_blob;
    std::vector<unsigned char> content_tlv;
    std::vector<unsigned char> identity_tlv;
    u32 ups;
    u64 tick;
    u64 seed;

    if (!rt) {
        return false;
    }
    world = dom_game_runtime_world((dom_game_runtime *)rt);
    if (!world) {
        return false;
    }

    ups = dom_game_runtime_get_ups(rt);
    tick = dom_game_runtime_get_tick(rt);
    seed = dom_game_runtime_get_seed(rt);
    if (ups == 0u) {
        return false;
    }

    if (!dom::game_save_world_blob(world, core_blob) || core_blob.empty()) {
        return false;
    }
    if (!build_media_bindings_blob(rt, media_bindings_blob)) {
        return false;
    }
    if (!build_weather_bindings_blob(rt, weather_bindings_blob)) {
        return false;
    }
    if (!build_aero_props_blob(rt, aero_props_blob)) {
        return false;
    }
    if (!build_aero_state_blob(rt, aero_state_blob)) {
        return false;
    }
    if (!build_construction_blob(rt, construction_blob)) {
        return false;
    }
    if (!build_station_blob(rt, stations_blob)) {
        return false;
    }
    if (!build_route_blob(rt, routes_blob)) {
        return false;
    }
    if (!build_transfer_blob(rt, transfers_blob)) {
        return false;
    }
    if (!build_production_blob(rt, production_blob)) {
        return false;
    }
    if (!build_macro_economy_blob(rt, macro_economy_blob)) {
        return false;
    }
    if (!build_macro_events_blob(rt, macro_events_blob)) {
        return false;
    }
    if (!build_factions_blob(rt, factions_blob)) {
        return false;
    }
    if (!build_ai_sched_blob(rt, ai_sched_blob)) {
        return false;
    }

    session = (const dom::DomSession *)dom_game_runtime_session(rt);
    if (!dom::dom_game_content_build_tlv(session, content_tlv)) {
        content_tlv.clear();
    }

    if (content_tlv.size() > 0xffffffffull ||
        core_blob.size() > 0xffffffffull ||
        orbit_blob.size() > 0xffffffffull ||
        surface_blob.size() > 0xffffffffull ||
        media_bindings_blob.size() > 0xffffffffull ||
        weather_bindings_blob.size() > 0xffffffffull ||
        aero_props_blob.size() > 0xffffffffull ||
        aero_state_blob.size() > 0xffffffffull ||
        construction_blob.size() > 0xffffffffull ||
        stations_blob.size() > 0xffffffffull ||
        routes_blob.size() > 0xffffffffull ||
        transfers_blob.size() > 0xffffffffull ||
        production_blob.size() > 0xffffffffull ||
        macro_economy_blob.size() > 0xffffffffull ||
        macro_events_blob.size() > 0xffffffffull ||
        factions_blob.size() > 0xffffffffull ||
        ai_sched_blob.size() > 0xffffffffull) {
        return false;
    }
    if (!build_identity_tlv(rt,
                            content_tlv.empty() ? (const unsigned char *)0 : &content_tlv[0],
                            content_tlv.size(),
                            identity_tlv)) {
        return false;
    }
    if (identity_tlv.size() > 0xffffffffull) {
        return false;
    }

    out.clear();
    append_bytes(out, "DMSG", 4u);
    append_u32_le(out, DMSG_VERSION);
    append_u32_le(out, DMSG_ENDIAN);
    append_u32_le(out, ups);
    append_u64_le(out, tick);
    append_u64_le(out, seed);
    append_u32_le(out, dom::dom_feature_epoch_current());
    append_u32_le(out, (u32)content_tlv.size());
    append_bytes(out, content_tlv.empty() ? (const unsigned char *)0 : &content_tlv[0], content_tlv.size());

    append_bytes(out, "IDEN", 4u);
    append_u32_le(out, DMSG_IDENTITY_VERSION);
    append_u32_le(out, (u32)identity_tlv.size());
    append_bytes(out, identity_tlv.empty() ? (const unsigned char *)0 : &identity_tlv[0], identity_tlv.size());

    append_bytes(out, "CORE", 4u);
    append_u32_le(out, DMSG_CORE_VERSION);
    append_u32_le(out, (u32)core_blob.size());
    append_bytes(out, &core_blob[0], core_blob.size());

    append_bytes(out, "ORBT", 4u);
    append_u32_le(out, DMSG_ORBIT_VERSION);
    append_u32_le(out, (u32)orbit_blob.size());
    append_bytes(out, orbit_blob.empty() ? (const unsigned char *)0 : &orbit_blob[0],
                 orbit_blob.size());

    append_bytes(out, "SOVR", 4u);
    append_u32_le(out, DMSG_SURFACE_VERSION);
    append_u32_le(out, (u32)surface_blob.size());
    append_bytes(out, surface_blob.empty() ? (const unsigned char *)0 : &surface_blob[0],
                 surface_blob.size());

    append_bytes(out, "MEDI", 4u);
    append_u32_le(out, DMSG_MEDIA_BINDINGS_VERSION);
    append_u32_le(out, (u32)media_bindings_blob.size());
    append_bytes(out, media_bindings_blob.empty() ? (const unsigned char *)0 : &media_bindings_blob[0],
                 media_bindings_blob.size());

    append_bytes(out, "WEAT", 4u);
    append_u32_le(out, DMSG_WEATHER_BINDINGS_VERSION);
    append_u32_le(out, (u32)weather_bindings_blob.size());
    append_bytes(out, weather_bindings_blob.empty() ? (const unsigned char *)0 : &weather_bindings_blob[0],
                 weather_bindings_blob.size());

    append_bytes(out, "AERP", 4u);
    append_u32_le(out, DMSG_AERO_PROPS_VERSION);
    append_u32_le(out, (u32)aero_props_blob.size());
    append_bytes(out, aero_props_blob.empty() ? (const unsigned char *)0 : &aero_props_blob[0],
                 aero_props_blob.size());

    append_bytes(out, "AERS", 4u);
    append_u32_le(out, DMSG_AERO_STATE_VERSION);
    append_u32_le(out, (u32)aero_state_blob.size());
    append_bytes(out, aero_state_blob.empty() ? (const unsigned char *)0 : &aero_state_blob[0],
                 aero_state_blob.size());

    append_bytes(out, "CNST", 4u);
    append_u32_le(out, DMSG_CONSTRUCTION_VERSION);
    append_u32_le(out, (u32)construction_blob.size());
    append_bytes(out, construction_blob.empty() ? (const unsigned char *)0 : &construction_blob[0],
                 construction_blob.size());

    append_bytes(out, "STAT", 4u);
    append_u32_le(out, DMSG_STATIONS_VERSION);
    append_u32_le(out, (u32)stations_blob.size());
    append_bytes(out, stations_blob.empty() ? (const unsigned char *)0 : &stations_blob[0],
                 stations_blob.size());

    append_bytes(out, "ROUT", 4u);
    append_u32_le(out, DMSG_ROUTES_VERSION);
    append_u32_le(out, (u32)routes_blob.size());
    append_bytes(out, routes_blob.empty() ? (const unsigned char *)0 : &routes_blob[0],
                 routes_blob.size());

    append_bytes(out, "TRAN", 4u);
    append_u32_le(out, DMSG_TRANSFERS_VERSION);
    append_u32_le(out, (u32)transfers_blob.size());
    append_bytes(out, transfers_blob.empty() ? (const unsigned char *)0 : &transfers_blob[0],
                 transfers_blob.size());

    append_bytes(out, "PROD", 4u);
    append_u32_le(out, DMSG_PRODUCTION_VERSION);
    append_u32_le(out, (u32)production_blob.size());
    append_bytes(out, production_blob.empty() ? (const unsigned char *)0 : &production_blob[0],
                 production_blob.size());

    append_bytes(out, "MECO", 4u);
    append_u32_le(out, DMSG_MACRO_ECONOMY_VERSION);
    append_u32_le(out, (u32)macro_economy_blob.size());
    append_bytes(out, macro_economy_blob.empty() ? (const unsigned char *)0 : &macro_economy_blob[0],
                 macro_economy_blob.size());

    append_bytes(out, "MEVT", 4u);
    append_u32_le(out, DMSG_MACRO_EVENTS_VERSION);
    append_u32_le(out, (u32)macro_events_blob.size());
    append_bytes(out, macro_events_blob.empty() ? (const unsigned char *)0 : &macro_events_blob[0],
                 macro_events_blob.size());

    append_bytes(out, "FACT", 4u);
    append_u32_le(out, DMSG_FACTIONS_VERSION);
    append_u32_le(out, (u32)factions_blob.size());
    append_bytes(out, factions_blob.empty() ? (const unsigned char *)0 : &factions_blob[0],
                 factions_blob.size());

    append_bytes(out, "AISC", 4u);
    append_u32_le(out, DMSG_AI_SCHED_VERSION);
    append_u32_le(out, (u32)ai_sched_blob.size());
    append_bytes(out, ai_sched_blob.empty() ? (const unsigned char *)0 : &ai_sched_blob[0],
                 ai_sched_blob.size());

    append_bytes(out, "RNG ", 4u);
    append_u32_le(out, DMSG_RNG_VERSION);
    append_u32_le(out, 4u);
    append_u32_le(out, world->rng.state);
    return true;
}

} // namespace

extern "C" {

int dom_game_save_read(const char *path,
                       dom_game_save_desc *out_desc,
                       unsigned char **out_storage,
                       u32 *out_storage_len) {
    unsigned char *data = (unsigned char *)0;
    size_t data_len = 0u;
    int rc;

    if (!path || !out_desc || !out_storage || !out_storage_len) {
        return DOM_GAME_SAVE_ERR;
    }

    *out_storage = (unsigned char *)0;
    *out_storage_len = 0u;

    if (!read_file_alloc(path, &data, &data_len)) {
        return DOM_GAME_SAVE_ERR;
    }
    if (data_len > 0xffffffffull) {
        std::free(data);
        return DOM_GAME_SAVE_ERR_FORMAT;
    }

    rc = parse_dmsg(data, data_len, out_desc);
    if (rc != DOM_GAME_SAVE_OK) {
        std::free(data);
        return rc;
    }

    *out_storage = data;
    *out_storage_len = (u32)data_len;
    return DOM_GAME_SAVE_OK;
}

void dom_game_save_release(unsigned char *storage) {
    if (storage) {
        std::free(storage);
    }
}

int dom_game_save_write(const char *path,
                        const dom_game_runtime *rt,
                        u32 flags) {
    std::vector<unsigned char> bytes;
    (void)flags;

    if (!path || !path[0] || !rt) {
        return DOM_GAME_SAVE_ERR;
    }
    if (!build_save_bytes(rt, bytes) || bytes.empty()) {
        return DOM_GAME_SAVE_ERR;
    }
    if (!write_file(path, &bytes[0], bytes.size())) {
        return DOM_GAME_SAVE_ERR;
    }
    return DOM_GAME_SAVE_OK;
}

int dom_game_runtime_save(dom_game_runtime *rt, const char *path) {
    return dom_game_save_write(path, rt, 0u);
}

int dom_game_runtime_load_save(dom_game_runtime *rt, const char *path) {
    dom_game_save_desc desc;
    unsigned char *storage = (unsigned char *)0;
    u32 storage_len = 0u;
    d_world *world;
    d_sim_context *sim;
    int rc;

    if (!rt || !path || !path[0]) {
        return DOM_GAME_SAVE_ERR;
    }

    std::memset(&desc, 0, sizeof(desc));
    rc = dom_game_save_read(path, &desc, &storage, &storage_len);
    if (rc != DOM_GAME_SAVE_OK) {
        if (rc == DOM_GAME_SAVE_ERR_MIGRATION) {
            std::fprintf(stderr, "DMSG load: migration required (version unsupported)\n");
        }
        return rc;
    }

    world = dom_game_runtime_world(rt);
    sim = dom_game_runtime_sim(rt);
    if (!world || !sim) {
        dom_game_save_release(storage);
        return DOM_GAME_SAVE_ERR;
    }
    if (desc.ups == 0u || desc.ups != dom_game_runtime_get_ups(rt)) {
        std::fprintf(stderr, "DMSG load: UPS mismatch (save=%u runtime=%u)\n",
                     (unsigned)desc.ups,
                     (unsigned)dom_game_runtime_get_ups(rt));
        dom_game_save_release(storage);
        return DOM_GAME_SAVE_ERR;
    }
    if (desc.tick_index > 0xffffffffull) {
        std::fprintf(stderr, "DMSG load: tick index out of range (%llu)\n",
                     (unsigned long long)desc.tick_index);
        dom_game_save_release(storage);
        return DOM_GAME_SAVE_ERR_FORMAT;
    }
    if (!desc.core_blob || desc.core_blob_len == 0u || !desc.has_rng) {
        dom_game_save_release(storage);
        return DOM_GAME_SAVE_ERR_FORMAT;
    }

    if (!dom::game_load_world_blob(world,
                                   desc.core_blob,
                                   desc.core_blob_len)) {
        dom_game_save_release(storage);
        return DOM_GAME_SAVE_ERR;
    }

    {
        const u32 tick = (u32)desc.tick_index;
        world->tick_count = tick;
        world->meta.seed = desc.seed;
        world->worldgen_seed = desc.seed;
        world->rng.state = desc.rng_state;
        sim->tick_index = tick;
    }

    if (desc.has_media_bindings) {
        rc = apply_media_bindings_blob(rt,
                                       desc.media_bindings_blob,
                                       desc.media_bindings_blob_len);
        if (rc != DOM_GAME_SAVE_OK) {
            dom_game_save_release(storage);
            return rc;
        }
    }
    if (desc.has_weather_bindings) {
        rc = apply_weather_bindings_blob(rt,
                                         desc.weather_bindings_blob,
                                         desc.weather_bindings_blob_len);
        if (rc != DOM_GAME_SAVE_OK) {
            dom_game_save_release(storage);
            return rc;
        }
    }
    if (desc.has_aero_props) {
        rc = apply_aero_props_blob(rt,
                                   desc.aero_props_blob,
                                   desc.aero_props_blob_len);
        if (rc != DOM_GAME_SAVE_OK) {
            dom_game_save_release(storage);
            return rc;
        }
    }
    if (desc.has_aero_state) {
        rc = apply_aero_state_blob(rt,
                                   desc.aero_state_blob,
                                   desc.aero_state_blob_len);
        if (rc != DOM_GAME_SAVE_OK) {
            dom_game_save_release(storage);
            return rc;
        }
    }

    if (desc.has_construction) {
        rc = apply_construction_blob(rt, desc.construction_blob, desc.construction_blob_len);
        if (rc != DOM_GAME_SAVE_OK) {
            dom_game_save_release(storage);
            return rc;
        }
    }

    if (desc.has_stations) {
        rc = apply_station_blob(rt, desc.stations_blob, desc.stations_blob_len);
        if (rc != DOM_GAME_SAVE_OK) {
            dom_game_save_release(storage);
            return rc;
        }
    }
    if (desc.has_routes) {
        rc = apply_route_blob(rt, desc.routes_blob, desc.routes_blob_len);
        if (rc != DOM_GAME_SAVE_OK) {
            dom_game_save_release(storage);
            return rc;
        }
    }
    if (desc.has_transfers) {
        rc = apply_transfer_blob(rt,
                                 desc.transfers_blob,
                                 desc.transfers_blob_len,
                                 desc.tick_index);
        if (rc != DOM_GAME_SAVE_OK) {
            dom_game_save_release(storage);
            return rc;
        }
    }
    if (desc.has_production) {
        rc = apply_production_blob(rt, desc.production_blob, desc.production_blob_len);
        if (rc != DOM_GAME_SAVE_OK) {
            dom_game_save_release(storage);
            return rc;
        }
        {
            dom_production *prod = (dom_production *)dom_game_runtime_production(rt);
            if (prod) {
                (void)dom_production_set_last_tick(prod, desc.tick_index);
            }
        }
    }
    if (desc.has_macro_economy) {
        rc = apply_macro_economy_blob(rt,
                                      desc.macro_economy_blob,
                                      desc.macro_economy_blob_len);
        if (rc != DOM_GAME_SAVE_OK) {
            dom_game_save_release(storage);
            return rc;
        }
    }
    if (desc.has_macro_events) {
        rc = apply_macro_events_blob(rt,
                                     desc.macro_events_blob,
                                     desc.macro_events_blob_len,
                                     desc.tick_index);
        if (rc != DOM_GAME_SAVE_OK) {
            dom_game_save_release(storage);
            return rc;
        }
    }
    if (desc.has_factions) {
        rc = apply_factions_blob(rt,
                                 desc.factions_blob,
                                 desc.factions_blob_len);
        if (rc != DOM_GAME_SAVE_OK) {
            dom_game_save_release(storage);
            return rc;
        }
    }
    if (desc.has_ai_sched) {
        rc = apply_ai_sched_blob(rt,
                                 desc.ai_sched_blob,
                                 desc.ai_sched_blob_len);
        if (rc != DOM_GAME_SAVE_OK) {
            dom_game_save_release(storage);
            return rc;
        }
    }

    (void)d_net_cmd_queue_init();
    dom_game_save_release(storage);
    return DOM_GAME_SAVE_OK;
}

} /* extern "C" */
