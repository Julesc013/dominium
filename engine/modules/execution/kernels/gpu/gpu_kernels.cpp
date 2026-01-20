/*
FILE: engine/modules/execution/kernels/gpu/gpu_kernels.cpp
MODULE: Domino
LAYER / SUBSYSTEM: Domino / execution/kernels/gpu
RESPONSIBILITY: GPU kernel backend for derived tasks (async simulation).
ALLOWED DEPENDENCIES: engine/include public headers and C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers outside execution.
DETERMINISM: GPU results are derived-only; authoritative tasks must not select this backend.
*/
#include "execution/kernels/gpu/gpu_kernels.h"
#include "execution/kernels/scalar/op_ids.h"
#include "execution/kernels/scalar/scalar_kernels.h"

#include <string.h>

enum {
    DOM_GPU_JOB_CAPACITY = 16u,
    DOM_GPU_JOB_PARAM_MAX = 64u,
    DOM_GPU_JOB_VIEW_MAX = 2
};

typedef enum dom_gpu_job_op {
    DOM_GPU_JOB_NONE = 0,
    DOM_GPU_JOB_APPLY_DELTA = 1,
    DOM_GPU_JOB_VIS_MASK = 2
} dom_gpu_job_op;

typedef struct dom_gpu_job {
    d_bool in_use;
    d_bool ready;
    dom_gpu_job_op op;
    dom_component_view inputs[DOM_GPU_JOB_VIEW_MAX];
    int input_count;
    dom_component_view outputs[DOM_GPU_JOB_VIEW_MAX];
    int output_count;
    dom_entity_range range;
    unsigned char params[DOM_GPU_JOB_PARAM_MAX];
    size_t params_size;
} dom_gpu_job;

static dom_gpu_job g_jobs[DOM_GPU_JOB_CAPACITY];

static unsigned char* dom_gpu_view_ptr(const dom_component_view* view)
{
    if (!view) {
        return 0;
    }
    return (unsigned char*)(size_t)view->backend_token;
}

static d_bool dom_gpu_view_can_read(const dom_component_view* view)
{
    return (view &&
            dom_component_view_is_valid(view) &&
            (view->access_mode & DOM_ECS_ACCESS_READ) != 0u) ? D_TRUE : D_FALSE;
}

static d_bool dom_gpu_view_can_write(const dom_component_view* view)
{
    return (view &&
            dom_component_view_is_valid(view) &&
            (view->access_mode & (DOM_ECS_ACCESS_WRITE | DOM_ECS_ACCESS_REDUCE)) != 0u)
               ? D_TRUE
               : D_FALSE;
}

static u32 dom_gpu_min_u32(u32 a, u32 b)
{
    return (a < b) ? a : b;
}

static void dom_gpu_clamp_range(u32 count, dom_entity_range range, u32* out_start, u32* out_end)
{
    u32 start = range.begin_index;
    u32 end = range.end_index;
    if (end > count) {
        end = count;
    }
    if (start > end) {
        start = end;
    }
    *out_start = start;
    *out_end = end;
}

static u32 dom_gpu_read_u32_le(const unsigned char* bytes)
{
    return (u32)bytes[0] |
           ((u32)bytes[1] << 8u) |
           ((u32)bytes[2] << 16u) |
           ((u32)bytes[3] << 24u);
}

static u32 dom_gpu_popcount_u8(u8 value)
{
    u32 count = 0u;
    u32 v = value;
    while (v) {
        count += (v & 1u);
        v >>= 1u;
    }
    return count;
}

static void dom_gpu_execute_apply_delta(const dom_gpu_job* job)
{
    const dom_component_view* baseline_view;
    const dom_component_view* out_view;
    const dom_kernel_apply_delta_params* delta_params;
    const unsigned char* delta;
    u32 delta_size;
    u32 header_bytes;
    u32 entity_count;
    u32 stride;
    u32 bitmask_bytes;
    u32 payload_bytes;
    u32 output_bytes;
    u32 baseline_bytes;
    u32 i;
    u32 start;
    u32 end;
    unsigned char* baseline_ptr;
    unsigned char* out_ptr;
    const unsigned char* bitmask;
    const unsigned char* payload;
    u32 payload_offset = 0u;

    if (!job || job->input_count < 1 || job->output_count < 1) {
        return;
    }
    baseline_view = &job->inputs[0];
    out_view = &job->outputs[0];
    if (!dom_gpu_view_can_read(baseline_view) || !dom_gpu_view_can_write(out_view)) {
        return;
    }
    if (baseline_view->element_size != 1u || out_view->element_size != 1u) {
        return;
    }
    baseline_ptr = dom_gpu_view_ptr(baseline_view);
    out_ptr = dom_gpu_view_ptr(out_view);
    if (!baseline_ptr || !out_ptr) {
        return;
    }
    delta_params = (const dom_kernel_apply_delta_params*)job->params;
    delta = delta_params->delta_bytes;
    delta_size = delta_params->delta_size;
    if (!delta || delta_size < 24u) {
        return;
    }
    header_bytes = 24u;
    entity_count = dom_gpu_read_u32_le(delta + 16u);
    stride = dom_gpu_read_u32_le(delta + 20u);
    if (stride == 0u) {
        return;
    }
    bitmask_bytes = (entity_count + 7u) / 8u;
    if (delta_size < header_bytes + bitmask_bytes) {
        return;
    }
    bitmask = delta + header_bytes;
    payload = bitmask + bitmask_bytes;

    payload_bytes = 0u;
    for (i = 0u; i < bitmask_bytes; ++i) {
        payload_bytes += dom_gpu_popcount_u8(bitmask[i]) * stride;
    }
    if (delta_size < header_bytes + bitmask_bytes + payload_bytes) {
        return;
    }

    output_bytes = out_view->count * out_view->stride;
    baseline_bytes = baseline_view->count * baseline_view->stride;
    if (output_bytes == 0u) {
        return;
    }
    {
        u32 copy_bytes = dom_gpu_min_u32(output_bytes, baseline_bytes);
        memmove(out_ptr, baseline_ptr, copy_bytes);
    }

    {
        u32 max_entities = output_bytes / stride;
        if (entity_count > max_entities) {
            entity_count = max_entities;
        }
        dom_gpu_clamp_range(entity_count, job->range, &start, &end);
    }

    for (i = 0u; i < entity_count; ++i) {
        u32 byte_index = i / 8u;
        u32 bit_index = i % 8u;
        d_bool changed = (bitmask[byte_index] & (1u << bit_index)) ? D_TRUE : D_FALSE;
        if (changed) {
            if (payload_offset + stride > payload_bytes) {
                break;
            }
            if (i >= start && i < end) {
                u32 dst_offset = i * stride;
                if (dst_offset + stride <= output_bytes) {
                    memcpy(out_ptr + dst_offset, payload + payload_offset, stride);
                }
            }
            payload_offset += stride;
        }
    }
}

static u64 dom_gpu_read_value_nonzero(const dom_component_view* view,
                                      const unsigned char* base_ptr,
                                      u32 index)
{
    size_t offset = (size_t)index * view->stride;
    if (view->element_type == DOM_ECS_ELEM_U8 ||
        view->element_type == DOM_ECS_ELEM_I8) {
        u8 value;
        memcpy(&value, base_ptr + offset, sizeof(u8));
        return value ? 1u : 0u;
    }
    if (view->element_type == DOM_ECS_ELEM_U16 ||
        view->element_type == DOM_ECS_ELEM_I16) {
        u16 value;
        memcpy(&value, base_ptr + offset, sizeof(u16));
        return value ? 1u : 0u;
    }
    if (view->element_type == DOM_ECS_ELEM_U32 ||
        view->element_type == DOM_ECS_ELEM_I32) {
        u32 value;
        memcpy(&value, base_ptr + offset, sizeof(u32));
        return value ? 1u : 0u;
    }
    if (view->element_type == DOM_ECS_ELEM_U64 ||
        view->element_type == DOM_ECS_ELEM_I64) {
        u64 value;
        memcpy(&value, base_ptr + offset, sizeof(u64));
        return value ? 1u : 0u;
    }
    return 0u;
}

static void dom_gpu_execute_visibility_mask(const dom_gpu_job* job)
{
    const dom_component_view* src;
    const dom_component_view* dst;
    const dom_kernel_visibility_params* vis_params;
    u32 entity_count;
    u32 max_entities;
    u32 start;
    u32 end;
    u32 i;
    unsigned char* src_ptr;
    unsigned char* dst_ptr;

    if (!job || job->input_count < 1 || job->output_count < 1) {
        return;
    }
    src = &job->inputs[0];
    dst = &job->outputs[0];
    if (!dom_gpu_view_can_read(src) || !dom_gpu_view_can_write(dst)) {
        return;
    }
    if (dst->element_type != DOM_ECS_ELEM_U32 || dst->element_size != sizeof(u32)) {
        return;
    }
    if (src->stride < src->element_size || dst->stride < dst->element_size) {
        return;
    }
    src_ptr = dom_gpu_view_ptr(src);
    dst_ptr = dom_gpu_view_ptr(dst);
    if (!src_ptr || !dst_ptr) {
        return;
    }

    entity_count = src->count;
    vis_params = (const dom_kernel_visibility_params*)job->params;
    if (vis_params && vis_params->entity_count > 0u &&
        vis_params->entity_count < entity_count) {
        entity_count = vis_params->entity_count;
    }
    max_entities = dst->count * 32u;
    if (entity_count > max_entities) {
        entity_count = max_entities;
    }
    dom_gpu_clamp_range(entity_count, job->range, &start, &end);

    for (i = start; i < end; ++i) {
        u32 word_index = i / 32u;
        u32 bit_index = i % 32u;
        u32* words = (u32*)(dst_ptr + (size_t)word_index * dst->stride);
        u32 mask = (1u << bit_index);
        u32 visible = (dom_gpu_read_value_nonzero(src, src_ptr, i) != 0u) ? 1u : 0u;
        if (visible) {
            *words |= mask;
        } else {
            *words &= ~mask;
        }
    }
}

static void dom_gpu_execute_job(const dom_gpu_job* job)
{
    if (!job) {
        return;
    }
    if (job->op == DOM_GPU_JOB_APPLY_DELTA) {
        dom_gpu_execute_apply_delta(job);
    } else if (job->op == DOM_GPU_JOB_VIS_MASK) {
        dom_gpu_execute_visibility_mask(job);
    }
}

static int dom_gpu_enqueue_job(dom_gpu_job_op op,
                               const dom_component_view* inputs,
                               int input_count,
                               dom_component_view* outputs,
                               int output_count,
                               const void* params,
                               size_t params_size,
                               dom_entity_range range)
{
    u32 i;
    dom_gpu_job* job = 0;
    if (input_count > DOM_GPU_JOB_VIEW_MAX || output_count > DOM_GPU_JOB_VIEW_MAX) {
        return -1;
    }
    if (params_size > DOM_GPU_JOB_PARAM_MAX) {
        return -2;
    }
    for (i = 0u; i < DOM_GPU_JOB_CAPACITY; ++i) {
        if (!g_jobs[i].in_use) {
            job = &g_jobs[i];
            break;
        }
    }
    if (!job) {
        return -3;
    }
    memset(job, 0, sizeof(*job));
    job->in_use = D_TRUE;
    job->ready = D_FALSE;
    job->op = op;
    job->input_count = input_count;
    job->output_count = output_count;
    if (inputs && input_count > 0) {
        for (i = 0u; i < (u32)input_count; ++i) {
            job->inputs[i] = inputs[i];
        }
    }
    if (outputs && output_count > 0) {
        for (i = 0u; i < (u32)output_count; ++i) {
            job->outputs[i] = outputs[i];
        }
    }
    job->range = range;
    job->params_size = params_size;
    if (params && params_size > 0u) {
        memcpy(job->params, params, params_size);
    }
    return 0;
}

static void dom_gpu_kernel_apply_delta(const dom_kernel_call_context&,
                                       const dom_component_view* inputs,
                                       int input_count,
                                       dom_component_view* outputs,
                                       int output_count,
                                       const void* params,
                                       size_t params_size,
                                       dom_entity_range range)
{
    if (dom_gpu_enqueue_job(DOM_GPU_JOB_APPLY_DELTA, inputs, input_count,
                            outputs, output_count, params, params_size, range) != 0) {
        dom_gpu_job fallback;
        memset(&fallback, 0, sizeof(fallback));
        fallback.op = DOM_GPU_JOB_APPLY_DELTA;
        fallback.input_count = input_count;
        fallback.output_count = output_count;
        if (inputs && input_count > 0) {
            fallback.inputs[0] = inputs[0];
        }
        if (outputs && output_count > 0) {
            fallback.outputs[0] = outputs[0];
        }
        fallback.range = range;
        if (params && params_size <= DOM_GPU_JOB_PARAM_MAX) {
            memcpy(fallback.params, params, params_size);
            fallback.params_size = params_size;
        }
        dom_gpu_execute_apply_delta(&fallback);
    }
}

static void dom_gpu_kernel_visibility_mask(const dom_kernel_call_context&,
                                           const dom_component_view* inputs,
                                           int input_count,
                                           dom_component_view* outputs,
                                           int output_count,
                                           const void* params,
                                           size_t params_size,
                                           dom_entity_range range)
{
    if (dom_gpu_enqueue_job(DOM_GPU_JOB_VIS_MASK, inputs, input_count,
                            outputs, output_count, params, params_size, range) != 0) {
        dom_gpu_job fallback;
        memset(&fallback, 0, sizeof(fallback));
        fallback.op = DOM_GPU_JOB_VIS_MASK;
        fallback.input_count = input_count;
        fallback.output_count = output_count;
        if (inputs && input_count > 0) {
            fallback.inputs[0] = inputs[0];
        }
        if (outputs && output_count > 0) {
            fallback.outputs[0] = outputs[0];
        }
        fallback.range = range;
        if (params && params_size <= DOM_GPU_JOB_PARAM_MAX) {
            memcpy(fallback.params, params, params_size);
            fallback.params_size = params_size;
        }
        dom_gpu_execute_visibility_mask(&fallback);
    }
}

void dom_register_gpu_kernels(dom_kernel_registry* registry,
                              const dom_gpu_caps* caps)
{
    dom_kernel_metadata meta;
    if (!registry || !caps) {
        return;
    }
    if ((caps->cap_mask & DOM_GPU_CAP_COMPUTE) == 0u) {
        return;
    }
    meta.capability_mask = DOM_GPU_CAP_COMPUTE;
    meta.deterministic = D_TRUE;
    meta.flags = DOM_KERNEL_META_DERIVED_ONLY;

    dom_kernel_register(registry, DOM_OP_BUILD_VISIBILITY_MASK, DOM_KERNEL_BACKEND_GPU,
                        dom_gpu_kernel_visibility_mask, &meta);
    dom_kernel_register(registry, DOM_OP_APPLY_DELTA_PACKED, DOM_KERNEL_BACKEND_GPU,
                        dom_gpu_kernel_apply_delta, &meta);
}

u32 dom_gpu_kernels_pending(void)
{
    u32 i;
    u32 count = 0u;
    for (i = 0u; i < DOM_GPU_JOB_CAPACITY; ++i) {
        if (g_jobs[i].in_use && !g_jobs[i].ready) {
            count += 1u;
        }
    }
    return count;
}

void dom_gpu_kernels_process(u32 max_jobs)
{
    u32 i;
    u32 processed = 0u;
    for (i = 0u; i < DOM_GPU_JOB_CAPACITY; ++i) {
        if (processed >= max_jobs) {
            return;
        }
        if (g_jobs[i].in_use && !g_jobs[i].ready) {
            dom_gpu_execute_job(&g_jobs[i]);
            g_jobs[i].ready = D_TRUE;
            g_jobs[i].in_use = D_FALSE;
            processed += 1u;
        }
    }
}

void dom_gpu_kernels_clear(void)
{
    memset(g_jobs, 0, sizeof(g_jobs));
}
