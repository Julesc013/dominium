/*
FILE: source/domino/render/soft/targets/null/dom_render_null.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / render/soft/targets/null/dom_render_null
RESPONSIBILITY: Implements `dom_render_null`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
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
