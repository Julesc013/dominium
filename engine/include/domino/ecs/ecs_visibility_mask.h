/*
FILE: include/domino/ecs/ecs_visibility_mask.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino API / ecs/visibility_mask
RESPONSIBILITY: Defines deterministic visibility/interest bitmask.
ALLOWED DEPENDENCIES: `include/domino/**` plus C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `source/**` private headers; keep contracts freestanding.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: Stable bit ordering only.
VERSIONING / ABI / DATA FORMAT NOTES: Public header; see `docs/SPEC_ABI_TEMPLATES.md`.
*/
#ifndef DOMINO_ECS_VISIBILITY_MASK_H
#define DOMINO_ECS_VISIBILITY_MASK_H

#include "domino/core/types.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct dom_visibility_mask {
    u32 entity_count;
    u32 word_count;
    u32 next_index;
    u32* words;
} dom_visibility_mask;

int dom_visibility_mask_init(dom_visibility_mask* mask,
                             u32 entity_count,
                             u32* storage_words,
                             u32 storage_count);
void dom_visibility_mask_clear(dom_visibility_mask* mask);
void dom_visibility_mask_reset_progress(dom_visibility_mask* mask);
d_bool dom_visibility_mask_get(const dom_visibility_mask* mask, u32 index);
void dom_visibility_mask_set(dom_visibility_mask* mask, u32 index, d_bool visible);
int dom_visibility_mask_update_range(dom_visibility_mask* mask,
                                     u32 start_index,
                                     u32 count,
                                     d_bool visible);
int dom_visibility_mask_copy_range(dom_visibility_mask* dst,
                                   const dom_visibility_mask* src,
                                   u32 start_index,
                                   u32 count);
int dom_visibility_mask_rebuild_step(dom_visibility_mask* dst,
                                     const dom_visibility_mask* src,
                                     u32 max_entities);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINO_ECS_VISIBILITY_MASK_H */
