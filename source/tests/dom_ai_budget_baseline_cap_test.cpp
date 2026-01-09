/*
FILE: source/tests/dom_ai_budget_baseline_cap_test.cpp
MODULE: Repository Tests
PURPOSE: Ensure baseline-tier AI budgets cap per-tick faction processing.
*/
#include <cassert>
#include <cstdio>
#include <cstring>
#include <vector>

extern "C" {
#include "domino/core/types.h"
#include "domino/core/spacetime.h"
#include "domino/core/fixed.h"
}

#include "dom_session.h"
#include "dom_instance.h"
#include "dom_paths.h"
#include "dom_game_net.h"
#include "dominium/caps_split.h"
#include "runtime/dom_game_runtime.h"
#include "runtime/dom_game_budgets.h"
#include "runtime/dom_faction_registry.h"
#include "runtime/dom_ai_scheduler.h"
#include "runtime/dom_macro_economy.h"
#include "runtime/dom_system_registry.h"
#include "runtime/dom_body_registry.h"

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

static bool register_systems_and_bodies(dom_system_registry *systems,
                                        dom_body_registry *bodies,
                                        u32 count,
                                        std::vector<dom_system_id> &out_systems) {
    if (!systems || !bodies) {
        return false;
    }
    out_systems.clear();
    out_systems.reserve(count);

    for (u32 i = 0u; i < count; ++i) {
        char sys_name[32];
        char body_name[32];
        u32 sys_len;
        u32 body_len;
        dom_system_desc sdesc;
        dom_body_desc bdesc;
        dom_system_id sys_id = 0ull;
        dom_body_id body_id = 0ull;

        std::snprintf(sys_name, sizeof(sys_name), "sys_%u", (unsigned)i);
        sys_len = (u32)std::strlen(sys_name);
        if (dom_id_hash64(sys_name, sys_len, &sys_id) != DOM_SPACETIME_OK || sys_id == 0ull) {
            return false;
        }
        std::memset(&sdesc, 0, sizeof(sdesc));
        sdesc.string_id = sys_name;
        sdesc.string_id_len = sys_len;
        sdesc.id = sys_id;
        sdesc.parent_id = 0ull;
        if (dom_system_registry_register(systems, &sdesc) != DOM_SYSTEM_REGISTRY_OK) {
            return false;
        }

        std::snprintf(body_name, sizeof(body_name), "body_%u", (unsigned)i);
        body_len = (u32)std::strlen(body_name);
        if (dom_id_hash64(body_name, body_len, &body_id) != DOM_SPACETIME_OK || body_id == 0ull) {
            return false;
        }
        std::memset(&bdesc, 0, sizeof(bdesc));
        bdesc.string_id = body_name;
        bdesc.string_id_len = body_len;
        bdesc.id = body_id;
        bdesc.system_id = sys_id;
        bdesc.kind = DOM_BODY_KIND_PLANET;
        bdesc.radius_m = d_q48_16_from_int(1000);
        bdesc.mu_m3_s2 = 1000000ull;
        bdesc.rotation_period_ticks = 1000ull;
        bdesc.rotation_epoch_tick = 0ull;
        bdesc.axial_tilt_turns = 0;
        bdesc.has_axial_tilt = 0u;
        if (dom_body_registry_register(bodies, &bdesc) != DOM_BODY_REGISTRY_OK) {
            return false;
        }

        out_systems.push_back(sys_id);
    }

    return true;
}

static bool seed_economy(dom_macro_economy *econ,
                         const std::vector<dom_system_id> &systems) {
    const dom_resource_id resource_id = 5000ull;
    if (!econ) {
        return false;
    }
    for (size_t i = 0u; i < systems.size(); ++i) {
        if (dom_macro_economy_rate_set(econ,
                                       DOM_MACRO_SCOPE_SYSTEM,
                                       systems[i],
                                       resource_id,
                                       0,
                                       1) != DOM_MACRO_ECONOMY_OK) {
            return false;
        }
    }
    return true;
}

static bool register_factions(dom_faction_registry *factions,
                              const std::vector<dom_system_id> &systems) {
    if (!factions) {
        return false;
    }
    for (size_t i = 0u; i < systems.size(); ++i) {
        dom_faction_desc fdesc;
        std::memset(&fdesc, 0, sizeof(fdesc));
        fdesc.faction_id = 1ull + (u64)i;
        fdesc.home_scope_kind = DOM_MACRO_SCOPE_SYSTEM;
        fdesc.home_scope_id = systems[i];
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
    std::vector<dom_system_id> systems;
    dom_system_registry *sys_reg = 0;
    dom_body_registry *body_reg = 0;
    dom_macro_economy *econ = 0;
    dom_faction_registry *factions = 0;
    dom_ai_scheduler *sched = 0;
    dom_game_budget_profile profile;
    u32 state_count = 0u;
    u32 processed = 0u;
    u64 tick = 0ull;

    assert(setup_runtime(tr));

    sys_reg = (dom_system_registry *)dom_game_runtime_system_registry(tr.rt);
    body_reg = (dom_body_registry *)dom_game_runtime_body_registry(tr.rt);
    econ = (dom_macro_economy *)dom_game_runtime_macro_economy(tr.rt);
    factions = (dom_faction_registry *)dom_game_runtime_faction_registry(tr.rt);
    assert(sys_reg && body_reg && econ && factions);

    assert(register_systems_and_bodies(sys_reg, body_reg, 100u, systems));
    assert(seed_economy(econ, systems));
    assert(register_factions(factions, systems));

    sched = (dom_ai_scheduler *)dom_game_runtime_ai_scheduler(tr.rt);
    assert(sched);
    assert(dom_game_budget_profile_for_tier(dom::DOM_PERF_TIER_BASELINE, &profile) ==
           DOM_GAME_BUDGET_OK);
    assert(profile.ai_max_factions_per_tick > 0u);
    assert(profile.ai_max_factions_per_tick < (u32)systems.size());
    assert(dom_ai_scheduler_set_budget(sched,
                                       profile.ai_max_ops_per_tick,
                                       profile.ai_max_factions_per_tick) ==
           DOM_AI_SCHEDULER_OK);

    assert(dom_game_runtime_step(tr.rt) == DOM_GAME_RUNTIME_OK);
    tick = dom_game_runtime_get_tick(tr.rt);

    assert(dom_ai_scheduler_list_states(sched, 0, 0u, &state_count) == DOM_AI_SCHEDULER_OK);
    assert(state_count == systems.size());

    {
        std::vector<dom_ai_faction_state> states;
        states.resize(state_count);
        assert(dom_ai_scheduler_list_states(sched,
                                            &states[0],
                                            state_count,
                                            &state_count) == DOM_AI_SCHEDULER_OK);
        for (u32 i = 0u; i < state_count; ++i) {
            if (states[i].next_decision_tick > tick) {
                processed += 1u;
            }
        }
    }

    assert(processed == profile.ai_max_factions_per_tick);
    assert(processed < state_count);

    teardown_runtime(tr);
    std::printf("dom_ai_budget_baseline_cap_test: OK\n");
    return 0;
}
