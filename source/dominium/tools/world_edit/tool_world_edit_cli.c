/*
FILE: source/dominium/tools/world_edit/tool_world_edit_cli.c
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / tools/world_edit/tool_world_edit_cli
RESPONSIBILITY: Implements `tool_world_edit_cli`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
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
#include <stdint.h>
#include "dominium/tool_api.h"
#include "dominium/world_edit_api.h"
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
    printf("Usage: world_edit --world <path> [--get-chunk sx sy sz] [--set-chunk sx sy sz]\n");
}

int dom_tool_world_edit_main(dom_tool_ctx *ctx, int argc, char **argv)
{
    const char *world_path = NULL;
    int get_chunk = 0;
    int set_chunk = 0;
    int32_t gx = 0, gy = 0, gz = 0;
    int32_t sx = 0, sy = 0, sz = 0;
    int i;
    dom_world_edit_desc desc;
    dom_world_edit_ctx *wctx;

    for (i = 1; i < argc; ++i) {
        if ((strcmp(argv[i], "--world") == 0 || strcmp(argv[i], "--file") == 0) && i + 1 < argc) {
            world_path = argv[++i];
        } else if (strcmp(argv[i], "--get-chunk") == 0 && i + 3 < argc) {
            get_chunk = 1;
            gx = (int32_t)atoi(argv[++i]);
            gy = (int32_t)atoi(argv[++i]);
            gz = (int32_t)atoi(argv[++i]);
        } else if (strcmp(argv[i], "--set-chunk") == 0 && i + 3 < argc) {
            set_chunk = 1;
            sx = (int32_t)atoi(argv[++i]);
            sy = (int32_t)atoi(argv[++i]);
            sz = (int32_t)atoi(argv[++i]);
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
    desc.world_path = world_path;

    wctx = dom_world_edit_open(&desc);
    if (!wctx) {
        tool_err(ctx, "Failed to open world\n");
        dsys_shutdown();
        return 1;
    }

    tool_log(ctx, "World editor backend ready\n");

    if (get_chunk) {
        dom_chunk_data chunk;
        if (dom_world_edit_get_chunk(wctx, gx, gy, gz, &chunk) == 0) {
            tool_log(ctx, "Chunk read OK\n");
        } else {
            tool_err(ctx, "Chunk read failed\n");
        }
    }

    if (set_chunk) {
        if (dom_world_edit_set_chunk(wctx, sx, sy, sz, NULL) == 0) {
            tool_log(ctx, "Chunk write flagged\n");
        } else {
            tool_err(ctx, "Chunk write failed\n");
        }
    }

    dom_world_edit_save(wctx);
    dom_world_edit_close(wctx);
    dsys_shutdown();
    return 0;
}
