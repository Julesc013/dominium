/*
FILE: source/domino/mod/host/mod_stub.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / mod/host/mod_stub
RESPONSIBILITY: Implements `mod_stub`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include "domino/mod.h"
#include <stdlib.h>

dm_mod_context* dm_mod_create(void)
{
    dm_mod_context* ctx = (dm_mod_context*)malloc(sizeof(dm_mod_context));
    if (!ctx) return NULL;
    ctx->placeholder = 0;
    return ctx;
}

void dm_mod_destroy(dm_mod_context* ctx)
{
    if (ctx) free(ctx);
}
