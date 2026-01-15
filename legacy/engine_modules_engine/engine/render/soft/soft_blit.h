/*
FILE: source/domino/render/soft/soft_blit.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / render/soft/soft_blit
RESPONSIBILITY: Defines internal contract for `soft_blit`; shared within its subsystem; does NOT define a public API (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (internal header).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOMINIUM_SOFT_BLIT_H
#define DOMINIUM_SOFT_BLIT_H

#include "soft_gfx.h"

typedef void (*soft_present_fn)(
    void* native_window,
    const soft_framebuffer* fb
);

/* Must be set up by platform integration code at startup */
void soft_blit_set_present_callback(soft_present_fn fn);
soft_present_fn soft_blit_get_present_callback(void);

#endif /* DOMINIUM_SOFT_BLIT_H */
