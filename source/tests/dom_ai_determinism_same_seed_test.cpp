/*
FILE: source/tests/dom_ai_determinism_same_seed_test.cpp
MODULE: Repository Tests
PURPOSE: Ensure AI scheduler outputs are deterministic for identical inputs.
*/
#include <cassert>
#include <cstdio>
#include <cstring>
#include <vector>

extern "C" {
#include "domino/core/types.h"
#include "domino/core/spacetime.h"
}

#include "dom_session.h"
#include "dom_instance.h"
#include "dom_paths.h"
#include "dom_game_net.h"
#include "dominium/core_tlv.h"
#include "runtime/dom_game_runtime.h"
#include "runtime/dom_faction_registry.h"
#include "runtime/dom_ai_scheduler.h"
#include "runtime/dom_macro_economy.h"
#include "runtime/dom_station_registry.h"

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

struct FactionCollectCtx {
    std::vector<dom_faction_info> *factions;
};

static void collect_faction_info(const dom_faction_info *info, void *user) {
    FactionCollectCtx *ctx = static_cast<FactionCollectCtx *>(user);
    if (ctx && ctx->factions && info) {
        ctx->factions->push_back(*info);
    }
}

static u64 ai_state_hash(const dom_game_runtime *rt) {
    std::vector<unsigned char> bytes;
    const dom_faction_registry *factions =
        (const dom_faction_registry *)dom_game_runtime_faction_registry(rt);
    const dom_ai_scheduler *sched =
        (const dom_ai_scheduler *)dom_game_runtime_ai_scheduler(rt);

    u32 faction_count = factions ? dom_faction_count(factions) : 0u;
    append_u32(bytes, faction_count);

    if (factions && faction_count > 0u) {
        std::vector<dom_faction_info> list;
        FactionCollectCtx ctx;
        list.reserve(faction_count);
        ctx.factions = &list;
        (void)dom_faction_iterate(factions, collect_faction_info, &ctx);

        for (size_t i = 0u; i < list.size(); ++i) {
            u32 res_count = 0u;
            u32 node_count = 0u;
            append_u64(bytes, list[i].faction_id);
            append_u32(bytes, list[i].home_scope_kind);
            append_u64(bytes, list[i].home_scope_id);
            append_u32(bytes, list[i].policy_kind);
            append_u32(bytes, list[i].policy_flags);
            append_u64(bytes, list[i].ai_seed);
            if (dom_faction_resource_list(factions,
                                          list[i].faction_id,
                                          0,
                                          0u,
                                          &res_count) != DOM_FACTION_OK) {
                res_count = 0u;
            }
            append_u32(bytes, res_count);
            if (res_count > 0u) {
                std::vector<dom_faction_resource_entry> entries;
                entries.resize(res_count);
                if (dom_faction_resource_list(factions,
                                              list[i].faction_id,
                                              &entries[0],
                                              res_count,
                                              &res_count) == DOM_FACTION_OK) {
                    for (u32 j = 0u; j < res_count; ++j) {
                        append_u64(bytes, entries[j].resource_id);
                        append_i64(bytes, entries[j].quantity);
                    }
                } else {
                    res_count = 0u;
                }
            }
            if (dom_faction_list_known_nodes(factions,
                                             list[i].faction_id,
                                             0,
                                             0u,
                                             &node_count) != DOM_FACTION_OK) {
                node_count = 0u;
            }
            append_u32(bytes, node_count);
            if (node_count > 0u) {
                std::vector<u64> nodes;
                nodes.resize(node_count);
                if (dom_faction_list_known_nodes(factions,
                                                 list[i].faction_id,
                                                 &nodes[0],
                                                 node_count,
                                                 &node_count) == DOM_FACTION_OK) {
                    for (u32 j = 0u; j < node_count; ++j) {
                        append_u64(bytes, nodes[j]);
                    }
                }
            }
        }
    }

    {
        u32 state_count = 0u;
        if (sched && dom_ai_scheduler_list_states(sched, 0, 0u, &state_count) == DOM_AI_SCHEDULER_OK) {
            append_u32(bytes, state_count);
            if (state_count > 0u) {
                std::vector<dom_ai_faction_state> states;
                states.resize(state_count);
                if (dom_ai_scheduler_list_states(sched,
                                                 &states[0],
                                                 state_count,
                                                 &state_count) == DOM_AI_SCHEDULER_OK) {
                    for (u32 i = 0u; i < state_count; ++i) {
                        append_u64(bytes, states[i].faction_id);
                        append_u64(bytes, states[i].next_decision_tick);
                        append_u64(bytes, states[i].last_plan_id);
                        append_u32(bytes, states[i].last_output_count);
                        append_u32(bytes, states[i].last_reason_code);
                        append_u32(bytes, states[i].last_budget_hit);
                    }
                }
            }
        } else {
            append_u32(bytes, 0u);
        }
    }

    if (bytes.empty()) {
        return 0ull;
    }
    return dom::core_tlv::tlv_fnv1a64(&bytes[0], bytes.size());
}

static bool setup_ai_baseline(TestRuntime &tr, u32 faction_count) {
    dom_faction_registry *factions =
        (dom_faction_registry *)dom_game_runtime_faction_registry(tr.rt);
    dom_macro_economy *econ =
        (dom_macro_economy *)dom_game_runtime_macro_economy(tr.rt);
    dom_station_registry *stations =
        (dom_station_registry *)dom_game_runtime_station_registry(tr.rt);
    dom_body_id earth_id = 0ull;
    dom_system_id sol_id = 0ull;
    dom_station_desc s1;
    dom_station_desc s2;
    dom_faction_desc fdesc;
    dom_faction_resource_delta delta;
    const dom_resource_id resource_id = 5000ull;

    if (!factions || !econ || !stations) {
        return false;
    }
    if (dom_id_hash64("earth", 5u, &earth_id) != DOM_SPACETIME_OK) {
        return false;
    }
    if (dom_id_hash64("sol", 3u, &sol_id) != DOM_SPACETIME_OK) {
        return false;
    }

    std::memset(&s1, 0, sizeof(s1));
    s1.station_id = 1ull;
    s1.body_id = earth_id;
    s1.frame_id = 0ull;
    std::memset(&s2, 0, sizeof(s2));
    s2.station_id = 2ull;
    s2.body_id = earth_id;
    s2.frame_id = 0ull;
    if (dom_station_register(stations, &s1) != DOM_STATION_REGISTRY_OK) {
        return false;
    }
    if (dom_station_register(stations, &s2) != DOM_STATION_REGISTRY_OK) {
        return false;
    }
    if (dom_station_inventory_add(stations, s1.station_id, resource_id, 25) != DOM_STATION_REGISTRY_OK) {
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

    for (u32 i = 0u; i < faction_count; ++i) {
        std::memset(&fdesc, 0, sizeof(fdesc));
        fdesc.faction_id = 1ull + (u64)i;
        fdesc.home_scope_kind = DOM_MACRO_SCOPE_SYSTEM;
        fdesc.home_scope_id = sol_id;
        fdesc.policy_kind = DOM_FACTION_POLICY_BALANCED;
        fdesc.policy_flags = DOM_FACTION_POLICY_ALLOW_STATION |
                             DOM_FACTION_POLICY_ALLOW_ROUTE |
                             DOM_FACTION_POLICY_ALLOW_EVENTS;
        fdesc.ai_seed = 111ull + (u64)i;
        fdesc.known_nodes = 0;
        fdesc.known_node_count = 0u;
        if (dom_faction_register(factions, &fdesc) != DOM_FACTION_OK) {
            return false;
        }
        delta.resource_id = resource_id;
        delta.delta = 5;
        if (dom_faction_update_resources(factions, fdesc.faction_id, &delta, 1u) != DOM_FACTION_OK) {
            return false;
        }
    }
    return true;
}

int main(void) {
    TestRuntime a;
    TestRuntime b;
    u64 hash_a = 0ull;
    u64 hash_b = 0ull;
    u64 sim_a = 0ull;
    u64 sim_b = 0ull;

    assert(setup_runtime(a));
    assert(setup_runtime(b));
    assert(setup_ai_baseline(a, 1u));
    assert(setup_ai_baseline(b, 1u));

    for (u32 i = 0u; i < 2u; ++i) {
        assert(dom_game_runtime_step(a.rt) == DOM_GAME_RUNTIME_OK);
        assert(dom_game_runtime_step(b.rt) == DOM_GAME_RUNTIME_OK);
    }

    hash_a = ai_state_hash(a.rt);
    hash_b = ai_state_hash(b.rt);
    sim_a = dom_game_runtime_get_hash(a.rt);
    sim_b = dom_game_runtime_get_hash(b.rt);
    assert(hash_a != 0ull);
    assert(hash_a == hash_b);
    assert(sim_a == sim_b);

    teardown_runtime(b);
    teardown_runtime(a);
    std::printf("dom_ai_determinism_same_seed_test: OK\n");
    return 0;
}
