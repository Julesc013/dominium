/*
FILE: server/authority/dom_server_authority.cpp
MODULE: Server
PURPOSE: Server-side authority validation and gating (TESTX3).
NOTES: Deterministic checks only; no secrets embedded here.
*/
#include "server/authority/dom_server_authority.h"
#include "dom_contracts/authority_token.h"

#include <string.h>

void dom_authority_claims_init(dom_authority_claims* claims,
                               u32 profile,
                               u32 scope_id,
                               u64 issued_act,
                               u64 expires_act)
{
    if (!claims) {
        return;
    }
    claims->profile = profile;
    claims->scope_id = scope_id;
    claims->issued_act = issued_act;
    claims->expires_act = expires_act;
    claims->flags = 0u;
}

int dom_authority_claims_upgrade(dom_authority_claims* claims, u32 new_profile)
{
    if (!claims || new_profile == DOM_AUTH_PROFILE_INVALID) {
        return 0;
    }
    claims->profile = new_profile;
    return 1;
}

int dom_authority_claims_downgrade(dom_authority_claims* claims, u32 new_profile)
{
    if (!claims || new_profile == DOM_AUTH_PROFILE_INVALID) {
        return 0;
    }
    claims->profile = new_profile;
    return 1;
}

static int dom_authority_action_allowed(u32 profile, u32 action)
{
    if (action == DOM_AUTH_ACTION_VIEW) {
        return 1;
    }
    switch (profile) {
    case DOM_AUTH_PROFILE_BASE_FREE:
        return 0;
    case DOM_AUTH_PROFILE_TOURIST:
        return (action == DOM_AUTH_ACTION_CONNECT);
    case DOM_AUTH_PROFILE_FULL_PLAYER:
        return (action == DOM_AUTH_ACTION_CONNECT ||
                action == DOM_AUTH_ACTION_AUTHORITATIVE_MUTATE ||
                action == DOM_AUTH_ACTION_DURABLE_SAVE ||
                action == DOM_AUTH_ACTION_ECONOMIC_IMPACT ||
                action == DOM_AUTH_ACTION_COMPETITIVE_MP ||
                action == DOM_AUTH_ACTION_MOD_EXPORT);
    case DOM_AUTH_PROFILE_SERVICE_SCOPED:
        return (action == DOM_AUTH_ACTION_CONNECT ||
                action == DOM_AUTH_ACTION_SERVICE_FEATURE);
    case DOM_AUTH_PROFILE_ADMIN:
        return 1;
    default:
        break;
    }
    return 0;
}

dom_authority_decision dom_server_authority_check(const dom_authority_claims* claims,
                                                  u32 action)
{
    dom_authority_decision out;
    out.allowed = 0;
    out.refusal_code = DOM_AUTH_REFUSE_PROFILE_MISSING;
    if (action == DOM_AUTH_ACTION_VIEW) {
        out.allowed = 1;
        out.refusal_code = DOM_AUTH_REFUSE_NONE;
        return out;
    }
    if (!claims || claims->profile == DOM_AUTH_PROFILE_INVALID) {
        return out;
    }
    if (dom_authority_action_allowed(claims->profile, action)) {
        out.allowed = 1;
        out.refusal_code = DOM_AUTH_REFUSE_NONE;
        return out;
    }
    out.refusal_code = DOM_AUTH_REFUSE_PROFILE_INSUFFICIENT;
    return out;
}

dom_authority_validation_result dom_server_authority_validate_token(const char* token,
                                                                     u64 now_act)
{
    dom_authority_validation_result res;
    dom_authority_token_fields fields;
    memset(&res, 0, sizeof(res));
    res.valid = 0;
    res.refusal_code = DOM_AUTH_REFUSE_TOKEN_INVALID;
    dom_authority_claims_init(&res.claims,
                              DOM_AUTH_PROFILE_INVALID,
                              0u,
                              0u,
                              0u);
    if (!token) {
        res.refusal_code = DOM_AUTH_REFUSE_PROFILE_MISSING;
        res.claims.profile = DOM_AUTH_PROFILE_BASE_FREE;
        return res;
    }
    if (!dom_auth_token_validate(token, &fields)) {
        res.refusal_code = DOM_AUTH_REFUSE_TOKEN_INVALID;
        res.claims.profile = DOM_AUTH_PROFILE_BASE_FREE;
        return res;
    }
    res.valid = 1;
    res.refusal_code = DOM_AUTH_REFUSE_NONE;
    dom_authority_claims_init(&res.claims,
                              fields.profile,
                              fields.scope_id,
                              fields.issued_act,
                              fields.expires_act);
    if (fields.expires_act != 0u && now_act > fields.expires_act) {
        res.valid = 0;
        res.claims.profile = DOM_AUTH_PROFILE_BASE_FREE;
        if (fields.profile == DOM_AUTH_PROFILE_SERVICE_SCOPED) {
            res.refusal_code = DOM_AUTH_REFUSE_SERVICE_EXPIRED;
        } else {
            res.refusal_code = DOM_AUTH_REFUSE_TOKEN_EXPIRED;
        }
    }
    return res;
}

dom_authority_save_class dom_server_authority_save_class(const dom_authority_claims* claims)
{
    if (!claims) {
        return DOM_AUTH_SAVE_NON_AUTHORITATIVE;
    }
    if (claims->profile == DOM_AUTH_PROFILE_FULL_PLAYER ||
        claims->profile == DOM_AUTH_PROFILE_ADMIN) {
        return DOM_AUTH_SAVE_AUTHORITATIVE;
    }
    return DOM_AUTH_SAVE_NON_AUTHORITATIVE;
}
