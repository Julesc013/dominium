/*
FILE: engine/modules/execution/kernels/kernel_selector.cpp
MODULE: Domino
LAYER / SUBSYSTEM: Domino / execution/kernels
RESPONSIBILITY: Deterministic kernel backend selection utilities.
ALLOWED DEPENDENCIES: engine/include public headers and C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers outside execution.
DETERMINISM: Selection for authoritative tasks must be deterministic.
*/
#include "execution/kernels/kernel_selector.h"
#include "domino/execution/task_node.h"

static d_bool dom_kernel_selector_allow_backend_for_class(u32 backend_id, u32 determinism_class)
{
    if (determinism_class == DOM_DET_DERIVED) {
        return D_TRUE;
    }
    if (backend_id == DOM_KERNEL_BACKEND_GPU) {
        return D_FALSE;
    }
    return D_TRUE;
}

static u32 dom_kernel_selector_allowed_mask(const dom_kernel_policy* policy, u32 determinism_class)
{
    u32 mask;
    if (determinism_class == DOM_DET_DERIVED) {
        mask = policy->derived_backend_mask;
    } else {
        mask = policy->strict_backend_mask;
    }
    if (policy->flags & DOM_KERNEL_POLICY_DISABLE_SIMD) {
        mask &= ~DOM_KERNEL_BACKEND_MASK_SIMD;
    }
    if (policy->flags & DOM_KERNEL_POLICY_DISABLE_GPU) {
        mask &= ~DOM_KERNEL_BACKEND_MASK_GPU;
    }
    return mask;
}

static u32 dom_kernel_selector_available_mask(const dom_kernel_select_request* req)
{
    if (!req || req->available_backend_mask == 0u) {
        return DOM_KERNEL_BACKEND_MASK_SCALAR;
    }
    return req->available_backend_mask;
}

static u32 dom_kernel_selector_law_mask(const dom_kernel_select_request* req)
{
    if (!req || req->law_backend_mask == 0u) {
        return DOM_KERNEL_BACKEND_MASK_ALL;
    }
    return req->law_backend_mask;
}

static void dom_kernel_selector_get_order(const dom_kernel_policy* policy,
                                          dom_kernel_op_id op_id,
                                          u32* out_order,
                                          u32* out_count)
{
    u32 i;
    const dom_kernel_policy_entry* override = dom_kernel_policy_get_override(policy, op_id);
    if (override && override->backend_count > 0u) {
        *out_count = override->backend_count;
        for (i = 0u; i < override->backend_count; ++i) {
            out_order[i] = override->backend_order[i];
        }
        return;
    }
    *out_count = policy->default_order_count;
    for (i = 0u; i < policy->default_order_count; ++i) {
        out_order[i] = policy->default_order[i];
    }
}

int dom_kernel_select_backend(const dom_kernel_policy* policy,
                              const dom_kernel_select_request* req,
                              dom_kernel_select_result* out_result)
{
    u32 order[DOM_KERNEL_POLICY_MAX_BACKENDS];
    u32 order_count = 0u;
    u32 allowed_mask;
    u32 available_mask;
    u32 law_mask;
    u32 combined_mask;
    u32 start_index = 0u;
    u32 pass;

    if (!policy || !req || !out_result) {
        return -1;
    }
    if (!dom_kernel_op_id_is_valid(req->op_id)) {
        out_result->status = DOM_KERNEL_SELECT_INVALID;
        out_result->backend_id = 0u;
        out_result->reason = DOM_KERNEL_SELECT_REASON_NO_MATCH;
        return -2;
    }

    dom_kernel_selector_get_order(policy, req->op_id, order, &order_count);
    allowed_mask = dom_kernel_selector_allowed_mask(policy, req->determinism_class);
    available_mask = dom_kernel_selector_available_mask(req);
    law_mask = dom_kernel_selector_law_mask(req);
    combined_mask = allowed_mask & available_mask & law_mask;

    if (policy->flags & DOM_KERNEL_POLICY_ADAPTIVE_DERIVED) {
        if (req->determinism_class == DOM_DET_DERIVED) {
            if ((req->profile_flags & DOM_KERNEL_PROFILE_SLOW) != 0u) {
                start_index = 1u;
            }
            if ((policy->flags & DOM_KERNEL_POLICY_ENFORCE_DERIVED_BUDGET) != 0u &&
                policy->max_cpu_time_us_derived > 0u &&
                req->derived_cpu_time_us >= policy->max_cpu_time_us_derived) {
                start_index = 1u;
            }
        }
    }

    for (pass = 0u; pass < 2u; ++pass) {
        u32 begin = (pass == 0u) ? start_index : 0u;
        u32 end = (pass == 0u) ? order_count : start_index;
        u32 i;
        if (begin >= end || begin >= order_count) {
            continue;
        }
        for (i = begin; i < end; ++i) {
            u32 backend_id = order[i];
            u32 backend_bit = (1u << backend_id);
            if ((combined_mask & backend_bit) == 0u) {
                continue;
            }
            if (!dom_kernel_selector_allow_backend_for_class(backend_id,
                                                             req->determinism_class)) {
                continue;
            }
            out_result->status = DOM_KERNEL_SELECT_OK;
            out_result->backend_id = backend_id;
            out_result->reason = DOM_KERNEL_SELECT_REASON_NONE;
            return 0;
        }
    }

    out_result->status = DOM_KERNEL_SELECT_NO_CANDIDATE;
    out_result->backend_id = 0u;
    out_result->reason = DOM_KERNEL_SELECT_REASON_NO_MATCH;
    return 0;
}

const dom_kernel_entry* dom_kernel_select_entry(const dom_kernel_registry* registry,
                                                const dom_kernel_policy* policy,
                                                const dom_kernel_select_request* req,
                                                dom_kernel_select_result* out_result)
{
    dom_kernel_select_result local_result;
    dom_kernel_requirements reqs;
    const dom_kernel_entry* entry;

    if (!out_result) {
        out_result = &local_result;
    }
    if (dom_kernel_select_backend(policy, req, out_result) != 0) {
        return 0;
    }
    if (out_result->status != DOM_KERNEL_SELECT_OK) {
        return 0;
    }

    reqs.backend_mask = (1u << out_result->backend_id);
    reqs.required_capabilities = 0u;
    reqs.flags = 0u;

    entry = dom_kernel_resolve(registry, req->op_id, &reqs, req->determinism_class);
    if (!entry) {
        out_result->status = DOM_KERNEL_SELECT_NO_CANDIDATE;
        out_result->backend_id = 0u;
        out_result->reason = DOM_KERNEL_SELECT_REASON_NO_MATCH;
    }
    return entry;
}
