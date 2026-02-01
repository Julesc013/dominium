/*
FILE: tests/contract/dominium_session_tests.cpp
MODULE: Repository
LAYER / SUBSYSTEM: tests/contract
RESPONSIBILITY: Contract tests for session roles/authority modes and desync bundle plumbing.
ALLOWED DEPENDENCIES: Project-local headers; C89/C++98 standard headers.
FORBIDDEN DEPENDENCIES: N/A.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/specs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A.
EXTENSION POINTS: Extend via public headers and relevant `docs/specs/SPEC_*.md` without cross-layer coupling.
*/
#include <cstdio>
#include <cstring>
#include <string>

#include "dom_game_net.h"
#include "dom_instance.h"
#include "dom_paths.h"
#include "dom_session.h"

#include "runtime/dom_game_command.h"
#include "runtime/dom_game_net_driver.h"
#include "runtime/dom_game_paths.h"
#include "runtime/dom_game_runtime.h"
#include "runtime/dom_game_session.h"
#include "runtime/dom_io_guard.h"

#ifndef DOMINIUM_TEST_RUN_ROOT
#define DOMINIUM_TEST_RUN_ROOT "tmp"
#endif

extern "C" {
#include "net/d_net_proto.h"
#include "net/d_net_transport.h"
}

static int fail(const char *msg) {
    std::fprintf(stderr, "FAIL: %s\n", msg);
    return 1;
}

static void init_instance(dom::InstanceInfo &inst) {
    inst.id = "session_test";
    inst.world_seed = 7u;
    inst.world_size_m = 256u;
    inst.vertical_min_m = -32;
    inst.vertical_max_m = 128;
    inst.suite_version = 1u;
    inst.core_version = 1u;
    inst.last_product = "game";
    inst.last_product_version = "0.0.0";
    inst.packs.clear();
    inst.mods.clear();
}

static bool init_session(dom::DomSession &session,
                         dom::Paths &paths,
                         dom::InstanceInfo &inst) {
    dom::SessionConfig scfg;
    scfg.platform_backend = "null";
    scfg.gfx_backend = "null";
    scfg.audio_backend = std::string();
    scfg.headless = true;
    scfg.tui = false;
    scfg.allow_missing_content = true;

    if (!dom::resolve_paths(paths, ".")) {
        return false;
    }
    return session.init(paths, inst, scfg);
}

static dom_game_runtime *make_runtime(dom::DomSession &session,
                                      dom::DomGameNet &net,
                                      dom::InstanceInfo &inst,
                                      u32 ups) {
    dom_game_runtime_init_desc desc;
    std::memset(&desc, 0, sizeof(desc));
    desc.struct_size = sizeof(desc);
    desc.struct_version = DOM_GAME_RUNTIME_INIT_DESC_VERSION;
    desc.session = &session;
    desc.net = &net;
    desc.instance = &inst;
    desc.ups = ups;
    desc.run_id = 1ull;
    return dom_game_runtime_create(&desc);
}

static void build_noop_command(dom_game_command &cmd, u32 tick) {
    std::memset(&cmd, 0, sizeof(cmd));
    cmd.struct_size = sizeof(cmd);
    cmd.struct_version = DOM_GAME_COMMAND_VERSION;
    cmd.tick = tick;
    cmd.schema_id = 999u;
    cmd.schema_ver = 1u;
    cmd.payload = 0;
    cmd.payload_size = 0u;
}

static int run_session_hash(dom::DomSessionRole role,
                            dom::DomSessionAuthority authority,
                            const dom_game_command *cmds,
                            size_t cmd_count,
                            u32 tick_count,
                            u64 *out_hash) {
    dom::DomSession session;
    dom::DomGameNet net;
    dom::InstanceInfo inst;
    dom::Paths paths;
    dom::DomGamePaths game_paths;
    dom_game_runtime *rt = 0;
    dom::DomNetDriver *driver = 0;
    std::string err;
    size_t i;
    u32 tick_us;
    int rc = 0;

    if (!out_hash) {
        return fail("missing out_hash");
    }
    *out_hash = 0ull;

    init_instance(inst);
    if (!init_session(session, paths, inst)) {
        return fail("session init failed");
    }

    rt = make_runtime(session, net, inst, 60u);
    if (!rt) {
        session.shutdown();
        return fail("runtime create failed");
    }

    dom::DomSessionConfig scfg;
    scfg.role = role;
    scfg.authority = authority;
    scfg.tick_rate_hz = 60u;
    scfg.net_port = 0u;
    scfg.input_delay_ticks = 1u;
    scfg.identity.instance_id = inst.id;
    scfg.identity.run_id = 1ull;

    {
        dom::DomNetDriverContext ctx;
        ctx.net = &net;
        ctx.runtime = rt;
        ctx.instance = &inst;
        ctx.paths = &game_paths;
        driver = dom::dom_net_driver_create(scfg, ctx, &err);
        if (!driver) {
            rc = fail(err.empty() ? "net driver create failed" : err.c_str());
            goto cleanup;
        }
        if (driver->start() != DOM_NET_DRIVER_OK) {
            rc = fail("net driver start failed");
            goto cleanup;
        }
    }

    for (i = 0u; i < cmd_count; ++i) {
        if (driver->submit_local_command(&cmds[i], 0) != DOM_NET_DRIVER_OK) {
            rc = fail("submit_local_command failed");
            goto cleanup;
        }
    }

    tick_us = 1000000u / 60u;
    for (i = 0u; i < tick_count; ++i) {
        u32 stepped = 0u;
        (void)driver->pump_network();
        if (dom_game_runtime_tick_wall(rt, tick_us, &stepped) != DOM_GAME_RUNTIME_OK) {
            rc = fail("runtime tick failed");
            goto cleanup;
        }
    }

    *out_hash = dom_game_runtime_get_hash(rt);

cleanup:
    if (driver) {
        driver->stop();
        dom::dom_net_driver_destroy(driver);
    }
    if (rt) {
        dom_game_runtime_destroy(rt);
    }
    session.shutdown();
    return rc;
}

static int test_session_hash_equivalence(void) {
    dom_game_command cmds[3];
    u64 hash_single = 0ull;
    u64 hash_host = 0ull;
    u64 hash_lockstep_a = 0ull;
    u64 hash_lockstep_b = 0ull;

    build_noop_command(cmds[0], 1u);
    build_noop_command(cmds[1], 2u);
    build_noop_command(cmds[2], 3u);

    if (run_session_hash(dom::DOM_SESSION_ROLE_SINGLE,
                         dom::DOM_SESSION_AUTH_SERVER_AUTH,
                         cmds, 3u, 5u, &hash_single) != 0) {
        return 1;
    }
    if (run_session_hash(dom::DOM_SESSION_ROLE_HOST,
                         dom::DOM_SESSION_AUTH_SERVER_AUTH,
                         cmds, 3u, 5u, &hash_host) != 0) {
        return 1;
    }
    if (hash_single != hash_host) {
        return fail("single vs host hash mismatch");
    }

    if (run_session_hash(dom::DOM_SESSION_ROLE_HOST,
                         dom::DOM_SESSION_AUTH_LOCKSTEP,
                         cmds, 3u, 5u, &hash_lockstep_a) != 0) {
        return 1;
    }
    if (run_session_hash(dom::DOM_SESSION_ROLE_HOST,
                         dom::DOM_SESSION_AUTH_LOCKSTEP,
                         cmds, 3u, 5u, &hash_lockstep_b) != 0) {
        return 1;
    }
    if (hash_lockstep_a != hash_lockstep_b) {
        return fail("lockstep peer hash mismatch");
    }
    if (hash_single != hash_lockstep_a) {
        return fail("server-auth vs lockstep hash mismatch");
    }
    return 0;
}

static int test_lockstep_desync_bundle(void) {
    dom::DomSession session;
    dom::DomGameNet net;
    dom::InstanceInfo inst;
    dom::Paths paths;
    dom::DomGamePaths game_paths;
    dom_game_runtime *rt = 0;
    dom::DomNetDriver *driver = 0;
    std::string err;
    int rc = 0;

    dom_io_guard_reset();
    init_instance(inst);
    if (!init_session(session, paths, inst)) {
        return fail("session init failed");
    }
    rt = make_runtime(session, net, inst, 60u);
    if (!rt) {
        session.shutdown();
        return fail("runtime create failed");
    }

    if (!dom::dir_exists(DOMINIUM_TEST_RUN_ROOT)) {
        rc = fail("expected tmp/ directory for desync bundle test");
        goto cleanup;
    }
    game_paths.run_root = DOMINIUM_TEST_RUN_ROOT;

    {
        dom::DomSessionConfig scfg;
        dom::DomNetDriverContext ctx;
        scfg.role = dom::DOM_SESSION_ROLE_HOST;
        scfg.authority = dom::DOM_SESSION_AUTH_LOCKSTEP;
        scfg.tick_rate_hz = 60u;
        scfg.net_port = 0u;
        scfg.input_delay_ticks = 1u;
        scfg.identity.instance_id = inst.id;
        scfg.identity.run_id = 1ull;

        ctx.net = &net;
        ctx.runtime = rt;
        ctx.instance = &inst;
        ctx.paths = &game_paths;

        driver = dom::dom_net_driver_create(scfg, ctx, &err);
        if (!driver) {
            rc = fail(err.empty() ? "net driver create failed" : err.c_str());
            goto cleanup;
        }
        if (driver->start() != DOM_NET_DRIVER_OK) {
            rc = fail("net driver start failed");
            goto cleanup;
        }
    }

    {
        d_net_hash h;
        unsigned char buf[64];
        u32 out_size = 0u;
        u64 local_tick = dom_game_runtime_get_tick(rt);
        u64 local_hash = dom_game_runtime_get_hash(rt);
        int enc_rc;

        h.tick = (u32)local_tick;
        h.world_hash = local_hash + 1ull;
        enc_rc = d_net_encode_hash(&h, buf, (u32)sizeof(buf), &out_size);
        if (enc_rc != 0 || out_size == 0u) {
            rc = fail("hash encode failed");
            goto cleanup;
        }
        if (d_net_receive_packet(net.session().id, 2u, buf, out_size) != 0) {
            rc = fail("hash receive failed");
            goto cleanup;
        }
    }

    (void)driver->pump_network();

    {
        char name[64];
        u64 local_tick = dom_game_runtime_get_tick(rt);
        std::snprintf(name, sizeof(name), "desync_bundle_%llu.tlv",
                      (unsigned long long)local_tick);
        std::string path = dom::join(game_paths.run_root, name);
        if (!dom::file_exists(path)) {
            rc = fail("desync bundle not written");
            goto cleanup;
        }
        std::remove(path.c_str());
    }

cleanup:
    if (driver) {
        driver->stop();
        dom::dom_net_driver_destroy(driver);
    }
    if (rt) {
        dom_game_runtime_destroy(rt);
    }
    session.shutdown();
    return rc;
}

int main(void) {
    int rc = 0;
    if ((rc = test_session_hash_equivalence()) != 0) return rc;
    if ((rc = test_lockstep_desync_bundle()) != 0) return rc;
    std::printf("dominium session tests passed\n");
    return 0;
}
