/*
Scalar kernel tests (KERN1).
*/
#include "execution/kernels/kernel_registry.h"
#include "execution/kernels/scalar/scalar_kernels.h"
#include "execution/kernels/scalar/op_ids.h"
#include "domino/execution/task_node.h"

#include <string.h>
#include <stdio.h>

#define TEST_CHECK(cond) do { if (!(cond)) return 1; } while (0)

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

static int dispatch_kernel(dom_kernel_registry* registry,
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

static int test_fill_and_copy(void)
{
    dom_kernel_entry storage[16];
    dom_kernel_registry registry;
    u32 data[4] = { 0u, 0u, 0u, 0u };
    u32 target[4] = { 0u, 0u, 0u, 0u };
    dom_component_view out_view;
    dom_component_view in_view;
    dom_kernel_fill_params fill;
    dom_entity_range range;

    dom_kernel_registry_init(&registry, storage, 16u);
    dom_register_scalar_kernels(&registry);

    out_view = make_view(DOM_ECS_ELEM_U32, sizeof(u32), sizeof(u32), 4u, data, DOM_ECS_ACCESS_WRITE);
    in_view = make_view(DOM_ECS_ELEM_U32, sizeof(u32), sizeof(u32), 4u, target, DOM_ECS_ACCESS_READ);

    memset(&fill, 0, sizeof(fill));
    fill.element_size = sizeof(u32);
    memcpy(fill.value, "\xEF\xBE\xAD\xDE", sizeof(u32));

    range.archetype_id = dom_archetype_id_make(1u);
    range.begin_index = 0u;
    range.end_index = 4u;

    TEST_CHECK(dispatch_kernel(&registry, DOM_OP_MEM_FILL_VIEW,
                               0, 0, &out_view, 1, &fill, sizeof(fill), range) == 0);
    TEST_CHECK(data[0] == 0xDEADBEEFu);
    TEST_CHECK(data[3] == 0xDEADBEEFu);

    memcpy(target, data, sizeof(data));
    memset(data, 0, sizeof(data));

    TEST_CHECK(dispatch_kernel(&registry, DOM_OP_MEM_COPY_VIEW,
                               &in_view, 1, &out_view, 1, 0, 0u, range) == 0);
    TEST_CHECK(data[0] == 0xDEADBEEFu);
    TEST_CHECK(data[3] == 0xDEADBEEFu);
    return 0;
}

static int test_reductions(void)
{
    dom_kernel_entry storage[16];
    dom_kernel_registry registry;
    u32 input[3] = { 5u, 1u, 9u };
    u32 output[3] = { 0u, 0u, 0u };
    dom_component_view in_view;
    dom_component_view out_view;
    dom_entity_range range;

    dom_kernel_registry_init(&registry, storage, 16u);
    dom_register_scalar_kernels(&registry);

    in_view = make_view(DOM_ECS_ELEM_U32, sizeof(u32), sizeof(u32), 3u, input, DOM_ECS_ACCESS_READ);
    out_view = make_view(DOM_ECS_ELEM_U32, sizeof(u32), sizeof(u32), 3u, output, DOM_ECS_ACCESS_WRITE);
    range.archetype_id = dom_archetype_id_make(1u);
    range.begin_index = 0u;
    range.end_index = 3u;

    TEST_CHECK(dispatch_kernel(&registry, DOM_OP_REDUCE_SUM_INT,
                               &in_view, 1, &out_view, 1, 0, 0u, range) == 0);
    TEST_CHECK(output[0] == 15u);

    TEST_CHECK(dispatch_kernel(&registry, DOM_OP_REDUCE_MIN_INT,
                               &in_view, 1, &out_view, 1, 0, 0u, range) == 0);
    TEST_CHECK(output[0] == 1u);

    TEST_CHECK(dispatch_kernel(&registry, DOM_OP_REDUCE_MAX_INT,
                               &in_view, 1, &out_view, 1, 0, 0u, range) == 0);
    TEST_CHECK(output[0] == 9u);
    return 0;
}

static int test_registry_resolution(void)
{
    dom_kernel_entry storage[8];
    dom_kernel_registry registry;
    dom_kernel_requirements reqs;
    const dom_kernel_entry* entry;

    dom_kernel_registry_init(&registry, storage, 8u);
    dom_register_scalar_kernels(&registry);

    reqs.backend_mask = DOM_KERNEL_BACKEND_MASK_ALL;
    reqs.required_capabilities = 0u;
    reqs.flags = 0u;

    entry = dom_kernel_resolve(&registry, DOM_OP_MEM_COPY_VIEW, &reqs, DOM_DET_STRICT);
    TEST_CHECK(entry != 0);
    TEST_CHECK(entry->backend_id == DOM_KERNEL_BACKEND_SCALAR);
    return 0;
}

static int test_cross_run_determinism(void)
{
    dom_kernel_entry storage[8];
    dom_kernel_registry registry;
    u32 data[2] = { 0u, 0u };
    dom_component_view out_view;
    dom_kernel_fill_params fill;
    dom_entity_range range;
    u32 snapshot[2];

    dom_kernel_registry_init(&registry, storage, 8u);
    dom_register_scalar_kernels(&registry);

    out_view = make_view(DOM_ECS_ELEM_U32, sizeof(u32), sizeof(u32), 2u, data, DOM_ECS_ACCESS_WRITE);
    memset(&fill, 0, sizeof(fill));
    fill.element_size = sizeof(u32);
    memcpy(fill.value, "\x11\x22\x33\x44", sizeof(u32));

    range.archetype_id = dom_archetype_id_make(1u);
    range.begin_index = 0u;
    range.end_index = 2u;

    TEST_CHECK(dispatch_kernel(&registry, DOM_OP_MEM_FILL_VIEW,
                               0, 0, &out_view, 1, &fill, sizeof(fill), range) == 0);
    snapshot[0] = data[0];
    snapshot[1] = data[1];

    data[0] = 0u;
    data[1] = 0u;

    TEST_CHECK(dispatch_kernel(&registry, DOM_OP_MEM_FILL_VIEW,
                               0, 0, &out_view, 1, &fill, sizeof(fill), range) == 0);
    TEST_CHECK(data[0] == snapshot[0]);
    TEST_CHECK(data[1] == snapshot[1]);
    return 0;
}

static int test_view_bounds_safety(void)
{
    dom_kernel_entry storage[8];
    dom_kernel_registry registry;
    u32 input[4] = { 10u, 20u, 30u, 40u };
    u32 output[4] = { 0u, 0u, 0u, 0u };
    dom_component_view in_view;
    dom_component_view out_view;
    dom_entity_range range;

    dom_kernel_registry_init(&registry, storage, 8u);
    dom_register_scalar_kernels(&registry);

    in_view = make_view(DOM_ECS_ELEM_U32, sizeof(u32), sizeof(u32), 4u, input, DOM_ECS_ACCESS_READ);
    out_view = make_view(DOM_ECS_ELEM_U32, sizeof(u32), sizeof(u32), 4u, output, DOM_ECS_ACCESS_WRITE);
    range.archetype_id = dom_archetype_id_make(1u);
    range.begin_index = 1u;
    range.end_index = 10u;

    TEST_CHECK(dispatch_kernel(&registry, DOM_OP_MEM_COPY_VIEW,
                               &in_view, 1, &out_view, 1, 0, 0u, range) == 0);
    TEST_CHECK(output[0] == 0u);
    TEST_CHECK(output[1] == 20u);
    TEST_CHECK(output[2] == 30u);
    TEST_CHECK(output[3] == 40u);
    return 0;
}

int main(void)
{
    if (test_fill_and_copy() != 0) return 1;
    if (test_reductions() != 0) return 1;
    if (test_registry_resolution() != 0) return 1;
    if (test_cross_run_determinism() != 0) return 1;
    if (test_view_bounds_safety() != 0) return 1;
    return 0;
}
