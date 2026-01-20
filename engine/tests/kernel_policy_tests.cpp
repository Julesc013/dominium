/*
Kernel policy selection tests (KERN4).
*/
#include "execution/kernels/kernel_policy.h"
#include "execution/kernels/kernel_selector.h"
#include "domino/execution/task_node.h"

#include <string.h>
#include <stdio.h>

#define TEST_CHECK(cond) do { if (!(cond)) return 1; } while (0)

static int test_strict_scalar_when_simd_not_proven(void)
{
    dom_kernel_policy policy;
    dom_kernel_policy_entry overrides[4];
    dom_kernel_select_request req;
    dom_kernel_select_result res;
    u32 order[2] = { DOM_KERNEL_BACKEND_SIMD, DOM_KERNEL_BACKEND_SCALAR };

    dom_kernel_policy_init(&policy, overrides, 4u);
    TEST_CHECK(dom_kernel_policy_set_default_order(&policy, order, 2u) == 0);
    policy.strict_backend_mask = DOM_KERNEL_BACKEND_MASK_SCALAR;
    policy.derived_backend_mask = DOM_KERNEL_BACKEND_MASK_ALL;

    memset(&req, 0, sizeof(req));
    req.op_id = dom_kernel_op_id_make(1u);
    req.determinism_class = DOM_DET_STRICT;
    req.available_backend_mask = DOM_KERNEL_BACKEND_MASK_SCALAR | DOM_KERNEL_BACKEND_MASK_SIMD;
    req.law_backend_mask = DOM_KERNEL_BACKEND_MASK_ALL;

    TEST_CHECK(dom_kernel_select_backend(&policy, &req, &res) == 0);
    TEST_CHECK(res.status == DOM_KERNEL_SELECT_OK);
    TEST_CHECK(res.backend_id == DOM_KERNEL_BACKEND_SCALAR);
    return 0;
}

static int test_strict_simd_when_allowed(void)
{
    dom_kernel_policy policy;
    dom_kernel_policy_entry overrides[4];
    dom_kernel_select_request req;
    dom_kernel_select_result res;
    u32 order[2] = { DOM_KERNEL_BACKEND_SIMD, DOM_KERNEL_BACKEND_SCALAR };

    dom_kernel_policy_init(&policy, overrides, 4u);
    TEST_CHECK(dom_kernel_policy_set_default_order(&policy, order, 2u) == 0);
    policy.strict_backend_mask = DOM_KERNEL_BACKEND_MASK_SCALAR | DOM_KERNEL_BACKEND_MASK_SIMD;

    memset(&req, 0, sizeof(req));
    req.op_id = dom_kernel_op_id_make(2u);
    req.determinism_class = DOM_DET_STRICT;
    req.available_backend_mask = DOM_KERNEL_BACKEND_MASK_SCALAR | DOM_KERNEL_BACKEND_MASK_SIMD;
    req.law_backend_mask = DOM_KERNEL_BACKEND_MASK_ALL;

    TEST_CHECK(dom_kernel_select_backend(&policy, &req, &res) == 0);
    TEST_CHECK(res.status == DOM_KERNEL_SELECT_OK);
    TEST_CHECK(res.backend_id == DOM_KERNEL_BACKEND_SIMD);
    return 0;
}

static int test_derived_gpu_when_enabled(void)
{
    dom_kernel_policy policy;
    dom_kernel_policy_entry overrides[4];
    dom_kernel_select_request req;
    dom_kernel_select_result res;
    u32 order[3] = { DOM_KERNEL_BACKEND_GPU, DOM_KERNEL_BACKEND_SIMD, DOM_KERNEL_BACKEND_SCALAR };

    dom_kernel_policy_init(&policy, overrides, 4u);
    TEST_CHECK(dom_kernel_policy_set_default_order(&policy, order, 3u) == 0);
    policy.derived_backend_mask = DOM_KERNEL_BACKEND_MASK_ALL;

    memset(&req, 0, sizeof(req));
    req.op_id = dom_kernel_op_id_make(3u);
    req.determinism_class = DOM_DET_DERIVED;
    req.available_backend_mask = DOM_KERNEL_BACKEND_MASK_ALL;
    req.law_backend_mask = DOM_KERNEL_BACKEND_MASK_ALL;

    TEST_CHECK(dom_kernel_select_backend(&policy, &req, &res) == 0);
    TEST_CHECK(res.status == DOM_KERNEL_SELECT_OK);
    TEST_CHECK(res.backend_id == DOM_KERNEL_BACKEND_GPU);
    return 0;
}

static int test_policy_order_respected(void)
{
    dom_kernel_policy policy;
    dom_kernel_policy_entry overrides[4];
    dom_kernel_select_request req;
    dom_kernel_select_result res;
    u32 order[2] = { DOM_KERNEL_BACKEND_SCALAR, DOM_KERNEL_BACKEND_SIMD };

    dom_kernel_policy_init(&policy, overrides, 4u);
    TEST_CHECK(dom_kernel_policy_set_default_order(&policy, order, 2u) == 0);
    policy.strict_backend_mask = DOM_KERNEL_BACKEND_MASK_SCALAR | DOM_KERNEL_BACKEND_MASK_SIMD;

    memset(&req, 0, sizeof(req));
    req.op_id = dom_kernel_op_id_make(4u);
    req.determinism_class = DOM_DET_STRICT;
    req.available_backend_mask = DOM_KERNEL_BACKEND_MASK_SCALAR | DOM_KERNEL_BACKEND_MASK_SIMD;
    req.law_backend_mask = DOM_KERNEL_BACKEND_MASK_ALL;

    TEST_CHECK(dom_kernel_select_backend(&policy, &req, &res) == 0);
    TEST_CHECK(res.status == DOM_KERNEL_SELECT_OK);
    TEST_CHECK(res.backend_id == DOM_KERNEL_BACKEND_SCALAR);
    return 0;
}

static int test_law_disables_gpu(void)
{
    dom_kernel_policy policy;
    dom_kernel_policy_entry overrides[4];
    dom_kernel_select_request req;
    dom_kernel_select_result res;
    u32 order[2] = { DOM_KERNEL_BACKEND_GPU, DOM_KERNEL_BACKEND_SCALAR };

    dom_kernel_policy_init(&policy, overrides, 4u);
    TEST_CHECK(dom_kernel_policy_set_default_order(&policy, order, 2u) == 0);
    policy.derived_backend_mask = DOM_KERNEL_BACKEND_MASK_ALL;

    memset(&req, 0, sizeof(req));
    req.op_id = dom_kernel_op_id_make(5u);
    req.determinism_class = DOM_DET_DERIVED;
    req.available_backend_mask = DOM_KERNEL_BACKEND_MASK_ALL;
    req.law_backend_mask = DOM_KERNEL_BACKEND_MASK_SCALAR;

    TEST_CHECK(dom_kernel_select_backend(&policy, &req, &res) == 0);
    TEST_CHECK(res.status == DOM_KERNEL_SELECT_OK);
    TEST_CHECK(res.backend_id == DOM_KERNEL_BACKEND_SCALAR);
    return 0;
}

static int test_no_candidate_refusal(void)
{
    dom_kernel_policy policy;
    dom_kernel_policy_entry overrides[4];
    dom_kernel_select_request req;
    dom_kernel_select_result res;
    u32 order[1] = { DOM_KERNEL_BACKEND_SCALAR };

    dom_kernel_policy_init(&policy, overrides, 4u);
    TEST_CHECK(dom_kernel_policy_set_default_order(&policy, order, 1u) == 0);
    policy.strict_backend_mask = 0u;

    memset(&req, 0, sizeof(req));
    req.op_id = dom_kernel_op_id_make(6u);
    req.determinism_class = DOM_DET_STRICT;
    req.available_backend_mask = DOM_KERNEL_BACKEND_MASK_SCALAR;
    req.law_backend_mask = DOM_KERNEL_BACKEND_MASK_ALL;

    TEST_CHECK(dom_kernel_select_backend(&policy, &req, &res) == 0);
    TEST_CHECK(res.status == DOM_KERNEL_SELECT_NO_CANDIDATE);
    return 0;
}

int main(void)
{
    if (test_strict_scalar_when_simd_not_proven() != 0) return 1;
    if (test_strict_simd_when_allowed() != 0) return 1;
    if (test_derived_gpu_when_enabled() != 0) return 1;
    if (test_policy_order_respected() != 0) return 1;
    if (test_law_disables_gpu() != 0) return 1;
    if (test_no_candidate_refusal() != 0) return 1;
    return 0;
}
