/*
Piracy containment tests (TESTX3).
*/
#include "launcher/launcher_authority.h"
#include "server/authority/dom_server_authority.h"
#include "tests/control/control_test_common.h"

#include <stdio.h>

#define EXPECT(cond, msg) do { \
    if (!(cond)) { \
        fprintf(stderr, "FAIL: %s\n", msg); \
        return 1; \
    } \
} while (0)

int main(void)
{
    launcher_entitlement_set ent;
    launcher_authority_selection sel;
    dom_authority_claims claims;
    dom_authority_decision decision;
    u64 hash_a = 0u;
    u64 hash_b = 0u;

    print_version_banner();

    launcher_entitlements_clear(&ent);
    sel = launcher_authority_default_profile(&ent, 1);
    EXPECT(sel.profile == DOM_AUTH_PROFILE_BASE_FREE, "offline bypass not base_free");

    sel = launcher_authority_select_profile(&ent, DOM_AUTH_PROFILE_FULL_PLAYER);
    EXPECT(sel.refusal_code == DOM_AUTH_REFUSE_ENTITLEMENT_MISSING,
           "missing entitlement refusal not set");

    dom_authority_claims_init(&claims, DOM_AUTH_PROFILE_BASE_FREE, 0u, 0u, 0u);
    decision = dom_server_authority_check(&claims, DOM_AUTH_ACTION_DURABLE_SAVE);
    EXPECT(decision.allowed == 0, "base_free durable save allowed");

    EXPECT(mp0_run_hash(&hash_a) != 0, "mp0 hash baseline");
    EXPECT(mp0_run_hash(&hash_b) != 0, "mp0 hash after refusal");
    EXPECT(hash_a == hash_b, "piracy refusal mutated state");

    return 0;
}
