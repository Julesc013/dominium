/*
FILE: source/dominium/game/runtime/dom_belief_store.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / game/runtime/belief_store
RESPONSIBILITY: Deterministic belief record store (derived cache) for capability derivation.
ALLOWED DEPENDENCIES: `include/domino/**`, `source/dominium/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: OS headers; locale/timezone libraries.
*/
#ifndef DOM_BELIEF_STORE_H
#define DOM_BELIEF_STORE_H

#include "domino/core/spacetime.h"
#include "domino/core/types.h"
#include "runtime/dom_capability_types.h"

#ifdef __cplusplus
extern "C" {
#endif

enum {
    DOM_BELIEF_OK = 0,
    DOM_BELIEF_ERR = -1,
    DOM_BELIEF_INVALID_ARGUMENT = -2,
    DOM_BELIEF_DUPLICATE_ID = -3,
    DOM_BELIEF_NOT_FOUND = -4
};

enum dom_belief_flags {
    DOM_BELIEF_FLAG_UNKNOWN = 1u << 0,
    DOM_BELIEF_FLAG_STALE = 1u << 1
};

typedef struct dom_belief_record {
    u64 record_id;
    dom_capability_id capability_id;
    dom_capability_subject subject;
    u32 resolution_tier;
    i64 value_min;
    i64 value_max;
    dom_tick observed_tick;
    dom_tick delivery_tick;
    dom_tick expiry_tick;
    u64 source_provenance;
    u32 flags;
} dom_belief_record;

typedef struct dom_belief_store dom_belief_store;

dom_belief_store *dom_belief_store_create(void);
void dom_belief_store_destroy(dom_belief_store *store);
int dom_belief_store_init(dom_belief_store *store);

int dom_belief_store_add_record(dom_belief_store *store,
                                const dom_belief_record *record);
int dom_belief_store_remove_record(dom_belief_store *store,
                                   u64 record_id);
int dom_belief_store_clear(dom_belief_store *store);

int dom_belief_store_list_records(const dom_belief_store *store,
                                  dom_belief_record *out_records,
                                  u32 max_records,
                                  u32 *out_count);
int dom_belief_store_iterate(const dom_belief_store *store,
                             void (*fn)(const dom_belief_record *record, void *user),
                             void *user);

int dom_belief_store_get_revision(const dom_belief_store *store,
                                  u64 *out_revision);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOM_BELIEF_STORE_H */
