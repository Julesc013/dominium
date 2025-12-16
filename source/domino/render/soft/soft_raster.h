/*
FILE: source/domino/render/soft/soft_raster.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / render/soft/soft_raster
RESPONSIBILITY: Implements `soft_raster`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOMINIUM_SOFT_RASTER_H
#define DOMINIUM_SOFT_RASTER_H

#include <stdint.h>
#include "domino/sys.h"
#include "soft_config.h"

typedef struct soft_framebuffer_t {
    uint8_t *color;
    uint8_t *depth;
    uint8_t *stencil;

    int width;
    int height;
    int stride_bytes;
    int depth_stride;
    int stencil_stride;

    dgfx_soft_format   format;
    int depth_bits;
    int stencil_bits;
} soft_framebuffer;

/* Basic framebuffer management */
bool soft_fb_create(soft_framebuffer* fb,
                    int width, int height,
                    dgfx_soft_format   fmt,
                    uint8_t depth_bits,
                    uint8_t stencil_bits);

void soft_fb_destroy(soft_framebuffer* fb);

/* Clears */
void soft_raster_clear_color(soft_framebuffer *fb,
                             uint8_t r, uint8_t g, uint8_t b, uint8_t a);

void soft_raster_clear_depth(soft_framebuffer *fb, float depth);
void soft_raster_clear_stencil(soft_framebuffer *fb, uint8_t value);

/* 2D primitives */
void soft_raster_fill_rect_2d(soft_framebuffer *fb,
                              int x, int y, int w, int h,
                              uint32_t rgba);

void soft_raster_draw_line_2d(soft_framebuffer *fb,
                              int x0, int y0, int x1, int y1,
                              uint32_t rgba);

/* 3D triangle rasterization */
typedef struct soft_vertex_t {
    float x, y, z, w;
    float u, v;
    uint32_t rgba;
} soft_vertex;

void soft_raster_draw_triangle(soft_framebuffer *fb,
                               const soft_vertex *v0,
                               const soft_vertex *v1,
                               const soft_vertex *v2,
                               int enable_depth_test);

/* Text stub */
void soft_raster_draw_text_stub(soft_framebuffer *fb,
                                int x, int y,
                                uint32_t rgba,
                                const char *text);

#endif /* DOMINIUM_SOFT_RASTER_H */
