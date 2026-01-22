/*
Control disabled determinism tests (TESTX2).
*/
#include "domino/control.h"
#include "tests/control/control_test_common.h"

#include <stdio.h>

#ifndef DOMINIUM_CONTROL_REGISTRY_PATH
#define DOMINIUM_CONTROL_REGISTRY_PATH "data/registries/control_capabilities.registry"
#endif

#define EXPECT(cond, msg) do { \
    if (!(cond)) { \
        fprintf(stderr, "FAIL: %s\n", msg); \
        return 1; \
    } \
} while (0)

int main(void)
{
    dom_control_caps caps;
    u64 hash_a = 0u;
    u64 hash_b = 0u;

    print_version_banner();
    EXPECT(dom_control_caps_init(&caps, DOMINIUM_CONTROL_REGISTRY_PATH) == DOM_CONTROL_OK,
           "control registry init");
    EXPECT(dom_control_caps_enabled_count(&caps) == 0u, "control disabled by default");

    EXPECT(mp0_run_hash(&hash_a) != 0, "mp0 run hash A");
    EXPECT(mp0_run_hash(&hash_b) != 0, "mp0 run hash B");
    EXPECT(hash_a == hash_b, "disabled control determinism mismatch");

    dom_control_caps_free(&caps);
    return 0;
}
