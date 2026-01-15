/*
FILE: source/domino/render/mda/mda_gfx.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / render/mda/mda_gfx
RESPONSIBILITY: Defines internal contract for `mda_gfx`; shared within its subsystem; does NOT define a public API (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (internal header).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOMINIUM_MDA_GFX_H
#define DOMINIUM_MDA_GFX_H

#include <stdint.h>

#include "domino/gfx.h"
#include "domino/canvas.h"

#include "soft_config.h"
#include "soft_raster.h"

typedef enum mda_mode_kind_t {
    MDA_MODE_KIND_720x350_1 = 0
} mda_mode_kind;

typedef struct mda_mode_info_t {
    mda_mode_kind kind;
    uint16_t      width;          /* 720 */
    uint16_t      height;         /* 350 */
    uint8_t       bits_per_pixel; /* 1 */
    uint8_t       reserved0;

    uint16_t      pitch_bytes;    /* bytes per scanline in VRAM after bit-packing */
    uint16_t      reserved1;

    uint16_t      vram_segment;   /* 0xB000 for MDA */
} mda_mode_info;

typedef struct mda_state_t {
    dgfx_soft_config config;
    mda_mode_info    mode;

    soft_framebuffer fb;      /* system RAM framebuffer (8-bit indexed / grayscale) */
    uint8_t *depth;
    uint8_t *stencil;

    int width;
    int height;

    int frame_in_progress;

    dgfx_caps caps;

    float view[16];
    float proj[16];
    float world[16];

    int vp_x, vp_y, vp_w, vp_h;
    int camera2d_x;
    int camera2d_y;

} mda_state_t;

extern mda_state_t g_mda;

const dgfx_backend_vtable *dgfx_mda_get_vtable(void);

#endif
