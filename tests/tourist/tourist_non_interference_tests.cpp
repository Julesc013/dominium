/*
Tourist non-interference tests (TESTX3).
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

    dom_authority_claims_init(&claims, DOM_AUTH_PROFILE_TOURIST, 0u, 0u, 0u);
    decision = dom_server_authority_check(&claims, DOM_AUTH_ACTION_AUTHORITATIVE_MUTATE);
    EXPECT(decision.allowed == 0, "tourist mutation allowed");
    EXPECT(decision.refusal_code == DOM_AUTH_REFUSE_PROFILE_INSUFFICIENT,
           "tourist refusal code");

    decision = dom_server_authority_check(&claims, DOM_AUTH_ACTION_CONNECT);
    EXPECT(decision.allowed != 0, "tourist connect denied");

    EXPECT(mp0_run_hash(&hash_a) != 0, "mp0 hash baseline");
    EXPECT(mp0_run_hash(&hash_b) != 0, "mp0 hash with tourist");
    EXPECT(hash_a == hash_b, "tourist presence altered hash");

    return 0;
}
