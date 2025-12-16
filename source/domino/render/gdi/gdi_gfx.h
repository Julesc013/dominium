/*
FILE: source/domino/render/gdi/gdi_gfx.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / render/gdi/gdi_gfx
RESPONSIBILITY: Implements `gdi_gfx`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOMINIUM_GDI_GFX_H
#define DOMINIUM_GDI_GFX_H

#include <stdint.h>

#include "domino/gfx.h"
#include "domino/canvas.h"

/* Forward-declare Windows types without pulling windows.h into headers */
typedef struct HWND__ *HWND;
typedef struct HDC__  *HDC;
typedef struct HBITMAP__ *HBITMAP;

/* GDI renderer state */
typedef struct gdi_state_t {
    void     *native_window;   /* from dgfx_desc; maps to HWND from dsys_win32/win16 */

    int       width;
    int       height;
    int       fullscreen;

    /* Window + DC */
    HWND      hwnd;              /* target window */
    HDC       hwnd_dc;           /* window DC (GetDC(hwnd)) */

    /* Offscreen framebuffer */
    HDC       mem_dc;            /* memory DC */
    HBITMAP   dib_bitmap;        /* DIB section bitmap */
    void     *dib_bits;          /* pointer to pixel data */
    int       dib_pitch;         /* bytes per scanline */
    int       dib_bpp;           /* bits per pixel, e.g. 32 */

    dgfx_caps caps;
    int       frame_in_progress;

    /* Simple 2D camera (pixel offsets) */
    int       camera_offset_x;
    int       camera_offset_y;

    /* Optional: current pen/brush color cache for simple pipelines */
    uint32_t  current_color_rgba;

} gdi_state_t;

extern gdi_state_t g_gdi;

const dgfx_backend_vtable *dgfx_gdi_get_vtable(void);

#endif /* DOMINIUM_GDI_GFX_H */
