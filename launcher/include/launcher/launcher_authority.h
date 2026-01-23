/*
FILE: include/launcher/launcher_authority.h
MODULE: Launcher
PURPOSE: Entitlement to authority issuance (TESTX3).
NOTES: Launcher issues authority tokens; server validates them.
REFERENCES: docs/arch/AUTHORITY_AND_ENTITLEMENTS.md
*/
#ifndef LAUNCHER_AUTHORITY_H
#define LAUNCHER_AUTHORITY_H

#include "dom_contracts/authority_token.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct launcher_entitlement_set_s {
    u32 flags;
} launcher_entitlement_set;

#define LAUNCHER_ENTITLEMENT_NONE          0u
#define LAUNCHER_ENTITLEMENT_FULL_PLAYER  (1u << 0u)
#define LAUNCHER_ENTITLEMENT_SERVICE      (1u << 1u)
#define LAUNCHER_ENTITLEMENT_ADMIN        (1u << 2u)

typedef struct launcher_authority_selection_s {
    u32 profile;
    u32 refusal_code;
} launcher_authority_selection;

void launcher_entitlements_clear(launcher_entitlement_set* ent);
void launcher_entitlements_grant(launcher_entitlement_set* ent, u32 flag);
int launcher_entitlements_has(const launcher_entitlement_set* ent, u32 flag);

int launcher_entitlements_can_issue(const launcher_entitlement_set* ent, u32 profile);
launcher_authority_selection launcher_authority_select_profile(const launcher_entitlement_set* ent,
                                                                u32 requested_profile);
launcher_authority_selection launcher_authority_default_profile(const launcher_entitlement_set* ent,
                                                                 int offline);

int launcher_authority_issue_token(const launcher_entitlement_set* ent,
                                   u32 requested_profile,
                                   u64 issued_act,
                                   u64 expires_act,
                                   char* out_token,
                                   u32 out_len,
                                   u32* out_profile,
                                   u32* out_refusal);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* LAUNCHER_AUTHORITY_H */
