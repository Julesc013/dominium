/*
GPU kernel fallback tests (KERN3).
*/
#include "execution/kernels/kernel_registry.h"
#include "execution/kernels/scalar/scalar_kernels.h"
#include "execution/kernels/scalar/op_ids.h"
#include "execution/kernels/gpu/gpu_kernels.h"
#include "execution/kernels/gpu/gpu_caps.h"
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

static int dispatch_with_class(dom_kernel_registry* registry,
                               dom_kernel_op_id op_id,
                               u32 determinism_class,
                               const dom_component_view* inputs,
                               int input_count,
                               dom_component_view* outputs,
                               int output_count,
                               const void* params,
                               size_t params_size,
                               dom_entity_range range,
                               u32 backend_mask)
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
    call.determinism_class = determinism_class;

    reqs.backend_mask = DOM_KERNEL_BACKEND_MASK_ALL;
    reqs.required_capabilities = 0u;
    reqs.flags = 0u;

    return dom_kernel_dispatch(registry, &call, &reqs, &ctx);
}

static int test_gpu_disabled_fallback(void)
{
    dom_kernel_entry storage[16];
    dom_kernel_registry registry;
    dom_gpu_caps caps;
    dom_kernel_requirements reqs;
    const dom_kernel_entry* entry;

    dom_kernel_registry_init(&registry, storage, 16u);
    dom_register_scalar_kernels(&registry);
    caps.cap_mask = 0u;
    caps.max_buffer_bytes = 0u;
    dom_register_gpu_kernels(&registry, &caps);

    reqs.backend_mask = DOM_KERNEL_BACKEND_MASK_ALL;
    reqs.required_capabilities = 0u;
    reqs.flags = 0u;

    entry = dom_kernel_resolve(&registry, DOM_OP_BUILD_VISIBILITY_MASK, &reqs, DOM_DET_DERIVED);
    TEST_CHECK(entry != 0);
    TEST_CHECK(entry->backend_id == DOM_KERNEL_BACKEND_SCALAR);
    return 0;
}

static int test_gpu_enabled_derived_selection(void)
{
    dom_kernel_entry storage[16];
    dom_kernel_registry registry;
    dom_gpu_caps caps;
    dom_kernel_requirements reqs;
    const dom_kernel_entry* entry;

    dom_kernel_registry_init(&registry, storage, 16u);
    dom_register_scalar_kernels(&registry);
    caps.cap_mask = DOM_GPU_CAP_COMPUTE;
    caps.max_buffer_bytes = 1024u;
    dom_register_gpu_kernels(&registry, &caps);

    reqs.backend_mask = DOM_KERNEL_BACKEND_MASK_ALL;
    reqs.required_capabilities = 0u;
    reqs.flags = 0u;

    entry = dom_kernel_resolve(&registry, DOM_OP_BUILD_VISIBILITY_MASK, &reqs, DOM_DET_DERIVED);
    TEST_CHECK(entry != 0);
    TEST_CHECK(entry->backend_id == DOM_KERNEL_BACKEND_GPU);
    return 0;
}

static int test_gpu_non_authoritative_guarantee(void)
{
    dom_kernel_entry storage[16];
    dom_kernel_registry registry;
    dom_gpu_caps caps;
    dom_kernel_requirements reqs;
    const dom_kernel_entry* entry;

    dom_kernel_registry_init(&registry, storage, 16u);
    dom_register_scalar_kernels(&registry);
    caps.cap_mask = DOM_GPU_CAP_COMPUTE;
    caps.max_buffer_bytes = 1024u;
    dom_register_gpu_kernels(&registry, &caps);

    reqs.backend_mask = DOM_KERNEL_BACKEND_MASK_ALL;
    reqs.required_capabilities = 0u;
    reqs.flags = 0u;

    entry = dom_kernel_resolve(&registry, DOM_OP_BUILD_VISIBILITY_MASK, &reqs, DOM_DET_STRICT);
    TEST_CHECK(entry != 0);
    TEST_CHECK(entry->backend_id != DOM_KERNEL_BACKEND_GPU);
    return 0;
}

static int test_gpu_fallback_correctness(void)
{
    dom_kernel_entry storage[32];
    dom_kernel_registry registry;
    dom_gpu_caps caps;
    u8 input[12];
    u32 out_cpu[1];
    u32 out_gpu[1];
    dom_component_view in_view;
    dom_component_view out_view_cpu;
    dom_component_view out_view_gpu;
    dom_kernel_visibility_params params;
    dom_entity_range range;
    u32 i;

    dom_kernel_registry_init(&registry, storage, 32u);
    dom_register_scalar_kernels(&registry);
    caps.cap_mask = DOM_GPU_CAP_COMPUTE;
    caps.max_buffer_bytes = 1024u;
    dom_register_gpu_kernels(&registry, &caps);

    for (i = 0u; i < 12u; ++i) {
        input[i] = (u8)((i % 2u) ? 1u : 0u);
    }
    out_cpu[0] = 0u;
    out_gpu[0] = 0u;
    in_view = make_view(DOM_ECS_ELEM_U8, sizeof(u8), sizeof(u8), 12u,
                        input, DOM_ECS_ACCESS_READ);
    out_view_cpu = make_view(DOM_ECS_ELEM_U32, sizeof(u32), sizeof(u32), 1u,
                             out_cpu, DOM_ECS_ACCESS_WRITE);
    out_view_gpu = make_view(DOM_ECS_ELEM_U32, sizeof(u32), sizeof(u32), 1u,
                             out_gpu, DOM_ECS_ACCESS_WRITE);

    params.entity_count = 12u;
    range.archetype_id = dom_archetype_id_make(1u);
    range.begin_index = 0u;
    range.end_index = 12u;

    TEST_CHECK(dispatch_with_class(&registry, DOM_OP_BUILD_VISIBILITY_MASK,
                                   DOM_DET_STRICT,
                                   &in_view, 1, &out_view_cpu, 1,
                                   &params, sizeof(params), range,
                                   DOM_KERNEL_BACKEND_MASK_ALL) == 0);

    out_gpu[0] = 0u;
    TEST_CHECK(dispatch_with_class(&registry, DOM_OP_BUILD_VISIBILITY_MASK,
                                   DOM_DET_DERIVED,
                                   &in_view, 1, &out_view_gpu, 1,
                                   &params, sizeof(params), range,
                                   DOM_KERNEL_BACKEND_MASK_ALL) == 0);
    TEST_CHECK(dom_gpu_kernels_pending() > 0u);
    dom_gpu_kernels_process(4u);
    TEST_CHECK(out_cpu[0] == out_gpu[0]);
    return 0;
}

int main(void)
{
    dom_gpu_kernels_clear();
    if (test_gpu_disabled_fallback() != 0) return 1;
    dom_gpu_kernels_clear();
    if (test_gpu_enabled_derived_selection() != 0) return 1;
    dom_gpu_kernels_clear();
    if (test_gpu_non_authoritative_guarantee() != 0) return 1;
    dom_gpu_kernels_clear();
    if (test_gpu_fallback_correctness() != 0) return 1;
    return 0;
}
