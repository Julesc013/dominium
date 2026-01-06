/*
FILE: source/tests/dom_qos_determinism_test.cpp
MODULE: Dominium Tests
PURPOSE: Validate QoS negotiation determinism under different message orders.
*/
#include <cstdio>
#include <cstring>

extern "C" {
#include "domino/core/types.h"
}

#include "runtime/dom_qos.h"

static int fail(const char *msg) {
    std::fprintf(stderr, "FAIL: %s\n", msg ? msg : "(null)");
    return 1;
}

static bool policy_equal(const dom_qos_policy &a, const dom_qos_policy &b) {
    return a.snapshot_hz == b.snapshot_hz &&
           a.delta_detail == b.delta_detail &&
           a.interest_radius_m == b.interest_radius_m &&
           a.recommended_profile == b.recommended_profile &&
           a.server_load_hint == b.server_load_hint &&
           a.assist_flags == b.assist_flags;
}

int main() {
    dom_qos_policy base;
    dom_qos_caps caps;
    dom_qos_status status;
    dom_qos_state s1;
    dom_qos_state s2;
    dom_qos_policy p1;
    dom_qos_policy p2;
    dom_qos_message msg_caps;
    dom_qos_message msg_status;
    std::vector<unsigned char> caps_bytes;
    std::vector<unsigned char> status_bytes;

    std::memset(&base, 0, sizeof(base));
    base.snapshot_hz = 60u;
    base.delta_detail = 90u;
    base.interest_radius_m = 1200u;
    base.recommended_profile = 1u;
    base.server_load_hint = DOM_QOS_SERVER_LOAD_NOMINAL;
    base.assist_flags = DOM_QOS_ASSIST_LOCAL_CACHE;

    std::memset(&caps, 0, sizeof(caps));
    caps.perf_caps_digest64 = 0x12345678ull;
    caps.preferred_profile = 2u;
    caps.max_snapshot_hz = 30u;
    caps.max_delta_detail = 80u;
    caps.max_interest_radius_m = 600u;
    caps.diagnostic_rate_cap = 25u;
    caps.assist_flags = DOM_QOS_ASSIST_LOCAL_CACHE;

    std::memset(&status, 0, sizeof(status));
    status.render_fps_avg = 25u;
    status.frame_time_ms_avg = 40u;
    status.backlog_jobs = 20u;
    status.derived_queue_pressure = 80u;
    status.request_detail_reduction = 1u;

    if (dom_qos_build_client_hello(&caps, caps_bytes) != DOM_QOS_OK ||
        caps_bytes.empty()) {
        return fail("build_client_hello");
    }
    if (dom_qos_build_client_status(&status, status_bytes) != DOM_QOS_OK ||
        status_bytes.empty()) {
        return fail("build_client_status");
    }
    if (dom_qos_parse_message(&caps_bytes[0], caps_bytes.size(), &msg_caps) != DOM_QOS_OK ||
        msg_caps.kind != DOM_QOS_KIND_CLIENT_HELLO) {
        return fail("parse_client_hello");
    }
    if (dom_qos_parse_message(&status_bytes[0], status_bytes.size(), &msg_status) != DOM_QOS_OK ||
        msg_status.kind != DOM_QOS_KIND_CLIENT_STATUS) {
        return fail("parse_client_status");
    }

    if (dom_qos_init(&s1, &base) != DOM_QOS_OK ||
        dom_qos_init(&s2, &base) != DOM_QOS_OK) {
        return fail("init_state");
    }

    (void)dom_qos_apply_client_caps(&s1, &msg_caps.caps);
    (void)dom_qos_apply_client_status(&s1, &msg_status.status);
    (void)dom_qos_apply_client_status(&s2, &msg_status.status);
    (void)dom_qos_apply_client_caps(&s2, &msg_caps.caps);

    if (dom_qos_get_effective_params(&s1, &p1) != DOM_QOS_OK ||
        dom_qos_get_effective_params(&s2, &p2) != DOM_QOS_OK) {
        return fail("get_effective");
    }

    if (!policy_equal(p1, p2)) {
        return fail("effective_policy_mismatch");
    }
    if (s1.last_reason_mask != s2.last_reason_mask) {
        return fail("reason_mask_mismatch");
    }

    return 0;
}
