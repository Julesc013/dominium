/*
Control capability refusal tests (TESTX2).
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
    dom_control_result res;

    print_version_banner();
    EXPECT(dom_control_caps_init(&caps, DOMINIUM_CONTROL_REGISTRY_PATH) == DOM_CONTROL_OK,
           "control registry init");

    res = dom_control_caps_require(&caps, 1u, "missing_capability");
    EXPECT(res == DOM_CONTROL_ERR_DISABLED, "refusal for disabled capability");

    res = dom_control_caps_require(&caps, 999u, "invalid_capability");
    EXPECT(res == DOM_CONTROL_ERR_INVALID, "refusal for invalid capability");

    dom_control_caps_free(&caps);
    return 0;
}
