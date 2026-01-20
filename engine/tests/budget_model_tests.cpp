/*
Budget model tests (HWCAPS0).
*/
#include "domino/execution/budget_model.h"

#include <stdio.h>

#define EXPECT(cond, msg) do { \
    if (!(cond)) { \
        fprintf(stderr, "FAIL: %s\n", msg); \
        return 1; \
    } \
} while (0)

static dom_exec_budget_profile make_profile(void)
{
    dom_exec_budget_profile profile;
    dom_exec_budget_profile_init(&profile);
    profile.base_cpu_authoritative = 100u;
    profile.base_cpu_derived = 50u;
    profile.base_io_derived = 20u;
    profile.base_net = 10u;
    profile.memory_class = DOM_EXEC_MEM_MEDIUM;
    profile.cpu_scale_min = 1u;
    profile.cpu_scale_max = 4u;
    profile.io_scale_max = 3u;
    profile.net_scale_max = 2u;
    return profile;
}

static int test_bucket_thresholds(void)
{
    dom_sys_caps_v1 caps_lo;
    dom_sys_caps_v1 caps_hi;
    dom_exec_budget_profile profile;
    dom_exec_budget_result res_lo;
    dom_exec_budget_result res_hi;

    dom_sys_caps_init(&caps_lo);
    dom_sys_caps_init(&caps_hi);
    caps_lo.cpu.logical_cores = 3u;
    caps_hi.cpu.logical_cores = 4u;
    profile = make_profile();

    EXPECT(dom_exec_budget_resolve(&caps_lo, &profile, &res_lo) == 0, "resolve low");
    EXPECT(dom_exec_budget_resolve(&caps_hi, &profile, &res_hi) == 0, "resolve high");
    EXPECT(res_lo.per_tick_cpu_budget_units_authoritative != res_hi.per_tick_cpu_budget_units_authoritative,
           "threshold change");
    return 0;
}

static int test_deterministic_outputs(void)
{
    dom_sys_caps_v1 caps;
    dom_exec_budget_profile profile;
    dom_exec_budget_result a;
    dom_exec_budget_result b;

    dom_sys_caps_init(&caps);
    caps.cpu.logical_cores = 8u;
    profile = make_profile();

    EXPECT(dom_exec_budget_resolve(&caps, &profile, &a) == 0, "resolve a");
    EXPECT(dom_exec_budget_resolve(&caps, &profile, &b) == 0, "resolve b");
    EXPECT(a.per_tick_cpu_budget_units_authoritative == b.per_tick_cpu_budget_units_authoritative,
           "deterministic auth");
    EXPECT(a.per_tick_cpu_budget_units_derived == b.per_tick_cpu_budget_units_derived,
           "deterministic derived");
    EXPECT(a.per_tick_io_budget_units_derived == b.per_tick_io_budget_units_derived,
           "deterministic io");
    EXPECT(a.per_tick_net_budget_units == b.per_tick_net_budget_units,
           "deterministic net");
    return 0;
}

static int test_scale_clamp(void)
{
    dom_sys_caps_v1 caps;
    dom_exec_budget_profile profile;
    dom_exec_budget_result res;

    dom_sys_caps_init(&caps);
    caps.cpu.logical_cores = 16u;

    profile = make_profile();
    profile.cpu_scale_max = 1u;

    EXPECT(dom_exec_budget_resolve(&caps, &profile, &res) == 0, "resolve clamp");
    EXPECT(res.cpu_scale == 1u, "cpu scale clamped");
    EXPECT(res.per_tick_cpu_budget_units_authoritative == profile.base_cpu_authoritative,
           "clamped auth budget");
    return 0;
}

int main(void)
{
    if (test_bucket_thresholds() != 0) return 1;
    if (test_deterministic_outputs() != 0) return 1;
    if (test_scale_clamp() != 0) return 1;
    return 0;
}
