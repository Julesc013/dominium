/*
FILE: include/domino/ecs/ecs_storage_iface.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino API / ecs/storage_iface
RESPONSIBILITY: Defines the ECS storage backend interface (logical vs physical separation).
ALLOWED DEPENDENCIES: `include/domino/**` plus C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `source/**` private headers; keep contracts freestanding.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: Stable iteration and commit ordering only.
VERSIONING / ABI / DATA FORMAT NOTES: Public header; see `docs/specs/SPEC_ABI_TEMPLATES.md`.
*/
#ifndef DOMINO_ECS_STORAGE_IFACE_H
#define DOMINO_ECS_STORAGE_IFACE_H

#include "domino/ecs/ecs_component_view.h"
#include "domino/ecs/ecs_entity_range.h"
#include "domino/execution/task_node.h"
#include "domino/execution/access_set.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct dom_ecs_write_op {
    dom_commit_key    commit_key;
    dom_archetype_id  archetype_id;
    dom_entity_range  range;
    dom_component_id  component_id;
    dom_field_id      field_id;
    u32               element_type;
    u32               element_size;
    u32               access_mode;
    u32               reduction_op;
    const void*       data;
    u32               stride;
} dom_ecs_write_op;

typedef struct dom_ecs_write_buffer {
    const dom_ecs_write_op* ops;
    u32                     count;
} dom_ecs_write_buffer;

typedef struct dom_ecs_commit_context {
    u64    epoch_id;
    u64    graph_id;
    d_bool allow_rollback;
    int    status;
} dom_ecs_commit_context;

#ifdef __cplusplus
} /* extern "C" */
#endif

#ifdef __cplusplus

class IEcsStorageBackend {
public:
    virtual ~IEcsStorageBackend();
    virtual dom_archetype_id get_archetype(dom_entity_id entity) const = 0;
    virtual dom_entity_range query_archetype(dom_archetype_id archetype) const = 0;

    virtual dom_component_view get_view(dom_archetype_id archetype,
                                        dom_component_id component,
                                        dom_field_id field) = 0;

    virtual void apply_writes(const dom_ecs_write_buffer& writes,
                              dom_ecs_commit_context& ctx) = 0;
};

#endif /* __cplusplus */

#endif /* DOMINO_ECS_STORAGE_IFACE_H */
