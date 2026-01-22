/*
Services expiry tests (TESTX3).
*/
#include "server/authority/dom_server_authority.h"
#include "dom_contracts/authority_token.h"
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
    char token[DOM_AUTH_TOKEN_MAX];
    dom_authority_validation_result res;
    u64 hash_a = 0u;
    u64 hash_b = 0u;

    print_version_banner();

    EXPECT(dom_auth_token_build(token,
                                (u32)sizeof(token),
                                DOM_AUTH_PROFILE_SERVICE_SCOPED,
                                0u,
                                1u,
                                1u) != 0,
           "service token build");

    res = dom_server_authority_validate_token(token, 2u);
    EXPECT(res.valid == 0, "expired token marked valid");
    EXPECT(res.refusal_code == DOM_AUTH_REFUSE_SERVICE_EXPIRED, "service expiry refusal");
    EXPECT(res.claims.profile == DOM_AUTH_PROFILE_BASE_FREE, "expired service did not degrade");

    EXPECT(mp0_run_hash(&hash_a) != 0, "mp0 hash baseline");
    EXPECT(mp0_run_hash(&hash_b) != 0, "mp0 hash after expiry");
    EXPECT(hash_a == hash_b, "service expiry mutated state");

    return 0;
}
