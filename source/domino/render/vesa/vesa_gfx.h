#ifndef DOMINIUM_VESA_GFX_H
#define DOMINIUM_VESA_GFX_H

#include <stdint.h>
#include <stddef.h>

#include "domino/gfx.h"
#include "domino/canvas.h"

#include "soft_config.h"
#include "soft_raster.h"

/* VESA mode info we care about */
typedef struct vesa_mode_info_t {
    uint16_t mode;      /* VBE mode number */
    uint16_t width;
    uint16_t height;
    uint8_t  bpp;       /* bits per pixel: 8, 16, 24, 32 */
    uint8_t  has_linear;/* linear framebuffer supported */
    uint8_t  reserved[2];

    uint32_t phys_base; /* physical address of LFB */
    uint16_t pitch;     /* bytes per scanline */
} vesa_mode_info;

/* Full VESA backend state */
typedef struct vesa_state_t {
    /* Core config (reused from software backend) */
    dgfx_soft_config config;

    /* Mode info */
    vesa_mode_info   mode;

    /* Soft framebuffer view into VRAM */
    soft_framebuffer fb;

    /* Depth/stencil buffers in system RAM */
    uint8_t* depth;
    uint8_t* stencil;

    int      width;
    int      height;

    int      frame_in_progress;

    dgfx_caps caps;

    /* Command-space state */
    float    view[16];
    float    proj[16];
    float    world[16];

    int      vp_x;
    int      vp_y;
    int      vp_w;
    int      vp_h;      /* viewport */
    int      camera2d_x;
    int      camera2d_y;

} vesa_state_t;

extern vesa_state_t g_vesa;

const dgfx_backend_vtable* dgfx_vesa_get_vtable(void);

#endif /* DOMINIUM_VESA_GFX_H */
