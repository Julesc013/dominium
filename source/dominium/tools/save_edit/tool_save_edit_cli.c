/*
FILE: source/dominium/tools/save_edit/tool_save_edit_cli.c
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / tools/save_edit/tool_save_edit_cli
RESPONSIBILITY: Implements `tool_save_edit_cli`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
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
#include "dominium/tool_api.h"
#include "dominium/save_edit_api.h"
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
    printf("Usage: save_edit --save <path> [--list <section>] [--get <section> <key>] [--set <section> <key> <value>]\n");
}

int dom_tool_save_edit_main(dom_tool_ctx *ctx, int argc, char **argv)
{
    const char *save_path = NULL;
    const char *list_section = NULL;
    const char *get_section = NULL;
    const char *get_key = NULL;
    const char *set_section = NULL;
    const char *set_key = NULL;
    const char *set_value = NULL;
    int i;
    dom_save_edit_desc desc;
    dom_save_edit_ctx *sctx;

    for (i = 1; i < argc; ++i) {
        if (strcmp(argv[i], "--save") == 0 && i + 1 < argc) {
            save_path = argv[++i];
        } else if (strcmp(argv[i], "--list") == 0 && i + 1 < argc) {
            list_section = argv[++i];
        } else if (strcmp(argv[i], "--get") == 0 && i + 2 < argc) {
            get_section = argv[++i];
            get_key = argv[++i];
        } else if (strcmp(argv[i], "--set") == 0 && i + 3 < argc) {
            set_section = argv[++i];
            set_key = argv[++i];
            set_value = argv[++i];
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
    desc.save_path = save_path;

    sctx = dom_save_edit_open(&desc);
    if (!sctx) {
        tool_err(ctx, "Failed to open save\n");
        dsys_shutdown();
        return 1;
    }

    if (list_section) {
        char buf[1024];
        int n = dom_save_edit_list_keys(sctx, list_section, buf, sizeof(buf));
        if (n >= 0) {
            tool_log(ctx, buf);
        } else {
            tool_err(ctx, "List failed\n");
        }
    }

    if (get_section && get_key) {
        char buf[512];
        if (dom_save_edit_get_value(sctx, get_section, get_key, buf, sizeof(buf)) == 0) {
            tool_log(ctx, buf);
            tool_log(ctx, "\n");
        } else {
            tool_err(ctx, "Get failed\n");
        }
    }

    if (set_section && set_key && set_value) {
        if (dom_save_edit_set_value(sctx, set_section, set_key, set_value) == 0) {
            tool_log(ctx, "Value set\n");
            dom_save_edit_save(sctx);
        } else {
            tool_err(ctx, "Set failed\n");
        }
    }

    dom_save_edit_close(sctx);
    dsys_shutdown();
    return 0;
}
