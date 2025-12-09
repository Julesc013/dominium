#ifndef DOMINIUM_VGA_GFX_H
#define DOMINIUM_VGA_GFX_H

#include <stddef.h>
#include <stdint.h>

#include "domino/gfx.h"
#include "domino/canvas.h"

#include "soft_config.h"
#include "soft_raster.h"

/* VGA modes supported (v1: mode 13h only) */
typedef enum vga_mode_kind_t {
    VGA_MODE_KIND_13H = 0
} vga_mode_kind;

/* VGA mode description */
typedef struct vga_mode_info_t {
    vga_mode_kind kind;
    uint16_t      width;
    uint16_t      height;
    uint8_t       bpp;          /* 8 for mode 13h */
    uint8_t       reserved0[3];

    uint32_t      vram_phys;    /* optional physical base */
    uint16_t      vram_segment; /* real-mode segment (0xA000) */
    uint16_t      pitch_bytes;  /* bytes per scanline, 320 for 13h */
} vga_mode_info;

/* VGA backend state */
typedef struct vga_state_t {
    dgfx_soft_config config;
    vga_mode_info    mode;

    /* System RAM framebuffer (blitted to VRAM each frame) */
    soft_framebuffer fb;

    /* Optional depth/stencil buffers in system RAM */
    uint8_t *depth;
    uint8_t *stencil;

    /* Optional direct VRAM pointer when available */
    uint8_t *vram_ptr;

    int      width;
    int      height;

    int      frame_in_progress;

    dgfx_caps caps;

    /* Command/IR state */
    float    view[16];
    float    proj[16];
    float    world[16];

    int      vp_x, vp_y, vp_w, vp_h;
    int      camera2d_x;
    int      camera2d_y;

} vga_state_t;

extern vga_state_t g_vga;

const dgfx_backend_vtable *dgfx_vga_get_vtable(void);

#endif /* DOMINIUM_VGA_GFX_H */
