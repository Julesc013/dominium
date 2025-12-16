/*
FILE: tests/domino_gfx/test_gfx_soft.c
MODULE: Repository
LAYER / SUBSYSTEM: tests/domino_gfx
RESPONSIBILITY: Owns documentation for this translation unit.
ALLOWED DEPENDENCIES: Project-local headers; C89/C++98 standard headers.
FORBIDDEN DEPENDENCIES: N/A.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A.
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include "domino/sys.h"
#include "domino/gfx.h"
#include <string.h>

int main(void)
{
    domino_sys_context* sys = NULL;
    domino_sys_desc sdesc;
    domino_gfx_desc gdesc;
    domino_gfx_device* dev = NULL;

    sdesc.profile_hint = DOMINO_SYS_PROFILE_AUTO;
    if (domino_sys_init(&sdesc, &sys) != 0 || !sys) {
        return 1;
    }

    memset(&gdesc, 0, sizeof(gdesc));
    gdesc.backend = DOMINO_GFX_BACKEND_SOFT;
    gdesc.profile_hint = DOMINO_GFX_PROFILE_FIXED;
    gdesc.width = 320;
    gdesc.height = 200;
    gdesc.fullscreen = 0;
    gdesc.vsync = 0;
    gdesc.framebuffer_fmt = DOMINO_PIXFMT_A8R8G8B8;

    if (domino_gfx_create_device(sys, &gdesc, &dev) != 0 || !dev) {
        domino_sys_shutdown(sys);
        return 1;
    }

    domino_gfx_begin_frame(dev);
    domino_gfx_clear(dev, 0.1f, 0.2f, 0.3f, 1.0f);
    {
        domino_gfx_rect rect;
        rect.x = 10.0f;
        rect.y = 10.0f;
        rect.w = 50.0f;
        rect.h = 40.0f;
        domino_gfx_draw_filled_rect(dev, &rect, 1.0f, 0.0f, 0.0f, 1.0f);
    }
    domino_gfx_end_frame(dev);

    domino_gfx_destroy_device(dev);
    domino_sys_shutdown(sys);
    return 0;
}
