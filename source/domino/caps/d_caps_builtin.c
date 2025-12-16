/*
FILE: source/domino/caps/d_caps_builtin.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / caps/d_caps_builtin
RESPONSIBILITY: Implements `d_caps_builtin`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include "domino/caps.h"

static u32 g_caps_builtins_registered = 0u;

dom_caps_result dom_dsys_register_caps_backends(void);
dom_caps_result dom_dgfx_register_caps_backends(void);

dom_caps_result dom_caps_register_builtin_backends(void)
{
    dom_caps_result r;

    if (g_caps_builtins_registered) {
        return DOM_CAPS_OK;
    }

    r = dom_dsys_register_caps_backends();
    if (r != DOM_CAPS_OK) {
        return r;
    }
    r = dom_dgfx_register_caps_backends();
    if (r != DOM_CAPS_OK) {
        return r;
    }

    g_caps_builtins_registered = 1u;
    return DOM_CAPS_OK;
}

