/*
FILE: include/domino/ecs/ecs_component_view.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino API / ecs/component_view
RESPONSIBILITY: Defines ComponentView for logical field access.
ALLOWED DEPENDENCIES: `include/domino/**` plus C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `source/**` private headers; keep contracts freestanding.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: Stable iteration order only.
VERSIONING / ABI / DATA FORMAT NOTES: Public header; see `docs/specs/SPEC_ABI_TEMPLATES.md`.
*/
#ifndef DOMINO_ECS_COMPONENT_VIEW_H
#define DOMINO_ECS_COMPONENT_VIEW_H

#include "domino/ecs/ecs_archetype_id.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef enum dom_ecs_access_mode {
    DOM_ECS_ACCESS_READ = 1u,
    DOM_ECS_ACCESS_WRITE = 2u,
    DOM_ECS_ACCESS_REDUCE = 4u,
    DOM_ECS_ACCESS_READWRITE = 3u
} dom_ecs_access_mode;

typedef enum dom_ecs_element_type {
    DOM_ECS_ELEM_U8 = 1u,
    DOM_ECS_ELEM_I8 = 2u,
    DOM_ECS_ELEM_U16 = 3u,
    DOM_ECS_ELEM_I16 = 4u,
    DOM_ECS_ELEM_U32 = 5u,
    DOM_ECS_ELEM_I32 = 6u,
    DOM_ECS_ELEM_U64 = 7u,
    DOM_ECS_ELEM_I64 = 8u,
    DOM_ECS_ELEM_FIXED_Q16 = 9u,
    DOM_ECS_ELEM_FIXED_Q32 = 10u
} dom_ecs_element_type;

enum {
    DOM_ECS_VIEW_VALID = 1u << 0,
    DOM_ECS_VIEW_DENIED = 1u << 1
};

typedef struct dom_component_view {
    dom_component_id component_id;
    dom_field_id     field_id;
    u32              element_type;
    u32              element_size;
    u32              stride;
    u32              count;
    u32              access_mode;
    u32              view_flags;
    u32              reserved;
    u64              backend_token;
} dom_component_view;

dom_component_view dom_component_view_invalid(void);
d_bool dom_component_view_is_valid(const dom_component_view* view);
d_bool dom_component_view_has_index(const dom_component_view* view, u32 index);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINO_ECS_COMPONENT_VIEW_H */
