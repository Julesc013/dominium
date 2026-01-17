/*
FILE: include/dominium/life/continuation_policy.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / life
RESPONSIBILITY: Defines continuation policy context and evaluation API.
ALLOWED DEPENDENCIES: `game/include/**`, `engine/include/**` public headers, and C89/C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; product-layer runtime code.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Deterministic selection and refusal codes are mandatory.
*/
#ifndef DOMINIUM_LIFE_CONTINUATION_POLICY_H
#define DOMINIUM_LIFE_CONTINUATION_POLICY_H

#include "dominium/life/ability_packages.h"
#include "dominium/life/control_authority.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct life_continuation_prereqs {
    u8 has_facility;
    u8 has_resources;
    u8 has_recording;
    u8 has_drone;
} life_continuation_prereqs;

typedef struct life_continuation_context {
    u64 controller_id;
    life_policy_type policy_type;
    const life_ability_package* ability;
    const life_candidate* candidates;
    u32 candidate_count;
    const life_epistemic_set* epistemic;
    const life_authority_set* authority;
    u8 allow_blind_delegation;
    life_continuation_prereqs prereqs;
} life_continuation_context;

/* Purpose: Evaluate continuation policy for a controller. */
int life_continuation_decide(const life_continuation_context* ctx,
                             life_continuation_decision* out_decision);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_LIFE_CONTINUATION_POLICY_H */
