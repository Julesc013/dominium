#ifndef D_GFX_SOFT_H
#define D_GFX_SOFT_H

#include "domino/gfx.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct d_gfx_backend_soft_s {
    int  (*init)(void);
    void (*shutdown)(void);
    void (*submit_cmd_buffer)(const d_gfx_cmd_buffer *buf);
    void (*present)(void);
} d_gfx_backend_soft;

/* Registration for dispatcher */
const d_gfx_backend_soft *d_gfx_soft_register_backend(void);
void d_gfx_soft_set_framebuffer_size(i32 w, i32 h);

#ifdef __cplusplus
}
#endif

#endif /* D_GFX_SOFT_H */
