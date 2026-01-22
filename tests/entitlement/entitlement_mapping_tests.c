/*
Entitlement to authority mapping tests (TESTX3).
*/
#include "launcher/launcher_authority.h"
#include "tests/test_version.h"

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
    char token[DOM_AUTH_TOKEN_MAX];
    u32 profile = 0u;
    u32 refusal = 0u;

    print_version_banner();

    launcher_entitlements_clear(&ent);
    sel = launcher_authority_select_profile(&ent, DOM_AUTH_PROFILE_FULL_PLAYER);
    EXPECT(sel.refusal_code == DOM_AUTH_REFUSE_ENTITLEMENT_MISSING,
           "missing entitlement refusal");

    sel = launcher_authority_default_profile(&ent, 1);
    EXPECT(sel.profile == DOM_AUTH_PROFILE_BASE_FREE, "offline default not base_free");
    EXPECT(sel.refusal_code == DOM_AUTH_REFUSE_ENTITLEMENT_MISSING,
           "offline default missing entitlement refusal");

    launcher_entitlements_grant(&ent, LAUNCHER_ENTITLEMENT_FULL_PLAYER);
    sel = launcher_authority_select_profile(&ent, DOM_AUTH_PROFILE_FULL_PLAYER);
    EXPECT(sel.refusal_code == DOM_AUTH_REFUSE_NONE, "full_player entitlement refused");
    EXPECT(sel.profile == DOM_AUTH_PROFILE_FULL_PLAYER, "full_player profile mismatch");

    EXPECT(launcher_authority_issue_token(&ent,
                                          DOM_AUTH_PROFILE_FULL_PLAYER,
                                          1u,
                                          0u,
                                          token,
                                          (u32)sizeof(token),
                                          &profile,
                                          &refusal) != 0,
           "token issue failed");
    EXPECT(refusal == DOM_AUTH_REFUSE_NONE, "token refusal set");
    EXPECT(profile == DOM_AUTH_PROFILE_FULL_PLAYER, "token profile mismatch");

    return 0;
}
