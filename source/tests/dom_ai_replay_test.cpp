/*
FILE: source/tests/dom_ai_replay_test.cpp
MODULE: Repository Tests
PURPOSE: Ensure AI-generated commands replay deterministically.
*/
#include <cassert>
#include <cstdio>
#include <cstring>
#include <vector>

extern "C" {
#include "domino/core/types.h"
#include "domino/core/spacetime.h"
#include "domino/core/d_tlv_kv.h"
}

#include "dom_session.h"
#include "dom_instance.h"
#include "dom_paths.h"
#include "dom_game_net.h"
#include "dominium/core_tlv.h"
#include "runtime/dom_game_runtime.h"
#include "runtime/dom_game_replay.h"
#include "runtime/dom_ai_planner_logistics.h"
#include "runtime/dom_macro_economy.h"
#include "runtime/dom_station_registry.h"
#include "runtime/dom_route_graph.h"
#include "runtime/dom_body_registry.h"
#include "runtime/dom_system_registry.h"

extern "C" {
#include "net/d_net_schema.h"
#include "net/d_net_proto.h"
}

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

static u64 station_registry_hash(dom_station_registry *registry) {
    std::vector<unsigned char> bytes;
    u32 count = registry ? dom_station_count(registry) : 0u;
    append_u32(bytes, count);
    if (count == 0u || !registry) {
        return 0ull;
    }
    {
        std::vector<dom_station_info> list;
        StationCollectCtx ctx;
        list.reserve(count);
        ctx.stations = &list;
        (void)dom_station_iterate(registry, collect_station_info, &ctx);
        for (size_t i = 0u; i < list.size(); ++i) {
            u32 inv_count = 0u;
            append_u64(bytes, list[i].station_id);
            append_u64(bytes, list[i].body_id);
            append_u64(bytes, list[i].frame_id);
            if (dom_station_inventory_list(registry,
                                           list[i].station_id,
                                           0,
                                           0u,
                                           &inv_count) != DOM_STATION_REGISTRY_OK) {
                inv_count = 0u;
            }
            append_u32(bytes, inv_count);
            if (inv_count > 0u) {
                std::vector<dom_inventory_entry> inv;
                inv.resize(inv_count);
                if (dom_station_inventory_list(registry,
                                               list[i].station_id,
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
    return dom::core_tlv::tlv_fnv1a64(&bytes[0], bytes.size());
}

static bool build_ai_commands(dom_game_runtime *rt,
                              std::vector<dom_ai_planned_cmd> &out_cmds) {
    dom_macro_economy *econ = (dom_macro_economy *)dom_game_runtime_macro_economy(rt);
    dom_station_registry *stations =
        (dom_station_registry *)dom_game_runtime_station_registry(rt);
    dom_route_graph *routes =
        (dom_route_graph *)dom_game_runtime_route_graph(rt);
    dom_body_registry *bodies =
        (dom_body_registry *)dom_game_runtime_body_registry(rt);
    dom_system_registry *systems =
        (dom_system_registry *)dom_game_runtime_system_registry(rt);
    dom_faction_info faction;
    dom_system_id sol_id = 0ull;
    const dom_resource_id resource_id = 5000ull;
    dom_ai_planner_logistics_result result;

    if (!econ || !stations || !routes || !bodies || !systems) {
        return false;
    }
    if (dom_id_hash64("sol", 3u, &sol_id) != DOM_SPACETIME_OK) {
        return false;
    }

    if (dom_macro_economy_rate_set(econ,
                                   DOM_MACRO_SCOPE_SYSTEM,
                                   sol_id,
                                   resource_id,
                                   0,
                                   3) != DOM_MACRO_ECONOMY_OK) {
        return false;
    }

    std::memset(&faction, 0, sizeof(faction));
    faction.faction_id = 1ull;
    faction.home_scope_kind = DOM_MACRO_SCOPE_SYSTEM;
    faction.home_scope_id = sol_id;
    faction.policy_kind = DOM_FACTION_POLICY_BALANCED;
    faction.policy_flags = DOM_FACTION_POLICY_ALLOW_STATION |
                           DOM_FACTION_POLICY_ALLOW_ROUTE |
                           DOM_FACTION_POLICY_ALLOW_EVENTS;
    faction.ai_seed = 111ull;

    if (dom_ai_planner_logistics_run(&faction,
                                     econ,
                                     stations,
                                     routes,
                                     bodies,
                                     systems,
                                     1ull,
                                     1u,
                                     &result) != DOM_AI_SCHEDULER_OK) {
        return false;
    }
    out_cmds = result.commands;
    return !out_cmds.empty();
}

static bool record_commands(const char *path,
                            const std::vector<dom_ai_planned_cmd> &cmds,
                            u32 tick_override) {
    dom_game_replay_record *rec;
    std::vector<unsigned char> packet;
    unsigned char tmp[2048];
    d_net_cmd cmd;
    u32 out_size = 0u;
    int rc;

    rec = dom_game_replay_record_open(path,
                                      60u,
                                      1ull,
                                      "inst",
                                      1ull,
                                      (const unsigned char *)0,
                                      0u,
                                      (const unsigned char *)0,
                                      0u,
                                      (const unsigned char *)0,
                                      0u,
                                      (const unsigned char *)0,
                                      0u,
                                      (const unsigned char *)0,
                                      0u,
                                      (const unsigned char *)0,
                                      0u,
                                      (const unsigned char *)0,
                                      0u,
                                      (const unsigned char *)0,
                                      0u,
                                      (const unsigned char *)0,
                                      0u);
    if (!rec) {
        return false;
    }

    for (size_t i = 0u; i < cmds.size(); ++i) {
        const dom_ai_planned_cmd &pcmd = cmds[i];
        u32 tick = pcmd.tick ? pcmd.tick : tick_override;
        std::memset(&cmd, 0, sizeof(cmd));
        cmd.id = 1u;
        cmd.source_peer = 1u;
        cmd.tick = tick;
        cmd.schema_id = pcmd.schema_id;
        cmd.schema_ver = pcmd.schema_ver;
        cmd.payload.ptr = pcmd.payload.empty() ? (unsigned char *)0
                                               : (unsigned char *)&pcmd.payload[0];
        cmd.payload.len = (u32)pcmd.payload.size();
        rc = d_net_encode_cmd(&cmd, tmp, (u32)sizeof(tmp), &out_size);
        if (rc != 0 || out_size == 0u) {
            dom_game_replay_record_close(rec);
            return false;
        }
        packet.assign(tmp, tmp + out_size);
        if (dom_game_replay_record_write_cmd(rec, tick, &packet[0], (u32)packet.size())
            != DOM_GAME_REPLAY_OK) {
            dom_game_replay_record_close(rec);
            return false;
        }
    }

    dom_game_replay_record_close(rec);
    return true;
}

static u64 run_replay_and_hash(dom_game_replay_play *playback, u32 last_tick) {
    TestRuntime tr;
    dom_station_registry *registry = 0;
    u64 hash = 0ull;

    if (!setup_runtime(tr)) {
        teardown_runtime(tr);
        return 0ull;
    }
    (void)dom_game_runtime_set_replay_playback(tr.rt, playback);
    (void)dom_game_runtime_set_replay_last_tick(tr.rt, last_tick);
    for (u32 i = 0u; i < last_tick; ++i) {
        int rc = dom_game_runtime_step(tr.rt);
        if (rc != DOM_GAME_RUNTIME_OK && rc != DOM_GAME_RUNTIME_REPLAY_END) {
            teardown_runtime(tr);
            return 0ull;
        }
    }
    registry = (dom_station_registry *)dom_game_runtime_station_registry(tr.rt);
    if (registry) {
        hash = station_registry_hash(registry);
    }
    teardown_runtime(tr);
    return hash;
}

int main(void) {
    const char *path = "tmp_ai_replay.dmrp";
    TestRuntime planner;
    std::vector<dom_ai_planned_cmd> cmds;
    dom_game_replay_play *play_a = 0;
    dom_game_replay_play *play_b = 0;
    dom_game_replay_desc desc;
    u64 hash_a = 0ull;
    u64 hash_b = 0ull;
    const u32 cmd_tick = 2u;
    const u32 last_tick = 3u;

    d_net_register_schemas();
    assert(setup_runtime(planner));
    assert(build_ai_commands(planner.rt, cmds));
    teardown_runtime(planner);

    assert(record_commands(path, cmds, cmd_tick));

    std::memset(&desc, 0, sizeof(desc));
    play_a = dom_game_replay_play_open(path, &desc);
    assert(play_a);
    play_b = dom_game_replay_play_open(path, &desc);
    assert(play_b);

    hash_a = run_replay_and_hash(play_a, last_tick);
    hash_b = run_replay_and_hash(play_b, last_tick);
    assert(hash_a != 0ull);
    assert(hash_a == hash_b);

    dom_game_replay_play_close(play_b);
    dom_game_replay_play_close(play_a);
    std::remove(path);

    std::printf("dom_ai_replay_test: OK\n");
    return 0;
}
