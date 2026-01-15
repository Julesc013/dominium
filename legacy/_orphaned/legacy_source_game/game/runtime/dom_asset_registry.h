/*
FILE: source/dominium/game/runtime/dom_asset_registry.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / game/runtime/asset_registry
RESPONSIBILITY: Deterministic asset registry (IDs + canonical ordering).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/dominium/**`, C++98 STL.
FORBIDDEN DEPENDENCIES: OS headers; non-deterministic inputs.
*/
#ifndef DOM_ASSET_REGISTRY_H
#define DOM_ASSET_REGISTRY_H

#include "domino/core/types.h"

#ifdef __cplusplus
extern "C" {
#endif

enum {
    DOM_ASSET_OK = 0,
    DOM_ASSET_ERR = -1,
    DOM_ASSET_INVALID_ARGUMENT = -2,
    DOM_ASSET_DUPLICATE_ID = -3,
    DOM_ASSET_INVALID_DATA = -4,
    DOM_ASSET_NOT_FOUND = -5
};

typedef u64 dom_asset_id;

typedef struct dom_asset_desc {
    const char *id;
    u32 id_len;
    dom_asset_id id_hash;
    u32 kind;
    u32 unit_scale;
    u32 divisibility;
    u32 provenance_required;
    const char *display_name;
    u32 display_name_len;
    const char *issuer_id;
    u32 issuer_id_len;
    dom_asset_id issuer_id_hash;
} dom_asset_desc;

typedef struct dom_asset_info {
    dom_asset_id id_hash;
    u32 kind;
    u32 unit_scale;
    u32 divisibility;
    u32 provenance_required;
    const char *id;
    u32 id_len;
    const char *display_name;
    u32 display_name_len;
    const char *issuer_id;
    u32 issuer_id_len;
    dom_asset_id issuer_id_hash;
} dom_asset_info;

typedef void (*dom_asset_iter_fn)(const dom_asset_info *info, void *user);

typedef struct dom_asset_registry dom_asset_registry;

dom_asset_registry *dom_asset_registry_create(void);
void dom_asset_registry_destroy(dom_asset_registry *registry);

int dom_asset_registry_register(dom_asset_registry *registry,
                                const dom_asset_desc *desc);
int dom_asset_registry_get(const dom_asset_registry *registry,
                           dom_asset_id id_hash,
                           dom_asset_info *out_info);
int dom_asset_registry_iterate(const dom_asset_registry *registry,
                               dom_asset_iter_fn fn,
                               void *user);
u32 dom_asset_registry_count(const dom_asset_registry *registry);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOM_ASSET_REGISTRY_H */
