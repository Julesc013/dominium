/*
FILE: tools/validate/hygiene_validate_cli.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Tools / validate
RESPONSIBILITY: Validates registry files for format and determinism.
ALLOWED DEPENDENCIES: engine public headers + libs/contracts public headers.
FORBIDDEN DEPENDENCIES: game internal headers; GUI/TUI APIs.
DETERMINISM: Validation results are deterministic.
*/
#include "domino/registry.h"
#include "domino/version.h"
#include "dom_contracts/version.h"
#include "dom_contracts/_internal/dom_build_version.h"

#include <stdio.h>
#include <stdlib.h>
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
    u32 expect_hash = 0u;
    u32 expect_count = 0u;
    int i;
    dom_registry reg;
    dom_registry_result res;

    for (i = 1; i < argc; ++i) {
        if (strcmp(argv[i], "--registry") == 0 && i + 1 < argc) {
            registry_path = argv[i + 1];
            i += 1;
            continue;
        }
        if (strcmp(argv[i], "--expect-hash") == 0 && i + 1 < argc) {
            expect_hash = (u32)strtoul(argv[i + 1], (char**)0, 10);
            i += 1;
            continue;
        }
        if (strcmp(argv[i], "--expect-count") == 0 && i + 1 < argc) {
            expect_count = (u32)strtoul(argv[i + 1], (char**)0, 10);
            i += 1;
            continue;
        }
        if (strcmp(argv[i], "--help") == 0) {
            printf("Usage: hygiene_validate_cli [--registry path] [--expect-hash n] [--expect-count n]\n");
            return 0;
        }
    }

    print_version_banner();
    res = dom_registry_load_file(registry_path, &reg);
    if (res != DOM_REGISTRY_OK) {
        fprintf(stderr, "hygiene_validate_cli: failed to load registry (%d)\n", (int)res);
        return 2;
    }

    printf("registry_path=%s\n", registry_path);
    printf("registry_count=%u\n", (unsigned int)dom_registry_count(&reg));
    printf("registry_hash=%u\n", (unsigned int)dom_registry_hash(&reg));

    if (expect_count && dom_registry_count(&reg) != expect_count) {
        fprintf(stderr, "hygiene_validate_cli: count mismatch (expected %u)\n", (unsigned int)expect_count);
        dom_registry_free(&reg);
        return 2;
    }
    if (expect_hash && dom_registry_hash(&reg) != expect_hash) {
        fprintf(stderr, "hygiene_validate_cli: hash mismatch (expected %u)\n", (unsigned int)expect_hash);
        dom_registry_free(&reg);
        return 2;
    }

    dom_registry_free(&reg);
    return 0;
}
