/*
FILE: source/dominium/tools/world_edit/world_edit_core.c
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / tools/world_edit/world_edit_core
RESPONSIBILITY: Implements `world_edit_core`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/dominium/**`, `source/dominium/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: Dependency inversions that violate `docs/architecture/OVERVIEW_ARCHITECTURE.md` layering.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/specs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/specs/SPEC_*.md` without cross-layer coupling.
*/
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include "dominium/world_edit_api.h"
#include "domino/sys.h"

typedef struct dom_world_edit_ctx_t {
    char world_path[260];
    int dirty;
} dom_world_edit_ctx;

dom_world_edit_ctx *dom_world_edit_open(const dom_world_edit_desc *desc)
{
    dom_world_edit_ctx *ctx;
    const char *path = "data/worlds/default.world";
    if (desc && desc->world_path) {
        path = desc->world_path;
    }

    ctx = (dom_world_edit_ctx*)malloc(sizeof(dom_world_edit_ctx));
    if (!ctx) {
        return NULL;
    }
    memset(ctx, 0, sizeof(*ctx));
    strncpy(ctx->world_path, path, sizeof(ctx->world_path) - 1);
    ctx->world_path[sizeof(ctx->world_path) - 1] = '\0';
    ctx->dirty = 0;
    return ctx;
}

void dom_world_edit_close(dom_world_edit_ctx *ctx)
{
    if (!ctx) return;
    free(ctx);
}

int dom_world_edit_get_chunk(dom_world_edit_ctx *ctx,
                             int32_t sx, int32_t sy, int32_t sz,
                             dom_chunk_data *out)
{
    (void)sx; (void)sy; (void)sz;
    if (!ctx) return -1;
    if (out) {
        memset(out, 0, sizeof(*out));
    }
    return 0;
}

int dom_world_edit_set_chunk(dom_world_edit_ctx *ctx,
                             int32_t sx, int32_t sy, int32_t sz,
                             const dom_chunk_data *in)
{
    (void)sx; (void)sy; (void)sz; (void)in;
    if (!ctx) return -1;
    ctx->dirty = 1;
    return 0;
}

int dom_world_edit_save(dom_world_edit_ctx *ctx)
{
    void *f;
    const char suffix[] = ".editlog";
    char path[280];
    size_t len;
    if (!ctx) return -1;

    strncpy(path, ctx->world_path, sizeof(path) - 1);
    path[sizeof(path) - 1] = '\0';
    len = strlen(path);
    if (len + sizeof(suffix) < sizeof(path)) {
        strcat(path, suffix);
    }

    f = dsys_file_open(path, "ab");
    if (!f) {
        return -1;
    }
    dsys_file_write(f, "save\n", 5);
    dsys_file_close(f);
    ctx->dirty = 0;
    return 0;
}
