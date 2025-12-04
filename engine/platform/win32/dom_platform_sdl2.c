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
