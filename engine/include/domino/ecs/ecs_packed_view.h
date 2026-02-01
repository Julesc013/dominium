/*
FILE: include/domino/ecs/ecs_packed_view.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino API / ecs/packed_view
RESPONSIBILITY: Defines deterministic packed view representation.
ALLOWED DEPENDENCIES: `include/domino/**` plus C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `source/**` private headers; keep contracts freestanding.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: Explicit byte order and stable field ordering.
VERSIONING / ABI / DATA FORMAT NOTES: Public header; see `docs/specs/SPEC_ABI_TEMPLATES.md`.
*/
#ifndef DOMINO_ECS_PACKED_VIEW_H
#define DOMINO_ECS_PACKED_VIEW_H

#include "domino/ecs/ecs_component_view.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef enum dom_packed_field_flags {
    DOM_PACK_FIELD_NONE = 0u,
    DOM_PACK_FIELD_QUANTIZE = 1u << 0,
    DOM_PACK_FIELD_PRESENTATION = 1u << 1
} dom_packed_field_flags;

typedef struct dom_packed_field_desc {
    dom_component_id component_id;
    dom_field_id     field_id;
    u32              element_type;
    u32              element_size;
    u32              flags;
    u32              quant_bits;
} dom_packed_field_desc;

typedef struct dom_packed_field_source {
    const void* data;
    u32         stride;
} dom_packed_field_source;

enum {
    DOM_PACKED_VIEW_VALID = 1u << 0,
    DOM_PACKED_VIEW_STALE = 1u << 1
};

/* Invalid tick sentinel for scheduling packed view refresh. */
#define DOM_PACKED_TICK_INVALID ((u64)0xFFFFFFFFFFFFFFFFull)

typedef struct dom_packed_view {
    u64                          view_id;
    u64                          baseline_id;
    u64                          next_due_tick;
    const dom_packed_field_desc* fields;
    u32                          field_count;
    u32                          entity_count;
    u32                          stride;
    u32                          byte_count;
    unsigned char*               bytes;
    u32                          bytes_capacity;
    u32                          next_index;
    u32                          view_flags;
} dom_packed_view;

u32 dom_packed_view_calc_stride(const dom_packed_field_desc* fields, u32 field_count);
d_bool dom_packed_fields_are_sorted(const dom_packed_field_desc* fields, u32 field_count);
int dom_packed_view_init(dom_packed_view* view,
                         u64 view_id,
                         const dom_packed_field_desc* fields,
                         u32 field_count,
                         u32 entity_count,
                         unsigned char* storage,
                         u32 storage_capacity);
void dom_packed_view_reset_progress(dom_packed_view* view);
d_bool dom_packed_view_is_complete(const dom_packed_view* view);
int dom_packed_view_rebuild(dom_packed_view* view,
                            const dom_packed_field_source* sources,
                            u32 source_count);
int dom_packed_view_rebuild_step(dom_packed_view* view,
                                 const dom_packed_field_source* sources,
                                 u32 source_count,
                                 u32 max_entities);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINO_ECS_PACKED_VIEW_H */
