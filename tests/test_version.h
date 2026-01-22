/*
Shared version banner for tests.
*/
#ifndef DOMINIUM_TEST_VERSION_H
#define DOMINIUM_TEST_VERSION_H

#include "domino/version.h"
#include "dom_contracts/version.h"
#include "dom_contracts/_internal/dom_build_version.h"

#include <stdio.h>

static void print_version_banner(void)
{
    printf("engine_version=%s\n", DOMINO_VERSION_STRING);
    printf("game_version=%s\n", DOMINIUM_GAME_VERSION);
    printf("build_number=%u\n", (unsigned int)DOM_BUILD_NUMBER);
    printf("protocol_law_targets=LAW_TARGETS@1.4.0\n");
    printf("protocol_control_caps=CONTROL_CAPS@1.0.0\n");
    printf("protocol_authority_tokens=AUTHORITY_TOKEN@1.0.0\n");
}

#endif /* DOMINIUM_TEST_VERSION_H */
