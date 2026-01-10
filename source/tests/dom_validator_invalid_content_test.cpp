/*
FILE: source/tests/dom_validator_invalid_content_test.cpp
MODULE: Dominium Tests
PURPOSE: Ensure validator reports invalid bundle content.
*/
#include <cstdio>
#include <cstring>
#include <string>

#include "dom_feature_epoch.h"
#include "runtime/dom_universe_bundle.h"
#include "validator/validator_checks.h"

static int fail(const char *msg) {
    std::fprintf(stderr, "FAIL: %s\n", msg ? msg : "(null)");
    return 1;
}

int main() {
    dom_universe_bundle *bundle = dom_universe_bundle_create();
    dom_universe_bundle_identity id;
    dom_universe_bundle_identity out_id;
    dom::tools::DomToolDiagnostics diag;
    bool ok;

    if (!bundle) {
        return fail("bundle_create_failed");
    }

    std::memset(&id, 0, sizeof(id));
    id.universe_id = "u1";
    id.universe_id_len = 2u;
    id.instance_id = "inst1";
    id.instance_id_len = 5u;
    id.ups = 60u;
    id.tick_index = 0ull;
    id.feature_epoch = DOM_FEATURE_EPOCH_DEFAULT;
    if (dom_universe_bundle_set_identity(bundle, &id) != DOM_UNIVERSE_BUNDLE_OK) {
        dom_universe_bundle_destroy(bundle);
        return fail("identity_set_failed");
    }

    ok = dom::tools::validator_check_bundle(bundle, diag, &out_id);
    if (ok || !diag.has_errors()) {
        dom_universe_bundle_destroy(bundle);
        return fail("expected_validator_errors");
    }

    dom_universe_bundle_destroy(bundle);
    std::printf("dom_validator_invalid_content_test: OK\n");
    return 0;
}
