#include "soft_raster.h"

#include <stdlib.h>
#include <string.h>

static uint8_t soft_luma_index(uint8_t r, uint8_t g, uint8_t b)
{
    unsigned int intensity;
    intensity = (unsigned int)((r * 30u + g * 59u + b * 11u) / 100u);
    return (uint8_t)intensity;
}

static uint16_t soft_pack_565(uint8_t r, uint8_t g, uint8_t b)
{
    return (uint16_t)(((uint16_t)(r >> 3) << 11) |
                      ((uint16_t)(g >> 2) << 5) |
                      ((uint16_t)(b >> 3) << 0));
}

static uint32_t soft_pack_argb(uint8_t r, uint8_t g, uint8_t b, uint8_t a)
{
    return ((uint32_t)a << 24) | ((uint32_t)r << 16) | ((uint32_t)g << 8) | (uint32_t)b;
}

static uint8_t clamp_u8(int v)
{
    if (v < 0) return 0;
    if (v > 255) return 255;
    return (uint8_t)v;
}

static void soft_store_pixel(soft_framebuffer *fb, int x, int y, uint32_t rgba)
{
    uint8_t r;
    uint8_t g;
    uint8_t b;
    uint8_t a;
    size_t offset;

    if (!fb || !fb->color) {
        return;
    }
    if (x < 0 || y < 0 || x >= fb->width || y >= fb->height) {
        return;
    }

    r = (uint8_t)((rgba >> 16) & 0xffu);
    g = (uint8_t)((rgba >> 8) & 0xffu);
    b = (uint8_t)(rgba & 0xffu);
    a = (uint8_t)((rgba >> 24) & 0xffu);

    offset = (size_t)y * (size_t)fb->stride_bytes;

    switch (fb->format) {
    case DGFX_SOFT_FMT_8_INDEXED:
        {
            uint8_t idx = soft_luma_index(r, g, b);
            fb->color[offset + (size_t)x] = idx;
        }
        break;
    case DGFX_SOFT_FMT_16_565:
        {
            uint16_t* row16;
            row16 = (uint16_t*)(fb->color + offset);
            row16[x] = soft_pack_565(r, g, b);
        }
        break;
    case DGFX_SOFT_FMT_32_ARGB:
    default:
        {
            uint32_t* row32;
            row32 = (uint32_t*)(fb->color + offset);
            row32[x] = soft_pack_argb(r, g, b, a);
        }
        break;
    }
}

static uint32_t soft_depth_to_uint(float depth, int bits)
{
    uint32_t maxv;
    if (depth < 0.0f) depth = 0.0f;
    if (depth > 1.0f) depth = 1.0f;
    maxv = (bits >= 32) ? 0xffffffffu : ((1u << bits) - 1u);
    return (uint32_t)(depth * (float)maxv);
}

static int soft_depth_test_and_write(soft_framebuffer *fb, int x, int y, float depth)
{
    uint32_t depth_u;
    size_t row_off;

    if (!fb || !fb->depth || fb->depth_bits == 0) {
        return 1; /* no depth buffer: always pass */
    }
    if (x < 0 || y < 0 || x >= fb->width || y >= fb->height) {
        return 0;
    }

    depth_u = soft_depth_to_uint(depth, fb->depth_bits);
    row_off = (size_t)y * (size_t)fb->depth_stride;

    if (fb->depth_bits == 16) {
        uint16_t *row16 = (uint16_t *)(fb->depth + row_off);
        uint16_t cur = row16[x];
        if (depth_u >= (uint32_t)cur) {
            return 0;
        }
        row16[x] = (uint16_t)depth_u;
        return 1;
    } else if (fb->depth_bits == 24) {
        uint8_t *row = fb->depth + row_off;
        size_t base = (size_t)x * 3u;
        uint32_t cur = (uint32_t)row[base] |
                       ((uint32_t)row[base + 1u] << 8) |
                       ((uint32_t)row[base + 2u] << 16);
        if (depth_u >= cur) {
            return 0;
        }
        row[base + 0u] = (uint8_t)(depth_u & 0xffu);
        row[base + 1u] = (uint8_t)((depth_u >> 8) & 0xffu);
        row[base + 2u] = (uint8_t)((depth_u >> 16) & 0xffu);
        return 1;
    } else {
        uint32_t *row32 = (uint32_t *)(fb->depth + row_off);
        uint32_t cur = row32[x];
        if (depth_u >= cur) {
            return 0;
        }
        row32[x] = depth_u;
        return 1;
    }
}

bool soft_fb_create(soft_framebuffer* fb,
                    int width, int height,
                    dgfx_soft_format   fmt,
                    uint8_t depth_bits,
                    uint8_t stencil_bits)
{
    size_t color_stride;
    size_t depth_stride;
    size_t stencil_stride;
    size_t color_size;
    size_t depth_size;
    size_t stencil_size;
    uint8_t* color;
    uint8_t* depth;
    uint8_t* stencil;
    int bpp;

    if (!fb || width <= 0 || height <= 0) {
        return false;
    }

    color = NULL;
    depth = NULL;
    stencil = NULL;

    bpp = 0;
    switch (fmt) {
    case DGFX_SOFT_FMT_8_INDEXED: bpp = 1; break;
    case DGFX_SOFT_FMT_16_565:    bpp = 2; break;
    case DGFX_SOFT_FMT_32_ARGB:   bpp = 4; break;
    default:
        return false;
    }

    color_stride = (size_t)width * (size_t)bpp;
    color_size = color_stride * (size_t)height;

    color = (uint8_t*)malloc(color_size);
    if (!color) {
        return false;
    }
    memset(color, 0, color_size);

    depth_stride = 0u;
    depth_size = 0u;
    if (depth_bits > 0u) {
        size_t depth_bytes_per_pixel;
        depth_bytes_per_pixel = (size_t)(depth_bits + 7u) / 8u;
        depth_stride = (size_t)width * depth_bytes_per_pixel;
        depth_size = depth_stride * (size_t)height;
        depth = (uint8_t*)malloc(depth_size);
        if (!depth) {
            free(color);
            return false;
        }
        memset(depth, 0xff, depth_size); /* default far depth */
    }

    stencil_stride = 0u;
    stencil_size = 0u;
    if (stencil_bits > 0u) {
        size_t stencil_bytes_per_pixel;
        stencil_bytes_per_pixel = (size_t)(stencil_bits + 7u) / 8u;
        stencil_stride = (size_t)width * stencil_bytes_per_pixel;
        stencil_size = stencil_stride * (size_t)height;
        stencil = (uint8_t*)malloc(stencil_size);
        if (!stencil) {
            if (depth) free(depth);
            free(color);
            return false;
        }
        memset(stencil, 0, stencil_size);
    }

    memset(fb, 0, sizeof(*fb));
    fb->color = color;
    fb->depth = depth;
    fb->stencil = stencil;
    fb->width = width;
    fb->height = height;
    fb->stride_bytes = (int)color_stride;
    fb->depth_stride = (int)depth_stride;
    fb->stencil_stride = (int)stencil_stride;
    fb->format = fmt;
    fb->depth_bits = depth_bits;
    fb->stencil_bits = stencil_bits;

    return true;
}

void soft_fb_destroy(soft_framebuffer* fb)
{
    if (!fb) {
        return;
    }
    if (fb->color) {
        free(fb->color);
    }
    if (fb->depth) {
        free(fb->depth);
    }
    if (fb->stencil) {
        free(fb->stencil);
    }
    memset(fb, 0, sizeof(*fb));
}

void soft_raster_clear_color(soft_framebuffer *fb,
                             uint8_t r, uint8_t g, uint8_t b, uint8_t a)
{
    size_t y;

    if (!fb || !fb->color) {
        return;
    }

    switch (fb->format) {
    case DGFX_SOFT_FMT_8_INDEXED:
        {
            size_t total;
            uint8_t idx;
            idx = soft_luma_index(r, g, b);
            total = (size_t)fb->stride_bytes * (size_t)fb->height;
            memset(fb->color, idx, total);
        }
        break;
    case DGFX_SOFT_FMT_16_565:
        {
            uint16_t packed;
            packed = soft_pack_565(r, g, b);
            for (y = 0u; y < (size_t)fb->height; ++y) {
                uint16_t* row = (uint16_t*)(fb->color + (size_t)y * (size_t)fb->stride_bytes);
                int x;
                for (x = 0; x < fb->width; ++x) {
                    row[x] = packed;
                }
            }
        }
        break;
    case DGFX_SOFT_FMT_32_ARGB:
    default:
        {
            uint32_t packed32;
            packed32 = soft_pack_argb(r, g, b, a);
            for (y = 0u; y < (size_t)fb->height; ++y) {
                uint32_t* row = (uint32_t*)(fb->color + (size_t)y * (size_t)fb->stride_bytes);
                int x;
                for (x = 0; x < fb->width; ++x) {
                    row[x] = packed32;
                }
            }
        }
        break;
    }
}

void soft_raster_clear_depth(soft_framebuffer *fb, float depth)
{
    uint32_t value32;
    uint32_t y;

    if (!fb || !fb->depth || fb->depth_bits == 0u) {
        return;
    }

    if (depth < 0.0f) depth = 0.0f;
    if (depth > 1.0f) depth = 1.0f;

    if (fb->depth_bits == 16u) {
        uint16_t v16;
        v16 = (uint16_t)(depth * 65535.0f);
        for (y = 0u; y < (uint32_t)fb->height; ++y) {
            uint16_t* row = (uint16_t*)(fb->depth + (size_t)y * (size_t)fb->depth_stride);
            int x;
            for (x = 0; x < fb->width; ++x) {
                row[x] = v16;
            }
        }
        return;
    }

    value32 = (uint32_t)(depth * 4294967295.0f);

    if (fb->depth_bits == 24u) {
        for (y = 0u; y < (uint32_t)fb->height; ++y) {
            uint8_t* row = fb->depth + (size_t)y * (size_t)fb->depth_stride;
            int x;
            for (x = 0; x < fb->width; ++x) {
                size_t base = (size_t)x * 3u;
                row[base + 0u] = (uint8_t)(value32 & 0xffu);
                row[base + 1u] = (uint8_t)((value32 >> 8) & 0xffu);
                row[base + 2u] = (uint8_t)((value32 >> 16) & 0xffu);
            }
        }
        return;
    }

    for (y = 0u; y < (uint32_t)fb->height; ++y) {
        uint32_t* row = (uint32_t*)(fb->depth + (size_t)y * (size_t)fb->depth_stride);
        int x;
        for (x = 0; x < fb->width; ++x) {
            row[x] = value32;
        }
    }
}

void soft_raster_clear_stencil(soft_framebuffer *fb, uint8_t s)
{
    if (!fb || !fb->stencil || fb->stencil_bits == 0u) {
        return;
    }
    memset(fb->stencil, s, (size_t)fb->stencil_stride * (size_t)fb->height);
}

void soft_raster_draw_line_2d(soft_framebuffer *fb,
                              int x0, int y0, int x1, int y1,
                              uint32_t rgba)
{
    int dx;
    int dy;
    int sx;
    int sy;
    int err;
    int e2;

    if (!fb || !fb->color) {
        return;
    }

    dx = (x1 > x0) ? (x1 - x0) : (x0 - x1);
    dy = (y1 > y0) ? (y1 - y0) : (y0 - y1);
    sx = (x0 < x1) ? 1 : -1;
    sy = (y0 < y1) ? 1 : -1;
    err = dx - dy;

    for (;;) {
        soft_store_pixel(fb, x0, y0, rgba);

        if (x0 == x1 && y0 == y1) {
            break;
        }

        e2 = err << 1;
        if (e2 > -dy) {
            err -= dy;
            x0 += sx;
        }
        if (e2 < dx) {
            err += dx;
            y0 += sy;
        }
    }
}

void soft_raster_fill_rect_2d(soft_framebuffer *fb,
                              int x, int y, int w, int h,
                              uint32_t rgba)
{
    int x0;
    int y0;
    int x1;
    int y1;
    int iy;

    if (!fb || !fb->color || w <= 0 || h <= 0) {
        return;
    }

    x0 = x;
    y0 = y;
    x1 = x + w;
    y1 = y + h;

    if (x0 < 0) x0 = 0;
    if (y0 < 0) y0 = 0;
    if (x1 > fb->width)  x1 = fb->width;
    if (y1 > fb->height) y1 = fb->height;

    for (iy = y0; iy < y1; ++iy) {
        int ix;
        for (ix = x0; ix < x1; ++ix) {
            soft_store_pixel(fb, ix, iy, rgba);
        }
    }
}

static uint32_t soft_interp_channel(uint32_t c0, uint32_t c1, uint32_t c2, float w0, float w1, float w2, int shift)
{
    int v0;
    int v1;
    int v2;
    float sum;
    v0 = (int)((c0 >> shift) & 0xffu);
    v1 = (int)((c1 >> shift) & 0xffu);
    v2 = (int)((c2 >> shift) & 0xffu);
    sum = w0 * (float)v0 + w1 * (float)v1 + w2 * (float)v2;
    return (uint32_t)clamp_u8((int)(sum + 0.5f));
}

void soft_raster_draw_triangle(soft_framebuffer *fb,
                               const soft_vertex *v0,
                               const soft_vertex *v1,
                               const soft_vertex *v2,
                               int enable_depth_test)
{
    float area;
    int min_x;
    int min_y;
    int max_x;
    int max_y;
    int x;
    int y;
    float inv_area;
    uint32_t c0;
    uint32_t c1;
    uint32_t c2;

    if (!fb || !fb->color || !v0 || !v1 || !v2) {
        return;
    }

    area = (v1->x - v0->x) * (v2->y - v0->y) - (v1->y - v0->y) * (v2->x - v0->x);
    if (area == 0.0f) {
        return;
    }
    inv_area = 1.0f / area;

    min_x = (int)(v0->x < v1->x ? (v0->x < v2->x ? v0->x : v2->x) : (v1->x < v2->x ? v1->x : v2->x));
    min_y = (int)(v0->y < v1->y ? (v0->y < v2->y ? v0->y : v2->y) : (v1->y < v2->y ? v1->y : v2->y));
    max_x = (int)(v0->x > v1->x ? (v0->x > v2->x ? v0->x : v2->x) : (v1->x > v2->x ? v1->x : v2->x));
    max_y = (int)(v0->y > v1->y ? (v0->y > v2->y ? v0->y : v2->y) : (v1->y > v2->y ? v1->y : v2->y));

    if (min_x < 0) min_x = 0;
    if (min_y < 0) min_y = 0;
    if (max_x > fb->width - 1) max_x = fb->width - 1;
    if (max_y > fb->height - 1) max_y = fb->height - 1;

    c0 = v0->rgba;
    c1 = v1->rgba;
    c2 = v2->rgba;

    for (y = min_y; y <= max_y; ++y) {
        for (x = min_x; x <= max_x; ++x) {
            float px;
            float py;
            float w0;
            float w1;
            float w2;
            float depth;
            uint32_t color;

            px = (float)x + 0.5f;
            py = (float)y + 0.5f;

            w0 = ((v1->x - v0->x) * (py - v0->y) - (v1->y - v0->y) * (px - v0->x)) * inv_area;
            w1 = ((v2->x - v1->x) * (py - v1->y) - (v2->y - v1->y) * (px - v1->x)) * inv_area;
            w2 = ((v0->x - v2->x) * (py - v2->y) - (v0->y - v2->y) * (px - v2->x)) * inv_area;

            if (w0 < 0.0f || w1 < 0.0f || w2 < 0.0f) {
                continue;
            }

            depth = w0 * v0->z + w1 * v1->z + w2 * v2->z;

            if (enable_depth_test && !soft_depth_test_and_write(fb, x, y, depth)) {
                continue;
            } else if (!enable_depth_test && fb->depth && fb->depth_bits > 0) {
                /* still write depth if buffer exists to keep determinism */
                soft_depth_test_and_write(fb, x, y, depth);
            }

            color = (soft_interp_channel(c0, c1, c2, w0, w1, w2, 16) << 16) |
                    (soft_interp_channel(c0, c1, c2, w0, w1, w2, 8) << 8) |
                    (soft_interp_channel(c0, c1, c2, w0, w1, w2, 0));
            color |= (soft_interp_channel(c0, c1, c2, w0, w1, w2, 24) << 24);

            soft_store_pixel(fb, x, y, color);
        }
    }
}

void soft_raster_draw_text_stub(soft_framebuffer *fb,
                                int x, int y,
                                uint32_t rgba,
                                const char *text)
{
    int cursor_x;
    int cursor_y;
    int i;
    int glyph_w;
    int glyph_h;

    if (!fb || !text) {
        return;
    }

    glyph_w = 8;
    glyph_h = 12;
    cursor_x = x;
    cursor_y = y;

    for (i = 0; text[i] != '\0'; ++i) {
        if (text[i] == '\n') {
            cursor_x = x;
            cursor_y += glyph_h;
            continue;
        }
        soft_raster_fill_rect_2d(fb, cursor_x, cursor_y, glyph_w, glyph_h, rgba);
        cursor_x += glyph_w;
    }
}
