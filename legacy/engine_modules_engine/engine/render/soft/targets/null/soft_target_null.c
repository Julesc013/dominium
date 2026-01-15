/*
FILE: source/domino/render/soft/targets/null/soft_target_null.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / render/soft/targets/null/soft_target_null
RESPONSIBILITY: Implements `soft_target_null`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include "../../soft_internal.h"

static int null_init(domino_sys_context* sys, int width, int height, domino_pixfmt fmt, void** out_state)
{
    (void)sys; (void)width; (void)height; (void)fmt; (void)out_state;
    return 0;
}

static void null_shutdown(void* state)
{
    (void)state;
}

static int null_present(void* state, const void* pixels, int width, int height, int stride_bytes)
{
    (void)state; (void)pixels; (void)width; (void)height; (void)stride_bytes;
    return 0;
}

static const domino_soft_target_ops g_null_target = {
    "null",
    null_init,
    null_shutdown,
    null_present
};

const domino_soft_target_ops* domino_soft_target_null(void)
{
    return &g_null_target;
}
