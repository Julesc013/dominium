/*
FILE: source/tests/dom_orbit_warp_authority_test.cpp
MODULE: Repository Tests
PURPOSE: Verifies warp command authority enforcement in net driver.
*/
#include <cassert>
#include <cstdio>
#include <cstring>
#include <string>
#include <vector>

extern "C" {
#include "domino/core/types.h"
}

#include "dom_session.h"
#include "dom_instance.h"
#include "dom_paths.h"
#include "dom_game_net.h"
#include "runtime/dom_game_runtime.h"
#include "runtime/dom_game_net_driver.h"
#include "runtime/dom_game_command.h"

extern "C" {
#include "net/d_net_schema.h"
}

namespace {

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

static void append_u32(std::vector<unsigned char> &out, u32 v) {
    out.push_back((unsigned char)(v & 0xffu));
    out.push_back((unsigned char)((v >> 8u) & 0xffu));
    out.push_back((unsigned char)((v >> 16u) & 0xffu));
    out.push_back((unsigned char)((v >> 24u) & 0xffu));
}

static void append_tlv_u32(std::vector<unsigned char> &out, u32 tag, u32 v) {
    append_u32(out, tag);
    append_u32(out, 4u);
    append_u32(out, v);
}

static void build_warp_command(dom_game_command &cmd,
                               std::vector<unsigned char> &payload,
                               u32 factor) {
    std::memset(&cmd, 0, sizeof(cmd));
    payload.clear();
    append_tlv_u32(payload, D_NET_TLV_WARP_FACTOR, factor);

    cmd.struct_size = sizeof(cmd);
    cmd.struct_version = DOM_GAME_COMMAND_VERSION;
    cmd.schema_id = D_NET_SCHEMA_CMD_WARP_V1;
    cmd.schema_ver = 1u;
    cmd.tick = 0u;
    cmd.payload = payload.empty() ? (const void *)0 : &payload[0];
    cmd.payload_size = (u32)payload.size();
}

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

static int assert_warp_result(dom::DomSessionRole role,
                              dom::DomSessionAuthority authority,
                              int expect_ok) {
    TestRuntime tr;
    dom::DomSessionConfig cfg;
    dom::DomNetDriverContext ctx;
    dom::DomNetDriver *driver = 0;
    dom_game_command cmd;
    std::vector<unsigned char> payload;
    u32 tick = 0u;
    int rc = 0;

    if (!setup_runtime(tr)) {
        teardown_runtime(tr);
        return 1;
    }

    std::memset(&cfg, 0, sizeof(cfg));
    cfg.struct_size = sizeof(cfg);
    cfg.struct_version = DOM_GAME_SESSION_CONFIG_VERSION;
    cfg.role = role;
    cfg.authority = authority;
    cfg.tick_rate_hz = 60u;
    cfg.input_delay_ticks = 1u;
    cfg.struct_size = sizeof(cfg);
    cfg.struct_version = DOM_GAME_SESSION_CONFIG_VERSION;

    ctx.net = &tr.net;
    ctx.runtime = tr.rt;
    ctx.instance = &tr.inst;
    ctx.paths = 0;

    driver = dom::dom_net_driver_create(cfg, ctx, 0);
    assert(driver);

    build_warp_command(cmd, payload, 2u);
    rc = driver->submit_local_command(&cmd, &tick);
    if (expect_ok) {
        assert(rc == dom::DOM_NET_DRIVER_OK);
    } else {
        assert(rc == dom::DOM_NET_DRIVER_ERR);
    }

    dom::dom_net_driver_destroy(driver);
    teardown_runtime(tr);
    return 0;
}

} // namespace

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
    shutdown();
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

int main(void) {
    assert(assert_warp_result(dom::DOM_SESSION_ROLE_CLIENT,
                              dom::DOM_SESSION_AUTH_SERVER_AUTH, 0) == 0);
    assert(assert_warp_result(dom::DOM_SESSION_ROLE_HOST,
                              dom::DOM_SESSION_AUTH_SERVER_AUTH, 1) == 0);
    assert(assert_warp_result(dom::DOM_SESSION_ROLE_CLIENT,
                              dom::DOM_SESSION_AUTH_LOCKSTEP, 0) == 0);
    assert(assert_warp_result(dom::DOM_SESSION_ROLE_HOST,
                              dom::DOM_SESSION_AUTH_LOCKSTEP, 1) == 0);

    std::printf("dom_orbit_warp_authority_test: OK\n");
    return 0;
}
