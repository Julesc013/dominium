/*
FILE: engine/modules/execution/kernels/scalar/scalar_kernels.cpp
MODULE: Domino
LAYER / SUBSYSTEM: Domino / execution/kernels/scalar
RESPONSIBILITY: Scalar kernel implementations and registration.
ALLOWED DEPENDENCIES: engine/include public headers and C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers outside execution.
DETERMINISM: Scalar implementations are deterministic by default.
*/
#include "execution/kernels/scalar/scalar_kernels.h"
#include "execution/kernels/scalar/op_ids.h"

#include <string.h>

static u32 dom_scalar_min_u32(u32 a, u32 b)
{
    return (a < b) ? a : b;
}

static unsigned char* dom_scalar_view_ptr(const dom_component_view* view)
{
    if (!view) {
        return 0;
    }
    return (unsigned char*)(size_t)view->backend_token;
}

static d_bool dom_scalar_view_can_read(const dom_component_view* view)
{
    return (view &&
            dom_component_view_is_valid(view) &&
            (view->access_mode & DOM_ECS_ACCESS_READ) != 0u) ? D_TRUE : D_FALSE;
}

static d_bool dom_scalar_view_can_write(const dom_component_view* view)
{
    return (view &&
            dom_component_view_is_valid(view) &&
            (view->access_mode & (DOM_ECS_ACCESS_WRITE | DOM_ECS_ACCESS_REDUCE)) != 0u)
               ? D_TRUE
               : D_FALSE;
}

static void dom_scalar_clamp_range(u32 count, dom_entity_range range, u32* out_start, u32* out_end)
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

static void dom_kernel_mem_copy_view(const dom_kernel_call_context&,
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
    if (!dom_scalar_view_can_read(src) || !dom_scalar_view_can_write(dst)) {
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
    src_ptr = dom_scalar_view_ptr(src);
    dst_ptr = dom_scalar_view_ptr(dst);
    if (!src_ptr || !dst_ptr) {
        return;
    }
    count = dom_scalar_min_u32(src->count, dst->count);
    dom_scalar_clamp_range(count, range, &start, &end);
    for (i = start; i < end; ++i) {
        size_t src_offset = (size_t)i * src->stride;
        size_t dst_offset = (size_t)i * dst->stride;
        memcpy(dst_ptr + dst_offset, src_ptr + src_offset, src->element_size);
    }
}

static void dom_kernel_mem_fill_view(const dom_kernel_call_context&,
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
    if (!dom_scalar_view_can_write(dst)) {
        return;
    }
    fill = (const dom_kernel_fill_params*)params;
    if (fill->element_size == 0u || fill->element_size > sizeof(fill->value)) {
        return;
    }
    if (dst->element_size != fill->element_size || dst->stride < dst->element_size) {
        return;
    }
    dst_ptr = dom_scalar_view_ptr(dst);
    if (!dst_ptr) {
        return;
    }
    dom_scalar_clamp_range(dst->count, range, &start, &end);
    for (i = start; i < end; ++i) {
        size_t dst_offset = (size_t)i * dst->stride;
        memcpy(dst_ptr + dst_offset, fill->value, dst->element_size);
    }
}

static int dom_scalar_reduce_params(const dom_component_view* src,
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
    if (!dom_scalar_view_can_read(src) || !dom_scalar_view_can_write(dst)) {
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
    *out_src_ptr = dom_scalar_view_ptr(src);
    *out_dst_ptr = dom_scalar_view_ptr(dst);
    if (!*out_src_ptr || !*out_dst_ptr) {
        return 0;
    }
    count = dom_scalar_min_u32(src->count, dst->count);
    dom_scalar_clamp_range(count, range, out_start, out_end);
    if (*out_start >= *out_end) {
        return 0;
    }
    return 1;
}

static void dom_kernel_reduce_sum_int(const dom_kernel_call_context&,
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
    if (!dom_scalar_reduce_params(src, dst, range, &start, &end, &src_ptr, &dst_ptr)) {
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

static void dom_kernel_reduce_min_int(const dom_kernel_call_context&,
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
    if (!dom_scalar_reduce_params(src, dst, range, &start, &end, &src_ptr, &dst_ptr)) {
        return;
    }
    if (src->element_type == DOM_ECS_ELEM_U64) {
        u64 acc;
        memcpy(&acc, src_ptr + (size_t)start * src->stride, sizeof(u64));
        for (i = start + 1u; i < end; ++i) {
            u64 value;
            memcpy(&value, src_ptr + (size_t)i * src->stride, sizeof(u64));
            acc = (value < acc) ? value : acc;
        }
        memcpy(dst_ptr + (size_t)start * dst->stride, &acc, sizeof(u64));
    } else if (src->element_type == DOM_ECS_ELEM_U32) {
        u32 acc;
        memcpy(&acc, src_ptr + (size_t)start * src->stride, sizeof(u32));
        for (i = start + 1u; i < end; ++i) {
            u32 value;
            memcpy(&value, src_ptr + (size_t)i * src->stride, sizeof(u32));
            acc = (value < acc) ? value : acc;
        }
        memcpy(dst_ptr + (size_t)start * dst->stride, &acc, sizeof(u32));
    } else if (src->element_type == DOM_ECS_ELEM_I64) {
        i64 acc;
        memcpy(&acc, src_ptr + (size_t)start * src->stride, sizeof(i64));
        for (i = start + 1u; i < end; ++i) {
            i64 value;
            memcpy(&value, src_ptr + (size_t)i * src->stride, sizeof(i64));
            acc = (value < acc) ? value : acc;
        }
        memcpy(dst_ptr + (size_t)start * dst->stride, &acc, sizeof(i64));
    } else if (src->element_type == DOM_ECS_ELEM_I32) {
        i32 acc;
        memcpy(&acc, src_ptr + (size_t)start * src->stride, sizeof(i32));
        for (i = start + 1u; i < end; ++i) {
            i32 value;
            memcpy(&value, src_ptr + (size_t)i * src->stride, sizeof(i32));
            acc = (value < acc) ? value : acc;
        }
        memcpy(dst_ptr + (size_t)start * dst->stride, &acc, sizeof(i32));
    }
}

static void dom_kernel_reduce_max_int(const dom_kernel_call_context&,
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
    if (!dom_scalar_reduce_params(src, dst, range, &start, &end, &src_ptr, &dst_ptr)) {
        return;
    }
    if (src->element_type == DOM_ECS_ELEM_U64) {
        u64 acc;
        memcpy(&acc, src_ptr + (size_t)start * src->stride, sizeof(u64));
        for (i = start + 1u; i < end; ++i) {
            u64 value;
            memcpy(&value, src_ptr + (size_t)i * src->stride, sizeof(u64));
            acc = (value > acc) ? value : acc;
        }
        memcpy(dst_ptr + (size_t)start * dst->stride, &acc, sizeof(u64));
    } else if (src->element_type == DOM_ECS_ELEM_U32) {
        u32 acc;
        memcpy(&acc, src_ptr + (size_t)start * src->stride, sizeof(u32));
        for (i = start + 1u; i < end; ++i) {
            u32 value;
            memcpy(&value, src_ptr + (size_t)i * src->stride, sizeof(u32));
            acc = (value > acc) ? value : acc;
        }
        memcpy(dst_ptr + (size_t)start * dst->stride, &acc, sizeof(u32));
    } else if (src->element_type == DOM_ECS_ELEM_I64) {
        i64 acc;
        memcpy(&acc, src_ptr + (size_t)start * src->stride, sizeof(i64));
        for (i = start + 1u; i < end; ++i) {
            i64 value;
            memcpy(&value, src_ptr + (size_t)i * src->stride, sizeof(i64));
            acc = (value > acc) ? value : acc;
        }
        memcpy(dst_ptr + (size_t)start * dst->stride, &acc, sizeof(i64));
    } else if (src->element_type == DOM_ECS_ELEM_I32) {
        i32 acc;
        memcpy(&acc, src_ptr + (size_t)start * src->stride, sizeof(i32));
        for (i = start + 1u; i < end; ++i) {
            i32 value;
            memcpy(&value, src_ptr + (size_t)i * src->stride, sizeof(i32));
            acc = (value > acc) ? value : acc;
        }
        memcpy(dst_ptr + (size_t)start * dst->stride, &acc, sizeof(i32));
    }
}

static u32 dom_scalar_read_u32_le(const unsigned char* bytes)
{
    return (u32)bytes[0] |
           ((u32)bytes[1] << 8u) |
           ((u32)bytes[2] << 16u) |
           ((u32)bytes[3] << 24u);
}

static u32 dom_scalar_popcount_u8(u8 value)
{
    u32 count = 0u;
    u32 v = value;
    while (v) {
        count += (v & 1u);
        v >>= 1u;
    }
    return count;
}

static void dom_kernel_apply_delta_packed(const dom_kernel_call_context&,
                                          const dom_component_view* inputs,
                                          int input_count,
                                          dom_component_view* outputs,
                                          int output_count,
                                          const void* params,
                                          size_t,
                                          dom_entity_range range)
{
    const dom_kernel_apply_delta_params* delta_params;
    const dom_component_view* baseline_view;
    dom_component_view* out_view;
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

    if (!inputs || !outputs || input_count < 1 || output_count < 1 || !params) {
        return;
    }
    baseline_view = &inputs[0];
    out_view = &outputs[0];
    if (!dom_scalar_view_can_read(baseline_view) || !dom_scalar_view_can_write(out_view)) {
        return;
    }
    if (baseline_view->element_size != 1u || out_view->element_size != 1u) {
        return;
    }
    if (baseline_view->stride < 1u || out_view->stride < 1u) {
        return;
    }
    baseline_ptr = dom_scalar_view_ptr(baseline_view);
    out_ptr = dom_scalar_view_ptr(out_view);
    if (!baseline_ptr || !out_ptr) {
        return;
    }
    delta_params = (const dom_kernel_apply_delta_params*)params;
    delta = delta_params->delta_bytes;
    delta_size = delta_params->delta_size;
    if (!delta || delta_size < 24u) {
        return;
    }
    header_bytes = 24u;
    entity_count = dom_scalar_read_u32_le(delta + 16u);
    stride = dom_scalar_read_u32_le(delta + 20u);
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
        payload_bytes += dom_scalar_popcount_u8(bitmask[i]) * stride;
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
        u32 copy_bytes = dom_scalar_min_u32(output_bytes, baseline_bytes);
        memmove(out_ptr, baseline_ptr, copy_bytes);
    }

    {
        u32 max_entities = output_bytes / stride;
        if (entity_count > max_entities) {
            entity_count = max_entities;
        }
        dom_scalar_clamp_range(entity_count, range, &start, &end);
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

static u64 dom_scalar_read_value_nonzero(const dom_component_view* view,
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

static void dom_kernel_build_visibility_mask(const dom_kernel_call_context&,
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
    if (!dom_scalar_view_can_read(src) || !dom_scalar_view_can_write(dst)) {
        return;
    }
    if (dst->element_type != DOM_ECS_ELEM_U32 || dst->element_size != sizeof(u32)) {
        return;
    }
    if (src->stride < src->element_size || dst->stride < dst->element_size) {
        return;
    }
    src_ptr = dom_scalar_view_ptr(src);
    dst_ptr = dom_scalar_view_ptr(dst);
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
    dom_scalar_clamp_range(entity_count, range, &start, &end);

    for (i = start; i < end; ++i) {
        u32 word_index = i / 32u;
        u32 bit_index = i % 32u;
        u32* words = (u32*)(dst_ptr + (size_t)word_index * dst->stride);
        u32 mask = (1u << bit_index);
        u32 visible = (dom_scalar_read_value_nonzero(src, src_ptr, i) != 0u) ? 1u : 0u;
        if (visible) {
            *words |= mask;
        } else {
            *words &= ~mask;
        }
    }
}

void dom_register_scalar_kernels(dom_kernel_registry* registry)
{
    dom_kernel_metadata meta;
    if (!registry) {
        return;
    }
    meta.capability_mask = 0u;
    meta.deterministic = D_TRUE;
    meta.flags = 0u;

    dom_kernel_register(registry, DOM_OP_MEM_COPY_VIEW, DOM_KERNEL_BACKEND_SCALAR,
                        dom_kernel_mem_copy_view, &meta);
    dom_kernel_register(registry, DOM_OP_MEM_FILL_VIEW, DOM_KERNEL_BACKEND_SCALAR,
                        dom_kernel_mem_fill_view, &meta);
    dom_kernel_register(registry, DOM_OP_REDUCE_SUM_INT, DOM_KERNEL_BACKEND_SCALAR,
                        dom_kernel_reduce_sum_int, &meta);
    dom_kernel_register(registry, DOM_OP_REDUCE_MIN_INT, DOM_KERNEL_BACKEND_SCALAR,
                        dom_kernel_reduce_min_int, &meta);
    dom_kernel_register(registry, DOM_OP_REDUCE_MAX_INT, DOM_KERNEL_BACKEND_SCALAR,
                        dom_kernel_reduce_max_int, &meta);
    dom_kernel_register(registry, DOM_OP_APPLY_DELTA_PACKED, DOM_KERNEL_BACKEND_SCALAR,
                        dom_kernel_apply_delta_packed, &meta);
    dom_kernel_register(registry, DOM_OP_BUILD_VISIBILITY_MASK, DOM_KERNEL_BACKEND_SCALAR,
                        dom_kernel_build_visibility_mask, &meta);
}
