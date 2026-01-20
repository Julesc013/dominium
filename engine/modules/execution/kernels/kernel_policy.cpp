/*
FILE: engine/modules/execution/kernels/kernel_policy.cpp
MODULE: Domino
LAYER / SUBSYSTEM: Domino / execution/kernels
RESPONSIBILITY: Implements deterministic kernel backend selection policy.
ALLOWED DEPENDENCIES: engine/include public headers and C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers outside execution.
DETERMINISM: Policy interpretation must be deterministic.
*/
#include "execution/kernels/kernel_policy.h"

static d_bool dom_kernel_policy_is_backend_id(u32 backend_id)
{
    return (backend_id <= DOM_KERNEL_BACKEND_GPU) ? D_TRUE : D_FALSE;
}

static d_bool dom_kernel_policy_order_is_valid(const u32* order, u32 count)
{
    u32 i;
    u32 j;
    if (!order || count == 0u || count > DOM_KERNEL_POLICY_MAX_BACKENDS) {
        return D_FALSE;
    }
    for (i = 0u; i < count; ++i) {
        if (!dom_kernel_policy_is_backend_id(order[i])) {
            return D_FALSE;
        }
        for (j = 0u; j < i; ++j) {
            if (order[j] == order[i]) {
                return D_FALSE;
            }
        }
    }
    return D_TRUE;
}

void dom_kernel_policy_init(dom_kernel_policy* policy,
                            dom_kernel_policy_entry* override_storage,
                            u32 override_capacity)
{
    if (!policy) {
        return;
    }
    policy->default_order[0] = DOM_KERNEL_BACKEND_SCALAR;
    policy->default_order[1] = DOM_KERNEL_BACKEND_SIMD;
    policy->default_order[2] = DOM_KERNEL_BACKEND_GPU;
    policy->default_order_count = 3u;
    policy->strict_backend_mask = DOM_KERNEL_BACKEND_MASK_SCALAR |
                                  DOM_KERNEL_BACKEND_MASK_SIMD;
    policy->derived_backend_mask = DOM_KERNEL_BACKEND_MASK_SCALAR |
                                   DOM_KERNEL_BACKEND_MASK_SIMD |
                                   DOM_KERNEL_BACKEND_MASK_GPU;
    policy->flags = 0u;
    policy->max_cpu_time_us_derived = 0u;
    policy->overrides = override_storage;
    policy->override_count = 0u;
    policy->override_capacity = override_capacity;
}

int dom_kernel_policy_set_default_order(dom_kernel_policy* policy,
                                        const u32* order,
                                        u32 count)
{
    u32 i;
    if (!policy) {
        return -1;
    }
    if (!dom_kernel_policy_order_is_valid(order, count)) {
        return -2;
    }
    for (i = 0u; i < count; ++i) {
        policy->default_order[i] = order[i];
    }
    policy->default_order_count = count;
    return 0;
}

int dom_kernel_policy_add_override(dom_kernel_policy* policy,
                                   dom_kernel_op_id op_id,
                                   const u32* order,
                                   u32 count)
{
    u32 i;
    dom_kernel_policy_entry* entry;
    if (!policy || !policy->overrides) {
        return -1;
    }
    if (!dom_kernel_op_id_is_valid(op_id)) {
        return -2;
    }
    if (!dom_kernel_policy_order_is_valid(order, count)) {
        return -3;
    }
    if (policy->override_count >= policy->override_capacity) {
        return -4;
    }
    for (i = 0u; i < policy->override_count; ++i) {
        if (dom_kernel_op_id_equal(policy->overrides[i].op_id, op_id)) {
            return -5;
        }
    }
    entry = &policy->overrides[policy->override_count++];
    entry->op_id = op_id;
    entry->backend_count = count;
    for (i = 0u; i < count; ++i) {
        entry->backend_order[i] = order[i];
    }
    return 0;
}

int dom_kernel_policy_apply_config(dom_kernel_policy* policy,
                                   const dom_kernel_policy_config* config)
{
    u32 i;
    if (!policy || !config) {
        return -1;
    }
    if (config->default_order && config->default_order_count > 0u) {
        if (dom_kernel_policy_set_default_order(policy,
                                                config->default_order,
                                                config->default_order_count) != 0) {
            return -2;
        }
    }
    policy->strict_backend_mask = config->strict_backend_mask;
    policy->derived_backend_mask = config->derived_backend_mask;
    policy->flags = config->flags;
    policy->max_cpu_time_us_derived = config->max_cpu_time_us_derived;

    if (config->overrides && config->override_count > 0u) {
        if (config->override_count > policy->override_capacity) {
            return -3;
        }
        policy->override_count = 0u;
        for (i = 0u; i < config->override_count; ++i) {
            const dom_kernel_policy_entry* src = &config->overrides[i];
            if (dom_kernel_policy_add_override(policy,
                                               src->op_id,
                                               src->backend_order,
                                               src->backend_count) != 0) {
                return -4;
            }
        }
    }
    return 0;
}

const dom_kernel_policy_entry* dom_kernel_policy_get_override(const dom_kernel_policy* policy,
                                                              dom_kernel_op_id op_id)
{
    u32 i;
    if (!policy || !policy->overrides || policy->override_count == 0u) {
        return 0;
    }
    for (i = 0u; i < policy->override_count; ++i) {
        if (dom_kernel_op_id_equal(policy->overrides[i].op_id, op_id)) {
            return &policy->overrides[i];
        }
    }
    return 0;
}
