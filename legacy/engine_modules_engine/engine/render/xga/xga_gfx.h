/*
FILE: source/domino/render/xga/xga_gfx.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / render/xga/xga_gfx
RESPONSIBILITY: Defines internal contract for `xga_gfx`; shared within its subsystem; does NOT define a public API (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (internal header).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOMINIUM_XGA_GFX_H
#define DOMINIUM_XGA_GFX_H

#include <stddef.h>
#include <stdint.h>

#include "domino/gfx.h"
#include "domino/canvas.h"

#include "soft_config.h"
#include "soft_raster.h"

/* Supported XGA mode kinds. Expandable later. */
typedef enum xga_mode_kind_t {
    XGA_MODE_KIND_640x480_8 = 0,
    XGA_MODE_KIND_800x600_8,
    XGA_MODE_KIND_1024x768_8
} xga_mode_kind;

/* XGA mode info (logical description) */
typedef struct xga_mode_info_t {
    xga_mode_kind kind;
    uint16_t      width;
    uint16_t      height;
    uint8_t       bpp;          /* 8 for v1 (indexed) */
    uint8_t       reserved0;

    uint16_t      pitch_bytes;  /* bytes per scanline in VRAM */
    uint16_t      reserved1;

    /* Physical or logical base of framebuffer, if needed */
    uint32_t      phys_base;    /* optional physical address */
} xga_mode_info;

/* XGA backend state */
typedef struct xga_state_t {
    dgfx_soft_config config;
    xga_mode_info    mode;

    /* System RAM framebuffer: 8bpp indexed. */
    soft_framebuffer fb;

    /* Depth/stencil buffers in system RAM. */
    uint8_t *depth;
    uint8_t *stencil;

    int      width;
    int      height;

    int      frame_in_progress;

    dgfx_caps caps;

    /* IR / camera / viewport state. */
    float    view[16];
    float    proj[16];
    float    world[16];

    int      vp_x, vp_y, vp_w, vp_h;
    int      camera2d_x;
    int      camera2d_y;

} xga_state_t;

extern xga_state_t g_xga;

const dgfx_backend_vtable *dgfx_xga_get_vtable(void);

#endif /* DOMINIUM_XGA_GFX_H */
