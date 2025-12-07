#ifndef DOM_PLATFORM_H
#define DOM_PLATFORM_H

/*
 * Canonical platform backend selector.
 * Each enum value maps to a single implementation subtree under /src/platform.
 *
 * DOM_PLATFORM is chosen at build time (CMake cache) and must be consistent
 * across engine/game/tools for a given build.
 */

#ifdef __cplusplus
extern "C" {
#endif

typedef enum dom_platform_e {
    DOM_PLATFORM_WIN32 = 0,      /* /src/platform/win32/ */
    DOM_PLATFORM_MACOSX,         /* /src/platform/cocoa/ */
    DOM_PLATFORM_POSIX_HEADLESS, /* /src/platform/shared/posix_headless/ */
    DOM_PLATFORM_POSIX_X11,      /* /src/platform/x11/ */
    DOM_PLATFORM_POSIX_WAYLAND,  /* /src/platform/wayland/ */
    DOM_PLATFORM_SDL1,           /* /src/platform/sdl1/ */
    DOM_PLATFORM_SDL2            /* /src/platform/sdl2/ */
} dom_platform;

#ifdef __cplusplus
}
#endif

#endif /* DOM_PLATFORM_H */
