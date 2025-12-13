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

/* Soft framebuffer hook:
 * Called by soft backend to hand over framebuffer for presentation.
 */
int d_system_present_framebuffer(
    const void *pixels,
    i32         width,
    i32         height,
    i32         pitch_bytes
);

#ifdef __cplusplus
}
#endif

#endif /* D_SYSTEM_H */
