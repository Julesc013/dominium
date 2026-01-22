/*
Control capability registry determinism tests (TESTX2).
*/
#include "domino/control.h"
#include "tests/control/control_test_common.h"

#include <stdio.h>
#include <string.h>

#ifndef DOMINIUM_CONTROL_REGISTRY_PATH
#define DOMINIUM_CONTROL_REGISTRY_PATH "data/registries/control_capabilities.registry"
#endif

#define EXPECT(cond, msg) do { \
    if (!(cond)) { \
        fprintf(stderr, "FAIL: %s\n", msg); \
        return 1; \
    } \
} while (0)

#define EXPECT_KEY_ID(reg, key, expected) do { \
    u32 id = dom_registry_id_from_key((reg), (key)); \
    const char* round = dom_registry_key_from_id((reg), (expected)); \
    if (id != (expected)) { \
        fprintf(stderr, "FAIL: id mismatch for %s (got %u expected %u)\n", \
                (key), (unsigned int)id, (unsigned int)(expected)); \
        return 1; \
    } \
    if (!round || strcmp(round, (key)) != 0) { \
        fprintf(stderr, "FAIL: round-trip mismatch for %s\n", (key)); \
        return 1; \
    } \
} while (0)

int main(void)
{
    dom_control_caps caps;
    const dom_registry* reg;

    print_version_banner();
    EXPECT(dom_control_caps_init(&caps, DOMINIUM_CONTROL_REGISTRY_PATH) == DOM_CONTROL_OK,
           "control registry init");
    reg = dom_control_caps_registry(&caps);
    EXPECT(reg != 0, "control registry missing");
    EXPECT(reg->count == 8u, "control registry count");

    EXPECT_KEY_ID(reg, "CAPABILITY.CONTROL.ANTICHEAT.CLIENT_PROBE", 1u);
    EXPECT_KEY_ID(reg, "CAPABILITY.CONTROL.ANTICHEAT.SERVER_VALIDATION", 2u);
    EXPECT_KEY_ID(reg, "CAPABILITY.CONTROL.CONNECTIVITY.GATE", 3u);
    EXPECT_KEY_ID(reg, "CAPABILITY.CONTROL.DRM.LICENSE_CHECK", 4u);
    EXPECT_KEY_ID(reg, "CAPABILITY.CONTROL.EXECUTION.GATE", 5u);
    EXPECT_KEY_ID(reg, "CAPABILITY.CONTROL.MODERATION.HOOK", 6u);
    EXPECT_KEY_ID(reg, "CAPABILITY.CONTROL.PLATFORM.ENTITLEMENT", 7u);
    EXPECT_KEY_ID(reg, "CAPABILITY.CONTROL.TELEMETRY.OPT_IN", 8u);

    dom_control_caps_free(&caps);
    return 0;
}
