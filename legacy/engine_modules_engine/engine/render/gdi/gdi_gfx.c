/*
FILE: source/domino/render/gdi/gdi_gfx.c
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
#include "gdi_gfx.h"

#include <stdbool.h>
#include <string.h>

gdi_state_t g_gdi;

static bool      gdi_init(const dgfx_desc *desc);
static void      gdi_shutdown(void);
static dgfx_caps gdi_get_caps(void);
static void      gdi_resize(int width, int height);
static void      gdi_begin_frame(void);
static void      gdi_execute(const dgfx_cmd_buffer *cmd);
static void      gdi_end_frame(void);

static const dgfx_backend_vtable g_gdi_vtable = {
    gdi_init,
    gdi_shutdown,
    gdi_get_caps,
    gdi_resize,
    gdi_begin_frame,
    gdi_execute,
    gdi_end_frame
};

static bool gdi_init(const dgfx_desc *desc)
{
    memset(&g_gdi, 0, sizeof(g_gdi));
    if (!desc) {
        return false;
    }

    g_gdi.native_window = desc->native_window;
    g_gdi.width = (desc->width > 0) ? desc->width : 640;
    g_gdi.height = (desc->height > 0) ? desc->height : 480;
    g_gdi.fullscreen = desc->fullscreen ? 1 : 0;

    memset(&g_gdi.caps, 0, sizeof(g_gdi.caps));
    g_gdi.caps.name = "gdi";
    g_gdi.caps.supports_2d = true;
    g_gdi.caps.supports_3d = false;
    g_gdi.caps.supports_text = false;
    g_gdi.frame_in_progress = 0;
    g_gdi.current_color_rgba = 0xffffffffu;

    return true;
}

static void gdi_shutdown(void)
{
    memset(&g_gdi, 0, sizeof(g_gdi));
}

static dgfx_caps gdi_get_caps(void)
{
    return g_gdi.caps;
}

static void gdi_resize(int width, int height)
{
    if (width > 0) g_gdi.width = width;
    if (height > 0) g_gdi.height = height;
}

static void gdi_begin_frame(void)
{
    g_gdi.frame_in_progress = 1;
}

static void gdi_execute(const dgfx_cmd_buffer *cmd)
{
    (void)cmd;
    /* Stub backend: no rendering performed. */
}

static void gdi_end_frame(void)
{
    g_gdi.frame_in_progress = 0;
}

const dgfx_backend_vtable *dgfx_gdi_get_vtable(void)
{
    return &g_gdi_vtable;
}
