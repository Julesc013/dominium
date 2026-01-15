/*
FILE: source/tests/dom_qos_overload_test.cpp
MODULE: Dominium Tests
PURPOSE: Validate overload reductions and ensure sim ticks continue.
*/
#include <cstdio>
#include <cstring>

extern "C" {
#include "domino/core/types.h"
#include "domino/core/fixed.h"
}

#include "dom_session.h"
#include "dom_game_net.h"
#include "runtime/dom_game_runtime.h"
#include "runtime/dom_io_guard.h"
#include "runtime/dom_qos.h"

static int fail(const char *msg) {
    std::fprintf(stderr, "FAIL: %s\n", msg ? msg : "(null)");
    return 1;
}

static void init_paths(dom::Paths &paths) {
    paths.root = ".";
    paths.products = ".";
    paths.mods = ".";
    paths.packs = ".";
    paths.instances = ".";
    paths.temp = ".";
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

void DomGameNet::shutdown() {
}

void DomGameNet::pump(d_world *world, d_sim_context *sim, const InstanceInfo &inst) {
    (void)world;
    (void)sim;
    (void)inst;
}

bool DomGameNet::submit_cmd(d_net_cmd *in_out_cmd) {
    (void)in_out_cmd;
    return false;
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

int main() {
    dom::Paths paths;
    dom::InstanceInfo inst;
    dom::SessionConfig cfg;
    dom::DomSession session;
    dom::DomGameNet net;
    dom_game_runtime_init_desc desc;
    dom_game_runtime *rt;
    u64 tick0;
    u64 tick1;
    u64 tick2;
    u32 stepped;
    dom_qos_policy base;
    dom_qos_policy overloaded;
    dom_qos_state state;
    dom_qos_policy effective;

    init_paths(paths);
    inst.id = "test_instance";
    inst.world_seed = 123u;
    inst.world_size_m = 1024u;
    inst.vertical_min_m = -64;
    inst.vertical_max_m = 64;
    inst.suite_version = 1u;
    inst.core_version = 1u;
    inst.packs.clear();
    inst.mods.clear();

    cfg.platform_backend = "null";
    cfg.gfx_backend = "null";
    cfg.audio_backend = "null";
    cfg.headless = true;
    cfg.tui = false;
    cfg.allow_missing_content = true;

    if (!session.init(paths, inst, cfg)) {
        return fail("session_init");
    }

    std::memset(&desc, 0, sizeof(desc));
    desc.struct_size = sizeof(desc);
    desc.struct_version = DOM_GAME_RUNTIME_INIT_DESC_VERSION;
    desc.session = &session;
    desc.net = &net;
    desc.instance = &inst;
    desc.ups = 60u;
    desc.run_id = 1u;

    rt = dom_game_runtime_create(&desc);
    if (!rt) {
        session.shutdown();
        return fail("runtime_create");
    }

    dom_io_guard_reset();
    tick0 = dom_game_runtime_get_tick(rt);
    stepped = 0u;
    if (dom_game_runtime_tick_wall(rt, 1000000ull, &stepped) != DOM_GAME_RUNTIME_OK ||
        stepped == 0u) {
        dom_game_runtime_destroy(rt);
        session.shutdown();
        return fail("tick_wall_pre");
    }
    tick1 = dom_game_runtime_get_tick(rt);
    if (tick1 <= tick0) {
        dom_game_runtime_destroy(rt);
        session.shutdown();
        return fail("tick_not_advanced");
    }

    std::memset(&base, 0, sizeof(base));
    base.snapshot_hz = 60u;
    base.delta_detail = 100u;
    base.interest_radius_m = 1024u;
    base.recommended_profile = 0u;
    base.server_load_hint = DOM_QOS_SERVER_LOAD_NOMINAL;
    base.assist_flags = DOM_QOS_ASSIST_LOCAL_MESH | DOM_QOS_ASSIST_LOCAL_CACHE;

    if (dom_qos_init(&state, &base) != DOM_QOS_OK) {
        dom_game_runtime_destroy(rt);
        session.shutdown();
        return fail("qos_init");
    }

    overloaded = base;
    overloaded.server_load_hint = DOM_QOS_SERVER_LOAD_OVERLOADED;
    (void)dom_qos_apply_server_policy(&state, &overloaded);
    if (dom_qos_get_effective_params(&state, &effective) != DOM_QOS_OK) {
        dom_game_runtime_destroy(rt);
        session.shutdown();
        return fail("qos_effective");
    }
    if (effective.snapshot_hz >= base.snapshot_hz) {
        dom_game_runtime_destroy(rt);
        session.shutdown();
        return fail("snapshot_hz_not_reduced");
    }

    stepped = 0u;
    if (dom_game_runtime_tick_wall(rt, 1000000ull, &stepped) != DOM_GAME_RUNTIME_OK ||
        stepped == 0u) {
        dom_game_runtime_destroy(rt);
        session.shutdown();
        return fail("tick_wall_post");
    }
    tick2 = dom_game_runtime_get_tick(rt);
    if (tick2 <= tick1) {
        dom_game_runtime_destroy(rt);
        session.shutdown();
        return fail("tick_not_advanced_post");
    }

    dom_game_runtime_destroy(rt);
    session.shutdown();
    return 0;
}
