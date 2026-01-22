/*
Authority profile and upgrade/downgrade tests (TESTX3).
*/
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
    dom_authority_claims claims;
    dom_authority_decision decision;
    u64 hash_a = 0u;
    u64 hash_b = 0u;

    print_version_banner();

    dom_authority_claims_init(&claims, DOM_AUTH_PROFILE_BASE_FREE, 0u, 0u, 0u);
    decision = dom_server_authority_check(&claims, DOM_AUTH_ACTION_DURABLE_SAVE);
    EXPECT(decision.allowed == 0, "base_free durable save allowed");
    EXPECT(decision.refusal_code == DOM_AUTH_REFUSE_PROFILE_INSUFFICIENT, "base_free refusal code");

    decision = dom_server_authority_check(&claims, DOM_AUTH_ACTION_VIEW);
    EXPECT(decision.allowed != 0, "view gated by authority");

    EXPECT(dom_authority_claims_upgrade(&claims, DOM_AUTH_PROFILE_FULL_PLAYER) != 0,
           "claims upgrade failed");
    decision = dom_server_authority_check(&claims, DOM_AUTH_ACTION_DURABLE_SAVE);
    EXPECT(decision.allowed != 0, "full_player durable save denied");

    EXPECT(mp0_run_hash(&hash_a) != 0, "mp0 hash baseline");
    EXPECT(dom_authority_claims_downgrade(&claims, DOM_AUTH_PROFILE_TOURIST) != 0,
           "claims downgrade failed");
    EXPECT(mp0_run_hash(&hash_b) != 0, "mp0 hash after downgrade");
    EXPECT(hash_a == hash_b, "authority downgrade mutated state");

    decision = dom_server_authority_check((const dom_authority_claims*)0,
                                          DOM_AUTH_ACTION_AUTHORITATIVE_MUTATE);
    EXPECT(decision.allowed == 0, "missing claims allowed mutation");
    EXPECT(decision.refusal_code == DOM_AUTH_REFUSE_PROFILE_MISSING, "missing claims refusal");

    return 0;
}
