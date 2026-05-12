/*
FILE: source/dominium/game/runtime/dom_system_registry.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / game/runtime/system_registry
RESPONSIBILITY: Deterministic system registry (IDs + ordering).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/dominium/**`, C++98 STL.
FORBIDDEN DEPENDENCIES: OS headers; non-deterministic inputs.
*/
#ifndef DOM_SYSTEM_REGISTRY_H
#define DOM_SYSTEM_REGISTRY_H

#include "domino/core/types.h"

#ifdef __cplusplus
extern "C" {
#endif

enum {
    DOM_SYSTEM_REGISTRY_OK = 0,
    DOM_SYSTEM_REGISTRY_ERR = -1,
    DOM_SYSTEM_REGISTRY_INVALID_ARGUMENT = -2,
    DOM_SYSTEM_REGISTRY_DUPLICATE_ID = -3,
    DOM_SYSTEM_REGISTRY_INVALID_DATA = -4,
    DOM_SYSTEM_REGISTRY_NOT_FOUND = -5
};

typedef u64 dom_system_id;

typedef struct dom_system_desc {
    const char *string_id;
    u32 string_id_len;
    dom_system_id id;
    dom_system_id parent_id;
} dom_system_desc;

typedef struct dom_system_info {
    dom_system_id id;
    dom_system_id parent_id;
    const char *string_id;
    u32 string_id_len;
} dom_system_info;

typedef void (*dom_system_iter_fn)(const dom_system_info *info, void *user);

typedef struct dom_system_registry dom_system_registry;

dom_system_registry *dom_system_registry_create(void);
void dom_system_registry_destroy(dom_system_registry *registry);

int dom_system_registry_register(dom_system_registry *registry,
                                 const dom_system_desc *desc);
int dom_system_registry_get(const dom_system_registry *registry,
                            dom_system_id id,
                            dom_system_info *out_info);
int dom_system_registry_iterate(const dom_system_registry *registry,
                                dom_system_iter_fn fn,
                                void *user);
u32 dom_system_registry_count(const dom_system_registry *registry);

int dom_system_registry_add_baseline(dom_system_registry *registry);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOM_SYSTEM_REGISTRY_H */
