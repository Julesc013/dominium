/*
FILE: include/domino/ecs/ecs_archetype_id.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino API / ecs/archetype_id
RESPONSIBILITY: Defines ECS identifier types for archetypes and components.
ALLOWED DEPENDENCIES: `include/domino/**` plus C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `source/**` private headers; keep contracts freestanding.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: Stable identifiers only; no pointer-based IDs.
VERSIONING / ABI / DATA FORMAT NOTES: Public header; see `docs/SPEC_ABI_TEMPLATES.md`.
*/
#ifndef DOMINO_ECS_ARCHETYPE_ID_H
#define DOMINO_ECS_ARCHETYPE_ID_H

#include "domino/core/types.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef u64 dom_entity_id;
typedef u64 dom_component_id;
typedef u64 dom_field_id;

typedef struct dom_archetype_id {
    u64 value;
} dom_archetype_id;

dom_archetype_id dom_archetype_id_make(u64 value);
d_bool dom_archetype_id_equal(dom_archetype_id a, dom_archetype_id b);
d_bool dom_archetype_id_is_valid(dom_archetype_id id);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINO_ECS_ARCHETYPE_ID_H */
