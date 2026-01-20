/*
Policy bridge tests (HWCAPS0).
*/
#include "game/core/execution/policy_bridge.h"

#include <stdio.h>
#include <string.h>
#include <string>

#ifndef DOMINIUM_DATA_ROOT
#define DOMINIUM_DATA_ROOT "."
#endif

#define EXPECT(cond, msg) do { \
    if (!(cond)) { \
        fprintf(stderr, "FAIL: %s\n", msg); \
        return 1; \
    } \
} while (0)

static std::string profile_path(const char* name)
{
    std::string path = DOMINIUM_DATA_ROOT;
    path += "/defaults/profiles/";
    path += name;
    path += ".tlv";
    return path;
}

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

static int test_profile_load_deterministic(void)
{
    dom_policy_bridge a;
    dom_policy_bridge b;
    std::string path = profile_path("baseline_2010");

    dom_policy_bridge_init(&a);
    dom_policy_bridge_init(&b);
    EXPECT(dom_policy_bridge_load_profile(&a, path.c_str()) == 0, "load a");
    EXPECT(dom_policy_bridge_load_profile(&b, path.c_str()) == 0, "load b");
    EXPECT(strcmp(a.profile.profile_id, b.profile.profile_id) == 0, "profile id stable");
    EXPECT(a.profile.allow_mask == b.profile.allow_mask, "allow mask stable");
    EXPECT(a.profile.budget_profile.base_cpu_authoritative ==
           b.profile.budget_profile.base_cpu_authoritative, "budget stable");
    return 0;
}

static int test_audit_summary_stable(void)
{
    dom_policy_bridge a;
    dom_policy_bridge b;
    dom_sys_caps_v1 caps;
    dom_exec_law_constraints law;
    std::string path = profile_path("modern_2020");
    const dom_exec_policy_audit* audit_a;
    const dom_exec_policy_audit* audit_b;

    init_caps(&caps, 8u, D_TRUE, D_TRUE);
    memset(&law, 0, sizeof(law));
    law.allow_multithread = 1u;
    law.allow_simd = 1u;
    law.allow_gpu_derived = 1u;
    law.allow_modified_clients = 1u;
    law.allow_unauthenticated = 1u;
    law.allow_debug_tools = 1u;

    dom_policy_bridge_init(&a);
    dom_policy_bridge_init(&b);
    EXPECT(dom_policy_bridge_load_profile(&a, path.c_str()) == 0, "load a");
    EXPECT(dom_policy_bridge_load_profile(&b, path.c_str()) == 0, "load b");
    EXPECT(dom_policy_bridge_set_sys_caps(&a, &caps) == 0, "caps a");
    EXPECT(dom_policy_bridge_set_sys_caps(&b, &caps) == 0, "caps b");
    EXPECT(dom_policy_bridge_apply(&a, &law) == 0, "apply a");
    EXPECT(dom_policy_bridge_apply(&b, &law) == 0, "apply b");

    audit_a = dom_policy_bridge_audit(&a);
    audit_b = dom_policy_bridge_audit(&b);
    EXPECT(audit_a != 0, "audit a");
    EXPECT(audit_b != 0, "audit b");
    EXPECT(audit_a->summary[0] != '\0', "summary present");
    EXPECT(audit_a->audit_hash == audit_b->audit_hash, "audit hash stable");
    return 0;
}

static int test_disable_gpu_derived_via_law(void)
{
    dom_policy_bridge bridge;
    dom_sys_caps_v1 caps;
    dom_exec_law_constraints law;
    std::string path = profile_path("modern_2020");

    init_caps(&caps, 8u, D_TRUE, D_TRUE);
    memset(&law, 0, sizeof(law));
    law.allow_multithread = 1u;
    law.allow_simd = 1u;
    law.allow_gpu_derived = 0u;
    law.allow_modified_clients = 1u;
    law.allow_unauthenticated = 1u;
    law.allow_debug_tools = 1u;

    dom_policy_bridge_init(&bridge);
    EXPECT(dom_policy_bridge_load_profile(&bridge, path.c_str()) == 0, "load profile");
    EXPECT(dom_policy_bridge_set_sys_caps(&bridge, &caps) == 0, "set caps");
    EXPECT(dom_policy_bridge_apply(&bridge, &law) == 0, "apply");
    EXPECT((dom_policy_bridge_kernel_mask_derived(&bridge) & DOM_KERNEL_BACKEND_MASK_GPU) == 0u,
           "gpu derived disabled");
    return 0;
}

int main(void)
{
    if (test_profile_load_deterministic() != 0) return 1;
    if (test_audit_summary_stable() != 0) return 1;
    if (test_disable_gpu_derived_via_law() != 0) return 1;
    return 0;
}
