/*
FILE: source/domino/system/plat/windows/win32/dom_platform_sdl2.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / system/plat/windows/win32/dom_platform_sdl2
RESPONSIBILITY: Defines internal contract for `dom_platform_sdl2`; shared within its subsystem; does NOT define a public API (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (internal header).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
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
