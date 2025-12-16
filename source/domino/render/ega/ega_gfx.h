/*
FILE: source/domino/render/ega/ega_gfx.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / render/ega/ega_gfx
RESPONSIBILITY: Implements `ega_gfx`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOMINIUM_EGA_GFX_H
#define DOMINIUM_EGA_GFX_H

#include <stdint.h>

#include "domino/gfx.h"
#include "domino/canvas.h"

#include "soft_config.h"
#include "soft_raster.h"

typedef enum ega_mode_kind_t {
    EGA_MODE_KIND_640x350_16 = 0,
    EGA_MODE_KIND_320x200_16
} ega_mode_kind;

typedef struct ega_mode_info_t {
    ega_mode_kind kind;
    uint16_t      width;
    uint16_t      height;
    uint8_t       logical_bpp;
    uint8_t       reserved0;

    uint16_t      pitch_bytes;
    uint16_t      reserved1;

    uint16_t      vram_segment;
} ega_mode_info;

typedef struct ega_state_t {
    dgfx_soft_config config;
    ega_mode_info    mode;

    soft_framebuffer fb;

    uint8_t* depth;
    uint8_t* stencil;

    int      width;
    int      height;

    int      frame_in_progress;

    dgfx_caps caps;

    float    view[16];
    float    proj[16];
    float    world[16];

    int      vp_x;
    int      vp_y;
    int      vp_w;
    int      vp_h;
    int      camera2d_x;
    int      camera2d_y;

} ega_state_t;

extern ega_state_t g_ega;

const dgfx_backend_vtable* dgfx_ega_get_vtable(void);

#endif /* DOMINIUM_EGA_GFX_H */
