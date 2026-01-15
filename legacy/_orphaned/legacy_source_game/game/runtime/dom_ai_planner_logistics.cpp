/*
FILE: source/dominium/game/runtime/dom_ai_planner_logistics.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / game/runtime/ai_planner_logistics
RESPONSIBILITY: Deterministic logistics planner (routes/transfers) for AI.
*/
#include "runtime/dom_ai_planner_logistics.h"

#include <vector>

#include "dominium/core_tlv.h"

extern "C" {
#include "net/d_net_schema.h"
}

namespace {

static const u64 DEFAULT_ROUTE_DURATION_TICKS = 3600ull;
static const u64 DEFAULT_ROUTE_CAPACITY_UNITS = 100ull;

static void append_u32(std::vector<unsigned char> &out, u32 v) {
    out.push_back((unsigned char)(v & 0xffu));
    out.push_back((unsigned char)((v >> 8u) & 0xffu));
    out.push_back((unsigned char)((v >> 16u) & 0xffu));
    out.push_back((unsigned char)((v >> 24u) & 0xffu));
}

static void append_u64(std::vector<unsigned char> &out, u64 v) {
    append_u32(out, (u32)(v & 0xffffffffu));
    append_u32(out, (u32)((v >> 32u) & 0xffffffffu));
}

static u64 hash_fields(u64 a, u64 b, u64 c) {
    unsigned char buf[24];
    dom::core_tlv::tlv_write_u64_le(&buf[0], a);
    dom::core_tlv::tlv_write_u64_le(&buf[8], b);
    dom::core_tlv::tlv_write_u64_le(&buf[16], c);
    return dom::core_tlv::tlv_fnv1a64(buf, sizeof(buf));
}

struct StationListCtx {
    std::vector<dom_station_info> stations;
};

static void collect_station(const dom_station_info *info, void *user) {
    StationListCtx *ctx = static_cast<StationListCtx *>(user);
    if (!ctx || !info) {
        return;
    }
    ctx->stations.push_back(*info);
}

struct RouteFindCtx {
    dom_station_id src_id;
    dom_station_id dst_id;
    dom_route_info best;
    int found;
};

static void find_route_cb(const dom_route_info *info, void *user) {
    RouteFindCtx *ctx = static_cast<RouteFindCtx *>(user);
    if (!ctx || !info) {
        return;
    }
    if (info->src_station_id != ctx->src_id ||
        info->dst_station_id != ctx->dst_id) {
        return;
    }
    if (!ctx->found || info->route_id < ctx->best.route_id) {
        ctx->best = *info;
        ctx->found = 1;
    }
}

struct BodyFindCtx {
    dom_system_id system_id;
    dom_body_id best_body;
    int found;
};

static void find_body_cb(const dom_body_info *info, void *user) {
    BodyFindCtx *ctx = static_cast<BodyFindCtx *>(user);
    if (!ctx || !info) {
        return;
    }
    if (info->system_id != ctx->system_id) {
        return;
    }
    if (!ctx->found || info->id < ctx->best_body) {
        ctx->best_body = info->id;
        ctx->found = 1;
    }
}

static int station_in_system(const dom_station_info &station,
                             const dom_body_registry *bodies,
                             dom_system_id system_id) {
    dom_body_info body;
    if (!bodies || station.body_id == 0ull) {
        return 0;
    }
    if (dom_body_registry_get(bodies, station.body_id, &body) != DOM_BODY_REGISTRY_OK) {
        return 0;
    }
    return body.system_id == system_id;
}

struct SysCtx {
    dom_system_id id;
    int found;
};

static void collect_system_cb(const dom_system_info *info, void *user) {
    SysCtx *ctx_ptr = static_cast<SysCtx *>(user);
    if (!ctx_ptr || !info) {
        return;
    }
    if (!ctx_ptr->found || info->id < ctx_ptr->id) {
        ctx_ptr->id = info->id;
        ctx_ptr->found = 1;
    }
}

static int pick_target_system(const dom_faction_info *faction,
                              const dom_system_registry *systems,
                              dom_system_id *out_system) {
    SysCtx ctx;
    if (!faction || !out_system) {
        return 0;
    }
    *out_system = 0ull;
    if (faction->home_scope_kind == DOM_MACRO_SCOPE_SYSTEM) {
        *out_system = (dom_system_id)faction->home_scope_id;
        return *out_system != 0ull;
    }
    if (!systems) {
        return 0;
    }
    ctx.id = 0ull;
    ctx.found = 0;
    (void)dom_system_registry_iterate(systems, collect_system_cb, &ctx);
    if (!ctx.found) {
        return 0;
    }
    *out_system = ctx.id;
    return 1;
}

static int find_shortage_resource(const dom_macro_economy *economy,
                                  dom_system_id system_id,
                                  dom_resource_id *out_resource) {
    dom_macro_rate_entry list[64];
    u32 count = 0u;
    if (!economy || !out_resource) {
        return 0;
    }
    *out_resource = 0ull;
    if (dom_macro_economy_list_demand(economy,
                                      DOM_MACRO_SCOPE_SYSTEM,
                                      system_id,
                                      list,
                                      64u,
                                      &count) != DOM_MACRO_ECONOMY_OK) {
        return 0;
    }
    for (u32 i = 0u; i < count; ++i) {
        i64 prod = 0;
        i64 dem = 0;
        dom_resource_id resource_id = list[i].resource_id;
        if (dom_macro_economy_rate_get(economy,
                                       DOM_MACRO_SCOPE_SYSTEM,
                                       system_id,
                                       resource_id,
                                       &prod,
                                       &dem) != DOM_MACRO_ECONOMY_OK) {
            continue;
        }
        if (dem > prod) {
            *out_resource = resource_id;
            return 1;
        }
    }
    return 0;
}

static void build_station_create_payload(u64 station_id,
                                         u64 body_id,
                                         u64 frame_id,
                                         std::vector<unsigned char> &out) {
    dom::core_tlv::TlvWriter writer;
    writer.add_u64(D_NET_TLV_STATION_ID, station_id);
    writer.add_u64(D_NET_TLV_STATION_BODY_ID, body_id);
    writer.add_u64(D_NET_TLV_STATION_FRAME_ID, frame_id);
    out = writer.bytes();
}

static void build_route_create_payload(u64 route_id,
                                       u64 src_station_id,
                                       u64 dst_station_id,
                                       u64 duration_ticks,
                                       u64 capacity_units,
                                       std::vector<unsigned char> &out) {
    dom::core_tlv::TlvWriter writer;
    writer.add_u64(D_NET_TLV_ROUTE_ID, route_id);
    writer.add_u64(D_NET_TLV_ROUTE_SRC_STATION_ID, src_station_id);
    writer.add_u64(D_NET_TLV_ROUTE_DST_STATION_ID, dst_station_id);
    writer.add_u64(D_NET_TLV_ROUTE_DURATION_TICKS, duration_ticks);
    writer.add_u64(D_NET_TLV_ROUTE_CAPACITY_UNITS, capacity_units);
    out = writer.bytes();
}

static void build_transfer_payload(u64 route_id,
                                   dom_resource_id resource_id,
                                   i64 quantity,
                                   std::vector<unsigned char> &out) {
    dom::core_tlv::TlvWriter writer;
    std::vector<unsigned char> items;
    append_u64(items, resource_id);
    append_u64(items, (u64)(i64)quantity);
    writer.add_u64(D_NET_TLV_TRANSFER_ROUTE_ID, route_id);
    writer.add_u32(D_NET_TLV_TRANSFER_ITEM_COUNT, 1u);
    writer.add_bytes(D_NET_TLV_TRANSFER_ITEMS, items.empty() ? 0 : &items[0],
                     (u32)items.size());
    out = writer.bytes();
}

} // namespace

int dom_ai_planner_logistics_run(const dom_faction_info *faction,
                                 const dom_macro_economy *economy,
                                 const dom_station_registry *stations,
                                 const dom_route_graph *routes,
                                 const dom_body_registry *bodies,
                                 const dom_system_registry *systems,
                                 u64 tick,
                                 u32 max_ops,
                                 dom_ai_planner_logistics_result *out_result) {
    dom_system_id target_system = 0ull;
    dom_resource_id shortage = 0ull;
    StationListCtx station_ctx;

    if (!faction || !economy || !stations || !routes || !bodies ||
        !systems || !out_result) {
        return DOM_AI_SCHEDULER_INVALID_ARGUMENT;
    }

    out_result->commands.clear();
    out_result->ops_used = 0u;
    out_result->reason_code = DOM_AI_REASON_NONE;

    if (max_ops == 0u) {
        out_result->reason_code = DOM_AI_REASON_BUDGET_HIT;
        return DOM_AI_SCHEDULER_OK;
    }

    if (!pick_target_system(faction, systems, &target_system)) {
        return DOM_AI_SCHEDULER_OK;
    }
    if (!find_shortage_resource(economy, target_system, &shortage)) {
        return DOM_AI_SCHEDULER_OK;
    }

    (void)dom_station_iterate(stations, collect_station, &station_ctx);

    dom_station_info dest_station;
    int have_dest = 0;
    for (size_t i = 0u; i < station_ctx.stations.size(); ++i) {
        const dom_station_info &info = station_ctx.stations[i];
        if (station_in_system(info, bodies, target_system)) {
            dest_station = info;
            have_dest = 1;
            break;
        }
    }

    if (!have_dest) {
        if (!(faction->policy_flags & DOM_FACTION_POLICY_ALLOW_STATION)) {
            return DOM_AI_SCHEDULER_OK;
        }
        BodyFindCtx body_ctx;
        body_ctx.system_id = target_system;
        body_ctx.best_body = 0ull;
        body_ctx.found = 0;
        (void)dom_body_registry_iterate(bodies, find_body_cb, &body_ctx);
        if (!body_ctx.found) {
            return DOM_AI_SCHEDULER_OK;
        }
        {
            u64 station_id = hash_fields(faction->faction_id,
                                         body_ctx.best_body,
                                         0x53544154ull);
            dom_station_info tmp;
            if (dom_station_get(stations, station_id, &tmp) == DOM_STATION_REGISTRY_OK) {
                return DOM_AI_SCHEDULER_OK;
            }
            dom_ai_planned_cmd cmd;
            cmd.schema_id = D_NET_SCHEMA_CMD_STATION_CREATE_V1;
            cmd.schema_ver = 1u;
            cmd._pad0 = 0u;
            cmd.tick = 0u;
            build_station_create_payload(station_id, body_ctx.best_body, 0ull, cmd.payload);
            out_result->commands.push_back(cmd);
            out_result->ops_used = 1u;
            out_result->reason_code = DOM_AI_REASON_ACTIONS;
            return DOM_AI_SCHEDULER_OK;
        }
    }

    dom_station_info supply_station;
    int have_supply = 0;
    i64 supply_qty = 0;
    for (size_t i = 0u; i < station_ctx.stations.size(); ++i) {
        const dom_station_info &info = station_ctx.stations[i];
        if (info.station_id == dest_station.station_id) {
            continue;
        }
        if (dom_station_inventory_get(stations,
                                      info.station_id,
                                      shortage,
                                      &supply_qty) == DOM_STATION_REGISTRY_OK &&
            supply_qty > 0) {
            supply_station = info;
            have_supply = 1;
            break;
        }
    }
    if (!have_supply) {
        return DOM_AI_SCHEDULER_OK;
    }

    RouteFindCtx route_ctx;
    route_ctx.src_id = supply_station.station_id;
    route_ctx.dst_id = dest_station.station_id;
    route_ctx.found = 0;
    (void)dom_route_graph_iterate(routes, find_route_cb, &route_ctx);

    if (!route_ctx.found) {
        if (!(faction->policy_flags & DOM_FACTION_POLICY_ALLOW_ROUTE)) {
            return DOM_AI_SCHEDULER_OK;
        }
        {
            u64 route_id = hash_fields(faction->faction_id,
                                       supply_station.station_id,
                                       dest_station.station_id);
            dom_route_info tmp;
            if (dom_route_graph_get(routes, route_id, &tmp) == DOM_ROUTE_GRAPH_OK) {
                return DOM_AI_SCHEDULER_OK;
            }
            dom_ai_planned_cmd cmd;
            cmd.schema_id = D_NET_SCHEMA_CMD_ROUTE_CREATE_V1;
            cmd.schema_ver = 1u;
            cmd._pad0 = 0u;
            cmd.tick = 0u;
            build_route_create_payload(route_id,
                                       supply_station.station_id,
                                       dest_station.station_id,
                                       DEFAULT_ROUTE_DURATION_TICKS,
                                       DEFAULT_ROUTE_CAPACITY_UNITS,
                                       cmd.payload);
            out_result->commands.push_back(cmd);
            out_result->ops_used = 1u;
            out_result->reason_code = DOM_AI_REASON_ACTIONS;
            return DOM_AI_SCHEDULER_OK;
        }
    }

    {
        i64 qty = supply_qty;
        if (route_ctx.best.capacity_units > 0u &&
            qty > (i64)route_ctx.best.capacity_units) {
            qty = (i64)route_ctx.best.capacity_units;
        }
        if (qty <= 0) {
            return DOM_AI_SCHEDULER_OK;
        }
        dom_ai_planned_cmd cmd;
        cmd.schema_id = D_NET_SCHEMA_CMD_TRANSFER_SCHEDULE_V1;
        cmd.schema_ver = 1u;
        cmd._pad0 = 0u;
        cmd.tick = 0u;
        build_transfer_payload(route_ctx.best.route_id, shortage, qty, cmd.payload);
        out_result->commands.push_back(cmd);
        out_result->ops_used = 1u;
        out_result->reason_code = DOM_AI_REASON_ACTIONS;
    }

    (void)tick;
    return DOM_AI_SCHEDULER_OK;
}
