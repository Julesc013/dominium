/*
FILE: tools/validate/registry_dump_cli.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Tools / validate
RESPONSIBILITY: Dumps registry tables with deterministic ordering.
ALLOWED DEPENDENCIES: engine public headers + libs/contracts public headers.
FORBIDDEN DEPENDENCIES: game internal headers; GUI/TUI APIs.
DETERMINISM: Output ordering follows registry id order.
*/
#include "domino/registry.h"
#include "domino/version.h"
#include "dom_contracts/version.h"
#include "dom_contracts/_internal/dom_build_version.h"

#include <stdio.h>
#include <string.h>

static void print_version_banner(void)
{
    printf("engine_version=%s\n", DOMINO_VERSION_STRING);
    printf("game_version=%s\n", DOMINIUM_GAME_VERSION);
    printf("build_number=%u\n", (unsigned int)DOM_BUILD_NUMBER);
    printf("protocol_law_targets=LAW_TARGETS@1.4.0\n");
}

int main(int argc, char** argv)
{
    const char* registry_path = "data/registries/law_targets.registry";
    int i;
    dom_registry reg;
    dom_registry_result res;

    for (i = 1; i < argc; ++i) {
        if (strcmp(argv[i], "--registry") == 0 && i + 1 < argc) {
            registry_path = argv[i + 1];
            i += 1;
            continue;
        }
        if (strcmp(argv[i], "--help") == 0) {
            printf("Usage: registry_dump_cli [--registry path]\n");
            return 0;
        }
    }

    print_version_banner();
    res = dom_registry_load_file(registry_path, &reg);
    if (res != DOM_REGISTRY_OK) {
        fprintf(stderr, "registry_dump_cli: failed to load registry (%d)\n", (int)res);
        return 2;
    }

    printf("registry_path=%s\n", registry_path);
    printf("registry_count=%u\n", (unsigned int)dom_registry_count(&reg));
    printf("registry_hash=%u\n", (unsigned int)dom_registry_hash(&reg));
    for (i = 0; i < (int)reg.count; ++i) {
        printf("%u %s\n", (unsigned int)reg.entries[i].id, reg.entries[i].key);
    }

    dom_registry_free(&reg);
    return 0;
}
