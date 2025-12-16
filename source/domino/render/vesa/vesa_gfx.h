/*
FILE: source/domino/render/vesa/vesa_gfx.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / render/vesa/vesa_gfx
RESPONSIBILITY: Implements `vesa_gfx`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
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
