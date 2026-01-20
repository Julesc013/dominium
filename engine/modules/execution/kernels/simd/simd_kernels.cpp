/*
FILE: engine/modules/execution/kernels/simd/simd_kernels.cpp
MODULE: Domino
LAYER / SUBSYSTEM: Domino / execution/kernels/simd
RESPONSIBILITY: SIMD kernel implementations and registration.
ALLOWED DEPENDENCIES: engine/include public headers and C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers outside execution.
DETERMINISM: SIMD variants must match scalar outputs for authoritative tasks.
*/
#include "execution/kernels/simd/simd_kernels.h"
#include "execution/kernels/scalar/op_ids.h"
#include "execution/kernels/scalar/scalar_kernels.h"

#include <string.h>

static u32 dom_simd_min_u32(u32 a, u32 b)
{
    return (a < b) ? a : b;
}

static unsigned char* dom_simd_view_ptr(const dom_component_view* view)
{
    if (!view) {
        return 0;
    }
    return (unsigned char*)(size_t)view->backend_token;
}

static d_bool dom_simd_view_can_read(const dom_component_view* view)
{
    return (view &&
            dom_component_view_is_valid(view) &&
            (view->access_mode & DOM_ECS_ACCESS_READ) != 0u) ? D_TRUE : D_FALSE;
}

static d_bool dom_simd_view_can_write(const dom_component_view* view)
{
    return (view &&
            dom_component_view_is_valid(view) &&
            (view->access_mode & (DOM_ECS_ACCESS_WRITE | DOM_ECS_ACCESS_REDUCE)) != 0u)
               ? D_TRUE
               : D_FALSE;
}

static void dom_simd_clamp_range(u32 count, dom_entity_range range, u32* out_start, u32* out_end)
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

static void dom_simd_mem_copy_view(const dom_kernel_call_context&,
                                   const dom_component_view* inputs,
                                   int input_count,
                                   dom_component_view* outputs,
                                   int output_count,
                                   const void*,
                                   size_t,
                                   dom_entity_range range)
{
    const dom_component_view* src;
    dom_component_view* dst;
    u32 count;
    u32 start;
    u32 end;
    u32 i;
    unsigned char* src_ptr;
    unsigned char* dst_ptr;

    if (!inputs || !outputs || input_count < 1 || output_count < 1) {
        return;
    }
    src = &inputs[0];
    dst = &outputs[0];
    if (!dom_simd_view_can_read(src) || !dom_simd_view_can_write(dst)) {
        return;
    }
    if (src->element_size == 0u || dst->element_size == 0u) {
        return;
    }
    if (src->element_size != dst->element_size) {
        return;
    }
    if (src->stride < src->element_size || dst->stride < dst->element_size) {
        return;
    }
    src_ptr = dom_simd_view_ptr(src);
    dst_ptr = dom_simd_view_ptr(dst);
    if (!src_ptr || !dst_ptr) {
        return;
    }
    count = dom_simd_min_u32(src->count, dst->count);
    dom_simd_clamp_range(count, range, &start, &end);
    for (i = start; i < end; ++i) {
        size_t src_offset = (size_t)i * src->stride;
        size_t dst_offset = (size_t)i * dst->stride;
        memcpy(dst_ptr + dst_offset, src_ptr + src_offset, src->element_size);
    }
}

static void dom_simd_mem_fill_view(const dom_kernel_call_context&,
                                   const dom_component_view*,
                                   int,
                                   dom_component_view* outputs,
                                   int output_count,
                                   const void* params,
                                   size_t,
                                   dom_entity_range range)
{
    const dom_kernel_fill_params* fill;
    dom_component_view* dst;
    u32 start;
    u32 end;
    u32 i;
    unsigned char* dst_ptr;

    if (!outputs || output_count < 1 || !params) {
        return;
    }
    dst = &outputs[0];
    if (!dom_simd_view_can_write(dst)) {
        return;
    }
    fill = (const dom_kernel_fill_params*)params;
    if (fill->element_size == 0u || fill->element_size > sizeof(fill->value)) {
        return;
    }
    if (dst->element_size != fill->element_size || dst->stride < dst->element_size) {
        return;
    }
    dst_ptr = dom_simd_view_ptr(dst);
    if (!dst_ptr) {
        return;
    }
    dom_simd_clamp_range(dst->count, range, &start, &end);
    for (i = start; i < end; ++i) {
        size_t dst_offset = (size_t)i * dst->stride;
        memcpy(dst_ptr + dst_offset, fill->value, dst->element_size);
    }
}

static int dom_simd_reduce_params(const dom_component_view* src,
                                  const dom_component_view* dst,
                                  dom_entity_range range,
                                  u32* out_start,
                                  u32* out_end,
                                  unsigned char** out_src_ptr,
                                  unsigned char** out_dst_ptr)
{
    u32 count;
    if (!src || !dst) {
        return 0;
    }
    if (!dom_simd_view_can_read(src) || !dom_simd_view_can_write(dst)) {
        return 0;
    }
    if (src->element_size == 0u || dst->element_size == 0u) {
        return 0;
    }
    if (src->element_size != dst->element_size) {
        return 0;
    }
    if (src->stride < src->element_size || dst->stride < dst->element_size) {
        return 0;
    }
    *out_src_ptr = dom_simd_view_ptr(src);
    *out_dst_ptr = dom_simd_view_ptr(dst);
    if (!*out_src_ptr || !*out_dst_ptr) {
        return 0;
    }
    count = dom_simd_min_u32(src->count, dst->count);
    dom_simd_clamp_range(count, range, out_start, out_end);
    if (*out_start >= *out_end) {
        return 0;
    }
    return 1;
}

static void dom_simd_reduce_sum_int(const dom_kernel_call_context&,
                                    const dom_component_view* inputs,
                                    int input_count,
                                    dom_component_view* outputs,
                                    int output_count,
                                    const void*,
                                    size_t,
                                    dom_entity_range range)
{
    const dom_component_view* src;
    dom_component_view* dst;
    u32 start;
    u32 end;
    u32 i;
    unsigned char* src_ptr;
    unsigned char* dst_ptr;

    if (!inputs || !outputs || input_count < 1 || output_count < 1) {
        return;
    }
    src = &inputs[0];
    dst = &outputs[0];
    if (!dom_simd_reduce_params(src, dst, range, &start, &end, &src_ptr, &dst_ptr)) {
        return;
    }
    if (src->element_type == DOM_ECS_ELEM_U64) {
        u64 acc;
        memcpy(&acc, src_ptr + (size_t)start * src->stride, sizeof(u64));
        for (i = start + 1u; i < end; ++i) {
            u64 value;
            memcpy(&value, src_ptr + (size_t)i * src->stride, sizeof(u64));
            acc += value;
        }
        memcpy(dst_ptr + (size_t)start * dst->stride, &acc, sizeof(u64));
    } else if (src->element_type == DOM_ECS_ELEM_U32) {
        u32 acc;
        memcpy(&acc, src_ptr + (size_t)start * src->stride, sizeof(u32));
        for (i = start + 1u; i < end; ++i) {
            u32 value;
            memcpy(&value, src_ptr + (size_t)i * src->stride, sizeof(u32));
            acc += value;
        }
        memcpy(dst_ptr + (size_t)start * dst->stride, &acc, sizeof(u32));
    } else if (src->element_type == DOM_ECS_ELEM_I64) {
        i64 acc;
        memcpy(&acc, src_ptr + (size_t)start * src->stride, sizeof(i64));
        for (i = start + 1u; i < end; ++i) {
            i64 value;
            memcpy(&value, src_ptr + (size_t)i * src->stride, sizeof(i64));
            acc += value;
        }
        memcpy(dst_ptr + (size_t)start * dst->stride, &acc, sizeof(i64));
    } else if (src->element_type == DOM_ECS_ELEM_I32) {
        i32 acc;
        memcpy(&acc, src_ptr + (size_t)start * src->stride, sizeof(i32));
        for (i = start + 1u; i < end; ++i) {
            i32 value;
            memcpy(&value, src_ptr + (size_t)i * src->stride, sizeof(i32));
            acc += value;
        }
        memcpy(dst_ptr + (size_t)start * dst->stride, &acc, sizeof(i32));
    }
}

static u64 dom_simd_read_value_nonzero(const dom_component_view* view,
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

static void dom_simd_build_visibility_mask(const dom_kernel_call_context&,
                                           const dom_component_view* inputs,
                                           int input_count,
                                           dom_component_view* outputs,
                                           int output_count,
                                           const void* params,
                                           size_t,
                                           dom_entity_range range)
{
    const dom_component_view* src;
    dom_component_view* dst;
    const dom_kernel_visibility_params* vis_params;
    u32 entity_count;
    u32 max_entities;
    u32 start;
    u32 end;
    u32 i;
    unsigned char* src_ptr;
    unsigned char* dst_ptr;

    if (!inputs || !outputs || input_count < 1 || output_count < 1) {
        return;
    }
    src = &inputs[0];
    dst = &outputs[0];
    if (!dom_simd_view_can_read(src) || !dom_simd_view_can_write(dst)) {
        return;
    }
    if (dst->element_type != DOM_ECS_ELEM_U32 || dst->element_size != sizeof(u32)) {
        return;
    }
    if (src->stride < src->element_size || dst->stride < dst->element_size) {
        return;
    }
    src_ptr = dom_simd_view_ptr(src);
    dst_ptr = dom_simd_view_ptr(dst);
    if (!src_ptr || !dst_ptr) {
        return;
    }

    entity_count = src->count;
    vis_params = (const dom_kernel_visibility_params*)params;
    if (vis_params && vis_params->entity_count > 0u &&
        vis_params->entity_count < entity_count) {
        entity_count = vis_params->entity_count;
    }
    max_entities = dst->count * 32u;
    if (entity_count > max_entities) {
        entity_count = max_entities;
    }
    dom_simd_clamp_range(entity_count, range, &start, &end);

    for (i = start; i < end; ++i) {
        u32 word_index = i / 32u;
        u32 bit_index = i % 32u;
        u32* words = (u32*)(dst_ptr + (size_t)word_index * dst->stride);
        u32 mask = (1u << bit_index);
        u32 visible = (dom_simd_read_value_nonzero(src, src_ptr, i) != 0u) ? 1u : 0u;
        if (visible) {
            *words |= mask;
        } else {
            *words &= ~mask;
        }
    }
}

void dom_register_simd_kernels(dom_kernel_registry* registry,
                               const dom_simd_caps* caps)
{
    dom_kernel_metadata meta;
    u32 required_caps;
    if (!registry || !caps) {
        return;
    }
    if ((caps->mask & DOM_SIMD_CAP_ANY) == 0u) {
        return;
    }
    required_caps = caps->mask & DOM_SIMD_CAP_ANY;
    meta.capability_mask = required_caps;
    meta.deterministic = D_TRUE;
    meta.flags = 0u;

    dom_kernel_register(registry, DOM_OP_MEM_COPY_VIEW, DOM_KERNEL_BACKEND_SIMD,
                        dom_simd_mem_copy_view, &meta);
    dom_kernel_register(registry, DOM_OP_MEM_FILL_VIEW, DOM_KERNEL_BACKEND_SIMD,
                        dom_simd_mem_fill_view, &meta);
    dom_kernel_register(registry, DOM_OP_REDUCE_SUM_INT, DOM_KERNEL_BACKEND_SIMD,
                        dom_simd_reduce_sum_int, &meta);
    dom_kernel_register(registry, DOM_OP_BUILD_VISIBILITY_MASK, DOM_KERNEL_BACKEND_SIMD,
                        dom_simd_build_visibility_mask, &meta);
}
