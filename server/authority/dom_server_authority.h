/*
FILE: server/authority/dom_server_authority.h
MODULE: Server
PURPOSE: Server-side authority validation and gating (TESTX3).
REFERENCES: docs/architecture/AUTHORITY_AND_ENTITLEMENTS.md, docs/architecture/DEMO_AND_TOURIST_MODEL.md
*/
#ifndef DOM_SERVER_AUTHORITY_H
#define DOM_SERVER_AUTHORITY_H

#include "dom_contracts/authority.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct dom_authority_decision_s {
    int allowed;
    u32 refusal_code;
} dom_authority_decision;

typedef struct dom_authority_validation_result_s {
    int valid;
    u32 refusal_code;
    dom_authority_claims claims;
} dom_authority_validation_result;

typedef struct dom_authority_context_s {
    const char* authority_origin;
    const char* experience_id;
    const char* law_profile_id;
    const char* entitlements_csv;
    u64 capability_set_hash;
    const char* epistemic_scope_id;
    const char* privilege_watermark_policy;
    int audit_required;
    int server_authoritative;
    const char* refusal_policy_id;
} dom_authority_context;

void dom_authority_claims_init(dom_authority_claims* claims,
                               u32 profile,
                               u32 scope_id,
                               u64 issued_act,
                               u64 expires_act);

int dom_authority_claims_upgrade(dom_authority_claims* claims, u32 new_profile);
int dom_authority_claims_downgrade(dom_authority_claims* claims, u32 new_profile);

dom_authority_decision dom_server_authority_check(const dom_authority_claims* claims,
                                                  u32 action);
dom_authority_decision dom_server_authority_check_with_context(const dom_authority_claims* claims,
                                                               const dom_authority_context* ctx,
                                                               u32 action);
dom_authority_validation_result dom_server_authority_validate_token(const char* token,
                                                                     u64 now_act);
dom_authority_save_class dom_server_authority_save_class(const dom_authority_claims* claims);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOM_SERVER_AUTHORITY_H */
