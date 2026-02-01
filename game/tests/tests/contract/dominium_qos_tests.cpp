/*
FILE: tests/contract/dominium_qos_tests.cpp
MODULE: Repository
LAYER / SUBSYSTEM: tests/contract
RESPONSIBILITY: Contract tests for QoS negotiation determinism and non-sim impact.
ALLOWED DEPENDENCIES: Project-local headers; C89/C++98 standard headers.
FORBIDDEN DEPENDENCIES: N/A.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: QoS logic must be deterministic and non-authoritative.
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

#include "runtime/dom_game_runtime.h"
#include "runtime/dom_game_session.h"
#include "runtime/dom_qos.h"

static int fail(const char *msg) {
    std::fprintf(stderr, "FAIL: %s\n", msg);
    return 1;
}

static void init_instance(dom::InstanceInfo &inst) {
    inst.id = "qos_test";
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

static int test_qos_determinism_logged(void) {
    dom_qos_policy defaults;
    dom_qos_caps caps;
    dom_qos_status status;
    dom_qos_state a;
    dom_qos_state b;
    dom_qos_policy pa;
    dom_qos_policy pb;

    std::memset(&defaults, 0, sizeof(defaults));
    defaults.update_hz = 30u;
    defaults.delta_detail = 100u;
    defaults.interest_radius_m = 1024u;
    defaults.recommended_profile = 0u;

    std::memset(&caps, 0, sizeof(caps));
    caps.perf_class = 2u;
    caps.max_update_hz = 30u;
    caps.max_delta_detail = 100u;
    caps.max_interest_radius_m = 1024u;

    std::memset(&status, 0, sizeof(status));
    status.fps_budget = 30u;
    status.backlog_ms = 200u;
    status.desired_reduction = DOM_QOS_REDUCTION_MILD;
    status.status_flags = 0u;

    if (dom_qos_init(&a, &defaults) != DOM_QOS_OK ||
        dom_qos_init(&b, &defaults) != DOM_QOS_OK) {
        return fail("qos init failed");
    }
    (void)dom_qos_apply_client_caps(&a, &caps);
    (void)dom_qos_apply_client_status(&a, &status);
    (void)dom_qos_apply_client_caps(&b, &caps);
    (void)dom_qos_apply_client_status(&b, &status);

    if (dom_qos_get_effective_params(&a, &pa) != DOM_QOS_OK ||
        dom_qos_get_effective_params(&b, &pb) != DOM_QOS_OK) {
        return fail("qos effective params failed");
    }
    if (pa.update_hz != pb.update_hz ||
        pa.delta_detail != pb.delta_detail ||
        pa.interest_radius_m != pb.interest_radius_m ||
        pa.recommended_profile != pb.recommended_profile) {
        return fail("qos determinism mismatch");
    }
    if (a.last_reason_mask != b.last_reason_mask) {
        return fail("qos reason mask mismatch");
    }
    if ((a.last_reason_mask & DOM_QOS_REASON_STATUS_BACKLOG) == 0u) {
        return fail("qos reason mask missing backlog flag");
    }
    return 0;
}

static int test_qos_overload_reduces_update(void) {
    dom_qos_policy defaults;
    dom_qos_status status;
    dom_qos_state state;
    dom_qos_policy eff;

    std::memset(&defaults, 0, sizeof(defaults));
    defaults.update_hz = 30u;
    defaults.delta_detail = 100u;
    defaults.interest_radius_m = 1024u;
    defaults.recommended_profile = 0u;

    std::memset(&status, 0, sizeof(status));
    status.fps_budget = 30u;
    status.backlog_ms = 250u;
    status.desired_reduction = DOM_QOS_REDUCTION_NONE;
    status.status_flags = 0u;

    if (dom_qos_init(&state, &defaults) != DOM_QOS_OK) {
        return fail("qos init failed");
    }
    (void)dom_qos_apply_client_status(&state, &status);
    if (dom_qos_get_effective_params(&state, &eff) != DOM_QOS_OK) {
        return fail("qos effective params failed");
    }
    if (eff.update_hz >= defaults.update_hz) {
        return fail("qos overload did not reduce update_hz");
    }
    return 0;
}

static int test_qos_hash_unchanged(void) {
    dom::DomSession session;
    dom::DomGameNet net;
    dom::InstanceInfo inst;
    dom::Paths paths;
    dom_game_runtime *rt = 0;
    u64 h0 = 0ull;
    u64 h1 = 0ull;
    dom_qos_policy defaults;
    dom_qos_status status;
    dom_qos_state state;

    init_instance(inst);
    if (!init_session(session, paths, inst)) {
        return fail("session init failed");
    }
    rt = make_runtime(session, net, inst, 60u);
    if (!rt) {
        session.shutdown();
        return fail("runtime create failed");
    }
    h0 = dom_game_runtime_get_hash(rt);

    std::memset(&defaults, 0, sizeof(defaults));
    defaults.update_hz = 30u;
    defaults.delta_detail = 100u;
    defaults.interest_radius_m = 1024u;
    defaults.recommended_profile = 0u;

    std::memset(&status, 0, sizeof(status));
    status.fps_budget = 30u;
    status.backlog_ms = 200u;
    status.desired_reduction = DOM_QOS_REDUCTION_MILD;
    status.status_flags = 0u;

    (void)dom_qos_init(&state, &defaults);
    (void)dom_qos_apply_client_status(&state, &status);

    h1 = dom_game_runtime_get_hash(rt);
    if (h0 != h1) {
        dom_game_runtime_destroy(rt);
        session.shutdown();
        return fail("qos changed sim hash");
    }

    dom_game_runtime_destroy(rt);
    session.shutdown();
    return 0;
}

int main(void) {
    int rc = 0;
    if ((rc = test_qos_determinism_logged()) != 0) return rc;
    if ((rc = test_qos_overload_reduces_update()) != 0) return rc;
    if ((rc = test_qos_hash_unchanged()) != 0) return rc;
    std::printf("dominium qos tests passed\n");
    return 0;
}
