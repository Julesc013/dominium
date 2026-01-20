/*
SIMD kernel equivalence tests (KERN2).
*/
#include "execution/kernels/kernel_registry.h"
#include "execution/kernels/scalar/scalar_kernels.h"
#include "execution/kernels/scalar/op_ids.h"
#include "execution/kernels/simd/simd_kernels.h"
#include "execution/kernels/simd/simd_caps.h"
#include "domino/execution/task_node.h"

#include <string.h>
#include <stdio.h>

#define TEST_CHECK(cond) do { if (!(cond)) return 1; } while (0)

static u32 lcg_next(u32* state)
{
    *state = (*state * 1664525u) + 1013904223u;
    return *state;
}

static dom_component_view make_view(u32 element_type,
                                    u32 element_size,
                                    u32 stride,
                                    u32 count,
                                    void* data,
                                    u32 access_mode)
{
    dom_component_view view;
    view.component_id = 1u;
    view.field_id = 1u;
    view.element_type = element_type;
    view.element_size = element_size;
    view.stride = stride;
    view.count = count;
    view.access_mode = access_mode;
    view.view_flags = DOM_ECS_VIEW_VALID;
    view.reserved = 0u;
    view.backend_token = (u64)(size_t)data;
    return view;
}

static int dispatch_with_mask(dom_kernel_registry* registry,
                              u32 backend_mask,
                              dom_kernel_op_id op_id,
                              const dom_component_view* inputs,
                              int input_count,
                              dom_component_view* outputs,
                              int output_count,
                              const void* params,
                              size_t params_size,
                              dom_entity_range range)
{
    dom_kernel_call call;
    dom_kernel_requirements reqs;
    dom_kernel_call_context ctx;

    dom_kernel_registry_set_backend_mask(registry, backend_mask);
    memset(&call, 0, sizeof(call));
    call.op_id = op_id;
    call.inputs = inputs;
    call.input_count = input_count;
    call.outputs = outputs;
    call.output_count = output_count;
    call.params = params;
    call.params_size = params_size;
    call.range = range;
    call.determinism_class = DOM_DET_STRICT;

    reqs.backend_mask = DOM_KERNEL_BACKEND_MASK_ALL;
    reqs.required_capabilities = 0u;
    reqs.flags = 0u;

    return dom_kernel_dispatch(registry, &call, &reqs, &ctx);
}

static int test_capability_gating(dom_kernel_registry* registry, d_bool simd_available)
{
    dom_kernel_requirements reqs;
    const dom_kernel_entry* entry;

    reqs.backend_mask = DOM_KERNEL_BACKEND_MASK_ALL;
    reqs.required_capabilities = 0u;
    reqs.flags = 0u;

    dom_kernel_registry_set_backend_mask(registry, DOM_KERNEL_BACKEND_MASK_SCALAR);
    entry = dom_kernel_resolve(registry, DOM_OP_MEM_COPY_VIEW, &reqs, DOM_DET_STRICT);
    TEST_CHECK(entry != 0);
    TEST_CHECK(entry->backend_id == DOM_KERNEL_BACKEND_SCALAR);

    if (!simd_available) {
        dom_kernel_registry_set_backend_mask(registry, DOM_KERNEL_BACKEND_MASK_ALL);
        entry = dom_kernel_resolve(registry, DOM_OP_MEM_COPY_VIEW, &reqs, DOM_DET_STRICT);
        TEST_CHECK(entry != 0);
        TEST_CHECK(entry->backend_id == DOM_KERNEL_BACKEND_SCALAR);
    }
    return 0;
}

static int test_mem_fill_copy_equivalence(dom_kernel_registry* registry)
{
    u32 data_scalar[16];
    u32 data_simd[16];
    u32 source[16];
    dom_component_view src_view;
    dom_component_view dst_scalar;
    dom_component_view dst_simd;
    dom_kernel_fill_params fill;
    dom_entity_range range;
    u32 i;

    for (i = 0u; i < 16u; ++i) {
        source[i] = (u32)(i * 3u);
        data_scalar[i] = 0u;
        data_simd[i] = 0u;
    }

    src_view = make_view(DOM_ECS_ELEM_U32, sizeof(u32), sizeof(u32), 16u,
                         source, DOM_ECS_ACCESS_READ);
    dst_scalar = make_view(DOM_ECS_ELEM_U32, sizeof(u32), sizeof(u32), 16u,
                           data_scalar, DOM_ECS_ACCESS_WRITE);
    dst_simd = make_view(DOM_ECS_ELEM_U32, sizeof(u32), sizeof(u32), 16u,
                         data_simd, DOM_ECS_ACCESS_WRITE);

    range.archetype_id = dom_archetype_id_make(1u);
    range.begin_index = 0u;
    range.end_index = 16u;

    memset(&fill, 0, sizeof(fill));
    fill.element_size = sizeof(u32);
    memcpy(fill.value, "\xAA\xBB\xCC\xDD", sizeof(u32));

    TEST_CHECK(dispatch_with_mask(registry, DOM_KERNEL_BACKEND_MASK_SCALAR,
                                  DOM_OP_MEM_FILL_VIEW,
                                  0, 0, &dst_scalar, 1,
                                  &fill, sizeof(fill), range) == 0);
    TEST_CHECK(dispatch_with_mask(registry, DOM_KERNEL_BACKEND_MASK_SIMD,
                                  DOM_OP_MEM_FILL_VIEW,
                                  0, 0, &dst_simd, 1,
                                  &fill, sizeof(fill), range) == 0);
    TEST_CHECK(memcmp(data_scalar, data_simd, sizeof(data_scalar)) == 0);

    memset(data_scalar, 0, sizeof(data_scalar));
    memset(data_simd, 0, sizeof(data_simd));

    TEST_CHECK(dispatch_with_mask(registry, DOM_KERNEL_BACKEND_MASK_SCALAR,
                                  DOM_OP_MEM_COPY_VIEW,
                                  &src_view, 1, &dst_scalar, 1,
                                  0, 0u, range) == 0);
    TEST_CHECK(dispatch_with_mask(registry, DOM_KERNEL_BACKEND_MASK_SIMD,
                                  DOM_OP_MEM_COPY_VIEW,
                                  &src_view, 1, &dst_simd, 1,
                                  0, 0u, range) == 0);
    TEST_CHECK(memcmp(data_scalar, data_simd, sizeof(data_scalar)) == 0);
    return 0;
}

static int test_reduce_sum_equivalence(dom_kernel_registry* registry)
{
    u32 input[9];
    u32 out_scalar[9];
    u32 out_simd[9];
    dom_component_view in_view;
    dom_component_view scalar_view;
    dom_component_view simd_view;
    dom_entity_range range;
    u32 i;

    for (i = 0u; i < 9u; ++i) {
        input[i] = (u32)(i + 1u);
        out_scalar[i] = 0u;
        out_simd[i] = 0u;
    }
    in_view = make_view(DOM_ECS_ELEM_U32, sizeof(u32), sizeof(u32), 9u,
                        input, DOM_ECS_ACCESS_READ);
    scalar_view = make_view(DOM_ECS_ELEM_U32, sizeof(u32), sizeof(u32), 9u,
                            out_scalar, DOM_ECS_ACCESS_WRITE);
    simd_view = make_view(DOM_ECS_ELEM_U32, sizeof(u32), sizeof(u32), 9u,
                          out_simd, DOM_ECS_ACCESS_WRITE);
    range.archetype_id = dom_archetype_id_make(1u);
    range.begin_index = 0u;
    range.end_index = 9u;

    TEST_CHECK(dispatch_with_mask(registry, DOM_KERNEL_BACKEND_MASK_SCALAR,
                                  DOM_OP_REDUCE_SUM_INT,
                                  &in_view, 1, &scalar_view, 1,
                                  0, 0u, range) == 0);
    TEST_CHECK(dispatch_with_mask(registry, DOM_KERNEL_BACKEND_MASK_SIMD,
                                  DOM_OP_REDUCE_SUM_INT,
                                  &in_view, 1, &simd_view, 1,
                                  0, 0u, range) == 0);
    TEST_CHECK(memcmp(out_scalar, out_simd, sizeof(out_scalar)) == 0);
    return 0;
}

static int test_visibility_mask_equivalence(dom_kernel_registry* registry)
{
    u8 input[20];
    u32 out_scalar[1];
    u32 out_simd[1];
    dom_component_view in_view;
    dom_component_view scalar_view;
    dom_component_view simd_view;
    dom_kernel_visibility_params params;
    dom_entity_range range;
    u32 i;

    for (i = 0u; i < 20u; ++i) {
        input[i] = (u8)((i % 3u) == 0u ? 1u : 0u);
    }
    out_scalar[0] = 0u;
    out_simd[0] = 0u;
    in_view = make_view(DOM_ECS_ELEM_U8, sizeof(u8), sizeof(u8), 20u,
                        input, DOM_ECS_ACCESS_READ);
    scalar_view = make_view(DOM_ECS_ELEM_U32, sizeof(u32), sizeof(u32), 1u,
                            out_scalar, DOM_ECS_ACCESS_WRITE);
    simd_view = make_view(DOM_ECS_ELEM_U32, sizeof(u32), sizeof(u32), 1u,
                          out_simd, DOM_ECS_ACCESS_WRITE);
    params.entity_count = 20u;
    range.archetype_id = dom_archetype_id_make(1u);
    range.begin_index = 0u;
    range.end_index = 20u;

    TEST_CHECK(dispatch_with_mask(registry, DOM_KERNEL_BACKEND_MASK_SCALAR,
                                  DOM_OP_BUILD_VISIBILITY_MASK,
                                  &in_view, 1, &scalar_view, 1,
                                  &params, sizeof(params), range) == 0);
    TEST_CHECK(dispatch_with_mask(registry, DOM_KERNEL_BACKEND_MASK_SIMD,
                                  DOM_OP_BUILD_VISIBILITY_MASK,
                                  &in_view, 1, &simd_view, 1,
                                  &params, sizeof(params), range) == 0);
    TEST_CHECK(out_scalar[0] == out_simd[0]);
    return 0;
}

static int test_cross_run_determinism(dom_kernel_registry* registry)
{
    u32 data[8];
    dom_component_view out_view;
    dom_kernel_fill_params fill;
    dom_entity_range range;
    u32 snapshot[8];
    u32 i;

    for (i = 0u; i < 8u; ++i) {
        data[i] = 0u;
    }
    out_view = make_view(DOM_ECS_ELEM_U32, sizeof(u32), sizeof(u32), 8u,
                         data, DOM_ECS_ACCESS_WRITE);
    memset(&fill, 0, sizeof(fill));
    fill.element_size = sizeof(u32);
    memcpy(fill.value, "\x10\x20\x30\x40", sizeof(u32));

    range.archetype_id = dom_archetype_id_make(1u);
    range.begin_index = 0u;
    range.end_index = 8u;

    TEST_CHECK(dispatch_with_mask(registry, DOM_KERNEL_BACKEND_MASK_SIMD,
                                  DOM_OP_MEM_FILL_VIEW,
                                  0, 0, &out_view, 1,
                                  &fill, sizeof(fill), range) == 0);
    memcpy(snapshot, data, sizeof(snapshot));

    memset(data, 0, sizeof(data));
    TEST_CHECK(dispatch_with_mask(registry, DOM_KERNEL_BACKEND_MASK_SIMD,
                                  DOM_OP_MEM_FILL_VIEW,
                                  0, 0, &out_view, 1,
                                  &fill, sizeof(fill), range) == 0);
    TEST_CHECK(memcmp(snapshot, data, sizeof(snapshot)) == 0);
    return 0;
}

int main(void)
{
    dom_kernel_entry storage[32];
    dom_kernel_registry registry;
    dom_simd_caps caps;
    dom_kernel_requirements reqs;
    const dom_kernel_entry* simd_entry;
    d_bool simd_available = D_FALSE;

    dom_kernel_registry_init(&registry, storage, 32u);
    dom_register_scalar_kernels(&registry);
    dom_simd_detect_caps(&caps);
    dom_register_simd_kernels(&registry, &caps);

    reqs.backend_mask = DOM_KERNEL_BACKEND_MASK_SIMD;
    reqs.required_capabilities = 0u;
    reqs.flags = 0u;
    simd_entry = dom_kernel_resolve(&registry, DOM_OP_MEM_COPY_VIEW, &reqs, DOM_DET_STRICT);
    simd_available = simd_entry ? D_TRUE : D_FALSE;

    if (test_capability_gating(&registry, simd_available) != 0) return 1;

    if (!simd_available) {
        return 0;
    }

    if (test_mem_fill_copy_equivalence(&registry) != 0) return 1;
    if (test_reduce_sum_equivalence(&registry) != 0) return 1;
    if (test_visibility_mask_equivalence(&registry) != 0) return 1;
    if (test_cross_run_determinism(&registry) != 0) return 1;
    return 0;
}
