/*
FILE: include/dom_contracts/authority.h
MODULE: Dominium
PURPOSE: Authority profile and refusal codes (TESTX3).
NOTES: Profiles are architectural and closed-world (no CUSTOM/OTHER).
REFERENCES: docs/architecture/AUTHORITY_AND_ENTITLEMENTS.md, docs/architecture/DEMO_AND_TOURIST_MODEL.md
*/
#ifndef DOM_CONTRACTS_AUTHORITY_H
#define DOM_CONTRACTS_AUTHORITY_H

#include "domino/core/types.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef enum dom_authority_profile_e {
    DOM_AUTH_PROFILE_INVALID = 0u,
    DOM_AUTH_PROFILE_BASE_FREE = 1u,
    DOM_AUTH_PROFILE_TOURIST = 2u,
    DOM_AUTH_PROFILE_FULL_PLAYER = 3u,
    DOM_AUTH_PROFILE_SERVICE_SCOPED = 4u,
    DOM_AUTH_PROFILE_ADMIN = 5u
} dom_authority_profile;

typedef enum dom_authority_action_e {
    DOM_AUTH_ACTION_VIEW = 1u,
    DOM_AUTH_ACTION_CONNECT = 2u,
    DOM_AUTH_ACTION_AUTHORITATIVE_MUTATE = 3u,
    DOM_AUTH_ACTION_DURABLE_SAVE = 4u,
    DOM_AUTH_ACTION_ECONOMIC_IMPACT = 5u,
    DOM_AUTH_ACTION_COMPETITIVE_MP = 6u,
    DOM_AUTH_ACTION_MOD_EXPORT = 7u,
    DOM_AUTH_ACTION_SERVICE_FEATURE = 8u
} dom_authority_action;

typedef enum dom_authority_refusal_code_e {
    DOM_AUTH_REFUSE_NONE = 0u,
    DOM_AUTH_REFUSE_PROFILE_MISSING = 1u,
    DOM_AUTH_REFUSE_PROFILE_INSUFFICIENT = 2u,
    DOM_AUTH_REFUSE_ENTITLEMENT_MISSING = 3u,
    DOM_AUTH_REFUSE_TOKEN_INVALID = 4u,
    DOM_AUTH_REFUSE_TOKEN_EXPIRED = 5u,
    DOM_AUTH_REFUSE_SERVICE_EXPIRED = 6u
} dom_authority_refusal_code;

typedef enum dom_authority_save_class_e {
    DOM_AUTH_SAVE_NON_AUTHORITATIVE = 0u,
    DOM_AUTH_SAVE_AUTHORITATIVE = 1u
} dom_authority_save_class;

typedef struct dom_authority_claims_s {
    u32 profile;
    u32 scope_id;
    u64 issued_act;
    u64 expires_act;
    u32 flags;
} dom_authority_claims;

static const char* dom_authority_profile_name(u32 profile)
{
    switch (profile) {
    case DOM_AUTH_PROFILE_BASE_FREE: return "base_free";
    case DOM_AUTH_PROFILE_TOURIST: return "tourist";
    case DOM_AUTH_PROFILE_FULL_PLAYER: return "full_player";
    case DOM_AUTH_PROFILE_SERVICE_SCOPED: return "service_scoped";
    case DOM_AUTH_PROFILE_ADMIN: return "admin";
    default: break;
    }
    return "invalid";
}

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOM_CONTRACTS_AUTHORITY_H */
