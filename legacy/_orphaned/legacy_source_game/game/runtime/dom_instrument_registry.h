/*
FILE: source/dominium/game/runtime/dom_instrument_registry.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / game/runtime/instrument_registry
RESPONSIBILITY: Deterministic instrument registry (contract bindings).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/dominium/**`, C++98 STL.
FORBIDDEN DEPENDENCIES: OS headers; non-deterministic inputs.
*/
#ifndef DOM_INSTRUMENT_REGISTRY_H
#define DOM_INSTRUMENT_REGISTRY_H

#include "domino/core/types.h"

#ifdef __cplusplus
extern "C" {
#endif

enum {
    DOM_INSTRUMENT_OK = 0,
    DOM_INSTRUMENT_ERR = -1,
    DOM_INSTRUMENT_INVALID_ARGUMENT = -2,
    DOM_INSTRUMENT_DUPLICATE_ID = -3,
    DOM_INSTRUMENT_INVALID_DATA = -4,
    DOM_INSTRUMENT_NOT_FOUND = -5
};

typedef u64 dom_instrument_id;

typedef struct dom_instrument_desc {
    const char *id;
    u32 id_len;
    dom_instrument_id id_hash;
    u32 kind;
    const char *contract_id;
    u32 contract_id_len;
    u64 contract_id_hash;
    const u64 *asset_ids;
    u32 asset_id_count;
} dom_instrument_desc;

typedef struct dom_instrument_info {
    dom_instrument_id id_hash;
    u32 kind;
    u64 contract_id_hash;
    const char *id;
    u32 id_len;
    const char *contract_id;
    u32 contract_id_len;
    const u64 *asset_ids;
    u32 asset_id_count;
} dom_instrument_info;

typedef void (*dom_instrument_iter_fn)(const dom_instrument_info *info, void *user);

typedef struct dom_instrument_registry dom_instrument_registry;

dom_instrument_registry *dom_instrument_registry_create(void);
void dom_instrument_registry_destroy(dom_instrument_registry *registry);

int dom_instrument_registry_register(dom_instrument_registry *registry,
                                     const dom_instrument_desc *desc);
int dom_instrument_registry_get(const dom_instrument_registry *registry,
                                dom_instrument_id id_hash,
                                dom_instrument_info *out_info);
int dom_instrument_registry_iterate(const dom_instrument_registry *registry,
                                    dom_instrument_iter_fn fn,
                                    void *user);
u32 dom_instrument_registry_count(const dom_instrument_registry *registry);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOM_INSTRUMENT_REGISTRY_H */
