/*
FILE: include/dominium/life/rights_post_death.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / life
RESPONSIBILITY: Defines post-death rights records for remains and salvage.
ALLOWED DEPENDENCIES: `game/include/**`, `engine/include/**` public headers, and C89/C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; product-layer runtime code.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Ordering and IDs are deterministic.
*/
#ifndef DOMINIUM_LIFE_RIGHTS_POST_DEATH_H
#define DOMINIUM_LIFE_RIGHTS_POST_DEATH_H

#include "domino/core/types.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct life_post_death_rights {
    u64 rights_id;
    u64 estate_id;
    u64 jurisdiction_id;
    u8 has_contract;
    u8 allow_finder;
    u8 jurisdiction_allows;
    u8 estate_locked;
} life_post_death_rights;

typedef struct life_post_death_rights_registry {
    life_post_death_rights* rights;
    u32 count;
    u32 capacity;
    u64 next_id;
} life_post_death_rights_registry;

void life_post_death_rights_registry_init(life_post_death_rights_registry* reg,
                                          life_post_death_rights* storage,
                                          u32 capacity,
                                          u64 start_id);
life_post_death_rights* life_post_death_rights_find(life_post_death_rights_registry* reg,
                                                    u64 rights_id);
int life_post_death_rights_create(life_post_death_rights_registry* reg,
                                  u64 estate_id,
                                  u64 jurisdiction_id,
                                  u8 has_contract,
                                  u8 allow_finder,
                                  u8 jurisdiction_allows,
                                  u8 estate_locked,
                                  u64* out_rights_id);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_LIFE_RIGHTS_POST_DEATH_H */
