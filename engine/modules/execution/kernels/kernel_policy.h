/*
FILE: engine/modules/execution/kernels/kernel_policy.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino / execution/kernels
RESPONSIBILITY: Defines deterministic kernel backend selection policy.
ALLOWED DEPENDENCIES: engine/include public headers and C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers outside execution.
DETERMINISM: Policy interpretation must be deterministic.
*/
#ifndef DOMINO_EXECUTION_KERNEL_POLICY_H
#define DOMINO_EXECUTION_KERNEL_POLICY_H

#include "domino/core/types.h"
#include "domino/execution/kernel_iface.h"

#ifdef __cplusplus
extern "C" {
#endif

enum {
    DOM_KERNEL_POLICY_DISABLE_SIMD = 1u << 0,
    DOM_KERNEL_POLICY_DISABLE_GPU = 1u << 1,
    DOM_KERNEL_POLICY_ADAPTIVE_DERIVED = 1u << 2,
    DOM_KERNEL_POLICY_ENFORCE_DERIVED_BUDGET = 1u << 3
};

enum {
    DOM_KERNEL_POLICY_MAX_BACKENDS = 3u
};

typedef struct dom_kernel_policy_entry {
    dom_kernel_op_id op_id;
    u32              backend_order[DOM_KERNEL_POLICY_MAX_BACKENDS];
    u32              backend_count;
} dom_kernel_policy_entry;

typedef struct dom_kernel_policy {
    u32                      default_order[DOM_KERNEL_POLICY_MAX_BACKENDS];
    u32                      default_order_count;
    u32                      strict_backend_mask;
    u32                      derived_backend_mask;
    u32                      flags;
    u32                      max_cpu_time_us_derived;
    dom_kernel_policy_entry* overrides;
    u32                      override_count;
    u32                      override_capacity;
} dom_kernel_policy;

typedef struct dom_kernel_policy_config {
    const u32*                 default_order;
    u32                        default_order_count;
    u32                        strict_backend_mask;
    u32                        derived_backend_mask;
    u32                        flags;
    u32                        max_cpu_time_us_derived;
    const dom_kernel_policy_entry* overrides;
    u32                        override_count;
} dom_kernel_policy_config;

void dom_kernel_policy_init(dom_kernel_policy* policy,
                            dom_kernel_policy_entry* override_storage,
                            u32 override_capacity);
int dom_kernel_policy_set_default_order(dom_kernel_policy* policy,
                                        const u32* order,
                                        u32 count);
int dom_kernel_policy_add_override(dom_kernel_policy* policy,
                                   dom_kernel_op_id op_id,
                                   const u32* order,
                                   u32 count);
int dom_kernel_policy_apply_config(dom_kernel_policy* policy,
                                   const dom_kernel_policy_config* config);
const dom_kernel_policy_entry* dom_kernel_policy_get_override(const dom_kernel_policy* policy,
                                                              dom_kernel_op_id op_id);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINO_EXECUTION_KERNEL_POLICY_H */
