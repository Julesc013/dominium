/*
FILE: source/dominium/game/runtime/dom_construction_registry.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / game/runtime/construction_registry
RESPONSIBILITY: Deterministic construction registry (instances + occupancy).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/dominium/**`, C++98 STL.
FORBIDDEN DEPENDENCIES: OS headers; floating-point math.
*/
#ifndef DOM_CONSTRUCTION_REGISTRY_H
#define DOM_CONSTRUCTION_REGISTRY_H

#include "domino/core/fixed.h"
#include "domino/core/types.h"
#include "runtime/dom_surface_chunks.h"

#ifdef __cplusplus
extern "C" {
#endif

enum {
    DOM_CONSTRUCTION_OK = 0,
    DOM_CONSTRUCTION_ERR = -1,
    DOM_CONSTRUCTION_INVALID_ARGUMENT = -2,
    DOM_CONSTRUCTION_DUPLICATE_ID = -3,
    DOM_CONSTRUCTION_NOT_FOUND = -4,
    DOM_CONSTRUCTION_OVERLAP = -5
};

enum {
    DOM_CONSTRUCTION_TYPE_HABITAT = 1u,
    DOM_CONSTRUCTION_TYPE_STORAGE = 2u,
    DOM_CONSTRUCTION_TYPE_GENERIC_PLATFORM = 3u
};

typedef u64 dom_construction_instance_id;

typedef struct dom_construction_instance {
    dom_construction_instance_id instance_id;
    u32 type_id;
    dom_body_id body_id;
    dom_surface_chunk_key chunk_key;
    q48_16 local_pos_m[3]; /* east, north, up */
    u32 orientation;
    i32 cell_x;
    i32 cell_y;
} dom_construction_instance;

typedef struct dom_construction_registry dom_construction_registry;

dom_construction_registry *dom_construction_registry_create(void);
void dom_construction_registry_destroy(dom_construction_registry *registry);
int dom_construction_registry_init(dom_construction_registry *registry);

int dom_construction_register_instance(dom_construction_registry *registry,
                                       const dom_construction_instance *inst,
                                       dom_construction_instance_id *out_id);
int dom_construction_remove_instance(dom_construction_registry *registry,
                                     dom_construction_instance_id id);
int dom_construction_get(const dom_construction_registry *registry,
                         dom_construction_instance_id id,
                         dom_construction_instance *out_instance);
int dom_construction_list(const dom_construction_registry *registry,
                          dom_construction_instance *out_list,
                          u32 max_entries,
                          u32 *out_count);
u32 dom_construction_count(const dom_construction_registry *registry);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOM_CONSTRUCTION_REGISTRY_H */
