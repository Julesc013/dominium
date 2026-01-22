/*
Control hooks removal tests (TESTX2).
*/
#include "domino/control.h"
#include "domino/version.h"
#include "dom_contracts/version.h"
#include "dom_contracts/_internal/dom_build_version.h"

#include <stdio.h>
#include <string.h>

#ifndef DOMINIUM_CONTROL_REGISTRY_PATH
#define DOMINIUM_CONTROL_REGISTRY_PATH "data/registries/control_capabilities.registry"
#endif

static void print_version_banner(void)
{
    printf("engine_version=%s\n", DOMINO_VERSION_STRING);
    printf("game_version=%s\n", DOMINIUM_GAME_VERSION);
    printf("build_number=%u\n", (unsigned int)DOM_BUILD_NUMBER);
    printf("protocol_law_targets=LAW_TARGETS@1.4.0\n");
    printf("protocol_control_caps=CONTROL_CAPS@1.0.0\n");
}

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
    memset(&caps, 0, sizeof(caps));
    res = dom_control_caps_init(&caps, "ignored");
    EXPECT(res == DOM_CONTROL_ERR_DISABLED, "control hooks removed");
    EXPECT(dom_control_caps_count(&caps) == 0u, "removed hooks count");
    EXPECT(dom_control_caps_is_enabled(&caps, 1u) == 0, "removed hooks disabled");
    return 0;
}
