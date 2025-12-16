/*
FILE: source/dominium/launcher/cli/launch_cli.c
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / launcher/cli/launch_cli
RESPONSIBILITY: Implements `launch_cli`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
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
#include <stdlib.h>

#include "domino/core.h"
#include "domino/sys.h"
#include "domino/view.h"
#include "domino/model_table.h"
#include "dominium/launch_api.h"

static void trim_newline(char* s)
{
    size_t len;
    if (!s) return;
    len = strlen(s);
    while (len > 0 && (s[len - 1] == '\n' || s[len - 1] == '\r')) {
        s[len - 1] = '\0';
        len -= 1;
    }
}

static int starts_with(const char* s, const char* prefix)
{
    size_t n;
    if (!s || !prefix) return 0;
    n = strlen(prefix);
    if (strncmp(s, prefix, n) != 0) {
        return 0;
    }
    if (s[n] == '\0' || s[n] == ' ') {
        return 1;
    }
    return 0;
}

static void print_table(dom_core* core, const char* table_id)
{
    dom_table_meta meta;
    uint32_t row;
    uint32_t col;
    char cell[256];

    if (!dom_table_get_meta(core, table_id, &meta)) {
        printf("Failed to read table '%s'\n", table_id ? table_id : "(null)");
        return;
    }

    for (col = 0u; col < meta.col_count; ++col) {
        printf("%s%s", meta.col_ids[col], (col + 1u == meta.col_count) ? "" : "\t");
    }
    printf("\n");

    for (row = 0u; row < meta.row_count; ++row) {
        for (col = 0u; col < meta.col_count; ++col) {
            memset(cell, 0, sizeof(cell));
            if (!dom_table_get_cell(core, table_id, row, col, cell, sizeof(cell))) {
                strcpy(cell, "-");
            }
            printf("%s%s", cell, (col + 1u == meta.col_count) ? "" : "\t");
        }
        printf("\n");
    }
}

static void print_help(void)
{
    printf("Commands:\n");
    printf("  help                 Show this help\n");
    printf("  list instances       List registered instances\n");
    printf("  create instance <name>\n");
    printf("                       Create a new instance\n");
    printf("  delete instance <id> Delete an instance by id\n");
    printf("  launch <id>          Launch instance by id\n");
    printf("  list packages        List installed packages\n");
    printf("  quit                 Exit launcher\n");
}

int main(int argc, char** argv)
{
    dsys_result     dres;
    dom_core_desc   core_desc;
    dom_core*       core;
    dom_launch_desc ldesc;
    dom_launch_ctx* ctx;
    char            line[512];
    int             running;

    (void)argc;
    (void)argv;

    dres = dsys_init();
    if (dres != DSYS_OK) {
        fprintf(stderr, "dsys_init failed (%d)\n", (int)dres);
        return 1;
    }

    memset(&core_desc, 0, sizeof(core_desc));
    core_desc.api_version = 1;
    core = dom_core_create(&core_desc);
    if (!core) {
        fprintf(stderr, "Failed to create dom_core\n");
        dsys_shutdown();
        return 1;
    }

    memset(&ldesc, 0, sizeof(ldesc));
    ldesc.struct_size = sizeof(ldesc);
    ldesc.struct_version = 1;
    ldesc.core = core;
    ldesc.ui_mode = DOM_UI_MODE_CLI;
    ldesc.product_id = "dominium";
    ldesc.version = "0.1.0";
    ctx = dom_launch_create(&ldesc);
    if (!ctx) {
        fprintf(stderr, "Failed to create launcher context\n");
        dom_core_destroy(core);
        dsys_shutdown();
        return 1;
    }

    printf("Dominium CLI launcher. Type 'help' for commands.\n");
    running = 1;
    while (running) {
        printf("dominium> ");
        fflush(stdout);
        if (!fgets(line, sizeof(line), stdin)) {
            break;
        }
        trim_newline(line);
        if (line[0] == '\0') {
            continue;
        }

        if (strcmp(line, "help") == 0) {
            print_help();
            continue;
        }

        if (starts_with(line, "list instances")) {
            dom_launch_handle_action(ctx, DOM_LAUNCH_ACTION_LIST_INSTANCES, 0u, NULL);
            print_table(core, "instances_table");
            continue;
        }

        if (starts_with(line, "list packages")) {
            dom_launch_handle_action(ctx, DOM_LAUNCH_ACTION_LIST_PACKAGES, 0u, NULL);
            print_table(core, "packages_table");
            continue;
        }

        if (starts_with(line, "create instance")) {
            const char* name = line + strlen("create instance");
            while (*name == ' ') {
                name += 1;
            }
            dom_launch_handle_action(ctx, DOM_LAUNCH_ACTION_CREATE_INSTANCE, 0u, name);
            dom_launch_handle_action(ctx, DOM_LAUNCH_ACTION_LIST_INSTANCES, 0u, NULL);
            print_table(core, "instances_table");
            continue;
        }

        if (starts_with(line, "delete instance")) {
            const char* arg = line + strlen("delete instance");
            unsigned long id = 0ul;
            while (*arg == ' ') {
                arg += 1;
            }
            if (*arg != '\0') {
                id = strtoul(arg, NULL, 10);
                dom_launch_handle_action(ctx, DOM_LAUNCH_ACTION_DELETE_INSTANCE, (uint32_t)id, NULL);
            } else {
                printf("Usage: delete instance <id>\n");
            }
            continue;
        }

        if (starts_with(line, "launch")) {
            const char* arg = line + strlen("launch");
            unsigned long id = 0ul;
            while (*arg == ' ') {
                arg += 1;
            }
            if (*arg != '\0') {
                id = strtoul(arg, NULL, 10);
                dom_launch_handle_action(ctx, DOM_LAUNCH_ACTION_LAUNCH_INSTANCE, (uint32_t)id, NULL);
            } else {
                printf("Usage: launch <id>\n");
            }
            continue;
        }

        if (strcmp(line, "quit") == 0 || strcmp(line, "exit") == 0) {
            dom_launch_handle_action(ctx, DOM_LAUNCH_ACTION_QUIT, 0u, NULL);
            running = 0;
            continue;
        }

        printf("Unknown command. Type 'help' for a list of commands.\n");
    }

    dom_launch_destroy(ctx);
    dom_core_destroy(core);
    dsys_shutdown();
    return 0;
}
