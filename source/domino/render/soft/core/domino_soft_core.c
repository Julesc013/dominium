/*
FILE: source/domino/render/soft/core/domino_soft_core.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / render/soft/core/domino_soft_core
RESPONSIBILITY: Implements `domino_soft_core`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include "domino_gfx_internal.h"
#include "soft_internal.h"

#include <stdlib.h>
#include <string.h>

struct domino_gfx_texture {
    int placeholder;
};

typedef struct domino_soft_state {
    int   width;
    int   height;
    int   stride_bytes;
    domino_pixfmt fmt;
    unsigned char* pixels;
    const domino_soft_target_ops* target;
    void* target_state;
} domino_soft_state;

static const domino_gfx_backend_vtable g_soft_vtable; /* fwd */

static unsigned int domino_soft_pack_color(float r, float g, float b, float a)
{
    int ir = (int)(r * 255.0f);
    int ig = (int)(g * 255.0f);
    int ib = (int)(b * 255.0f);
    int ia = (int)(a * 255.0f);
    if (ir < 0) ir = 0; if (ir > 255) ir = 255;
    if (ig < 0) ig = 0; if (ig > 255) ig = 255;
    if (ib < 0) ib = 0; if (ib > 255) ib = 255;
    if (ia < 0) ia = 0; if (ia > 255) ia = 255;
    return ((unsigned int)ia << 24) | ((unsigned int)ir << 16) | ((unsigned int)ig << 8) | (unsigned int)ib;
}

static int domino_soft_present(domino_gfx_device* dev)
{
    domino_soft_state* st;
    if (!dev || !dev->backend_data) return -1;
    st = (domino_soft_state*)dev->backend_data;
    if (st->target && st->target->present) {
        return st->target->present(st->target_state,
                                   st->pixels,
                                   st->width,
                                   st->height,
                                   st->stride_bytes);
    }
    return 0;
}

static void domino_soft_destroy(domino_gfx_device* dev)
{
    domino_soft_state* st;
    if (!dev) return;
    st = (domino_soft_state*)dev->backend_data;
    if (st) {
        if (st->target && st->target->shutdown) {
            st->target->shutdown(st->target_state);
        }
        if (st->pixels) {
            free(st->pixels);
        }
        free(st);
    }
    free(dev);
}

static int domino_soft_begin(domino_gfx_device* dev)
{
    (void)dev;
    return 0;
}

static int domino_soft_end(domino_gfx_device* dev)
{
    return domino_soft_present(dev);
}

static int domino_soft_clear(domino_gfx_device* dev,
                             float r, float g, float b, float a)
{
    domino_soft_state* st;
    unsigned int color;
    unsigned int* row;
    int y, x;
    if (!dev || !dev->backend_data) return -1;
    st = (domino_soft_state*)dev->backend_data;
    color = domino_soft_pack_color(r, g, b, a);
    row = (unsigned int*)st->pixels;
    for (y = 0; y < st->height; ++y) {
        for (x = 0; x < st->width; ++x) {
            row[x] = color;
        }
        row = (unsigned int*)((unsigned char*)row + st->stride_bytes);
    }
    return 0;
}

static int domino_soft_draw_rect(domino_gfx_device* dev,
                                 const domino_gfx_rect* rect,
                                 float r, float g, float b, float a)
{
    domino_soft_state* st;
    unsigned int color;
    int x0, y0, x1, y1;
    int y;
    if (!dev || !dev->backend_data || !rect) return -1;
    st = (domino_soft_state*)dev->backend_data;
    color = domino_soft_pack_color(r, g, b, a);

    x0 = (int)rect->x;
    y0 = (int)rect->y;
    x1 = x0 + (int)rect->w;
    y1 = y0 + (int)rect->h;
    if (x0 < 0) x0 = 0;
    if (y0 < 0) y0 = 0;
    if (x1 > st->width)  x1 = st->width;
    if (y1 > st->height) y1 = st->height;

    for (y = y0; y < y1; ++y) {
        unsigned int* row = (unsigned int*)((unsigned char*)st->pixels + y * st->stride_bytes);
        int x;
        for (x = x0; x < x1; ++x) {
            row[x] = color;
        }
    }
    return 0;
}

static int domino_soft_tex_create(domino_gfx_device* dev,
                                  const domino_gfx_texture_desc* desc,
                                  domino_gfx_texture** out_tex)
{
    domino_gfx_texture* tex;
    (void)dev; (void)desc;
    if (!out_tex) return -1;
    tex = (domino_gfx_texture*)malloc(sizeof(domino_gfx_texture));
    if (!tex) return -1;
    tex->placeholder = 0;
    *out_tex = tex;
    return 0;
}

static void domino_soft_tex_destroy(domino_gfx_texture* tex)
{
    if (tex) free(tex);
}

static int domino_soft_tex_update(domino_gfx_texture* tex,
                                  int x, int y, int w, int h,
                                  const void* pixels, int pitch_bytes)
{
    (void)tex; (void)x; (void)y; (void)w; (void)h; (void)pixels; (void)pitch_bytes;
    return -1;
}

static int domino_soft_draw_texture(domino_gfx_device* dev,
                                    domino_gfx_texture* tex,
                                    const domino_gfx_rect* dst_rect,
                                    const domino_gfx_uv_rect* src_uv)
{
    (void)dev; (void)tex; (void)dst_rect; (void)src_uv;
    return -1;
}

static int domino_soft_draw_text(domino_gfx_device* dev,
                                 domino_gfx_font* font,
                                 float x, float y,
                                 const char* text,
                                 float r, float g, float b, float a)
{
    (void)dev; (void)font; (void)x; (void)y; (void)text; (void)r; (void)g; (void)b; (void)a;
    return -1;
}

static const domino_gfx_backend_vtable g_soft_vtable = {
    domino_soft_destroy,
    domino_soft_begin,
    domino_soft_end,
    domino_soft_clear,
    domino_soft_draw_rect,
    domino_soft_tex_create,
    domino_soft_tex_destroy,
    domino_soft_tex_update,
    domino_soft_draw_texture,
    domino_soft_draw_text
};

static const domino_soft_target_ops* domino_soft_choose_target(domino_sys_context* sys)
{
    domino_sys_platform_info info;
    if (sys) {
        domino_sys_get_platform_info(sys, &info);
        if (info.os == DOMINO_OS_WINDOWS) {
            return domino_soft_target_win32();
        }
    }
    return domino_soft_target_null();
}

int domino_gfx_soft_create(domino_sys_context* sys,
                           const domino_gfx_desc* desc,
                           domino_gfx_device** out_dev)
{
    domino_gfx_device* dev;
    domino_soft_state* st;
    const domino_soft_target_ops* target;

    if (!out_dev || !desc) return -1;
    *out_dev = NULL;

    dev = (domino_gfx_device*)malloc(sizeof(domino_gfx_device));
    if (!dev) return -1;
    memset(dev, 0, sizeof(*dev));

    st = (domino_soft_state*)malloc(sizeof(domino_soft_state));
    if (!st) {
        free(dev);
        return -1;
    }
    memset(st, 0, sizeof(*st));

    st->width = desc->width;
    st->height = desc->height;
    st->fmt = desc->framebuffer_fmt;
    st->stride_bytes = st->width * 4;
    st->pixels = (unsigned char*)malloc((size_t)st->stride_bytes * (size_t)st->height);
    if (!st->pixels) {
        free(st);
        free(dev);
        return -1;
    }
    memset(st->pixels, 0, (size_t)st->stride_bytes * (size_t)st->height);

    target = domino_soft_choose_target(sys);
    st->target = target;
    if (target && target->init) {
        if (target->init(sys, st->width, st->height, st->fmt, &st->target_state) != 0) {
            target = domino_soft_target_null();
            st->target = target;
            st->target_state = NULL;
            if (target && target->init) {
                target->init(sys, st->width, st->height, st->fmt, &st->target_state);
            }
        }
    }

    dev->backend = DOMINO_GFX_BACKEND_SOFT;
    dev->profile = desc->profile_hint;
    dev->framebuffer_fmt = desc->framebuffer_fmt;
    dev->width = desc->width;
    dev->height = desc->height;
    dev->fullscreen = desc->fullscreen;
    dev->vsync = desc->vsync;
    dev->sys = sys;
    dev->vt = &g_soft_vtable;
    dev->backend_data = st;

    *out_dev = dev;
    return 0;
}
