#ifndef DOM_PLATFORM_WIN32_H
#define DOM_PLATFORM_WIN32_H

/*
 * Minimal Win32 platform shell (window + message pump) for the MVP renderer.
 * No simulation or game logic here.
 */

#ifdef __cplusplus
extern "C" {
#endif

#include "dom_core_types.h"
#include "dom_core_err.h"

typedef struct DomPlatformWin32Window DomPlatformWin32Window;

typedef struct DomPlatformInputFrame {
    dom_bool8 key_down[256];
    dom_i32 mouse_x;
    dom_i32 mouse_y;
    dom_i32 mouse_dx;
    dom_i32 mouse_dy;
    dom_i32 wheel_delta;
} DomPlatformInputFrame;

dom_err_t dom_platform_win32_create_window(const char *title,
                                           dom_u32 width,
                                           dom_u32 height,
                                           dom_bool8 fullscreen,
                                           DomPlatformWin32Window **out_win);

void dom_platform_win32_destroy_window(DomPlatformWin32Window *win);

void dom_platform_win32_pump_messages(DomPlatformWin32Window *win);
dom_bool8 dom_platform_win32_should_close(const DomPlatformWin32Window *win);
void dom_platform_win32_get_size(const DomPlatformWin32Window *win,
                                 dom_u32 *width,
                                 dom_u32 *height);

/* Opaque native handle passed to render backends (HWND) */
void *dom_platform_win32_native_handle(DomPlatformWin32Window *win);

/* Input polling (keyboard/mouse) */
void dom_platform_win32_poll_input(DomPlatformWin32Window *win,
                                   DomPlatformInputFrame *out_frame);

/* Wallclock milliseconds for pacing (non-deterministic, allowed for timing only) */
dom_u64 dom_platform_win32_now_msec(void);
void    dom_platform_win32_sleep_msec(dom_u32 ms);

#ifdef __cplusplus
}
#endif

#endif /* DOM_PLATFORM_WIN32_H */
