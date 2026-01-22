/*
FILE: launcher/core/launcher_authority.c
MODULE: Launcher
PURPOSE: Entitlement to authority issuance (TESTX3).
NOTES: Uses deterministic token builder; no secrets in launcher core.
*/
#include "launcher/launcher_authority.h"
#include "dom_contracts/authority_token.h"

#include <string.h>

void launcher_entitlements_clear(launcher_entitlement_set* ent)
{
    if (!ent) {
        return;
    }
    ent->flags = 0u;
}

void launcher_entitlements_grant(launcher_entitlement_set* ent, u32 flag)
{
    if (!ent) {
        return;
    }
    ent->flags |= flag;
}

int launcher_entitlements_has(const launcher_entitlement_set* ent, u32 flag)
{
    if (!ent) {
        return 0;
    }
    return (ent->flags & flag) ? 1 : 0;
}

int launcher_entitlements_can_issue(const launcher_entitlement_set* ent, u32 profile)
{
    if (profile == DOM_AUTH_PROFILE_BASE_FREE || profile == DOM_AUTH_PROFILE_TOURIST) {
        return 1;
    }
    if (profile == DOM_AUTH_PROFILE_FULL_PLAYER) {
        return launcher_entitlements_has(ent, LAUNCHER_ENTITLEMENT_FULL_PLAYER);
    }
    if (profile == DOM_AUTH_PROFILE_SERVICE_SCOPED) {
        return launcher_entitlements_has(ent, LAUNCHER_ENTITLEMENT_SERVICE);
    }
    if (profile == DOM_AUTH_PROFILE_ADMIN) {
        return launcher_entitlements_has(ent, LAUNCHER_ENTITLEMENT_ADMIN);
    }
    return 0;
}

launcher_authority_selection launcher_authority_select_profile(const launcher_entitlement_set* ent,
                                                                u32 requested_profile)
{
    launcher_authority_selection sel;
    sel.profile = DOM_AUTH_PROFILE_BASE_FREE;
    sel.refusal_code = DOM_AUTH_REFUSE_NONE;
    if (launcher_entitlements_can_issue(ent, requested_profile)) {
        sel.profile = requested_profile;
        return sel;
    }
    sel.refusal_code = DOM_AUTH_REFUSE_ENTITLEMENT_MISSING;
    return sel;
}

launcher_authority_selection launcher_authority_default_profile(const launcher_entitlement_set* ent,
                                                                 int offline)
{
    launcher_authority_selection sel;
    sel.profile = DOM_AUTH_PROFILE_BASE_FREE;
    sel.refusal_code = DOM_AUTH_REFUSE_NONE;
    if (!offline) {
        return launcher_authority_select_profile(ent, DOM_AUTH_PROFILE_FULL_PLAYER);
    }
    if (launcher_entitlements_has(ent, LAUNCHER_ENTITLEMENT_FULL_PLAYER)) {
        sel.profile = DOM_AUTH_PROFILE_FULL_PLAYER;
        return sel;
    }
    sel.refusal_code = DOM_AUTH_REFUSE_ENTITLEMENT_MISSING;
    return sel;
}

int launcher_authority_issue_token(const launcher_entitlement_set* ent,
                                   u32 requested_profile,
                                   u64 issued_act,
                                   u64 expires_act,
                                   char* out_token,
                                   u32 out_len,
                                   u32* out_profile,
                                   u32* out_refusal)
{
    launcher_authority_selection sel;
    if (!out_token || out_len < DOM_AUTH_TOKEN_MAX) {
        return 0;
    }
    sel = launcher_authority_select_profile(ent, requested_profile);
    if (out_refusal) {
        *out_refusal = sel.refusal_code;
    }
    if (sel.refusal_code != DOM_AUTH_REFUSE_NONE) {
        out_token[0] = '\0';
        if (out_profile) {
            *out_profile = DOM_AUTH_PROFILE_INVALID;
        }
        return 0;
    }
    if (!dom_auth_token_build(out_token,
                              out_len,
                              sel.profile,
                              0u,
                              issued_act,
                              expires_act)) {
        if (out_profile) {
            *out_profile = DOM_AUTH_PROFILE_INVALID;
        }
        return 0;
    }
    if (out_profile) {
        *out_profile = sel.profile;
    }
    return 1;
}
