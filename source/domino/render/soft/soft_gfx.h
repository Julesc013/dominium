#ifndef DOMINIUM_SOFT_GFX_H
#define DOMINIUM_SOFT_GFX_H

#include <stdint.h>

#include "domino/gfx.h"
#include "domino/canvas.h"

#include "soft_config.h"

/* Software framebuffer */
typedef struct soft_framebuffer_t {
    uint8_t* color;         /* color buffer (8,16,32 bpp) */
    uint8_t* depth;         /* optional depth buffer (16/24/32 bits as packed/normalized) */
    uint8_t* stencil;       /* optional stencil buffer (8 bits) */

    int       width;
    int       height;
    int       stride_bytes;  /* bytes per color row */
    int       depth_stride;  /* bytes per depth row */
    int       stencil_stride;

    dgfx_soft_format format;
    uint8_t  depth_bits;
    uint8_t  stencil_bits;
    uint8_t  pad[2];

} soft_framebuffer;

/* Backend state */
typedef struct soft_state_t {
    void*    native_window;   /* dsys/native handle: HWND, WindowPtr, X11 Window, etc. */

    int       width;
    int       height;
    int       fullscreen;      /* hint */

    dgfx_soft_config config;
    soft_framebuffer fb;

    dgfx_caps caps;
    int       frame_in_progress;

    /* Mixed 2D/3D view state */
    float     view[16];
    float     proj[16];
    float     world[16];

    /* 2D camera (HUD) offset */
    int       camera2d_x;
    int       camera2d_y;

    /* Viewport for current draw commands */
    int       vp_x, vp_y;
    int       vp_w, vp_h;

} soft_state_t;

extern soft_state_t g_soft;

const dgfx_backend_vtable* dgfx_soft_get_vtable(void);

#endif /* DOMINIUM_SOFT_GFX_H */
