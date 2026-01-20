/*
FILE: engine/modules/ecs/delta_codec.cpp
MODULE: Domino
LAYER / SUBSYSTEM: Domino / ecs
RESPONSIBILITY: Deterministic delta codec for packed views.
ALLOWED DEPENDENCIES: engine/include public headers and C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers outside ecs.
DETERMINISM: Stable ordering and explicit byte layout only.
*/
#include "domino/ecs/ecs_delta_codec.h"

#include <string.h>

static void dom_delta_write_u32(unsigned char* dst, u32 value)
{
    dst[0] = (unsigned char)(value & 0xFFu);
    dst[1] = (unsigned char)((value >> 8u) & 0xFFu);
    dst[2] = (unsigned char)((value >> 16u) & 0xFFu);
    dst[3] = (unsigned char)((value >> 24u) & 0xFFu);
}

static void dom_delta_write_u64(unsigned char* dst, u64 value)
{
    u32 i;
    for (i = 0u; i < 8u; ++i) {
        dst[i] = (unsigned char)((value >> (i * 8u)) & 0xFFu);
    }
}

int dom_delta_build(const dom_packed_view* baseline,
                    const dom_packed_view* current,
                    unsigned char* out_bytes,
                    u32 out_capacity,
                    dom_packed_delta_info* out_info)
{
    u32 i;
    u32 stride;
    u32 entity_count;
    u32 bitmask_bytes;
    u32 header_bytes = 8u + 8u + 4u + 4u;
    u32 changed_count = 0u;
    u32 payload_bytes;
    u32 total_bytes;
    unsigned char* bitmask;
    unsigned char* payload;

    if (!baseline || !current || !out_bytes || !out_info) {
        return -1;
    }
    if (baseline->view_id != current->view_id) {
        return -2;
    }
    if (baseline->entity_count != current->entity_count ||
        baseline->stride != current->stride) {
        return -3;
    }
    if (!baseline->bytes || !current->bytes) {
        return -4;
    }
    stride = current->stride;
    entity_count = current->entity_count;
    if (stride == 0u && entity_count > 0u) {
        return -5;
    }
    bitmask_bytes = (entity_count + 7u) / 8u;

    for (i = 0u; i < entity_count; ++i) {
        const unsigned char* base_ptr = baseline->bytes + (size_t)i * stride;
        const unsigned char* cur_ptr = current->bytes + (size_t)i * stride;
        if (memcmp(base_ptr, cur_ptr, stride) != 0) {
            changed_count += 1u;
        }
    }

    payload_bytes = changed_count * stride;
    total_bytes = header_bytes + bitmask_bytes + payload_bytes;
    if (total_bytes > out_capacity) {
        return -6;
    }

    dom_delta_write_u64(out_bytes, current->view_id);
    dom_delta_write_u64(out_bytes + 8u, baseline->baseline_id);
    dom_delta_write_u32(out_bytes + 16u, entity_count);
    dom_delta_write_u32(out_bytes + 20u, stride);

    bitmask = out_bytes + header_bytes;
    payload = bitmask + bitmask_bytes;
    memset(bitmask, 0, bitmask_bytes);

    for (i = 0u; i < entity_count; ++i) {
        const unsigned char* base_ptr = baseline->bytes + (size_t)i * stride;
        const unsigned char* cur_ptr = current->bytes + (size_t)i * stride;
        if (memcmp(base_ptr, cur_ptr, stride) != 0) {
            u32 byte_index = i / 8u;
            u32 bit_index = i % 8u;
            bitmask[byte_index] |= (unsigned char)(1u << bit_index);
            memcpy(payload, cur_ptr, stride);
            payload += stride;
        }
    }

    out_info->view_id = current->view_id;
    out_info->baseline_id = baseline->baseline_id;
    out_info->entity_count = entity_count;
    out_info->stride = stride;
    out_info->changed_count = changed_count;
    out_info->bitmask_bytes = bitmask_bytes;
    out_info->payload_bytes = payload_bytes;
    out_info->total_bytes = total_bytes;
    return 0;
}
