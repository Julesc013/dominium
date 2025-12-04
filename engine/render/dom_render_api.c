#include "dom_render_api.h"
#include "dom_render_dx9.h"
#include "dom_render_null.h"

#include <string.h>

static const DomRenderBackendAPI *dom_render_get_backend(DomRenderBackendKind kind)
{
    switch (kind) {
    case DOM_RENDER_BACKEND_DX9:
        return dom_render_backend_dx9();
    case DOM_RENDER_BACKEND_VECTOR2D:
        return dom_render_backend_vector2d();
    case DOM_RENDER_BACKEND_NULL:
    default:
        return dom_render_backend_null();
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
    if (!cb) {
        return;
    }
    cb->count = 0;
}

dom_err_t dom_render_cmd_push(DomRenderCommandBuffer *cb, const DomRenderCmd *cmd)
{
    if (!cb || !cmd) {
        return DOM_ERR_INVALID_ARG;
    }
    if (cb->count >= DOM_RENDER_CMD_MAX) {
        return DOM_ERR_OVERFLOW;
    }
    cb->cmds[cb->count] = *cmd;
    cb->count += 1;
    return DOM_OK;
}

static dom_err_t dom_render_push_line(DomRenderer *r, const DomRenderCmd *cmd)
{
    return dom_render_cmd_push(&r->cmd, cmd);
}

dom_err_t dom_render_create(DomRenderer *r,
                            DomRenderBackendKind backend,
                            dom_u32 width,
                            dom_u32 height,
                            void *platform_window)
{
    if (!r) {
        return DOM_ERR_INVALID_ARG;
    }

    memset(r, 0, sizeof(*r));
    r->backend = backend;
    r->width = width;
    r->height = height;
    r->platform_window = platform_window;
    dom_render_state_init(&r->state);
    dom_render_cmd_init(&r->cmd);

    r->api = dom_render_get_backend(backend);
    if (!r->api || !r->api->init) {
        return DOM_ERR_NOT_IMPLEMENTED;
    }

    return r->api->init(r);
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
    cmd.kind = DOM_CMD_RECT;
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
    cmd.kind = DOM_CMD_LINE;
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
    cmd.kind = DOM_CMD_POLY;
    cmd.u.poly.count = count;
    cmd.u.poly.color = c;
    for (i = 0; i < count; ++i) {
        cmd.u.poly.pts[i] = pts[i];
    }
    return dom_render_cmd_push(&r->cmd, &cmd);
}

dom_err_t dom_render_submit(DomRenderer *r)
{
    if (!r || !r->api || !r->api->submit) {
        return DOM_ERR_INVALID_ARG;
    }
    r->api->submit(r, &r->cmd);
    return DOM_OK;
}

void dom_render_present(DomRenderer *r)
{
    if (!r || !r->api || !r->api->present) {
        return;
    }
    r->api->present(r);
}
