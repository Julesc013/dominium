/*
FILE: include/dominium/life/lineage.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / life
RESPONSIBILITY: Defines lineage records and deterministic storage.
ALLOWED DEPENDENCIES: `game/include/**`, `engine/include/**` public headers, and C89/C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; product-layer runtime code.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Lineage ordering must be deterministic.
*/
#ifndef DOMINIUM_LIFE_LINEAGE_H
#define DOMINIUM_LIFE_LINEAGE_H

#include "domino/core/types.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef enum life_lineage_certainty {
    LIFE_LINEAGE_EXACT = 1,
    LIFE_LINEAGE_LIKELY = 2,
    LIFE_LINEAGE_UNKNOWN = 3
} life_lineage_certainty;

typedef struct life_lineage_record {
    u64 person_id;
    u64 parent_ids[2];
    u32 parent_count;
    u32 parent_certainty[2];
    u64 lineage_provenance_ref;
} life_lineage_record;

typedef struct life_lineage_registry {
    life_lineage_record* records;
    u32 count;
    u32 capacity;
} life_lineage_registry;

void life_lineage_registry_init(life_lineage_registry* reg,
                                life_lineage_record* storage,
                                u32 capacity);
const life_lineage_record* life_lineage_find(const life_lineage_registry* reg,
                                             u64 person_id);
int life_lineage_set(life_lineage_registry* reg,
                     const life_lineage_record* record);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_LIFE_LINEAGE_H */
