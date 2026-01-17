/*
FILE: include/dominium/fidelity.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / fidelity
RESPONSIBILITY: Defines fidelity tiers, state model, and refine/collapse interfaces.
ALLOWED DEPENDENCIES: `game/include/**`, `engine/include/**` public headers, and C89 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; product-layer runtime code.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Deterministic ordering and transitions are mandatory.
*/
#ifndef DOMINIUM_FIDELITY_H
#define DOMINIUM_FIDELITY_H

#include "domino/core/types.h"
#include "domino/core/dom_time_core.h"
#include "dominium/interest_set.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef enum dom_fidelity_tier {
    DOM_FIDELITY_LATENT = 0,
    DOM_FIDELITY_MACRO = 1,
    DOM_FIDELITY_MESO = 2,
    DOM_FIDELITY_MICRO = 3,
    DOM_FIDELITY_FOCUS = 4
} dom_fidelity_tier;

enum {
    DOM_FIDELITY_PIN_VISIBLE = 1u << 0,
    DOM_FIDELITY_PIN_MISSION = 1u << 1,
    DOM_FIDELITY_PIN_AUTHORITY = 1u << 2
};

typedef struct dom_fidelity_state {
    dom_fidelity_tier current_tier;
    dom_act_time_t    last_transition_tick;
    u32               pin_flags;
    u64               provenance_summary_hash;
} dom_fidelity_state;

typedef struct dom_fidelity_object {
    u64               object_id;
    u32               object_kind;
    dom_fidelity_state state;
    u64               count;
    u64               inventory;
    u64               obligations;
} dom_fidelity_object;

typedef enum dom_fidelity_request_type {
    DOM_FIDELITY_REQUEST_REFINE = 1,
    DOM_FIDELITY_REQUEST_COLLAPSE = 2
} dom_fidelity_request_type;

typedef struct dom_fidelity_request {
    u64                     object_id;
    u32                     object_kind;
    dom_fidelity_request_type type;
    dom_fidelity_tier        target_tier;
    u32                     reason;
} dom_fidelity_request;

typedef struct dom_fidelity_transition {
    u64               object_id;
    u32               object_kind;
    dom_fidelity_tier from_tier;
    dom_fidelity_tier to_tier;
} dom_fidelity_transition;

typedef struct dom_fidelity_policy {
    u32            refine_min_strength;
    u32            collapse_max_strength;
    dom_act_time_t min_dwell_ticks;
} dom_fidelity_policy;

typedef struct dom_fidelity_context {
    dom_fidelity_object*  objects;
    u32                   object_capacity;
    u32                   object_count;
    dom_fidelity_request* requests;
    u32                   request_capacity;
    u32                   request_count;
} dom_fidelity_context;

int dom_fidelity_context_init(dom_fidelity_context* ctx,
                              dom_fidelity_object* object_storage,
                              u32 object_capacity,
                              dom_fidelity_request* request_storage,
                              u32 request_capacity);

dom_fidelity_object* dom_fidelity_register_object(dom_fidelity_context* ctx,
                                                  u32 object_kind,
                                                  u64 object_id,
                                                  dom_fidelity_tier tier);

dom_fidelity_object* dom_fidelity_find_object(dom_fidelity_context* ctx,
                                              u32 object_kind,
                                              u64 object_id);

void dom_fidelity_set_pins(dom_fidelity_object* obj, u32 pin_flags);
void dom_fidelity_set_provenance_hash(dom_fidelity_object* obj, u64 hash);

int dom_fidelity_request_refine(dom_fidelity_context* ctx,
                                u32 object_kind,
                                u64 object_id,
                                dom_fidelity_tier target_tier,
                                u32 reason);

int dom_fidelity_request_collapse(dom_fidelity_context* ctx,
                                  u32 object_kind,
                                  u64 object_id,
                                  dom_fidelity_tier target_tier,
                                  u32 reason);

/* Apply queued requests deterministically; returns number of transitions recorded. */
u32 dom_fidelity_apply_requests(dom_fidelity_context* ctx,
                                const dom_interest_set* interest,
                                const dom_fidelity_policy* policy,
                                dom_act_time_t now_tick,
                                dom_fidelity_transition* out_transitions,
                                u32* in_out_transition_count);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_FIDELITY_H */
