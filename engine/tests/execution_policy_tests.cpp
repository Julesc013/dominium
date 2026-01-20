/*
Execution policy tests (HWCAPS0).
*/
#include "domino/execution/execution_policy.h"

#include <stdio.h>
#include <string.h>

#define EXPECT(cond, msg) do { \
    if (!(cond)) { \
        fprintf(stderr, "FAIL: %s\n", msg); \
        return 1; \
    } \
} while (0)

static void init_caps(dom_sys_caps_v1* caps, u32 cores, d_bool simd, d_bool gpu)
{
    dom_sys_caps_init(caps);
    caps->cpu.logical_cores = cores;
    if (simd) {
        caps->cpu.simd_caps.sse2 = DOM_SYS_CAPS_BOOL_TRUE;
    }
    if (gpu) {
        caps->gpu.has_gpu = 1u;
        caps->gpu.has_compute_queue = DOM_SYS_CAPS_BOOL_TRUE;
        caps->gpu.gpu_class = DOM_SYS_CAPS_GPU_MID;
    }
}

static void init_law(dom_exec_law_constraints* law,
                     u32 allow_mt,
                     u32 allow_simd,
                     u32 allow_gpu)
{
    memset(law, 0, sizeof(*law));
    law->allow_multithread = allow_mt;
    law->allow_simd = allow_simd;
    law->allow_gpu_derived = allow_gpu;
    law->allow_modified_clients = 1u;
    law->allow_unauthenticated = 1u;
    law->allow_debug_tools = 1u;
}

static void set_budget(dom_exec_budget_profile* profile,
                       const char* id,
                       u32 cpu_auth,
                       u32 cpu_der,
                       u32 io_der,
                       u32 net,
                       u32 mem_class,
                       const char* degradation_id,
                       u32 cpu_scale_min,
                       u32 cpu_scale_max,
                       u32 io_scale_max,
                       u32 net_scale_max)
{
    dom_exec_budget_profile_init(profile);
    strncpy(profile->budget_profile_id, id, DOM_EXEC_BUDGET_ID_MAX - 1u);
    profile->budget_profile_id[DOM_EXEC_BUDGET_ID_MAX - 1u] = '\0';
    profile->base_cpu_authoritative = cpu_auth;
    profile->base_cpu_derived = cpu_der;
    profile->base_io_derived = io_der;
    profile->base_net = net;
    profile->memory_class = mem_class;
    strncpy(profile->degradation_policy_id, degradation_id, DOM_EXEC_DEGRADATION_ID_MAX - 1u);
    profile->degradation_policy_id[DOM_EXEC_DEGRADATION_ID_MAX - 1u] = '\0';
    profile->cpu_scale_min = cpu_scale_min;
    profile->cpu_scale_max = cpu_scale_max;
    profile->io_scale_max = io_scale_max;
    profile->net_scale_max = net_scale_max;
}

static void init_profile_retro(dom_exec_profile_config* profile)
{
    dom_exec_profile_init(profile);
    strncpy(profile->profile_id, "retro_1990s", DOM_EXEC_PROFILE_ID_MAX - 1u);
    profile->scheduler_order[0] = DOM_EXEC_SCHED_EXEC2_SINGLE_THREAD;
    profile->scheduler_order_count = 1u;
    profile->kernel_order[0] = DOM_KERNEL_BACKEND_SCALAR;
    profile->kernel_order_count = 1u;
    profile->allow_mask = 0u;
    profile->min_cores_for_exec3 = 0u;
    set_budget(&profile->budget_profile, "retro_1990s", 50u, 25u, 8u, 4u,
               DOM_EXEC_MEM_SMALL, "retro_aggressive", 1u, 1u, 1u, 1u);
}

static void init_profile_modern(dom_exec_profile_config* profile)
{
    dom_exec_profile_init(profile);
    strncpy(profile->profile_id, "modern_2020", DOM_EXEC_PROFILE_ID_MAX - 1u);
    profile->scheduler_order[0] = DOM_EXEC_SCHED_EXEC3_PARALLEL;
    profile->scheduler_order[1] = DOM_EXEC_SCHED_EXEC2_SINGLE_THREAD;
    profile->scheduler_order_count = 2u;
    profile->kernel_order[0] = DOM_KERNEL_BACKEND_SIMD;
    profile->kernel_order[1] = DOM_KERNEL_BACKEND_SCALAR;
    profile->kernel_order[2] = DOM_KERNEL_BACKEND_GPU;
    profile->kernel_order_count = 3u;
    profile->allow_mask = DOM_EXEC_PROFILE_ALLOW_EXEC3 |
                          DOM_EXEC_PROFILE_ALLOW_SIMD |
                          DOM_EXEC_PROFILE_ALLOW_GPU_DERIVED;
    profile->min_cores_for_exec3 = 4u;
    set_budget(&profile->budget_profile, "modern_2020", 400u, 300u, 120u, 40u,
               DOM_EXEC_MEM_LARGE, "modern_balanced", 1u, 4u, 3u, 2u);
}

static int test_deterministic_policy(void)
{
    dom_sys_caps_v1 caps;
    dom_exec_profile_config profile;
    dom_exec_law_constraints law;
    dom_exec_policy a;
    dom_exec_policy b;

    init_caps(&caps, 8u, D_TRUE, D_TRUE);
    init_profile_modern(&profile);
    init_law(&law, 1u, 1u, 1u);

    EXPECT(dom_exec_policy_select(&caps, &profile, &law, &a) == 0, "select a");
    EXPECT(dom_exec_policy_select(&caps, &profile, &law, &b) == 0, "select b");
    EXPECT(a.scheduler_backend == b.scheduler_backend, "sched deterministic");
    EXPECT(a.kernel_mask_strict == b.kernel_mask_strict, "kernel strict deterministic");
    EXPECT(a.kernel_mask_derived == b.kernel_mask_derived, "kernel derived deterministic");
    EXPECT(a.audit.audit_hash == b.audit.audit_hash, "audit hash deterministic");
    return 0;
}

static int test_law_overrides_profile(void)
{
    dom_sys_caps_v1 caps;
    dom_exec_profile_config profile;
    dom_exec_law_constraints law;
    dom_exec_policy policy;

    init_caps(&caps, 8u, D_TRUE, D_TRUE);
    init_profile_modern(&profile);
    init_law(&law, 1u, 0u, 0u);

    EXPECT(dom_exec_policy_select(&caps, &profile, &law, &policy) == 0, "select law");
    EXPECT((policy.kernel_mask_derived & DOM_KERNEL_BACKEND_MASK_SIMD) == 0u, "law simd deny");
    EXPECT((policy.kernel_mask_derived & DOM_KERNEL_BACKEND_MASK_GPU) == 0u, "law gpu deny");
    return 0;
}

static int test_retro_profile(void)
{
    dom_sys_caps_v1 caps;
    dom_exec_profile_config profile;
    dom_exec_law_constraints law;
    dom_exec_policy policy;

    init_caps(&caps, 16u, D_TRUE, D_TRUE);
    init_profile_retro(&profile);
    init_law(&law, 1u, 1u, 1u);

    EXPECT(dom_exec_policy_select(&caps, &profile, &law, &policy) == 0, "select retro");
    EXPECT(policy.scheduler_backend == DOM_EXEC_SCHED_EXEC2_SINGLE_THREAD, "retro exec2");
    EXPECT(policy.kernel_mask_strict == DOM_KERNEL_BACKEND_MASK_SCALAR, "retro strict scalar");
    EXPECT(policy.kernel_mask_derived == DOM_KERNEL_BACKEND_MASK_SCALAR, "retro derived scalar");
    return 0;
}

static int test_modern_exec3_allowed(void)
{
    dom_sys_caps_v1 caps;
    dom_exec_profile_config profile;
    dom_exec_law_constraints law;
    dom_exec_policy policy;

    init_caps(&caps, 8u, D_TRUE, D_FALSE);
    init_profile_modern(&profile);
    init_law(&law, 1u, 1u, 0u);

    EXPECT(dom_exec_policy_select(&caps, &profile, &law, &policy) == 0, "select modern");
    EXPECT(policy.scheduler_backend == DOM_EXEC_SCHED_EXEC3_PARALLEL, "exec3 selected");
    return 0;
}

static int test_no_auth_gpu(void)
{
    dom_sys_caps_v1 caps;
    dom_exec_profile_config profile;
    dom_exec_law_constraints law;
    dom_exec_policy policy;

    init_caps(&caps, 8u, D_TRUE, D_TRUE);
    init_profile_modern(&profile);
    init_law(&law, 1u, 1u, 1u);

    EXPECT(dom_exec_policy_select(&caps, &profile, &law, &policy) == 0, "select gpu");
    EXPECT((policy.kernel_mask_strict & DOM_KERNEL_BACKEND_MASK_GPU) == 0u, "strict no gpu");
    return 0;
}

static int test_fallback_exec2(void)
{
    dom_sys_caps_v1 caps;
    dom_exec_profile_config profile;
    dom_exec_law_constraints law;
    dom_exec_policy policy;

    init_caps(&caps, 8u, D_TRUE, D_FALSE);
    init_profile_modern(&profile);
    init_law(&law, 0u, 1u, 0u);

    EXPECT(dom_exec_policy_select(&caps, &profile, &law, &policy) == 0, "select fallback");
    EXPECT(policy.scheduler_backend == DOM_EXEC_SCHED_EXEC2_SINGLE_THREAD, "fallback exec2");
    EXPECT((policy.audit.flags & DOM_EXEC_AUDIT_FLAG_FALLBACK_SCHED) != 0u, "fallback flag");
    return 0;
}

int main(void)
{
    if (test_deterministic_policy() != 0) return 1;
    if (test_law_overrides_profile() != 0) return 1;
    if (test_retro_profile() != 0) return 1;
    if (test_modern_exec3_allowed() != 0) return 1;
    if (test_no_auth_gpu() != 0) return 1;
    if (test_fallback_exec2() != 0) return 1;
    return 0;
}
