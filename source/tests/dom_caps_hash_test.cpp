/*
FILE: source/tests/dom_caps_hash_test.cpp
MODULE: Dominium Tests
PURPOSE: Validate SIM_CAPS hash stability and PERF_CAPS hash variability.
*/
#include <cstdio>

#include "dom_caps.h"

static int fail(const char *msg) {
    std::fprintf(stderr, "FAIL: %s\n", msg ? msg : "(null)");
    return 1;
}

int main() {
    dom::DomSimCaps sim;
    dom::DomSimCaps sim2;
    dom::DomPerfCaps perf;
    dom::DomPerfCaps perf2;
    u64 h1;
    u64 h2;
    u64 h3;
    u64 p1;
    u64 p2;

    dom::dom_sim_caps_init_default(sim);
    sim2 = sim;

    h1 = dom::dom_sim_caps_hash64(sim);
    h2 = dom::dom_sim_caps_hash64(sim);
    if (h1 == 0ull || h1 != h2) {
        return fail("sim_caps_hash_stable");
    }

    sim2.sim_flags = sim.sim_flags + 1u;
    h3 = dom::dom_sim_caps_hash64(sim2);
    if (h1 == h3) {
        return fail("sim_caps_hash_diff");
    }

    dom::dom_perf_caps_init_default(perf, dom::DOM_PERF_TIER_BASELINE);
    perf2 = perf;
    p1 = dom::dom_perf_caps_hash64(perf);
    perf2.tier_profile = dom::DOM_PERF_TIER_SERVER;
    p2 = dom::dom_perf_caps_hash64(perf2);
    if (p1 == p2) {
        return fail("perf_caps_hash_diff");
    }

    std::printf("dom_caps_hash_test: OK\n");
    return 0;
}
