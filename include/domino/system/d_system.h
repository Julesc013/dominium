/* Minimal Domino system wrapper (C89). */
#ifndef D_SYSTEM_H
#define D_SYSTEM_H

#include "domino/core/types.h"

#ifdef __cplusplus
extern "C" {
#endif

int d_system_init(const char *backend_name);
void d_system_shutdown(void);
int  d_system_pump_events(void);
void d_system_sleep_ms(u32 ms);
int  d_system_process_spawn(const char *path, const char *args);

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
