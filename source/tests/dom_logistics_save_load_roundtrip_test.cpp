/*
FILE: source/tests/dom_logistics_save_load_roundtrip_test.cpp
MODULE: Repository
PURPOSE: Ensures logistics state round-trips through DMSG save/load.
*/
#include <cassert>
#include <cstdio>
#include <cstring>
#include <vector>

extern "C" {
#include "domino/core/types.h"
#include "domino/core/spacetime.h"
}

#include "dominium/core_tlv.h"
#include "dom_session.h"
#include "dom_instance.h"
#include "dom_paths.h"
#include "dom_game_net.h"
#include "runtime/dom_game_runtime.h"
#include "runtime/dom_game_save.h"
#include "runtime/dom_station_registry.h"
#include "runtime/dom_route_graph.h"
#include "runtime/dom_transfer_scheduler.h"
#include "runtime/dom_production.h"
#include "runtime/dom_io_guard.h"

static void init_paths(dom::Paths &paths) {
    paths.root = ".";
    paths.products = ".";
    paths.mods = ".";
    paths.packs = ".";
    paths.instances = ".";
    paths.temp = ".";
}

static void init_instance(dom::InstanceInfo &inst) {
    inst.id = "test_instance";
    inst.world_seed = 123u;
    inst.world_size_m = 1024u;
    inst.vertical_min_m = -64;
    inst.vertical_max_m = 64;
    inst.suite_version = 1u;
    inst.core_version = 1u;
    inst.packs.clear();
    inst.mods.clear();
}

namespace dom {

DomGameNet::DomGameNet()
    : m_local_peer(1u),
      m_cmd_seq(1u),
      m_ready(true),
      m_dedicated(false),
      m_handshake_sent(true),
      m_impl(0),
      m_hash_events(),
      m_qos_events() {
    std::memset(&m_session, 0, sizeof(m_session));
}

DomGameNet::~DomGameNet() {
}

bool DomGameNet::init_single(u32 tick_rate) {
    (void)tick_rate;
    m_ready = true;
    return true;
}

bool DomGameNet::init_listen(u32 tick_rate, unsigned port) {
    (void)tick_rate;
    (void)port;
    m_ready = true;
    return true;
}

bool DomGameNet::init_dedicated(u32 tick_rate, unsigned port) {
    (void)tick_rate;
    (void)port;
    m_ready = true;
    return true;
}

bool DomGameNet::init_client(u32 tick_rate, const std::string &addr_port) {
    (void)tick_rate;
    (void)addr_port;
    m_ready = true;
    return true;
}

void DomGameNet::shutdown() {
    m_ready = false;
    m_hash_events.clear();
    m_qos_events.clear();
}

void DomGameNet::pump(d_world *world, d_sim_context *sim, const InstanceInfo &inst) {
    (void)world;
    (void)sim;
    (void)inst;
}

bool DomGameNet::submit_cmd(d_net_cmd *in_out_cmd) {
    (void)in_out_cmd;
    return true;
}

bool DomGameNet::poll_hash(d_net_hash *out_hash) {
    (void)out_hash;
    return false;
}

bool DomGameNet::poll_qos(d_peer_id *out_peer, std::vector<unsigned char> &out_bytes) {
    (void)out_peer;
    out_bytes.clear();
    return false;
}

} // namespace dom

struct TestRuntime {
    dom::Paths paths;
    dom::InstanceInfo inst;
    dom::SessionConfig cfg;
    dom::DomSession session;
    dom::DomGameNet net;
    dom_game_runtime *rt;

    TestRuntime() : rt(0) {}
};

static bool setup_runtime(TestRuntime &tr) {
    dom_game_runtime_init_desc desc;

    init_paths(tr.paths);
    init_instance(tr.inst);

    tr.cfg.platform_backend = "null";
    tr.cfg.gfx_backend = "null";
    tr.cfg.audio_backend = "null";
    tr.cfg.headless = true;
    tr.cfg.tui = false;
    tr.cfg.allow_missing_content = true;

    if (!tr.session.init(tr.paths, tr.inst, tr.cfg)) {
        return false;
    }

    std::memset(&desc, 0, sizeof(desc));
    desc.struct_size = sizeof(desc);
    desc.struct_version = DOM_GAME_RUNTIME_INIT_DESC_VERSION;
    desc.session = &tr.session;
    desc.net = &tr.net;
    desc.instance = &tr.inst;
    desc.ups = 60u;
    desc.run_id = 1u;

    tr.rt = dom_game_runtime_create(&desc);
    return tr.rt != 0;
}

static void teardown_runtime(TestRuntime &tr) {
    if (tr.rt) {
        dom_game_runtime_destroy(tr.rt);
        tr.rt = 0;
    }
    tr.session.shutdown();
}

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

static void append_i64(std::vector<unsigned char> &out, i64 v) {
    append_u64(out, (u64)v);
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

static void collect_production_info(const dom_production_rule_info *info, void *user) {
    ProductionCollectCtx *ctx = static_cast<ProductionCollectCtx *>(user);
    if (ctx && ctx->rules && info) {
        ctx->rules->push_back(*info);
    }
}

static u64 logistics_state_hash(dom_game_runtime *rt) {
    std::vector<unsigned char> bytes;
    const dom_station_registry *stations =
        (const dom_station_registry *)dom_game_runtime_station_registry(rt);
    const dom_route_graph *routes =
        (const dom_route_graph *)dom_game_runtime_route_graph(rt);
    const dom_transfer_scheduler *sched =
        (const dom_transfer_scheduler *)dom_game_runtime_transfer_scheduler(rt);
    const dom_production *prod =
        (const dom_production *)dom_game_runtime_production(rt);

    {
        std::vector<dom_station_info> station_list;
        StationCollectCtx ctx;
        u32 count = stations ? dom_station_count(stations) : 0u;
        append_u32(bytes, count);
        if (stations && count > 0u) {
            ctx.stations = &station_list;
            (void)dom_station_iterate(stations, collect_station_info, &ctx);
            for (u32 i = 0u; i < station_list.size(); ++i) {
                u32 inv_count = 0u;
                append_u64(bytes, station_list[i].station_id);
                append_u64(bytes, station_list[i].body_id);
                append_u64(bytes, station_list[i].frame_id);
                if (dom_station_inventory_list(stations,
                                               station_list[i].station_id,
                                               0,
                                               0u,
                                               &inv_count) != DOM_STATION_REGISTRY_OK) {
                    inv_count = 0u;
                }
                append_u32(bytes, inv_count);
                if (inv_count > 0u) {
                    std::vector<dom_inventory_entry> inv;
                    inv.resize(inv_count);
                    if (dom_station_inventory_list(stations,
                                                   station_list[i].station_id,
                                                   &inv[0],
                                                   inv_count,
                                                   &inv_count) == DOM_STATION_REGISTRY_OK) {
                        for (u32 j = 0u; j < inv_count; ++j) {
                            append_u64(bytes, inv[j].resource_id);
                            append_i64(bytes, inv[j].quantity);
                        }
                    }
                }
            }
        }
    }

    {
        std::vector<dom_route_info> route_list;
        RouteCollectCtx ctx;
        u32 count = routes ? dom_route_graph_count(routes) : 0u;
        append_u32(bytes, count);
        if (routes && count > 0u) {
            ctx.routes = &route_list;
            (void)dom_route_graph_iterate(routes, collect_route_info, &ctx);
            for (u32 i = 0u; i < route_list.size(); ++i) {
                append_u64(bytes, route_list[i].route_id);
                append_u64(bytes, route_list[i].src_station_id);
                append_u64(bytes, route_list[i].dst_station_id);
                append_u64(bytes, route_list[i].duration_ticks);
                append_u64(bytes, route_list[i].capacity_units);
            }
        }
    }

    {
        u32 count = 0u;
        append_u32(bytes, sched ? dom_transfer_count(sched) : 0u);
        if (sched && dom_transfer_list(sched, 0, 0u, &count) == DOM_TRANSFER_OK && count > 0u) {
            std::vector<dom_transfer_info> transfers;
            transfers.resize(count);
            if (dom_transfer_list(sched, &transfers[0], count, &count) == DOM_TRANSFER_OK) {
                for (u32 i = 0u; i < count; ++i) {
                    std::vector<dom_transfer_entry> entries;
                    u32 entry_count = transfers[i].entry_count;
                    append_u64(bytes, transfers[i].transfer_id);
                    append_u64(bytes, transfers[i].route_id);
                    append_u64(bytes, transfers[i].start_tick);
                    append_u64(bytes, transfers[i].arrival_tick);
                    append_u32(bytes, entry_count);
                    if (entry_count > 0u) {
                        entries.resize(entry_count);
                        if (dom_transfer_get_entries(sched,
                                                     transfers[i].transfer_id,
                                                     &entries[0],
                                                     entry_count,
                                                     &entry_count) == DOM_TRANSFER_OK) {
                            for (u32 j = 0u; j < entry_count; ++j) {
                                append_u64(bytes, entries[j].resource_id);
                                append_i64(bytes, entries[j].quantity);
                            }
                        }
                    }
                }
            }
        }
    }

    {
        std::vector<dom_production_rule_info> rules;
        ProductionCollectCtx ctx;
        u32 count = prod ? dom_production_count(prod) : 0u;
        append_u32(bytes, count);
        if (prod && count > 0u) {
            ctx.rules = &rules;
            (void)dom_production_iterate(prod, collect_production_info, &ctx);
            for (u32 i = 0u; i < rules.size(); ++i) {
                append_u64(bytes, rules[i].rule_id);
                append_u64(bytes, rules[i].station_id);
                append_u64(bytes, rules[i].resource_id);
                append_i64(bytes, rules[i].delta_per_period);
                append_u64(bytes, rules[i].period_ticks);
            }
        }
    }

    return bytes.empty() ? 0ull : dom::core_tlv::tlv_fnv1a64(&bytes[0], bytes.size());
}

int main(void) {
    const char *path = "tmp_logistics_save.dmsg";
    TestRuntime a;
    TestRuntime b;
    dom_station_registry *stations = 0;
    dom_route_graph *routes = 0;
    dom_transfer_scheduler *sched = 0;
    dom_production *prod = 0;
    dom_station_desc s1;
    dom_station_desc s2;
    dom_route_desc route;
    dom_transfer_entry entry;
    dom_production_rule_desc rule;
    dom_transfer_id out_id = 0ull;
    dom_body_id earth_id = 0ull;
    u64 hash_a = 0ull;
    u64 hash_b = 0ull;

    assert(setup_runtime(a));
    assert(setup_runtime(b));

    assert(dom_id_hash64("earth", 5u, &earth_id) == DOM_SPACETIME_OK);
    stations = (dom_station_registry *)dom_game_runtime_station_registry(a.rt);
    routes = (dom_route_graph *)dom_game_runtime_route_graph(a.rt);
    sched = (dom_transfer_scheduler *)dom_game_runtime_transfer_scheduler(a.rt);
    prod = (dom_production *)dom_game_runtime_production(a.rt);
    assert(stations && routes && sched && prod);

    s1.station_id = 1ull;
    s1.body_id = earth_id;
    s1.frame_id = 0ull;
    s2.station_id = 2ull;
    s2.body_id = earth_id;
    s2.frame_id = 0ull;
    assert(dom_station_register(stations, &s1) == DOM_STATION_REGISTRY_OK);
    assert(dom_station_register(stations, &s2) == DOM_STATION_REGISTRY_OK);
    assert(dom_station_inventory_add(stations, s1.station_id, 1000ull, 40) == DOM_STATION_REGISTRY_OK);

    route.route_id = 10ull;
    route.src_station_id = s1.station_id;
    route.dst_station_id = s2.station_id;
    route.duration_ticks = 4ull;
    route.capacity_units = 50ull;
    assert(dom_route_graph_register(routes, &route) == DOM_ROUTE_GRAPH_OK);

    entry.resource_id = 1000ull;
    entry.quantity = 15;
    assert(dom_transfer_schedule(sched,
                                 routes,
                                 stations,
                                 route.route_id,
                                 &entry,
                                 1u,
                                 1ull,
                                 &out_id) == DOM_TRANSFER_OK);

    rule.rule_id = 1ull;
    rule.station_id = s2.station_id;
    rule.resource_id = 2000ull;
    rule.delta_per_period = 2;
    rule.period_ticks = 5ull;
    assert(dom_production_register(prod, &rule) == DOM_PRODUCTION_OK);

    hash_a = logistics_state_hash(a.rt);
    dom_io_guard_reset();
    assert(dom_game_runtime_save(a.rt, path) == DOM_GAME_SAVE_OK);
    assert(dom_game_runtime_load_save(b.rt, path) == DOM_GAME_SAVE_OK);
    hash_b = logistics_state_hash(b.rt);
    assert(hash_a == hash_b);

    teardown_runtime(b);
    teardown_runtime(a);
    std::remove(path);

    std::printf("dom_logistics_save_load_roundtrip_test: OK\n");
    return 0;
}
