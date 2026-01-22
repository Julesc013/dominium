/*
FILE: source/domino/system/d_system.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / system/d_system
RESPONSIBILITY: Defines internal contract for `d_system`; shared within its subsystem; does NOT define a public API (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (internal header).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
/* Minimal Domino system wrapper (C89). */
#ifndef D_SYSTEM_H
#define D_SYSTEM_H

#include "domino/core/types.h"

#ifdef __cplusplus
extern "C" {
#endif

/* Initialize system layer with backend key, e.g. "sdl2", "win32", etc. */
int d_system_init(const char *backend_name);
void d_system_shutdown(void);

/* Process step: pump events, etc. Returns 0 if OK, non-zero to request exit. */
int d_system_pump_events(void);

/* Simple sleep/yield in milliseconds. */
void d_system_sleep_ms(u32 ms);

/* Process spawn API used by launcher. Stub OK for now. */
int d_system_process_spawn(const char *path, const char *args);

/* Returns a native window handle for the current platform (e.g. HWND on Win32),
 * or NULL when no window exists (e.g. headless).
 */
void* d_system_get_native_window_handle(void);
void d_system_set_native_window_handle(void* handle);

/* Soft framebuffer hook:
 * Called by soft backend to hand over framebuffer for presentation.
 * native_window may be NULL to use the current platform handle.
 */
int d_system_present_framebuffer(
    void*       native_window,
    const void *pixels,
    i32         width,
    i32         height,
    i32         pitch_bytes
);

#ifdef __cplusplus
}
#endif

#endif /* D_SYSTEM_H */
