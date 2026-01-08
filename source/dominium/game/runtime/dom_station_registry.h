/*
FILE: source/dominium/game/runtime/dom_station_registry.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / game/runtime/station_registry
RESPONSIBILITY: Deterministic station registry + inventory storage.
ALLOWED DEPENDENCIES: `include/domino/**`, `source/dominium/**`, C++98 STL.
FORBIDDEN DEPENDENCIES: OS headers; non-deterministic inputs.
*/
#ifndef DOM_STATION_REGISTRY_H
#define DOM_STATION_REGISTRY_H

#include "domino/core/types.h"
#include "runtime/dom_body_registry.h"
#include "runtime/dom_frames.h"

#ifdef __cplusplus
extern "C" {
#endif

enum {
    DOM_STATION_REGISTRY_OK = 0,
    DOM_STATION_REGISTRY_ERR = -1,
    DOM_STATION_REGISTRY_INVALID_ARGUMENT = -2,
    DOM_STATION_REGISTRY_DUPLICATE_ID = -3,
    DOM_STATION_REGISTRY_NOT_FOUND = -4,
    DOM_STATION_REGISTRY_INVALID_DATA = -5,
    DOM_STATION_REGISTRY_INSUFFICIENT = -6,
    DOM_STATION_REGISTRY_OVERFLOW = -7
};

typedef u64 dom_station_id;
typedef u64 dom_resource_id;

typedef struct dom_inventory_entry {
    dom_resource_id resource_id;
    i64 quantity;
} dom_inventory_entry;

typedef struct dom_station_desc {
    dom_station_id station_id;
    dom_body_id body_id;
    dom_frame_id frame_id;
} dom_station_desc;

typedef struct dom_station_info {
    dom_station_id station_id;
    dom_body_id body_id;
    dom_frame_id frame_id;
} dom_station_info;

typedef void (*dom_station_iter_fn)(const dom_station_info *info, void *user);

typedef struct dom_station_registry dom_station_registry;

dom_station_registry *dom_station_registry_create(void);
void dom_station_registry_destroy(dom_station_registry *registry);
int dom_station_registry_init(dom_station_registry *registry);

int dom_station_register(dom_station_registry *registry,
                         const dom_station_desc *desc);
int dom_station_get(const dom_station_registry *registry,
                    dom_station_id station_id,
                    dom_station_info *out_info);
int dom_station_iterate(const dom_station_registry *registry,
                        dom_station_iter_fn fn,
                        void *user);
u32 dom_station_count(const dom_station_registry *registry);

int dom_station_inventory_get(const dom_station_registry *registry,
                              dom_station_id station_id,
                              dom_resource_id resource_id,
                              i64 *out_quantity);
int dom_station_inventory_add(dom_station_registry *registry,
                              dom_station_id station_id,
                              dom_resource_id resource_id,
                              i64 amount);
int dom_station_inventory_remove(dom_station_registry *registry,
                                 dom_station_id station_id,
                                 dom_resource_id resource_id,
                                 i64 amount);
int dom_station_inventory_list(const dom_station_registry *registry,
                               dom_station_id station_id,
                               dom_inventory_entry *out_entries,
                               u32 max_entries,
                               u32 *out_count);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOM_STATION_REGISTRY_H */
