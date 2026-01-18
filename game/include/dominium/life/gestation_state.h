/*
FILE: include/dominium/life/gestation_state.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / life
RESPONSIBILITY: Defines gestation state records and registries.
ALLOWED DEPENDENCIES: `game/include/**`, `engine/include/**` public headers, and C89/C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; product-layer runtime code.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Gestation ordering is deterministic.
*/
#ifndef DOMINIUM_LIFE_GESTATION_STATE_H
#define DOMINIUM_LIFE_GESTATION_STATE_H

#include "domino/core/dom_time_core.h"
#include "domino/core/types.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef enum life_gestation_status {
    LIFE_GESTATION_ACTIVE = 1,
    LIFE_GESTATION_FAILED = 2,
    LIFE_GESTATION_COMPLETED = 3
} life_gestation_status;

typedef struct life_gestation_state {
    u64 gestation_id;
    u64 parent_ids[2];
    u32 parent_count;
    u32 parent_certainty[2];
    dom_act_time_t start_act;
    dom_act_time_t expected_end_act;
    u64 resource_contract_refs[2];
    u32 resource_contract_count;
    u32 status;
    u64 cohort_id;
    u64 location_ref;
    u64 provenance_ref;
    u8 micro_active;
} life_gestation_state;

typedef struct life_gestation_registry {
    life_gestation_state* states;
    u32 count;
    u32 capacity;
    u64 next_id;
} life_gestation_registry;

void life_gestation_registry_init(life_gestation_registry* reg,
                                  life_gestation_state* storage,
                                  u32 capacity,
                                  u64 start_id);
life_gestation_state* life_gestation_find_active(life_gestation_registry* reg,
                                                 const u64* parent_ids,
                                                 u32 parent_count);
int life_gestation_append(life_gestation_registry* reg,
                          const life_gestation_state* state,
                          u64* out_id);
life_gestation_state* life_gestation_find_by_id(life_gestation_registry* reg,
                                                u64 gestation_id);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_LIFE_GESTATION_STATE_H */
