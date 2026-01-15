/*
FILE: source/domino/render/soft/soft_gfx.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / render/soft/soft_gfx
RESPONSIBILITY: Defines internal contract for `soft_gfx`; shared within its subsystem; does NOT define a public API (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (internal header).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOMINIUM_SOFT_GFX_H
#define DOMINIUM_SOFT_GFX_H

#include <stdint.h>
#include "domino/gfx.h"
#include "soft_raster.h"
#include "soft_config.h"

typedef struct soft_state_t {
    dgfx_soft_config config;
    soft_framebuffer fb;

    uint8_t *depth_mem;
    uint8_t *stencil_mem;

    int width;
    int height;
    int frame_in_progress;

    dgfx_caps caps;

    float view[16];
    float proj[16];
    float world[16];

    dgfx_viewport_t vp;
} soft_state_t;

extern soft_state_t g_soft;

const dgfx_backend_vtable *dgfx_soft_get_vtable(void);

#endif /* DOMINIUM_SOFT_GFX_H */
