#ifndef DOM_PLATFORM_SDL2_H
#define DOM_PLATFORM_SDL2_H

#include "dom_core_types.h"
#include "dom_core_err.h"

/*
 * SDL2-based platform stub for Windows (build-time selectable).
 * This MVP implementation returns NOT_IMPLEMENTED unless SDL2
 * support is added later.
 */

#ifdef __cplusplus
extern "C" {
#endif

typedef struct DomPlatformSDL2Window DomPlatformSDL2Window;

dom_err_t dom_platform_sdl2_create_window(const char *title,
                                          dom_u32 width,
                                          dom_u32 height,
                                          dom_bool8 fullscreen,
                                          DomPlatformSDL2Window **out_win);

void dom_platform_sdl2_destroy_window(DomPlatformSDL2Window *win);
void dom_platform_sdl2_pump_messages(DomPlatformSDL2Window *win);
dom_bool8 dom_platform_sdl2_should_close(const DomPlatformSDL2Window *win);
void *dom_platform_sdl2_native_handle(DomPlatformSDL2Window *win);

#ifdef __cplusplus
}
#endif

#endif /* DOM_PLATFORM_SDL2_H */
