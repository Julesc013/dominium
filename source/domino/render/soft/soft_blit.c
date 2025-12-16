/*
FILE: source/domino/render/soft/soft_blit.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / render/soft/soft_blit
RESPONSIBILITY: Implements `soft_blit`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include "soft_blit.h"

static soft_present_fn g_soft_present = (soft_present_fn)0;

void soft_blit_set_present_callback(soft_present_fn fn)
{
    g_soft_present = fn;
}

soft_present_fn soft_blit_get_present_callback(void)
{
    return g_soft_present;
}
