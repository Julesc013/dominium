/*
FILE: include/dominium/rules/infrastructure/store_model.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / infrastructure
RESPONSIBILITY: Defines deterministic asset stores for production/logistics.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C89/C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Store ordering and asset updates are deterministic.
*/
#ifndef DOMINIUM_RULES_INFRA_STORE_MODEL_H
#define DOMINIUM_RULES_INFRA_STORE_MODEL_H

#include "domino/core/types.h"

#ifdef __cplusplus
extern "C" {
#endif

#define INFRA_STORE_MAX_ASSETS 16u

typedef struct infra_store_asset {
    u64 asset_id;
    u32 quantity;
} infra_store_asset;

typedef struct infra_store {
    u64 store_id;
    infra_store_asset assets[INFRA_STORE_MAX_ASSETS];
    u32 asset_count;
} infra_store;

typedef struct infra_store_registry {
    infra_store* stores;
    u32 count;
    u32 capacity;
} infra_store_registry;

void infra_store_registry_init(infra_store_registry* reg,
                               infra_store* storage,
                               u32 capacity);
int infra_store_register(infra_store_registry* reg,
                         u64 store_id);
infra_store* infra_store_find(infra_store_registry* reg, u64 store_id);
const infra_store* infra_store_find_const(const infra_store_registry* reg, u64 store_id);
int infra_store_get_qty(const infra_store_registry* reg,
                        u64 store_id,
                        u64 asset_id,
                        u32* out_qty);
int infra_store_add(infra_store_registry* reg,
                    u64 store_id,
                    u64 asset_id,
                    u32 qty);
int infra_store_consume(infra_store_registry* reg,
                        u64 store_id,
                        u64 asset_id,
                        u32 qty);
int infra_store_take(infra_store_registry* reg,
                     u64 store_id,
                     u64 asset_id,
                     u32 qty,
                     u32* out_taken);
int infra_store_clear(infra_store_registry* reg, u64 store_id);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_RULES_INFRA_STORE_MODEL_H */
