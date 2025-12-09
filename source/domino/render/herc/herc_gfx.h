#ifndef DOMINIUM_HERC_GFX_H
#define DOMINIUM_HERC_GFX_H

#include <stdint.h>

#include "domino/gfx.h"
#include "domino/canvas.h"

#include "soft_config.h"
#include "soft_raster.h"

/* Hercules mode kind (v1: single mode) */
typedef enum herc_mode_kind_t {
    HERC_MODE_KIND_720x348_1 = 0  /* 720x348, 1bpp monochrome */
} herc_mode_kind;

/* Hercules mode info */
typedef struct herc_mode_info_t {
    herc_mode_kind kind;
    uint16_t       width;          /* 720 */
    uint16_t       height;         /* 348 */
    uint8_t        bits_per_pixel; /* 1 */
    uint8_t        reserved0;

    uint16_t       pitch_bytes;    /* bytes per scanline in VRAM (logical) */
    uint16_t       reserved1;

    uint16_t       vram_segment;   /* 0xB000 for Hercules graphics */
} herc_mode_info;

/* Hercules backend state */
typedef struct herc_state_t {
    dgfx_soft_config config;
    herc_mode_info   mode;
    soft_framebuffer fb;

    uint8_t* depth;
    uint8_t* stencil;

    int      width;
    int      height;

    int      frame_in_progress;

    dgfx_caps caps;

    /* IR / camera / viewport state */
    float    view[16];
    float    proj[16];
    float    world[16];

    int      vp_x, vp_y, vp_w, vp_h;
    int      camera2d_x;
    int      camera2d_y;

} herc_state_t;

extern herc_state_t g_herc;

const dgfx_backend_vtable* dgfx_herc_get_vtable(void);

#endif /* DOMINIUM_HERC_GFX_H */
