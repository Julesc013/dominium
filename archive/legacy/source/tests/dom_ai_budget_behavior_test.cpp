/*
FILE: source/tests/dom_ai_budget_behavior_test.cpp
MODULE: Repository Tests
PURPOSE: Ensure AI scheduler honors budgets deterministically.
*/
#include <cassert>
#include <cstdio>
#include <cstring>

extern "C" {
#include "domino/core/types.h"
#include "domino/core/spacetime.h"
}

#include "dom_session.h"
#include "dom_instance.h"
#include "dom_paths.h"
#include "dom_game_net.h"
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
    }
    return true;
}

int main(void) {
    TestRuntime tr;
    dom_ai_scheduler *sched = 0;
    dom_ai_faction_state f1;
    dom_ai_faction_state f2;

    assert(setup_runtime(tr));
    assert(setup_ai_baseline(tr, 2u));

    sched = (dom_ai_scheduler *)dom_game_runtime_ai_scheduler(tr.rt);
    assert(sched);
    assert(dom_ai_scheduler_set_budget(sched, 1u, 2u) == DOM_AI_SCHEDULER_OK);

    assert(dom_game_runtime_step(tr.rt) == DOM_GAME_RUNTIME_OK);

    assert(dom_ai_scheduler_get_state(sched, 1ull, &f1) == DOM_AI_SCHEDULER_OK);
    assert(dom_ai_scheduler_get_state(sched, 2ull, &f2) == DOM_AI_SCHEDULER_OK);
    assert(f1.last_budget_hit == 0u);
    assert(f2.last_budget_hit == 1u);
    assert(f2.last_reason_code == DOM_AI_REASON_BUDGET_HIT);

    teardown_runtime(tr);
    std::printf("dom_ai_budget_behavior_test: OK\n");
    return 0;
}
