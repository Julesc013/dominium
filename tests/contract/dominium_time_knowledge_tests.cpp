/*
FILE: tests/contract/dominium_time_knowledge_tests.cpp
MODULE: Repository
LAYER / SUBSYSTEM: tests/contract
RESPONSIBILITY: Contract tests for epistemic time knowledge and clock drift.
ALLOWED DEPENDENCIES: Project-local headers; C89/C++98 standard headers.
FORBIDDEN DEPENDENCIES: OS time APIs; locale/timezone libraries.
*/
#include <cstdio>
#include <cstring>

#include "runtime/dom_time_knowledge.h"

static int fail(const char *msg) {
    std::fprintf(stderr, "FAIL: %s\n", msg);
    return 1;
}

static dom_time_knowledge *make_knowledge(void) {
    dom_time_knowledge *k = dom_time_knowledge_create(1ull);
    return k;
}

static int test_no_clock_unknown(void) {
    dom_time_knowledge *k = make_knowledge();
    dom_time_clock_reading readings[4];
    dom_time_clock_env env;
    u32 count = 0u;
    int rc;

    if (!k) {
        return fail("knowledge create failed");
    }
    env.has_daylight = D_TRUE;
    env.has_power = D_TRUE;
    env.has_network = D_TRUE;
    env.extra_drift_ppm = 0u;
    env.extra_uncertainty_seconds = 0u;

    std::memset(readings, 0, sizeof(readings));
    rc = dom_time_knowledge_sample_all(k, 0ull, 60u, &env, readings, 4u, &count);
    dom_time_knowledge_destroy(k);
    if (rc != DOM_TIME_KNOWLEDGE_UNKNOWN) {
        return fail("expected UNKNOWN when no clocks are present");
    }
    if (count != 0u) {
        return fail("expected zero readings when no clocks are present");
    }
    return 0;
}

static int test_drift_accumulation(void) {
    dom_time_knowledge *k = make_knowledge();
    dom_time_clock_def def;
    dom_time_clock_env env;
    dom_time_clock_reading reading;
    const dom_ups ups = 10u;
    const dom_tick tick = 1000ull * (dom_tick)ups;
    int rc;

    if (!k) {
        return fail("knowledge create failed");
    }
    def.clock_id = 1ull;
    def.kind = DOM_TIME_CLOCK_MECHANICAL;
    def.frame = DOM_TIME_FRAME_ACT;
    def.base_accuracy_seconds = 1u;
    def.drift_ppm = 100000u;
    def.flags = 0u;
    rc = dom_time_knowledge_add_clock(k, &def, 0ull);
    if (rc != DOM_TIME_KNOWLEDGE_OK) {
        dom_time_knowledge_destroy(k);
        return fail("clock add failed");
    }

    env.has_daylight = D_TRUE;
    env.has_power = D_TRUE;
    env.has_network = D_TRUE;
    env.extra_drift_ppm = 0u;
    env.extra_uncertainty_seconds = 0u;

    std::memset(&reading, 0, sizeof(reading));
    rc = dom_time_knowledge_sample_clock(k, def.clock_id, tick, ups, &env, &reading);
    dom_time_knowledge_destroy(k);
    if (rc != DOM_TIME_KNOWLEDGE_OK) {
        return fail("clock sample failed");
    }
    if (reading.observed_act != 1100) {
        return fail("drift accumulation produced unexpected reading");
    }
    if (reading.uncertainty_seconds != 101ull) {
        return fail("drift accumulation produced unexpected uncertainty");
    }
    return 0;
}

static int test_calibration_reduces_uncertainty(void) {
    dom_time_knowledge *k_a = make_knowledge();
    dom_time_knowledge *k_b = make_knowledge();
    dom_time_clock_def def;
    dom_time_clock_env env;
    dom_time_clock_reading a;
    dom_time_clock_reading b;
    const dom_ups ups = 10u;
    const dom_tick tick_1000 = 1000ull * (dom_tick)ups;
    const dom_tick tick_2000 = 2000ull * (dom_tick)ups;
    int rc;

    if (!k_a || !k_b) {
        dom_time_knowledge_destroy(k_a);
        dom_time_knowledge_destroy(k_b);
        return fail("knowledge create failed");
    }
    def.clock_id = 2ull;
    def.kind = DOM_TIME_CLOCK_MECHANICAL;
    def.frame = DOM_TIME_FRAME_ACT;
    def.base_accuracy_seconds = 1u;
    def.drift_ppm = 100000u;
    def.flags = 0u;

    if (dom_time_knowledge_add_clock(k_a, &def, 0ull) != DOM_TIME_KNOWLEDGE_OK ||
        dom_time_knowledge_add_clock(k_b, &def, 0ull) != DOM_TIME_KNOWLEDGE_OK) {
        dom_time_knowledge_destroy(k_a);
        dom_time_knowledge_destroy(k_b);
        return fail("clock add failed");
    }

    env.has_daylight = D_TRUE;
    env.has_power = D_TRUE;
    env.has_network = D_TRUE;
    env.extra_drift_ppm = 0u;
    env.extra_uncertainty_seconds = 0u;

    std::memset(&a, 0, sizeof(a));
    std::memset(&b, 0, sizeof(b));
    rc = dom_time_knowledge_sample_clock(k_a, def.clock_id, tick_2000, ups, &env, &a);
    if (rc != DOM_TIME_KNOWLEDGE_OK) {
        dom_time_knowledge_destroy(k_a);
        dom_time_knowledge_destroy(k_b);
        return fail("sample failed (uncalibrated)");
    }
    if (dom_time_knowledge_calibrate_clock(k_b, def.clock_id, tick_1000) != DOM_TIME_KNOWLEDGE_OK) {
        dom_time_knowledge_destroy(k_a);
        dom_time_knowledge_destroy(k_b);
        return fail("calibration failed");
    }
    rc = dom_time_knowledge_sample_clock(k_b, def.clock_id, tick_2000, ups, &env, &b);
    dom_time_knowledge_destroy(k_a);
    dom_time_knowledge_destroy(k_b);
    if (rc != DOM_TIME_KNOWLEDGE_OK) {
        return fail("sample failed (calibrated)");
    }
    if (b.uncertainty_seconds >= a.uncertainty_seconds) {
        return fail("calibration did not reduce uncertainty");
    }
    return 0;
}

static int test_device_damage_effect(void) {
    dom_time_knowledge *k = make_knowledge();
    dom_time_clock_def def;
    dom_time_clock_env env;
    dom_time_clock_reading reading;
    const dom_ups ups = 10u;
    const dom_tick tick = 1000ull * (dom_tick)ups;
    int rc;

    if (!k) {
        return fail("knowledge create failed");
    }
    def.clock_id = 3ull;
    def.kind = DOM_TIME_CLOCK_MECHANICAL;
    def.frame = DOM_TIME_FRAME_ACT;
    def.base_accuracy_seconds = 1u;
    def.drift_ppm = 100000u;
    def.flags = 0u;
    rc = dom_time_knowledge_add_clock(k, &def, 0ull);
    if (rc != DOM_TIME_KNOWLEDGE_OK) {
        dom_time_knowledge_destroy(k);
        return fail("clock add failed");
    }
    rc = dom_time_knowledge_set_clock_state(k, def.clock_id,
                                            DOM_TIME_CLOCK_STATE_DAMAGED,
                                            50000u,
                                            20u);
    if (rc != DOM_TIME_KNOWLEDGE_OK) {
        dom_time_knowledge_destroy(k);
        return fail("set clock state failed");
    }

    env.has_daylight = D_TRUE;
    env.has_power = D_TRUE;
    env.has_network = D_TRUE;
    env.extra_drift_ppm = 0u;
    env.extra_uncertainty_seconds = 0u;

    std::memset(&reading, 0, sizeof(reading));
    rc = dom_time_knowledge_sample_clock(k, def.clock_id, tick, ups, &env, &reading);
    dom_time_knowledge_destroy(k);
    if (rc != DOM_TIME_KNOWLEDGE_OK) {
        return fail("clock sample failed");
    }
    if (reading.uncertainty_seconds <= 101ull) {
        return fail("damage did not increase uncertainty");
    }
    return 0;
}

static int test_multiple_clock_disagreement(void) {
    dom_time_knowledge *k = make_knowledge();
    dom_time_clock_def a;
    dom_time_clock_def b;
    dom_time_clock_env env;
    dom_time_clock_reading readings[2];
    u32 count = 0u;
    const dom_ups ups = 10u;
    const dom_tick tick = 1000ull * (dom_tick)ups;
    int rc;

    if (!k) {
        return fail("knowledge create failed");
    }
    a.clock_id = 4ull;
    a.kind = DOM_TIME_CLOCK_MECHANICAL;
    a.frame = DOM_TIME_FRAME_ACT;
    a.base_accuracy_seconds = 1u;
    a.drift_ppm = 0u;
    a.flags = 0u;

    b.clock_id = 5ull;
    b.kind = DOM_TIME_CLOCK_MECHANICAL;
    b.frame = DOM_TIME_FRAME_ACT;
    b.base_accuracy_seconds = 1u;
    b.drift_ppm = 100000u;
    b.flags = 0u;

    if (dom_time_knowledge_add_clock(k, &a, 0ull) != DOM_TIME_KNOWLEDGE_OK ||
        dom_time_knowledge_add_clock(k, &b, 0ull) != DOM_TIME_KNOWLEDGE_OK) {
        dom_time_knowledge_destroy(k);
        return fail("clock add failed");
    }

    env.has_daylight = D_TRUE;
    env.has_power = D_TRUE;
    env.has_network = D_TRUE;
    env.extra_drift_ppm = 0u;
    env.extra_uncertainty_seconds = 0u;

    std::memset(readings, 0, sizeof(readings));
    rc = dom_time_knowledge_sample_all(k, tick, ups, &env, readings, 2u, &count);
    dom_time_knowledge_destroy(k);
    if (rc != DOM_TIME_KNOWLEDGE_OK || count != 2u) {
        return fail("expected two clock readings");
    }
    if (readings[0].observed_act == readings[1].observed_act) {
        return fail("expected clock disagreement");
    }
    return 0;
}

static int test_determinism(void) {
    dom_time_knowledge *k = make_knowledge();
    dom_time_clock_def def;
    dom_time_clock_env env;
    dom_time_clock_reading a;
    dom_time_clock_reading b;
    const dom_ups ups = 60u;
    const dom_tick tick = 12345ull * (dom_tick)ups;
    int rc;

    if (!k) {
        return fail("knowledge create failed");
    }
    def.clock_id = 6ull;
    def.kind = DOM_TIME_CLOCK_MECHANICAL;
    def.frame = DOM_TIME_FRAME_ACT;
    def.base_accuracy_seconds = 1u;
    def.drift_ppm = 50000u;
    def.flags = 0u;
    rc = dom_time_knowledge_add_clock(k, &def, 0ull);
    if (rc != DOM_TIME_KNOWLEDGE_OK) {
        dom_time_knowledge_destroy(k);
        return fail("clock add failed");
    }

    env.has_daylight = D_TRUE;
    env.has_power = D_TRUE;
    env.has_network = D_TRUE;
    env.extra_drift_ppm = 0u;
    env.extra_uncertainty_seconds = 0u;

    std::memset(&a, 0, sizeof(a));
    std::memset(&b, 0, sizeof(b));
    rc = dom_time_knowledge_sample_clock(k, def.clock_id, tick, ups, &env, &a);
    if (rc != DOM_TIME_KNOWLEDGE_OK) {
        dom_time_knowledge_destroy(k);
        return fail("sample failed");
    }
    rc = dom_time_knowledge_sample_clock(k, def.clock_id, tick, ups, &env, &b);
    dom_time_knowledge_destroy(k);
    if (rc != DOM_TIME_KNOWLEDGE_OK) {
        return fail("sample failed (repeat)");
    }
    if (a.observed_act != b.observed_act || a.uncertainty_seconds != b.uncertainty_seconds) {
        return fail("non-deterministic clock sample");
    }
    return 0;
}

int main(void) {
    int rc = 0;
    if ((rc = test_no_clock_unknown()) != 0) return rc;
    if ((rc = test_drift_accumulation()) != 0) return rc;
    if ((rc = test_calibration_reduces_uncertainty()) != 0) return rc;
    if ((rc = test_device_damage_effect()) != 0) return rc;
    if ((rc = test_multiple_clock_disagreement()) != 0) return rc;
    if ((rc = test_determinism()) != 0) return rc;
    std::printf("dominium time knowledge tests passed\n");
    return 0;
}
