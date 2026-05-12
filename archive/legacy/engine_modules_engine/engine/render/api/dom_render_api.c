/*
FILE: source/domino/render/api/dom_render_api.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / render/api/dom_render_api
RESPONSIBILITY: Implements `dom_render_api`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include "dom_render_api.h"
#include "dom_render_dx9.h"
#include "dom_render_null.h"
#include "soft/core/dom_render_software.h"

#include <string.h>
#include <stdlib.h>

static const DomRenderBackendAPI *dom_render_get_backend(dom_render_backend kind)
{
    switch (kind) {
    case DOM_RENDER_BACKEND_DX9:
        return dom_render_backend_dx9();
    case DOM_RENDER_BACKEND_GL1:
    case DOM_RENDER_BACKEND_GL2:
    case DOM_RENDER_BACKEND_VK1:
    case DOM_RENDER_BACKEND_DX11:
    case DOM_RENDER_BACKEND_DX12:
        /* Not implemented yet; fall through to software/null placeholder. */
        return dom_render_backend_null();
    case DOM_RENDER_BACKEND_SOFTWARE:
    default:
        return dom_render_backend_software();
    }
}

void dom_render_state_init(DomRenderState *s)
{
    if (!s) {
        return;
    }
    s->clear_color = 0xFF000000;   /* opaque black */
    s->default_color = 0xFFFFFFFF; /* white */
    s->default_sprite = 0;
}

void dom_render_cmd_init(DomRenderCommandBuffer *cb)
{
    dom_draw_cmd_buffer_init(cb);
}

dom_err_t dom_render_cmd_push(DomRenderCommandBuffer *cb, const DomRenderCmd *cmd)
{
    return dom_draw_cmd_buffer_push(cb, cmd);
}

static dom_err_t dom_render_push_line(DomRenderer *r, const DomRenderCmd *cmd)
{
    return dom_render_cmd_push(&r->cmd, cmd);
}

dom_err_t dom_render_create(DomRenderer *r,
                            dom_render_backend backend,
                            const dom_render_config *cfg,
                            dom_render_caps *out_caps)
{
    dom_render_config local_cfg;
    dom_render_caps *caps_ptr;
    dom_err_t err;
    if (!r) {
        return DOM_ERR_INVALID_ARG;
    }

    if (!cfg) {
        return DOM_ERR_INVALID_ARG;
    }

    memset(r, 0, sizeof(*r));
    local_cfg = *cfg;
    r->backend = backend;
    r->config = local_cfg;
    r->mode = local_cfg.mode;
    r->width = local_cfg.width;
    r->height = local_cfg.height;
    r->platform_window = local_cfg.platform_window;
    dom_render_state_init(&r->state);
    dom_render_cmd_init(&r->cmd);

    r->api = dom_render_get_backend(backend);
    if (!r->api || !r->api->init) {
        return DOM_ERR_NOT_IMPLEMENTED;
    }

    memset(&r->caps, 0, sizeof(r->caps));
    if (out_caps) {
        memset(out_caps, 0, sizeof(*out_caps));
    }

    caps_ptr = out_caps ? out_caps : &r->caps;
    err = r->api->init(r, &local_cfg, caps_ptr);
    if (err == DOM_OK && out_caps) {
        r->caps = *out_caps;
    }
    return err;
}

void dom_render_destroy(DomRenderer *r)
{
    if (!r || !r->api || !r->api->shutdown) {
        return;
    }
    r->api->shutdown(r);
    r->backend_state = 0;
}

void dom_render_resize(DomRenderer *r, dom_u32 width, dom_u32 height)
{
    if (!r) {
        return;
    }
    r->width = width;
    r->height = height;
    r->config.width = width;
    r->config.height = height;
    if (r->api && r->api->resize) {
        r->api->resize(r, width, height);
    }
}

void dom_render_begin(DomRenderer *r, DomColor clear_color)
{
    if (!r) {
        return;
    }
    r->state.clear_color = clear_color;
    dom_render_cmd_init(&r->cmd);
}

dom_err_t dom_render_rect(DomRenderer *r, const DomRect *rc, DomColor c)
{
    DomRenderCmd cmd;
    if (!r || !rc) {
        return DOM_ERR_INVALID_ARG;
    }
    cmd.type = DOM_CMD_RECT;
    cmd.u.rect.rect = *rc;
    cmd.u.rect.color = c;
    return dom_render_cmd_push(&r->cmd, &cmd);
}

dom_err_t dom_render_line(DomRenderer *r,
                          dom_i32 x0, dom_i32 y0,
                          dom_i32 x1, dom_i32 y1,
                          DomColor c)
{
    DomRenderCmd cmd;
    if (!r) {
        return DOM_ERR_INVALID_ARG;
    }
    cmd.type = DOM_CMD_LINE;
    cmd.u.line.x0 = x0;
    cmd.u.line.y0 = y0;
    cmd.u.line.x1 = x1;
    cmd.u.line.y1 = y1;
    cmd.u.line.color = c;
    return dom_render_push_line(r, &cmd);
}

dom_err_t dom_render_poly(DomRenderer *r,
                          const DomVec2i *pts,
                          dom_u32 count,
                          DomColor c)
{
    DomRenderCmd cmd;
    dom_u32 i;
    if (!r || !pts) {
        return DOM_ERR_INVALID_ARG;
    }
    if (count == 0 || count > DOM_CMD_POLY_MAX) {
        return DOM_ERR_BOUNDS;
    }
    cmd.type = DOM_CMD_POLY;
    cmd.u.poly.count = count;
    cmd.u.poly.color = c;
    for (i = 0; i < count; ++i) {
        cmd.u.poly.pts[i] = pts[i];
    }
    return dom_render_cmd_push(&r->cmd, &cmd);
}

dom_err_t dom_render_sprite(DomRenderer *r,
                            DomSpriteId id,
                            dom_i32 x,
                            dom_i32 y)
{
    DomRenderCmd cmd;
    if (!r) {
        return DOM_ERR_INVALID_ARG;
    }
    cmd.type = DOM_CMD_SPRITE;
    cmd.u.sprite.id = id;
    cmd.u.sprite.x = x;
    cmd.u.sprite.y = y;
    return dom_render_cmd_push(&r->cmd, &cmd);
}

dom_err_t dom_render_text(DomRenderer *r,
                          DomFontId font,
                          DomColor color,
                          const char *text,
                          dom_i32 x,
                          dom_i32 y)
{
    DomRenderCmd cmd;
    size_t len;
    if (!r || !text) {
        return DOM_ERR_INVALID_ARG;
    }
    cmd.type = DOM_CMD_TEXT;
    cmd.u.text.font = font;
    cmd.u.text.color = color;
    cmd.u.text.x = x;
    cmd.u.text.y = y;
    cmd.u.text.text[0] = '\0';
    len = strlen(text);
    if (len >= DOM_CMD_TEXT_MAX) {
        len = DOM_CMD_TEXT_MAX - 1u;
    }
    memcpy(cmd.u.text.text, text, len);
    cmd.u.text.text[len] = '\0';
    return dom_render_cmd_push(&r->cmd, &cmd);
}

dom_err_t dom_render_submit(DomRenderer *r,
                            const DomDrawCommand *cmds,
                            dom_u32 count)
{
    const DomDrawCommand *submit_cmds;
    dom_u32 submit_count;

    if (!r || !r->api || !r->api->submit) {
        return DOM_ERR_INVALID_ARG;
    }

    if (!cmds) {
        submit_cmds = r->cmd.cmds;
        submit_count = r->cmd.count;
    } else {
        submit_cmds = cmds;
        submit_count = count;
    }

    r->api->submit(r, submit_cmds, submit_count);
    return DOM_OK;
}

void dom_render_present(DomRenderer *r)
{
    if (!r || !r->api || !r->api->present) {
        return;
    }
    r->api->present(r);
}

int dom_renderer_create(const dom_render_config *cfg,
                        dom_renderer           **out_renderer,
                        dom_render_caps        *out_caps)
{
    DomRenderer *r;
    dom_err_t err;
    if (!cfg || !out_renderer) {
        return (int)DOM_ERR_INVALID_ARG;
    }
    r = (DomRenderer *)malloc(sizeof(DomRenderer));
    if (!r) {
        return (int)DOM_ERR_OUT_OF_MEMORY;
    }
    memset(r, 0, sizeof(DomRenderer));
    err = dom_render_create(r, cfg->backend, cfg, out_caps);
    if (err != DOM_OK) {
        free(r);
        return (int)err;
    }
    *out_renderer = r;
    return (int)DOM_OK;
}

void dom_renderer_destroy(dom_renderer *r)
{
    if (!r) {
        return;
    }
    dom_render_destroy(r);
    free(r);
}

void dom_renderer_submit(dom_renderer *r,
                         const DomDrawCommand *cmds,
                         unsigned count)
{
    if (!r) {
        return;
    }
    dom_render_submit(r, cmds, count);
}
