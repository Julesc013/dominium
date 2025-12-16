/*
FILE: source/domino/render/null/d_gfx_null.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / render/null/d_gfx_null
RESPONSIBILITY: Implements `d_gfx_null`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include "d_gfx_null.h"

static int d_gfx_null_init(void)
{
    return 0;
}

static void d_gfx_null_shutdown(void)
{
}

static void d_gfx_null_submit(const d_gfx_cmd_buffer* buf)
{
    (void)buf;
}

static void d_gfx_null_present(void)
{
}

static d_gfx_backend_soft g_null_backend = {
    d_gfx_null_init,
    d_gfx_null_shutdown,
    d_gfx_null_submit,
    d_gfx_null_present
};

const d_gfx_backend_soft* d_gfx_null_register_backend(void)
{
    return &g_null_backend;
}

