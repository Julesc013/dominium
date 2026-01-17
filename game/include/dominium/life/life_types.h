/*
LIFE types and enums (LIFE1).
*/
#ifndef DOMINIUM_LIFE_TYPES_H
#define DOMINIUM_LIFE_TYPES_H

#include "domino/core/types.h"

#ifdef __cplusplus
extern "C" {
#endif

#define LIFE_POLICY_MASK(type) (1u << ((u32)(type) - 1u))

typedef enum life_policy_type {
    LIFE_POLICY_S1 = 1,
    LIFE_POLICY_S2 = 2,
    LIFE_POLICY_S3 = 3,
    LIFE_POLICY_S4 = 4
} life_policy_type;

typedef enum life_refusal_code {
    LIFE_REFUSAL_NONE = 0,
    LIFE_REFUSAL_NO_ELIGIBLE_PERSON,
    LIFE_REFUSAL_INSUFFICIENT_AUTHORITY,
    LIFE_REFUSAL_PREREQ_MISSING_FACILITY,
    LIFE_REFUSAL_PREREQ_MISSING_RESOURCES,
    LIFE_REFUSAL_PREREQ_MISSING_RECORDING,
    LIFE_REFUSAL_POLICY_NOT_ALLOWED,
    LIFE_REFUSAL_EPISTEMIC_INSUFFICIENT_KNOWLEDGE
} life_refusal_code;

typedef enum life_cont_action {
    LIFE_CONT_ACTION_NONE = 0,
    LIFE_CONT_ACTION_TRANSFER,
    LIFE_CONT_ACTION_PENDING,
    LIFE_CONT_ACTION_SPECTATOR
} life_cont_action;

typedef enum life_candidate_reason {
    LIFE_CANDIDATE_SPOUSE = 0,
    LIFE_CANDIDATE_ADULT_CHILD = 1,
    LIFE_CANDIDATE_ORG_MEMBER = 2,
    LIFE_CANDIDATE_DELEGATED = 3
} life_candidate_reason;

typedef enum life_authority_source {
    LIFE_AUTH_CONTRACT = 0,
    LIFE_AUTH_GUARDIAN = 1,
    LIFE_AUTH_ORG = 2,
    LIFE_AUTH_JURISDICTION = 3,
    LIFE_AUTH_PERSONAL = 4
} life_authority_source;

enum {
    LIFE_ABILITY_HARDCORE_ID = 1,
    LIFE_ABILITY_SOFTCORE_ID = 2,
    LIFE_ABILITY_CREATIVE_ID = 3,
    LIFE_ABILITY_SPECTATOR_ID = 4
};

typedef struct life_candidate {
    u64 person_id;
    u32 reason;
} life_candidate;

typedef struct life_epistemic_set {
    const u64* known_person_ids;
    u32 count;
} life_epistemic_set;

typedef struct life_continuation_decision {
    u32 policy_id;
    u64 target_person_id;
    life_cont_action action;
    life_refusal_code refusal;
} life_continuation_decision;

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_LIFE_TYPES_H */
