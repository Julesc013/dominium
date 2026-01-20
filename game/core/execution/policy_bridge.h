/*
FILE: game/core/execution/policy_bridge.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium core / execution
RESPONSIBILITY: Bridge between data profiles, law constraints, and engine execution policy.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
DETERMINISM: Policy selection is deterministic given identical inputs.
*/
#ifndef DOMINIUM_CORE_EXECUTION_POLICY_BRIDGE_H
#define DOMINIUM_CORE_EXECUTION_POLICY_BRIDGE_H

#include "domino/sys/sys_caps.h"
#include "domino/execution/execution_policy.h"

typedef struct dom_policy_bridge {
    dom_sys_caps_v1         sys_caps;
    dom_exec_profile_config profile;
    dom_exec_law_constraints law;
    dom_exec_policy         policy;
    d_bool                  has_sys_caps;
    d_bool                  has_profile;
    d_bool                  has_policy;
} dom_policy_bridge;

void dom_policy_bridge_init(dom_policy_bridge* bridge);
int dom_policy_bridge_set_sys_caps(dom_policy_bridge* bridge,
                                   const dom_sys_caps_v1* caps);
int dom_policy_bridge_collect_sys_caps(dom_policy_bridge* bridge);
int dom_policy_bridge_load_profile(dom_policy_bridge* bridge,
                                   const char* profile_path);
int dom_policy_bridge_apply(dom_policy_bridge* bridge,
                            const dom_exec_law_constraints* law);

u32 dom_policy_bridge_scheduler_backend(const dom_policy_bridge* bridge);
u32 dom_policy_bridge_kernel_mask_strict(const dom_policy_bridge* bridge);
u32 dom_policy_bridge_kernel_mask_derived(const dom_policy_bridge* bridge);
const dom_exec_budget_result* dom_policy_bridge_budgets(const dom_policy_bridge* bridge);
const dom_exec_policy_audit* dom_policy_bridge_audit(const dom_policy_bridge* bridge);

#endif /* DOMINIUM_CORE_EXECUTION_POLICY_BRIDGE_H */
