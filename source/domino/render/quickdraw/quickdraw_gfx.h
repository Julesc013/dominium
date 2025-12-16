/*
FILE: source/domino/render/quickdraw/quickdraw_gfx.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / render/quickdraw/quickdraw_gfx
RESPONSIBILITY: Defines internal contract for `quickdraw_gfx`; shared within its subsystem; does NOT define a public API (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (internal header).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOMINIUM_QUICKDRAW_GFX_H
#define DOMINIUM_QUICKDRAW_GFX_H

#include <stdint.h>

#include "domino/gfx.h"
#include "domino/canvas.h"

/* Forward declarations from Mac OS headers; actual types defined in .c */
typedef struct WindowRecord* WindowPtr;
typedef struct CGrafPort*    CGrafPtr;
typedef struct GWorldRecord* GWorldPtr;

typedef struct quickdraw_state_t {
    void*     native_window;
    int       width;
    int       height;
    int       fullscreen;

    WindowPtr window;
    CGrafPtr  window_port;
    GWorldPtr offscreen_gworld;
    CGrafPtr  offscreen_port;

    int       depth;

    dgfx_caps caps;

    int       frame_in_progress;
} quickdraw_state_t;

extern quickdraw_state_t g_quickdraw;

const dgfx_backend_vtable* dgfx_quickdraw_get_vtable(void);

#endif /* DOMINIUM_QUICKDRAW_GFX_H */
