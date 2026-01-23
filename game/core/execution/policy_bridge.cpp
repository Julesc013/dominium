/*
FILE: game/core/execution/policy_bridge.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium core / execution
RESPONSIBILITY: Bridge between data profiles, law constraints, and engine execution policy.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
DETERMINISM: Policy selection is deterministic given identical inputs.
*/
#include "policy_bridge.h"

#include <string.h>

void dom_policy_bridge_init(dom_policy_bridge* bridge)
{
    if (!bridge) {
        return;
    }
    memset(bridge, 0, sizeof(*bridge));
    dom_sys_caps_init(&bridge->sys_caps);
    dom_exec_profile_init(&bridge->profile);
    dom_exec_policy_init(&bridge->policy);
}

int dom_policy_bridge_set_sys_caps(dom_policy_bridge* bridge,
                                   const dom_sys_caps_v1* caps)
{
    if (!bridge || !caps) {
        return -1;
    }
    bridge->sys_caps = *caps;
    bridge->has_sys_caps = D_TRUE;
    return 0;
}

int dom_policy_bridge_collect_sys_caps(dom_policy_bridge* bridge)
{
    if (!bridge) {
        return -1;
    }
    dom_sys_caps_collect(&bridge->sys_caps);
    bridge->has_sys_caps = D_TRUE;
    return 0;
}

int dom_policy_bridge_load_profile(dom_policy_bridge* bridge,
                                   const char* profile_path)
{
    int rc;
    if (!bridge || !profile_path) {
        return -1;
    }
    rc = dom_exec_profile_load_tlv(profile_path, &bridge->profile);
    if (rc != DOM_EXEC_PROFILE_LOAD_OK) {
        bridge->has_profile = D_FALSE;
        return -2;
    }
    bridge->has_profile = D_TRUE;
    return 0;
}

int dom_policy_bridge_apply(dom_policy_bridge* bridge,
                            const dom_exec_law_constraints* law)
{
    dom_exec_law_constraints local_law;
    int rc;
    if (!bridge) {
        return -1;
    }
    if (!bridge->has_sys_caps) {
        dom_sys_caps_collect(&bridge->sys_caps);
        bridge->has_sys_caps = D_TRUE;
    }
    if (!bridge->has_profile) {
        return -2;
    }
    if (law) {
        bridge->law = *law;
    } else {
        memset(&local_law, 0, sizeof(local_law));
        local_law.allow_multithread = 1u;
        local_law.allow_simd = 1u;
        local_law.allow_gpu_derived = 1u;
        local_law.allow_modified_clients = 1u;
        local_law.allow_unauthenticated = 1u;
        local_law.allow_debug_tools = 1u;
        bridge->law = local_law;
    }

    rc = dom_exec_policy_select(&bridge->sys_caps,
                                &bridge->profile,
                                &bridge->law,
                                &bridge->policy);
    if (rc != 0) {
        bridge->has_policy = D_FALSE;
        return -3;
    }
    bridge->has_policy = D_TRUE;
    return 0;
}

u32 dom_policy_bridge_scheduler_backend(const dom_policy_bridge* bridge)
{
    if (!bridge || !bridge->has_policy) {
        return DOM_EXEC_SCHED_EXEC2_SINGLE_THREAD;
    }
    return bridge->policy.scheduler_backend;
}

u32 dom_policy_bridge_kernel_mask_strict(const dom_policy_bridge* bridge)
{
    if (!bridge || !bridge->has_policy) {
        return DOM_KERNEL_BACKEND_MASK_SCALAR;
    }
    return bridge->policy.kernel_mask_strict;
}

u32 dom_policy_bridge_kernel_mask_derived(const dom_policy_bridge* bridge)
{
    if (!bridge || !bridge->has_policy) {
        return DOM_KERNEL_BACKEND_MASK_SCALAR;
    }
    return bridge->policy.kernel_mask_derived;
}

const dom_exec_budget_result* dom_policy_bridge_budgets(const dom_policy_bridge* bridge)
{
    if (!bridge || !bridge->has_policy) {
        return (const dom_exec_budget_result*)0;
    }
    return &bridge->policy.budgets;
}

const dom_exec_policy_audit* dom_policy_bridge_audit(const dom_policy_bridge* bridge)
{
    if (!bridge || !bridge->has_policy) {
        return (const dom_exec_policy_audit*)0;
    }
    return &bridge->policy.audit;
}
