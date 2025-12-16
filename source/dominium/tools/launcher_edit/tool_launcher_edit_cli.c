/*
FILE: source/dominium/tools/launcher_edit/tool_launcher_edit_cli.c
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / tools/launcher_edit/tool_launcher_edit_cli
RESPONSIBILITY: Implements `tool_launcher_edit_cli`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
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
#include "dominium/tool_api.h"
#include "dominium/launcher_edit_api.h"
#include "domino/sys.h"

static void tool_log(dom_tool_ctx *ctx, const char *msg)
{
    if (ctx && ctx->env.write_stdout) {
        ctx->env.write_stdout(msg, ctx->env.io_user);
    } else {
        printf("%s", msg);
    }
}

static void tool_err(dom_tool_ctx *ctx, const char *msg)
{
    if (ctx && ctx->env.write_stderr) {
        ctx->env.write_stderr(msg, ctx->env.io_user);
    } else {
        fprintf(stderr, "%s", msg);
    }
}

static void usage(void)
{
    printf("Usage: launcher_edit --config <path> [--list] [--add <view_id> <title> <index>] [--remove <view_id>]\n");
}

int dom_tool_launcher_edit_main(dom_tool_ctx *ctx, int argc, char **argv)
{
    const char *config = NULL;
    int list = 0;
    const char *add_view = NULL;
    const char *add_title = NULL;
    uint32_t add_index = 0;
    const char *remove_view = NULL;
    int i;
    dom_launcher_edit_desc desc;
    dom_launcher_edit_ctx *lctx;

    for (i = 1; i < argc; ++i) {
        if (strcmp(argv[i], "--config") == 0 && i + 1 < argc) {
            config = argv[++i];
        } else if (strcmp(argv[i], "--list") == 0) {
            list = 1;
        } else if (strcmp(argv[i], "--add") == 0 && i + 3 < argc) {
            add_view = argv[++i];
            add_title = argv[++i];
            add_index = (uint32_t)atoi(argv[++i]);
        } else if (strcmp(argv[i], "--remove") == 0 && i + 1 < argc) {
            remove_view = argv[++i];
        } else {
            usage();
            return 1;
        }
    }

    if (dsys_init() != DSYS_OK) {
        tool_err(ctx, "Failed to initialize dsys\n");
        return 1;
    }

    desc.struct_size = sizeof(desc);
    desc.struct_version = 1;
    desc.config_path = config;

    lctx = dom_launcher_edit_open(&desc);
    if (!lctx) {
        tool_err(ctx, "Failed to open launcher config\n");
        dsys_shutdown();
        return 1;
    }

    if (list) {
        char buf[1024];
        int n = dom_launcher_edit_list_tabs(lctx, buf, sizeof(buf));
        if (n >= 0) {
            tool_log(ctx, buf);
        } else {
            tool_err(ctx, "List failed\n");
        }
    }

    if (add_view && add_title) {
        if (dom_launcher_edit_add_tab(lctx, add_view, add_title, add_index) == 0) {
            tool_log(ctx, "Tab added\n");
            dom_launcher_edit_save(lctx);
        } else {
            tool_err(ctx, "Add failed\n");
        }
    }

    if (remove_view) {
        if (dom_launcher_edit_remove_tab(lctx, remove_view) == 0) {
            tool_log(ctx, "Tab removed\n");
            dom_launcher_edit_save(lctx);
        } else {
            tool_err(ctx, "Remove failed\n");
        }
    }

    dom_launcher_edit_close(lctx);
    dsys_shutdown();
    return 0;
}
