#include "dom_render_software.h"

#include <stdlib.h>
#include <string.h>

typedef struct DomRenderSoftwareState {
    dom_u32 width;
    dom_u32 height;
    dom_u32 pitch_pixels;
    dom_u32 pitch_bytes;
    dom_u32 *pixels;
    dom_present_fn present;
    void *present_user;
} DomRenderSoftwareState;

static dom_err_t dom_render_software_resize_buffer(DomRenderer *r,
                                                   DomRenderSoftwareState *st,
                                                   dom_u32 w,
                                                   dom_u32 h)
{
    size_t count;
    dom_u32 *buf;
    if (!r || !st) {
        return DOM_ERR_INVALID_ARG;
    }
    if (w == 0 || h == 0) {
        return DOM_ERR_INVALID_ARG;
    }

    if (h != 0 && w > ((size_t)-1) / h / sizeof(dom_u32)) {
        return DOM_ERR_OVERFLOW;
    }
    count = (size_t)w * (size_t)h;

    buf = (dom_u32 *)malloc(count * sizeof(dom_u32));
    if (!buf) {
        return DOM_ERR_OUT_OF_MEMORY;
    }

    if (st->pixels) {
        free(st->pixels);
    }

    st->pixels = buf;
    st->width = w;
    st->height = h;
    st->pitch_pixels = w;
    st->pitch_bytes = w * (dom_u32)sizeof(dom_u32);

    r->width = w;
    r->height = h;
    r->config.width = w;
    r->config.height = h;
    return DOM_OK;
}

static dom_err_t dom_render_software_init(DomRenderer *r,
                                          const dom_render_config *cfg,
                                          dom_render_caps *out_caps)
{
    DomRenderSoftwareState *st;
    dom_err_t err;

    if (!r || !cfg || !out_caps) {
        return DOM_ERR_INVALID_ARG;
    }

    out_caps->supports_textures = 0;
    out_caps->supports_blending = 0;
    out_caps->supports_linear_filter = 0;
    out_caps->supports_aniso = 0;

    st = (DomRenderSoftwareState *)malloc(sizeof(DomRenderSoftwareState));
    if (!st) {
        return DOM_ERR_OUT_OF_MEMORY;
    }
    memset(st, 0, sizeof(*st));

    st->present = cfg->present;
    st->present_user = cfg->present_user;

    r->config = *cfg;
    r->mode = cfg->mode;
    r->backend_state = st;

    err = dom_render_software_resize_buffer(r, st, cfg->width, cfg->height);
    if (err != DOM_OK) {
        free(st);
        r->backend_state = 0;
    }
    return err;
}

static void dom_render_software_shutdown(DomRenderer *r)
{
    DomRenderSoftwareState *st;
    if (!r || !r->backend_state) {
        return;
    }
    st = (DomRenderSoftwareState *)r->backend_state;
    if (st->pixels) {
        free(st->pixels);
    }
    free(st);
    r->backend_state = 0;
}

static void dom_render_software_resize(DomRenderer *r, dom_u32 w, dom_u32 h)
{
    DomRenderSoftwareState *st;
    if (!r || !r->backend_state) {
        return;
    }
    st = (DomRenderSoftwareState *)r->backend_state;
    (void)dom_render_software_resize_buffer(r, st, w, h);
}

static void dom_sw_clear(DomRenderSoftwareState *st, DomColor c)
{
    dom_u32 i;
    dom_u32 total;
    if (!st || !st->pixels) {
        return;
    }
    total = st->width * st->height;
    for (i = 0; i < total; ++i) {
        st->pixels[i] = c;
    }
}

static void dom_sw_put_pixel(DomRenderSoftwareState *st,
                             dom_i32 x,
                             dom_i32 y,
                             DomColor c)
{
    if (!st || !st->pixels) {
        return;
    }
    if (x < 0 || y < 0) {
        return;
    }
    if ((dom_u32)x >= st->width || (dom_u32)y >= st->height) {
        return;
    }
    st->pixels[(dom_u32)y * st->pitch_pixels + (dom_u32)x] = c;
}

static void dom_sw_draw_line(DomRenderSoftwareState *st,
                             dom_i32 x0, dom_i32 y0,
                             dom_i32 x1, dom_i32 y1,
                             DomColor c)
{
    dom_i32 dx = (x1 > x0) ? (x1 - x0) : (x0 - x1);
    dom_i32 sx = (x0 < x1) ? 1 : -1;
    dom_i32 dy = (y1 > y0) ? (y1 - y0) : (y0 - y1);
    dom_i32 sy = (y0 < y1) ? 1 : -1;
    dom_i32 err = dx - dy;

    for (;;) {
        dom_sw_put_pixel(st, x0, y0, c);
        if (x0 == x1 && y0 == y1) {
            break;
        }
        if ((err << 1) > -dy) {
            err -= dy;
            x0 += sx;
        }
        if ((err << 1) < dx) {
            err += dx;
            y0 += sy;
        }
    }
}

static void dom_sw_draw_rect(DomRenderSoftwareState *st, const DomCmdRect *rc)
{
    dom_i32 x0 = rc->rect.x;
    dom_i32 y0 = rc->rect.y;
    dom_i32 x1 = rc->rect.x + rc->rect.w;
    dom_i32 y1 = rc->rect.y + rc->rect.h;
    DomColor c = rc->color;

    dom_sw_draw_line(st, x0, y0, x1, y0, c);
    dom_sw_draw_line(st, x1, y0, x1, y1, c);
    dom_sw_draw_line(st, x1, y1, x0, y1, c);
    dom_sw_draw_line(st, x0, y1, x0, y0, c);
}

static void dom_sw_draw_poly(DomRenderSoftwareState *st, const DomCmdPoly *poly)
{
    dom_u32 i;
    if (poly->count < 2) {
        return;
    }
    for (i = 0; i < poly->count; ++i) {
        DomVec2i a = poly->pts[i];
        DomVec2i b = poly->pts[(i + 1u) % poly->count];
        dom_sw_draw_line(st, a.x, a.y, b.x, b.y, poly->color);
    }
}

static void dom_sw_draw_placeholder_sprite(DomRenderSoftwareState *st,
                                           dom_i32 x,
                                           dom_i32 y,
                                           DomColor c)
{
    dom_sw_draw_line(st, x, y, x + 8, y + 8, c);
    dom_sw_draw_line(st, x, y + 8, x + 8, y, c);
}

static void dom_render_software_submit(DomRenderer *r,
                                       const DomDrawCommand *cmds,
                                       dom_u32 count)
{
    DomRenderSoftwareState *st;
    dom_u32 i;

    if (!r || !r->backend_state) {
        return;
    }
    if (!cmds && count > 0) {
        return;
    }

    st = (DomRenderSoftwareState *)r->backend_state;
    dom_sw_clear(st, r->state.clear_color);

    for (i = 0; i < count; ++i) {
        const DomDrawCommand *cmd = &cmds[i];
        switch (cmd->type) {
        case DOM_CMD_LINE:
            dom_sw_draw_line(st,
                             cmd->u.line.x0, cmd->u.line.y0,
                             cmd->u.line.x1, cmd->u.line.y1,
                             cmd->u.line.color);
            break;
        case DOM_CMD_RECT:
            dom_sw_draw_rect(st, &cmd->u.rect);
            break;
        case DOM_CMD_POLY:
            dom_sw_draw_poly(st, &cmd->u.poly);
            break;
        case DOM_CMD_SPRITE:
        case DOM_CMD_TILEMAP:
            if (r->mode == DOM_RENDER_MODE_VECTOR_ONLY || !r->caps.supports_textures) {
                dom_sw_draw_placeholder_sprite(st,
                                               cmd->u.sprite.x,
                                               cmd->u.sprite.y,
                                               r->state.default_color);
                break;
            }
            /* Textured path not implemented yet; draw deterministic placeholder. */
            dom_sw_draw_placeholder_sprite(st,
                                           cmd->u.sprite.x,
                                           cmd->u.sprite.y,
                                           r->state.default_color);
            break;
        case DOM_CMD_TEXT:
            dom_sw_draw_placeholder_sprite(st,
                                           cmd->u.text.x,
                                           cmd->u.text.y,
                                           r->state.default_color);
            break;
        case DOM_CMD_CLEAR:
        case DOM_CMD_NONE:
        default:
            /* No-op */
            break;
        }
    }
}

static void dom_render_software_present(DomRenderer *r)
{
    DomRenderSoftwareState *st;
    if (!r || !r->backend_state) {
        return;
    }
    st = (DomRenderSoftwareState *)r->backend_state;
    if (st->present && st->pixels) {
        st->present(st->present_user,
                    st->pixels,
                    (int)st->width,
                    (int)st->height,
                    (int)st->pitch_bytes);
    }
}

static const DomRenderBackendAPI g_dom_render_software = {
    dom_render_software_init,
    dom_render_software_shutdown,
    dom_render_software_resize,
    dom_render_software_submit,
    dom_render_software_present
};

const DomRenderBackendAPI *dom_render_backend_software(void)
{
    return &g_dom_render_software;
}
