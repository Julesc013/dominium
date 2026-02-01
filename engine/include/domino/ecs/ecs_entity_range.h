/*
FILE: include/domino/ecs/ecs_entity_range.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino API / ecs/entity_range
RESPONSIBILITY: Defines deterministic entity range representation.
ALLOWED DEPENDENCIES: `include/domino/**` plus C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `source/**` private headers; keep contracts freestanding.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: Stable range ordering only.
VERSIONING / ABI / DATA FORMAT NOTES: Public header; see `docs/specs/SPEC_ABI_TEMPLATES.md`.
*/
#ifndef DOMINO_ECS_ENTITY_RANGE_H
#define DOMINO_ECS_ENTITY_RANGE_H

#include "domino/ecs/ecs_archetype_id.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct dom_entity_range {
    dom_archetype_id archetype_id;
    u32              begin_index;
    u32              end_index;
} dom_entity_range;

u32    dom_entity_range_count(const dom_entity_range* range);
d_bool dom_entity_range_is_valid(const dom_entity_range* range);
d_bool dom_entity_range_contains(const dom_entity_range* range, u32 index);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINO_ECS_ENTITY_RANGE_H */
