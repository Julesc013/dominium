/*
FILE: include/dominium/interest_set.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / interest_set
RESPONSIBILITY: Defines the public contract for Interest Sets (types + function signatures).
ALLOWED DEPENDENCIES: `game/include/**`, `engine/include/**` public headers, and C89 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; product-layer runtime code.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Deterministic ordering and membership are mandatory.
*/
#ifndef DOMINIUM_INTEREST_SET_H
#define DOMINIUM_INTEREST_SET_H

#include "domino/core/types.h"
#include "domino/core/dom_time_core.h"

#ifdef __cplusplus
extern "C" {
#endif

/* Interest reason taxonomy (stable IDs). */
typedef enum dom_interest_reason {
    DOM_INTEREST_REASON_PLAYER_FOCUS = 1,
    DOM_INTEREST_REASON_COMMAND_INTENT = 2,
    DOM_INTEREST_REASON_LOGISTICS_ROUTE = 3,
    DOM_INTEREST_REASON_SENSOR_COMMS = 4,
    DOM_INTEREST_REASON_HAZARD_CONFLICT = 5,
    DOM_INTEREST_REASON_GOVERNANCE_SCOPE = 6
} dom_interest_reason;

/* Interest target kinds (stable IDs). */
typedef enum dom_interest_target_kind {
    DOM_INTEREST_TARGET_SYSTEM = 1,
    DOM_INTEREST_TARGET_REGION = 2,
    DOM_INTEREST_TARGET_ENTITY = 3,
    DOM_INTEREST_TARGET_ROUTE = 4,
    DOM_INTEREST_TARGET_ORG = 5
} dom_interest_target_kind;

/* Interest strengths (0..100). */
enum {
    DOM_INTEREST_STRENGTH_LOW = 25,
    DOM_INTEREST_STRENGTH_MED = 50,
    DOM_INTEREST_STRENGTH_HIGH = 75,
    DOM_INTEREST_STRENGTH_CRITICAL = 100
};

/* Persistent interest expiry marker. */
#define DOM_INTEREST_PERSISTENT DOM_TIME_ACT_MAX

typedef struct dom_interest_entry {
    u64            target_id;
    u32            target_kind;
    u32            reason;
    u32            strength;
    dom_act_time_t expiry_tick;
} dom_interest_entry;

typedef struct dom_interest_set {
    dom_interest_entry* entries;
    u32                 count;
    u32                 capacity;
    u32                 overflow;
} dom_interest_set;

/* Purpose: Initialize an interest set (no allocation). */
void dom_interest_set_init(dom_interest_set* set);
/* Purpose: Release storage owned by the set. */
void dom_interest_set_free(dom_interest_set* set);
/* Purpose: Reserve storage for entries. Returns 0 on success. */
int  dom_interest_set_reserve(dom_interest_set* set, u32 capacity);
/* Purpose: Clear entries but keep storage. */
void dom_interest_set_clear(dom_interest_set* set);
/* Purpose: Add an entry. Returns 0 on success. */
int  dom_interest_set_add(dom_interest_set* set,
                          u32 target_kind,
                          u64 target_id,
                          dom_interest_reason reason,
                          u32 strength,
                          dom_act_time_t expiry_tick);
/* Purpose: Canonicalize order and deduplicate deterministically. */
void dom_interest_set_finalize(dom_interest_set* set);
/* Purpose: Get overflow count from add() failures. */
u32  dom_interest_set_overflow(const dom_interest_set* set);

/* Purpose: Query the max strength for a target at time `now` (ignores expired entries). */
u32  dom_interest_set_strength(const dom_interest_set* set,
                               u32 target_kind,
                               u64 target_id,
                               dom_act_time_t now,
                               dom_act_time_t* out_expiry);

/* Relevance states. */
typedef enum dom_relevance_state {
    DOM_REL_LATENT = 0,
    DOM_REL_COLD = 1,
    DOM_REL_WARM = 2,
    DOM_REL_HOT = 3
} dom_relevance_state;

typedef struct dom_interest_policy {
    u32            enter_warm;
    u32            exit_warm;
    u32            enter_hot;
    u32            exit_hot;
    dom_act_time_t min_dwell_ticks;
} dom_interest_policy;

typedef struct dom_interest_state {
    u64             target_id;
    u32             target_kind;
    dom_relevance_state state;
    dom_act_time_t  last_change_tick;
} dom_interest_state;

typedef struct dom_interest_transition {
    u64                 target_id;
    u32                 target_kind;
    dom_relevance_state from_state;
    dom_relevance_state to_state;
} dom_interest_transition;

/* Purpose: Initialize relevance state array to LATENT. */
void dom_interest_state_init(dom_interest_state* states, u32 state_count);

/* Purpose: Apply interest and update relevance states deterministically.
 * Returns number of transitions written to out_transitions (bounded by *in_out_count).
 */
u32 dom_interest_state_apply(const dom_interest_set* set,
                             dom_interest_state* states,
                             u32 state_count,
                             const dom_interest_policy* policy,
                             dom_act_time_t now_tick,
                             dom_interest_transition* out_transitions,
                             u32* in_out_count);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_INTEREST_SET_H */
