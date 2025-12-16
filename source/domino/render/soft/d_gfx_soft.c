/*
FILE: source/domino/render/soft/d_gfx_soft.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / render/soft/d_gfx_soft
RESPONSIBILITY: Implements `d_gfx_soft`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include <stdlib.h>
#include <string.h>

#include "d_gfx_soft.h"
#include "domino/system/d_system.h"

static u32 *g_soft_fb = 0;
static i32 g_soft_width = 800;
static i32 g_soft_height = 600;
static d_gfx_viewport g_soft_vp = { 0, 0, 800, 600 };

static u32 d_gfx_soft_pack_color(const d_gfx_color *c)
{
    u32 v = 0u;
    if (!c) {
        return 0xff000000u;
    }
    v |= ((u32)c->a << 24);
    v |= ((u32)c->r << 16);
    v |= ((u32)c->g << 8);
    v |= ((u32)c->b);
    return v;
}

static void d_gfx_soft_fill_rect(const d_gfx_draw_rect_cmd *rect)
{
    i32 x0;
    i32 y0;
    i32 x1;
    i32 y1;
    u32 color;
    i32 y;

    if (!g_soft_fb || !rect) {
        return;
    }

    x0 = rect->x;
    y0 = rect->y;
    x1 = rect->x + rect->w;
    y1 = rect->y + rect->h;

    if (x0 < g_soft_vp.x) x0 = g_soft_vp.x;
    if (y0 < g_soft_vp.y) y0 = g_soft_vp.y;
    if (x1 > g_soft_vp.x + g_soft_vp.w) x1 = g_soft_vp.x + g_soft_vp.w;
    if (y1 > g_soft_vp.y + g_soft_vp.h) y1 = g_soft_vp.y + g_soft_vp.h;

    if (x0 >= x1 || y0 >= y1) {
        return;
    }

    color = d_gfx_soft_pack_color(&rect->color);
    for (y = y0; y < y1; ++y) {
        u32 *row = g_soft_fb + (u32)y * (u32)g_soft_width;
        i32 x;
        for (x = x0; x < x1; ++x) {
            row[x] = color;
        }
    }
}

static void d_gfx_soft_stub_text(const d_gfx_draw_text_cmd *text)
{
    d_gfx_draw_rect_cmd r;
    size_t len;

    if (!text) {
        return;
    }
    len = text->text ? strlen(text->text) : 0u;
    r.x = text->x;
    r.y = text->y;
    r.w = (i32)(len ? (len * 8u) : 8u);
    r.h = 12;
    r.color = text->color;
    d_gfx_soft_fill_rect(&r);
}

static int d_gfx_soft_init(void)
{
    size_t bytes;
    bytes = (size_t)g_soft_width * (size_t)g_soft_height * sizeof(u32);
    g_soft_fb = (u32 *)malloc(bytes);
    if (!g_soft_fb) {
        g_soft_width = 0;
        g_soft_height = 0;
        return -1;
    }
    memset(g_soft_fb, 0, bytes);
    g_soft_vp.x = 0;
    g_soft_vp.y = 0;
    g_soft_vp.w = g_soft_width;
    g_soft_vp.h = g_soft_height;
    return 0;
}

static void d_gfx_soft_shutdown(void)
{
    if (g_soft_fb) {
        free(g_soft_fb);
        g_soft_fb = (u32 *)0;
    }
    g_soft_width = 0;
    g_soft_height = 0;
}

static void d_gfx_soft_submit(const d_gfx_cmd_buffer *buf)
{
    u32 i;

    if (!buf || !buf->cmds || buf->count == 0u || !g_soft_fb) {
        return;
    }

    for (i = 0u; i < buf->count; ++i) {
        const d_gfx_cmd *cmd = buf->cmds + i;
        switch (cmd->opcode) {
        case D_GFX_OP_CLEAR: {
            u32 color = d_gfx_soft_pack_color(&cmd->u.clear.color);
            u32 pix_count = (u32)g_soft_width * (u32)g_soft_height;
            u32 p;
            for (p = 0u; p < pix_count; ++p) {
                g_soft_fb[p] = color;
            }
            break;
        }
        case D_GFX_OP_SET_VIEWPORT:
            g_soft_vp = cmd->u.viewport.vp;
            break;
        case D_GFX_OP_SET_CAMERA:
            /* ignored in minimal slice */
            break;
        case D_GFX_OP_DRAW_RECT:
            d_gfx_soft_fill_rect(&cmd->u.rect);
            break;
        case D_GFX_OP_DRAW_TEXT:
            d_gfx_soft_stub_text(&cmd->u.text);
            break;
        default:
            break;
        }
    }
}

static void d_gfx_soft_present(void)
{
    d_system_present_framebuffer(
        g_soft_fb,
        g_soft_width,
        g_soft_height,
        g_soft_width * 4);
}

static d_gfx_backend_soft g_soft_backend = {
    d_gfx_soft_init,
    d_gfx_soft_shutdown,
    d_gfx_soft_submit,
    d_gfx_soft_present
};

const d_gfx_backend_soft *d_gfx_soft_register_backend(void)
{
    return &g_soft_backend;
}

void d_gfx_soft_set_framebuffer_size(i32 w, i32 h)
{
    if (w > 0) {
        g_soft_width = w;
    }
    if (h > 0) {
        g_soft_height = h;
    }
    g_soft_vp.x = 0;
    g_soft_vp.y = 0;
    g_soft_vp.w = g_soft_width;
    g_soft_vp.h = g_soft_height;
}

const u32* d_gfx_soft_get_framebuffer(i32* out_w, i32* out_h, i32* out_pitch_bytes)
{
    if (out_w) {
        *out_w = g_soft_width;
    }
    if (out_h) {
        *out_h = g_soft_height;
    }
    if (out_pitch_bytes) {
        *out_pitch_bytes = g_soft_width * 4;
    }
    return g_soft_fb;
}
