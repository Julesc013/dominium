/*
TEST: dom_econ_access_control_test
PURPOSE: Access control grant/revoke determinism.
*/
#include "runtime/dom_econ_access_control.h"

int main(void) {
    dom_econ_access_control *ctrl = dom_econ_access_control_create();
    dom_econ_access_grant_desc grant;
    u32 flags;

    if (!ctrl) {
        return 1;
    }

    grant.actor_id = 10ull;
    grant.account_id = 20ull;
    grant.flags = DOM_ECON_ACCESS_VIEW_BALANCE | DOM_ECON_ACCESS_VIEW_TRANSACTIONS;

    if (dom_econ_access_grant(ctrl, &grant) != DOM_ECON_ACCESS_OK) {
        dom_econ_access_control_destroy(ctrl);
        return 2;
    }

    flags = dom_econ_access_check(ctrl, grant.actor_id, grant.account_id);
    if (flags != grant.flags) {
        dom_econ_access_control_destroy(ctrl);
        return 3;
    }

    if (dom_econ_access_revoke(ctrl, grant.actor_id, grant.account_id) != DOM_ECON_ACCESS_OK) {
        dom_econ_access_control_destroy(ctrl);
        return 4;
    }

    flags = dom_econ_access_check(ctrl, grant.actor_id, grant.account_id);
    if (flags != 0u) {
        dom_econ_access_control_destroy(ctrl);
        return 5;
    }

    dom_econ_access_control_destroy(ctrl);
    return 0;
}
