/*
FILE: include/domino/registry.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino API / registry
RESPONSIBILITY: Defines the public contract for deterministic registry loading.
ALLOWED DEPENDENCIES: `include/domino/**` plus C89/C++98 standard headers only.
FORBIDDEN DEPENDENCIES: product-layer headers; keep contracts freestanding.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Registry ordering is deterministic (sorted by key).
*/
#ifndef DOMINO_REGISTRY_H
#define DOMINO_REGISTRY_H

#include "domino/core/types.h"

#ifdef __cplusplus
extern "C" {
#endif

#define DOM_REGISTRY_INVALID_ID 0u

typedef enum dom_registry_result {
    DOM_REGISTRY_OK = 0,
    DOM_REGISTRY_ERR_NULL = 1,
    DOM_REGISTRY_ERR_IO = 2,
    DOM_REGISTRY_ERR_FORMAT = 3,
    DOM_REGISTRY_ERR_DUPLICATE = 4,
    DOM_REGISTRY_ERR_OOM = 5,
    DOM_REGISTRY_ERR_EMPTY = 6
} dom_registry_result;

typedef struct dom_registry_entry {
    u32 id;
    const char* key;
} dom_registry_entry;

typedef struct dom_registry {
    dom_registry_entry* entries;
    u32 count;
    u32 capacity;
    u32 hash;
} dom_registry;

dom_registry_result dom_registry_load_file(const char* path, dom_registry* out);
void dom_registry_free(dom_registry* reg);

const dom_registry_entry* dom_registry_find(const dom_registry* reg, const char* key);
u32 dom_registry_id_from_key(const dom_registry* reg, const char* key);
const char* dom_registry_key_from_id(const dom_registry* reg, u32 id);
u32 dom_registry_hash(const dom_registry* reg);
u32 dom_registry_count(const dom_registry* reg);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINO_REGISTRY_H */
