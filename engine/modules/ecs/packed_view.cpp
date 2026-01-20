/*
FILE: engine/modules/ecs/packed_view.cpp
MODULE: Domino
LAYER / SUBSYSTEM: Domino / ecs
RESPONSIBILITY: Deterministic packed view builder.
ALLOWED DEPENDENCIES: engine/include public headers and C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers outside ecs.
DETERMINISM: Explicit byte order and stable field ordering only.
*/
#include "domino/ecs/ecs_packed_view.h"

#include <string.h>

static u32 dom_packed_expected_size(u32 element_type)
{
    switch (element_type) {
    case DOM_ECS_ELEM_U8:
    case DOM_ECS_ELEM_I8:
        return 1u;
    case DOM_ECS_ELEM_U16:
    case DOM_ECS_ELEM_I16:
        return 2u;
    case DOM_ECS_ELEM_U32:
    case DOM_ECS_ELEM_I32:
    case DOM_ECS_ELEM_FIXED_Q16:
        return 4u;
    case DOM_ECS_ELEM_U64:
    case DOM_ECS_ELEM_I64:
    case DOM_ECS_ELEM_FIXED_Q32:
        return 8u;
    default:
        return 0u;
    }
}

static int dom_packed_validate_fields(const dom_packed_field_desc* fields, u32 field_count)
{
    u32 i;
    if (!fields || field_count == 0u) {
        return 0;
    }
    for (i = 0u; i < field_count; ++i) {
        u32 expected = dom_packed_expected_size(fields[i].element_type);
        if (expected == 0u) {
            return 0;
        }
        if (fields[i].element_size != expected) {
            return 0;
        }
    }
    return 1;
}

static void dom_packed_write_u16(unsigned char* dst, u16 value)
{
    dst[0] = (unsigned char)(value & 0xFFu);
    dst[1] = (unsigned char)((value >> 8u) & 0xFFu);
}

static void dom_packed_write_u32(unsigned char* dst, u32 value)
{
    dst[0] = (unsigned char)(value & 0xFFu);
    dst[1] = (unsigned char)((value >> 8u) & 0xFFu);
    dst[2] = (unsigned char)((value >> 16u) & 0xFFu);
    dst[3] = (unsigned char)((value >> 24u) & 0xFFu);
}

static void dom_packed_write_u64(unsigned char* dst, u64 value)
{
    u32 i;
    for (i = 0u; i < 8u; ++i) {
        dst[i] = (unsigned char)((value >> (i * 8u)) & 0xFFu);
    }
}

static int dom_packed_pack_value(const dom_packed_field_desc* desc,
                                 const dom_packed_field_source* source,
                                 u32 index,
                                 unsigned char* dst)
{
    const unsigned char* src_bytes;
    if (!desc || !source || !dst || !source->data) {
        return 0;
    }
    src_bytes = (const unsigned char*)source->data + (size_t)index * source->stride;
    switch (desc->element_size) {
    case 1u: {
        u8 value;
        memcpy(&value, src_bytes, sizeof(u8));
        dst[0] = (unsigned char)value;
        return 1;
    }
    case 2u: {
        u16 value;
        memcpy(&value, src_bytes, sizeof(u16));
        dom_packed_write_u16(dst, value);
        return 1;
    }
    case 4u: {
        u32 value;
        memcpy(&value, src_bytes, sizeof(u32));
        dom_packed_write_u32(dst, value);
        return 1;
    }
    case 8u: {
        u64 value;
        memcpy(&value, src_bytes, sizeof(u64));
        dom_packed_write_u64(dst, value);
        return 1;
    }
    default:
        return 0;
    }
}

u32 dom_packed_view_calc_stride(const dom_packed_field_desc* fields, u32 field_count)
{
    u32 i;
    u32 stride = 0u;
    if (!fields || field_count == 0u) {
        return 0u;
    }
    for (i = 0u; i < field_count; ++i) {
        stride += fields[i].element_size;
    }
    return stride;
}

d_bool dom_packed_fields_are_sorted(const dom_packed_field_desc* fields, u32 field_count)
{
    u32 i;
    if (!fields || field_count < 2u) {
        return D_TRUE;
    }
    for (i = 1u; i < field_count; ++i) {
        const dom_packed_field_desc* prev = &fields[i - 1u];
        const dom_packed_field_desc* cur = &fields[i];
        if (prev->component_id > cur->component_id) {
            return D_FALSE;
        }
        if (prev->component_id == cur->component_id &&
            prev->field_id > cur->field_id) {
            return D_FALSE;
        }
    }
    return D_TRUE;
}

int dom_packed_view_init(dom_packed_view* view,
                         u64 view_id,
                         const dom_packed_field_desc* fields,
                         u32 field_count,
                         u32 entity_count,
                         unsigned char* storage,
                         u32 storage_capacity)
{
    u32 stride;
    u32 byte_count;
    if (!view || !fields || field_count == 0u) {
        return -1;
    }
    if (!dom_packed_fields_are_sorted(fields, field_count)) {
        return -2;
    }
    if (!dom_packed_validate_fields(fields, field_count)) {
        return -3;
    }
    stride = dom_packed_view_calc_stride(fields, field_count);
    byte_count = stride * entity_count;
    if (byte_count > 0u && !storage) {
        return -4;
    }
    if (byte_count > storage_capacity) {
        return -4;
    }
    view->view_id = view_id;
    view->baseline_id = 0u;
    view->next_due_tick = DOM_PACKED_TICK_INVALID;
    view->fields = fields;
    view->field_count = field_count;
    view->entity_count = entity_count;
    view->stride = stride;
    view->byte_count = byte_count;
    view->bytes = storage;
    view->bytes_capacity = storage_capacity;
    view->next_index = 0u;
    view->view_flags = 0u;
    return 0;
}

void dom_packed_view_reset_progress(dom_packed_view* view)
{
    if (!view) {
        return;
    }
    view->next_index = 0u;
    view->view_flags &= ~DOM_PACKED_VIEW_VALID;
    view->view_flags |= DOM_PACKED_VIEW_STALE;
}

d_bool dom_packed_view_is_complete(const dom_packed_view* view)
{
    if (!view) {
        return D_FALSE;
    }
    return (view->next_index >= view->entity_count) ? D_TRUE : D_FALSE;
}

int dom_packed_view_rebuild(dom_packed_view* view,
                            const dom_packed_field_source* sources,
                            u32 source_count)
{
    if (!view) {
        return -1;
    }
    dom_packed_view_reset_progress(view);
    if (view->entity_count == 0u) {
        view->view_flags |= DOM_PACKED_VIEW_VALID;
        view->view_flags &= ~DOM_PACKED_VIEW_STALE;
        return 1;
    }
    return dom_packed_view_rebuild_step(view, sources, source_count, view->entity_count);
}

int dom_packed_view_rebuild_step(dom_packed_view* view,
                                 const dom_packed_field_source* sources,
                                 u32 source_count,
                                 u32 max_entities)
{
    u32 i;
    u32 entity;
    u32 field_index;
    u32 offset;
    if (!view || !sources || source_count != view->field_count) {
        return -1;
    }
    if (!view->bytes || view->stride == 0u) {
        return -2;
    }
    if (max_entities == 0u) {
        return -3;
    }
    for (field_index = 0u; field_index < view->field_count; ++field_index) {
        const dom_packed_field_desc* desc = &view->fields[field_index];
        const dom_packed_field_source* src = &sources[field_index];
        if (!src->data || src->stride < desc->element_size) {
            return -4;
        }
    }
    if (view->next_index >= view->entity_count) {
        view->view_flags |= DOM_PACKED_VIEW_VALID;
        view->view_flags &= ~DOM_PACKED_VIEW_STALE;
        return 1;
    }
    for (i = 0u; i < max_entities; ++i) {
        entity = view->next_index + i;
        if (entity >= view->entity_count) {
            break;
        }
        offset = entity * view->stride;
        {
            u32 field_offset = 0u;
            for (field_index = 0u; field_index < view->field_count; ++field_index) {
                const dom_packed_field_desc* desc = &view->fields[field_index];
                if (!dom_packed_pack_value(desc, &sources[field_index], entity,
                                           view->bytes + offset + field_offset)) {
                    return -5;
                }
                field_offset += desc->element_size;
            }
        }
    }
    view->next_index += i;
    if (view->next_index >= view->entity_count) {
        view->view_flags |= DOM_PACKED_VIEW_VALID;
        view->view_flags &= ~DOM_PACKED_VIEW_STALE;
        return 1;
    }
    view->view_flags |= DOM_PACKED_VIEW_STALE;
    view->view_flags &= ~DOM_PACKED_VIEW_VALID;
    return 0;
}
