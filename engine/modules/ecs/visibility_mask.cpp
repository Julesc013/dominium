/*
FILE: engine/modules/ecs/visibility_mask.cpp
MODULE: Domino
LAYER / SUBSYSTEM: Domino / ecs
RESPONSIBILITY: Deterministic visibility/interest bitmask helpers.
ALLOWED DEPENDENCIES: engine/include public headers and C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers outside ecs.
DETERMINISM: Stable bit ordering only.
*/
#include "domino/ecs/ecs_visibility_mask.h"

#include <string.h>

static u32 dom_visibility_required_words(u32 entity_count)
{
    return (entity_count + 31u) / 32u;
}

int dom_visibility_mask_init(dom_visibility_mask* mask,
                             u32 entity_count,
                             u32* storage_words,
                             u32 storage_count)
{
    u32 required;
    if (!mask || !storage_words) {
        return -1;
    }
    required = dom_visibility_required_words(entity_count);
    if (storage_count < required) {
        return -2;
    }
    mask->entity_count = entity_count;
    mask->word_count = required;
    mask->next_index = 0u;
    mask->words = storage_words;
    memset(mask->words, 0, sizeof(u32) * mask->word_count);
    return 0;
}

void dom_visibility_mask_clear(dom_visibility_mask* mask)
{
    if (!mask || !mask->words) {
        return;
    }
    memset(mask->words, 0, sizeof(u32) * mask->word_count);
    mask->next_index = 0u;
}

void dom_visibility_mask_reset_progress(dom_visibility_mask* mask)
{
    if (!mask) {
        return;
    }
    mask->next_index = 0u;
}

d_bool dom_visibility_mask_get(const dom_visibility_mask* mask, u32 index)
{
    u32 word_index;
    u32 bit_index;
    if (!mask || !mask->words || index >= mask->entity_count) {
        return D_FALSE;
    }
    word_index = index / 32u;
    bit_index = index % 32u;
    return (mask->words[word_index] & (1u << bit_index)) ? D_TRUE : D_FALSE;
}

void dom_visibility_mask_set(dom_visibility_mask* mask, u32 index, d_bool visible)
{
    u32 word_index;
    u32 bit_index;
    if (!mask || !mask->words || index >= mask->entity_count) {
        return;
    }
    word_index = index / 32u;
    bit_index = index % 32u;
    if (visible) {
        mask->words[word_index] |= (1u << bit_index);
    } else {
        mask->words[word_index] &= ~(1u << bit_index);
    }
}

int dom_visibility_mask_update_range(dom_visibility_mask* mask,
                                     u32 start_index,
                                     u32 count,
                                     d_bool visible)
{
    u32 i;
    if (!mask || !mask->words) {
        return -1;
    }
    if (start_index + count > mask->entity_count) {
        return -2;
    }
    for (i = 0u; i < count; ++i) {
        dom_visibility_mask_set(mask, start_index + i, visible);
    }
    return 0;
}

int dom_visibility_mask_copy_range(dom_visibility_mask* dst,
                                   const dom_visibility_mask* src,
                                   u32 start_index,
                                   u32 count)
{
    u32 i;
    if (!dst || !src || !dst->words || !src->words) {
        return -1;
    }
    if (dst->entity_count != src->entity_count) {
        return -2;
    }
    if (start_index + count > dst->entity_count) {
        return -3;
    }
    for (i = 0u; i < count; ++i) {
        d_bool visible = dom_visibility_mask_get(src, start_index + i);
        dom_visibility_mask_set(dst, start_index + i, visible);
    }
    return 0;
}

int dom_visibility_mask_rebuild_step(dom_visibility_mask* dst,
                                     const dom_visibility_mask* src,
                                     u32 max_entities)
{
    u32 remaining;
    u32 count;
    if (!dst || !src) {
        return -1;
    }
    if (dst->entity_count != src->entity_count) {
        return -2;
    }
    if (max_entities == 0u) {
        return -3;
    }
    if (dst->next_index >= dst->entity_count) {
        return 1;
    }
    remaining = dst->entity_count - dst->next_index;
    count = (remaining < max_entities) ? remaining : max_entities;
    if (dom_visibility_mask_copy_range(dst, src, dst->next_index, count) != 0) {
        return -4;
    }
    dst->next_index += count;
    if (dst->next_index >= dst->entity_count) {
        return 1;
    }
    return 0;
}
