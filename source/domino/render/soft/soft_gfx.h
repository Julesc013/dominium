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
