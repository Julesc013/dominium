/*
Control audit/disclosure tests (TESTX2).
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
    const dom_registry* reg;
    u32 enabled_seen = 0u;
    u32 i;

    print_version_banner();
    EXPECT(dom_control_caps_init(&caps, DOMINIUM_CONTROL_REGISTRY_PATH) == DOM_CONTROL_OK,
           "control registry init");

    EXPECT(dom_control_caps_enable_id(&caps, 1u) == DOM_CONTROL_OK, "enable capability 1");
    EXPECT(dom_control_caps_enable_id(&caps, 5u) == DOM_CONTROL_OK, "enable capability 5");
    EXPECT(dom_control_caps_enabled_count(&caps) == 2u, "enabled count mismatch");

    reg = dom_control_caps_registry(&caps);
    EXPECT(reg != 0, "control registry missing");
    for (i = 0u; i < reg->count; ++i) {
        const dom_registry_entry* entry = &reg->entries[i];
        if (dom_control_caps_is_enabled(&caps, entry->id)) {
            enabled_seen += 1u;
        }
    }
    EXPECT(enabled_seen == 2u, "enabled enumeration mismatch");

    dom_control_caps_free(&caps);
    return 0;
}
