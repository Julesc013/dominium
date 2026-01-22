/*
Single distribution tests (TESTX3).
*/
#include "dom_contracts/authority_token.h"
#include "tests/test_version.h"

#include <stdio.h>
#include <string.h>

#define EXPECT(cond, msg) do { \
    if (!(cond)) { \
        fprintf(stderr, "FAIL: %s\n", msg); \
        return 1; \
    } \
} while (0)

static int token_has_marker(const char* token, const char* marker)
{
    if (!token || !marker) {
        return 0;
    }
    return strstr(token, marker) != 0;
}

int main(void)
{
    char token_free[DOM_AUTH_TOKEN_MAX];
    char token_paid[DOM_AUTH_TOKEN_MAX];

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

    EXPECT(strncmp(token_free, DOM_AUTH_TOKEN_PREFIX, strlen(DOM_AUTH_TOKEN_PREFIX)) == 0,
           "base_free token prefix");
    EXPECT(strncmp(token_paid, DOM_AUTH_TOKEN_PREFIX, strlen(DOM_AUTH_TOKEN_PREFIX)) == 0,
           "full_player token prefix");

    EXPECT(token_has_marker(token_free, "demo") == 0, "demo marker in token");
    EXPECT(token_has_marker(token_paid, "paid") == 0, "paid marker in token");

    return 0;
}
