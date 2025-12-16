/*
FILE: source/domino/system/plat/windows/win32/dom_platform_sdl2.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / system/plat/windows/win32/dom_platform_sdl2
RESPONSIBILITY: Implements `dom_platform_sdl2`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include "dom_platform_sdl2.h"

/*
 * SDL2 backend is stubbed out for now to keep the MVP build minimal.
 * Functions return NOT_IMPLEMENTED so callers can fall back to Win32.
 */

dom_err_t dom_platform_sdl2_create_window(const char *title,
                                          dom_u32 width,
                                          dom_u32 height,
                                          dom_bool8 fullscreen,
                                          DomPlatformSDL2Window **out_win)
{
    (void)title;
    (void)width;
    (void)height;
    (void)fullscreen;
    (void)out_win;
    return DOM_ERR_NOT_IMPLEMENTED;
}

void dom_platform_sdl2_destroy_window(DomPlatformSDL2Window *win)
{
    (void)win;
}

void dom_platform_sdl2_pump_messages(DomPlatformSDL2Window *win)
{
    (void)win;
}

dom_bool8 dom_platform_sdl2_should_close(const DomPlatformSDL2Window *win)
{
    (void)win;
    return 1;
}

void *dom_platform_sdl2_native_handle(DomPlatformSDL2Window *win)
{
    (void)win;
    return 0;
}
