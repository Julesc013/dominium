/*
FILE: source/dominium/setup/cli/dominium_setup_cli.c
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / setup/cli/dominium_setup_cli
RESPONSIBILITY: Implements `dominium_setup_cli`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/dominium/**`, `source/dominium/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: Dependency inversions that violate `docs/OVERVIEW_ARCHITECTURE.md` layering.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include <stdio.h>
#include <string.h>

#include "domino/version.h"
#include "dominium/version.h"
#include "dominium_setup_core.h"
#include "dominium_setup_model.h"

static int dom_parse_kv(const char* arg, const char* key, char* out, size_t cap)
{
    size_t len;
    if (!arg || !key || !out || cap == 0) return 0;
    len = strlen(key);
    if (strncmp(arg, key, len) != 0) return 0;
    strncpy(out, arg + len, cap - 1);
    out[cap - 1] = '\0';
    return 1;
}

static void dom_setup_print_usage(void)
{
    printf("dominium_setup_cli commands:\n");
    printf("  list\n");
    printf("  install --product=<id> --version=<semver> [--root=<path>]\n");
}

static int dom_setup_cmd_list(void)
{
    dominium_installed_product products[16];
    unsigned int count = 0;
    unsigned int i;
    if (dominium_setup_list_installed(products, 16, &count) != 0) {
        printf("Failed to list installed products\n");
        return 1;
    }
    if (count == 0) {
        printf("No products found\n");
        return 0;
    }
    for (i = 0; i < count && i < 16; ++i) {
        printf("- %s %d.%d.%d (content_api=%d)\n",
               products[i].id,
               products[i].version.major,
               products[i].version.minor,
               products[i].version.patch,
               products[i].content_api);
    }
    return 0;
}

static int dom_setup_cmd_install(int argc, char** argv)
{
    dominium_setup_plan plan;
    char version_str[64];
    int i;

    memset(&plan, 0, sizeof(plan));
    plan.mode = DOMINIUM_SETUP_MODE_INSTALL;
    strncpy(plan.product_id, DOMINIUM_GAME_ID, sizeof(plan.product_id) - 1);
    dominium_game_get_version(&plan.product_version);
    version_str[0] = '\0';

    for (i = 2; i < argc; ++i) {
        dom_parse_kv(argv[i], "--product=", plan.product_id, sizeof(plan.product_id));
        dom_parse_kv(argv[i], "--root=", plan.install_root, sizeof(plan.install_root));
        if (dom_parse_kv(argv[i], "--version=", version_str, sizeof(version_str))) {
            domino_semver_parse(version_str, &plan.product_version);
        }
    }

    if (!plan.product_id[0]) {
        printf("Missing --product\n");
        return 1;
    }

    if (dominium_setup_execute(&plan) != 0) {
        printf("Install failed\n");
        return 1;
    }
    printf("Install stub completed for %s\n", plan.product_id);
    return 0;
}

int dominium_setup_cli_main(int argc, char** argv)
{
    if (argc < 2) {
        dom_setup_print_usage();
        return 0;
    }
    if (strcmp(argv[1], "list") == 0) {
        return dom_setup_cmd_list();
    }
    if (strcmp(argv[1], "install") == 0) {
        return dom_setup_cmd_install(argc, argv);
    }
    dom_setup_print_usage();
    return 1;
}
