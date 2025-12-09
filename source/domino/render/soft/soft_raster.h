#ifndef DOMINIUM_SOFT_RASTER_H
#define DOMINIUM_SOFT_RASTER_H

#include "soft_gfx.h"

typedef struct soft_vertex_t {
    float x, y, z, w;
    float u, v;
    uint32_t color;
} soft_vertex;

bool soft_fb_create(soft_framebuffer* fb,
                    int width, int height,
                    dgfx_soft_format fmt,
                    uint8_t depth_bits,
                    uint8_t stencil_bits);

void soft_fb_destroy(soft_framebuffer* fb);

void soft_raster_clear_color(const soft_framebuffer* fb,
                             uint8_t r, uint8_t g, uint8_t b, uint8_t a);

void soft_raster_clear_depth(const soft_framebuffer* fb, float depth);
void soft_raster_clear_stencil(const soft_framebuffer* fb, uint8_t s);

/* 2D primitives */
void soft_raster_draw_line_2d(const soft_framebuffer* fb,
                              int x0, int y0, int x1, int y1,
                              uint32_t rgba);

void soft_raster_fill_rect_2d(const soft_framebuffer* fb,
                              int x, int y, int w, int h,
                              uint32_t rgba);

/* 3D triangles: assumes transformed vertices already in screen-space or NDC */
void soft_raster_draw_triangle(const soft_framebuffer* fb,
                               const soft_vertex* v0,
                               const soft_vertex* v1,
                               const soft_vertex* v2,
                               int enable_depth,
                               int enable_texture);

#endif /* DOMINIUM_SOFT_RASTER_H */
