/*
Demo vs paid read-path determinism tests (TESTX3).
*/
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
    char token_free[DOM_AUTH_TOKEN_MAX];
    char token_paid[DOM_AUTH_TOKEN_MAX];
    dom_authority_token_fields fields;
    u64 hash_free = 0u;
    u64 hash_paid = 0u;

    print_version_banner();

    EXPECT(dom_auth_token_build(token_free,
                                (u32)sizeof(token_free),
                                DOM_AUTH_PROFILE_BASE_FREE,
                                0u,
                                1u,
                                0u) != 0,
           "base_free token build");
    EXPECT(dom_auth_token_build(token_paid,
                                (u32)sizeof(token_paid),
                                DOM_AUTH_PROFILE_FULL_PLAYER,
                                0u,
                                1u,
                                0u) != 0,
           "full_player token build");

    EXPECT(dom_auth_token_validate(token_free, &fields) != 0, "base_free token validate");
    EXPECT(dom_auth_token_validate(token_paid, &fields) != 0, "full_player token validate");

    EXPECT(mp0_run_hash(&hash_free) != 0, "mp0 hash free");
    EXPECT(mp0_run_hash(&hash_paid) != 0, "mp0 hash paid");
    EXPECT(hash_free == hash_paid, "demo vs paid hash mismatch");

    return 0;
}
