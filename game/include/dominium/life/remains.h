/*
FILE: include/dominium/life/remains.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / life
RESPONSIBILITY: Defines remains records, aggregates, and deterministic registries.
ALLOWED DEPENDENCIES: `game/include/**`, `engine/include/**` public headers, and C89/C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; product-layer runtime code.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Ordering and IDs are deterministic.
*/
#ifndef DOMINIUM_LIFE_REMAINS_H
#define DOMINIUM_LIFE_REMAINS_H

#include "domino/core/dom_time_core.h"
#include "domino/core/dom_ledger.h"
#include "domino/core/types.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef enum life_remains_state {
    LIFE_REMAINS_FRESH = 1,
    LIFE_REMAINS_DECAYED = 2,
    LIFE_REMAINS_SKELETAL = 3,
    LIFE_REMAINS_UNKNOWN = 4,
    LIFE_REMAINS_COLLAPSED = 5
} life_remains_state;

typedef struct life_remains {
    u64 remains_id;
    u64 person_id;
    u64 body_id;
    u64 location_ref;
    dom_act_time_t created_act;
    u32 state;
    u64 ownership_rights_ref;
    dom_act_time_t next_due_tick;
    u64 provenance_ref;
    dom_account_id_t inventory_account_id;
    u64 active_claim_id;
} life_remains;

typedef struct life_remains_registry {
    life_remains* remains;
    u32 count;
    u32 capacity;
    u64 next_id;
    void* notice_user;
    void (*notice_cb)(void* user, const life_remains* remains);
} life_remains_registry;

typedef struct life_remains_epistemic_set {
    const u64* known_remains_ids;
    u32 count;
} life_remains_epistemic_set;

typedef struct life_remains_aggregate {
    u64 aggregate_id;
    u64 location_ref;
    u64 ownership_rights_ref;
    u64 provenance_hash;
    u64 count;
    u32 state;
} life_remains_aggregate;

typedef struct life_remains_aggregate_registry {
    life_remains_aggregate* aggregates;
    u32 count;
    u32 capacity;
    u64 next_id;
} life_remains_aggregate_registry;

void life_remains_registry_init(life_remains_registry* reg,
                                life_remains* storage,
                                u32 capacity,
                                u64 start_id);
void life_remains_registry_set_notice(life_remains_registry* reg,
                                      void (*notice_cb)(void*, const life_remains*),
                                      void* notice_user);
life_remains* life_remains_find(life_remains_registry* reg, u64 remains_id);
int life_remains_create(life_remains_registry* reg,
                        u64 person_id,
                        u64 body_id,
                        u64 location_ref,
                        dom_act_time_t created_act,
                        u64 ownership_rights_ref,
                        u64 provenance_ref,
                        dom_account_id_t inventory_account_id,
                        u64* out_remains_id);
int life_remains_set_next_due(life_remains_registry* reg,
                              u64 remains_id,
                              dom_act_time_t next_due_tick);

void life_remains_aggregate_registry_init(life_remains_aggregate_registry* reg,
                                          life_remains_aggregate* storage,
                                          u32 capacity,
                                          u64 start_id);
life_remains_aggregate* life_remains_aggregate_find(life_remains_aggregate_registry* reg,
                                                    u64 aggregate_id);
int life_remains_aggregate_add(life_remains_aggregate_registry* reg,
                               u64 location_ref,
                               u64 ownership_rights_ref,
                               u32 state,
                               u64 provenance_hash,
                               u64 count,
                               u64* out_id);
int life_remains_collapse(life_remains_registry* reg,
                          life_remains_aggregate_registry* aggregates,
                          u64 remains_id,
                          u64* out_aggregate_id);
int life_remains_refine(life_remains_aggregate_registry* aggregates,
                        life_remains_registry* reg,
                        u64 aggregate_id,
                        u32 count,
                        dom_act_time_t created_act);

int life_remains_epistemic_knows(const life_remains_epistemic_set* set,
                                 u64 remains_id);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_LIFE_REMAINS_H */
