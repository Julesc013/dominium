#include "dom_render_null.h"
#include <stdlib.h>
#include <string.h>

typedef struct DomRenderNullState {
    int unused;
} DomRenderNullState;

static dom_err_t dom_render_null_init(DomRenderer *r,
                                      const dom_render_config *cfg,
                                      dom_render_caps *out_caps)
{
    if (!r || !cfg || !out_caps) {
        return DOM_ERR_INVALID_ARG;
    }
    out_caps->supports_textures = 0;
    out_caps->supports_blending = 0;
    out_caps->supports_linear_filter = 0;
    out_caps->supports_aniso = 0;
    r->config = *cfg;
    r->mode = cfg->mode;
    r->width = cfg->width;
    r->height = cfg->height;

    r->backend_state = malloc(sizeof(DomRenderNullState));
    if (!r->backend_state) {
        return DOM_ERR_OUT_OF_MEMORY;
    }
    memset(r->backend_state, 0, sizeof(DomRenderNullState));
    return DOM_OK;
}

static void dom_render_null_shutdown(DomRenderer *r)
{
    if (r && r->backend_state) {
        free(r->backend_state);
        r->backend_state = 0;
    }
}

static void dom_render_null_resize(DomRenderer *r, dom_u32 w, dom_u32 h)
{
    (void)r;
    (void)w;
    (void)h;
}

static void dom_render_null_submit(DomRenderer *r,
                                   const DomDrawCommand *cmds,
                                   dom_u32 count)
{
    (void)r;
    (void)cmds;
    (void)count;
}

static void dom_render_null_present(DomRenderer *r)
{
    (void)r;
}

static const DomRenderBackendAPI g_dom_render_null = {
    dom_render_null_init,
    dom_render_null_shutdown,
    dom_render_null_resize,
    dom_render_null_submit,
    dom_render_null_present
};

const DomRenderBackendAPI *dom_render_backend_null(void)
{
    return &g_dom_render_null;
}

/*
 * Vector2D stub backend: for now it simply aliases the null backend.
 * A future revision can map this to GL1/GL2 immediate-mode vector drawing.
 */
const DomRenderBackendAPI *dom_render_backend_vector2d(void)
{
    return &g_dom_render_null;
}
