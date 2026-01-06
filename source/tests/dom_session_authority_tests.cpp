/*
FILE: source/tests/dom_session_authority_tests.cpp
MODULE: Dominium Tests
PURPOSE: Smoke tests for session roles/authority modes and desync bundle emission.
*/
#include <cstdio>
#include <cstring>
#include <fstream>
#include <map>
#include <string>
#include <vector>

extern "C" {
#include "domino/core/types.h"
#include "domino/core/fixed.h"
}

#include "dom_session.h"
#include "dom_game_net.h"
#include "runtime/dom_game_runtime.h"
#include "runtime/dom_game_net_driver.h"
#include "runtime/dom_game_session.h"
#include "runtime/dom_game_paths.h"
#include "runtime/dom_io_guard.h"

namespace {

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
    if (!tr.rt) {
        tr.session.shutdown();
        return false;
    }
    return true;
}

static void teardown_runtime(TestRuntime &tr) {
    if (tr.rt) {
        dom_game_runtime_destroy(tr.rt);
        tr.rt = 0;
    }
    tr.net.shutdown();
    tr.session.shutdown();
}

struct HashQueue {
    std::vector<d_net_hash> items;
};

static std::map<const dom::DomGameNet*, HashQueue> g_hash_queues;

static void queue_hash(dom::DomGameNet *net, u32 tick, u64 hash) {
    d_net_hash h;
    std::memset(&h, 0, sizeof(h));
    h.tick = tick;
    h.world_hash = hash;
    g_hash_queues[net].items.push_back(h);
}

static int test_server_auth_equivalence() {
    TestRuntime single_rt;
    TestRuntime host_rt;
    dom::DomSessionConfig single_cfg;
    dom::DomSessionConfig host_cfg;
    dom::DomNetDriverContext ctx_single;
    dom::DomNetDriverContext ctx_host;
    dom::DomNetDriver *driver_single = 0;
    dom::DomNetDriver *driver_host = 0;
    std::string err;
    u32 stepped = 0u;
    u64 hash_single = 0u;
    u64 hash_host = 0u;
    int rc = 0;
    unsigned i;

    if (!setup_runtime(single_rt) || !setup_runtime(host_rt)) {
        teardown_runtime(single_rt);
        teardown_runtime(host_rt);
        return fail("setup_runtime");
    }

    single_cfg.role = DOM_SESSION_ROLE_SINGLE;
    single_cfg.authority = DOM_SESSION_AUTH_SERVER_AUTH;
    single_cfg.tick_rate_hz = 60u;

    host_cfg.role = DOM_SESSION_ROLE_HOST;
    host_cfg.authority = DOM_SESSION_AUTH_SERVER_AUTH;
    host_cfg.tick_rate_hz = 60u;

    if (!dom::dom_session_config_validate(single_cfg, 0, 0)) {
        teardown_runtime(single_rt);
        teardown_runtime(host_rt);
        return fail("single_cfg_validate");
    }
    if (!dom::dom_session_config_validate(host_cfg, 0, 0)) {
        teardown_runtime(single_rt);
        teardown_runtime(host_rt);
        return fail("host_cfg_validate");
    }

    ctx_single.net = &single_rt.net;
    ctx_single.runtime = single_rt.rt;
    ctx_single.instance = &single_rt.inst;
    ctx_single.paths = 0;

    ctx_host.net = &host_rt.net;
    ctx_host.runtime = host_rt.rt;
    ctx_host.instance = &host_rt.inst;
    ctx_host.paths = 0;

    driver_single = dom::dom_net_driver_create(single_cfg, ctx_single, &err);
    if (!driver_single) {
        rc = fail("driver_single_create");
        goto cleanup;
    }
    driver_host = dom::dom_net_driver_create(host_cfg, ctx_host, &err);
    if (!driver_host) {
        rc = fail("driver_host_create");
        goto cleanup;
    }
    if (driver_single->start() != DOM_NET_DRIVER_OK ||
        driver_host->start() != DOM_NET_DRIVER_OK) {
        rc = fail("driver_start");
        goto cleanup;
    }

    for (i = 0u; i < 8u; ++i) {
        (void)driver_single->pump_network();
        (void)driver_host->pump_network();
        (void)dom_game_runtime_tick_wall(single_rt.rt, 16666ull, &stepped);
        (void)dom_game_runtime_tick_wall(host_rt.rt, 16666ull, &stepped);
    }

    hash_single = dom_game_runtime_get_hash(single_rt.rt);
    hash_host = dom_game_runtime_get_hash(host_rt.rt);
    if (hash_single != hash_host) {
        rc = fail("server_auth_hash_mismatch");
        goto cleanup;
    }

cleanup:
    if (driver_single) {
        driver_single->stop();
        dom::dom_net_driver_destroy(driver_single);
    }
    if (driver_host) {
        driver_host->stop();
        dom::dom_net_driver_destroy(driver_host);
    }
    teardown_runtime(single_rt);
    teardown_runtime(host_rt);
    return rc;
}

static int test_lockstep_smoke() {
    TestRuntime host_rt;
    TestRuntime client_rt;
    dom::DomSessionConfig host_cfg;
    dom::DomSessionConfig client_cfg;
    dom::DomNetDriverContext ctx_host;
    dom::DomNetDriverContext ctx_client;
    dom::DomNetDriver *driver_host = 0;
    dom::DomNetDriver *driver_client = 0;
    u32 stepped = 0u;
    u64 hash_host = 0u;
    u64 hash_client = 0u;
    int rc = 0;
    unsigned i;

    if (!setup_runtime(host_rt) || !setup_runtime(client_rt)) {
        teardown_runtime(host_rt);
        teardown_runtime(client_rt);
        return fail("setup_runtime");
    }

    host_cfg.role = DOM_SESSION_ROLE_HOST;
    host_cfg.authority = DOM_SESSION_AUTH_LOCKSTEP;
    host_cfg.tick_rate_hz = 60u;

    client_cfg.role = DOM_SESSION_ROLE_CLIENT;
    client_cfg.authority = DOM_SESSION_AUTH_LOCKSTEP;
    client_cfg.tick_rate_hz = 60u;
    client_cfg.connect_addr = "127.0.0.1";

    if (!dom::dom_session_config_validate(host_cfg, 0, 0)) {
        teardown_runtime(host_rt);
        teardown_runtime(client_rt);
        return fail("lockstep_host_validate");
    }
    if (!dom::dom_session_config_validate(client_cfg, 0, 0)) {
        teardown_runtime(host_rt);
        teardown_runtime(client_rt);
        return fail("lockstep_client_validate");
    }

    ctx_host.net = &host_rt.net;
    ctx_host.runtime = host_rt.rt;
    ctx_host.instance = &host_rt.inst;
    ctx_host.paths = 0;

    ctx_client.net = &client_rt.net;
    ctx_client.runtime = client_rt.rt;
    ctx_client.instance = &client_rt.inst;
    ctx_client.paths = 0;

    driver_host = dom::dom_net_driver_create(host_cfg, ctx_host, 0);
    if (!driver_host) {
        rc = fail("lockstep_host_create");
        goto cleanup;
    }
    driver_client = dom::dom_net_driver_create(client_cfg, ctx_client, 0);
    if (!driver_client) {
        rc = fail("lockstep_client_create");
        goto cleanup;
    }
    if (driver_host->start() != DOM_NET_DRIVER_OK ||
        driver_client->start() != DOM_NET_DRIVER_OK) {
        rc = fail("lockstep_driver_start");
        goto cleanup;
    }

    for (i = 0u; i < 8u; ++i) {
        (void)driver_host->pump_network();
        (void)driver_client->pump_network();
        (void)dom_game_runtime_tick_wall(host_rt.rt, 16666ull, &stepped);
        (void)dom_game_runtime_tick_wall(client_rt.rt, 16666ull, &stepped);
    }

    hash_host = dom_game_runtime_get_hash(host_rt.rt);
    hash_client = dom_game_runtime_get_hash(client_rt.rt);
    if (hash_host != hash_client) {
        rc = fail("lockstep_hash_mismatch");
        goto cleanup;
    }

cleanup:
    if (driver_host) {
        driver_host->stop();
        dom::dom_net_driver_destroy(driver_host);
    }
    if (driver_client) {
        driver_client->stop();
        dom::dom_net_driver_destroy(driver_client);
    }
    teardown_runtime(host_rt);
    teardown_runtime(client_rt);
    return rc;
}

static int test_desync_bundle() {
    TestRuntime host_rt;
    dom::DomSessionConfig host_cfg;
    dom::DomNetDriverContext ctx;
    dom::DomGamePaths paths;
    dom::DomNetDriver *driver = 0;
    u64 tick = 0ull;
    u64 hash = 0ull;
    char name[64];
    std::string path;
    int rc = 0;

    if (!setup_runtime(host_rt)) {
        teardown_runtime(host_rt);
        return fail("setup_runtime");
    }

    host_cfg.role = DOM_SESSION_ROLE_HOST;
    host_cfg.authority = DOM_SESSION_AUTH_LOCKSTEP;
    host_cfg.tick_rate_hz = 60u;

    if (!dom::dom_session_config_validate(host_cfg, 0, 0)) {
        teardown_runtime(host_rt);
        return fail("desync_cfg_validate");
    }

    paths.run_root = ".";
    ctx.net = &host_rt.net;
    ctx.runtime = host_rt.rt;
    ctx.instance = &host_rt.inst;
    ctx.paths = &paths;

    driver = dom::dom_net_driver_create(host_cfg, ctx, 0);
    if (!driver) {
        rc = fail("desync_driver_create");
        goto cleanup;
    }
    if (driver->start() != DOM_NET_DRIVER_OK) {
        rc = fail("desync_driver_start");
        goto cleanup;
    }

    dom_io_guard_reset();
    (void)dom_game_runtime_step(host_rt.rt);
    tick = dom_game_runtime_get_tick(host_rt.rt);
    hash = dom_game_runtime_get_hash(host_rt.rt);
    queue_hash(&host_rt.net, (u32)tick, hash ^ 1ull);
    (void)driver->pump_network();

    std::snprintf(name, sizeof(name), "desync_bundle_%llu.tlv", (unsigned long long)tick);
    path = paths.run_root + "/" + name;
    {
        std::ifstream in(path.c_str(), std::ios::binary);
        if (!in) {
            rc = fail("desync_bundle_missing");
            goto cleanup;
        }
    }
    (void)std::remove(path.c_str());

cleanup:
    if (driver) {
        driver->stop();
        dom::dom_net_driver_destroy(driver);
    }
    teardown_runtime(host_rt);
    return rc;
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
    (void)d_net_session_init(&m_session, D_NET_ROLE_SINGLE, tick_rate);
    m_local_peer = 1u;
    m_ready = true;
    m_dedicated = false;
    m_handshake_sent = true;
    return true;
}

bool DomGameNet::init_listen(u32 tick_rate, unsigned port) {
    (void)port;
    (void)d_net_session_init(&m_session, D_NET_ROLE_HOST, tick_rate);
    m_local_peer = 1u;
    m_ready = true;
    m_dedicated = false;
    m_handshake_sent = true;
    return true;
}

bool DomGameNet::init_dedicated(u32 tick_rate, unsigned port) {
    (void)port;
    (void)d_net_session_init(&m_session, D_NET_ROLE_HOST, tick_rate);
    m_local_peer = 1u;
    m_ready = true;
    m_dedicated = true;
    m_handshake_sent = true;
    return true;
}

bool DomGameNet::init_client(u32 tick_rate, const std::string &addr_port) {
    (void)addr_port;
    (void)d_net_session_init(&m_session, D_NET_ROLE_CLIENT, tick_rate);
    m_local_peer = 1u;
    m_ready = true;
    m_dedicated = false;
    m_handshake_sent = true;
    return true;
}

void DomGameNet::shutdown() {
    d_net_session_shutdown(&m_session);
    std::memset(&m_session, 0, sizeof(m_session));
    m_ready = false;
    g_hash_queues.erase(this);
    m_hash_events.clear();
    m_qos_events.clear();
}

void DomGameNet::pump(d_world *world, d_sim_context *sim, const InstanceInfo &inst) {
    (void)sim;
    (void)inst;
    if (world) {
        m_session.tick = world->tick_count;
    }
}

bool DomGameNet::submit_cmd(d_net_cmd *in_out_cmd) {
    (void)in_out_cmd;
    return true;
}

bool DomGameNet::poll_hash(d_net_hash *out_hash) {
    HashQueue &queue = g_hash_queues[this];
    if (!out_hash || queue.items.empty()) {
        return false;
    }
    *out_hash = queue.items.front();
    queue.items.erase(queue.items.begin());
    return true;
}

bool DomGameNet::poll_qos(d_peer_id *out_peer, std::vector<unsigned char> &out_bytes) {
    (void)out_peer;
    out_bytes.clear();
    return false;
}

} // namespace dom

int main() {
    int rc;
    rc = test_server_auth_equivalence();
    if (rc) {
        return rc;
    }
    rc = test_lockstep_smoke();
    if (rc) {
        return rc;
    }
    rc = test_desync_bundle();
    if (rc) {
        return rc;
    }
    return 0;
}
