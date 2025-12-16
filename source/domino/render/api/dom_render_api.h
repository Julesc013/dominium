/*
FILE: source/domino/render/api/dom_render_api.h
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
#ifndef DOM_RENDER_API_H
#define DOM_RENDER_API_H

#ifdef __cplusplus
extern "C" {
#endif

#include "dom_core_types.h"
#include "dom_core_err.h"
#include "core/dom_draw_common.h"

/*
 * Dominium rendering API
 * - Backend-agnostic command buffer.
 * - Supports vector-only or full (textured) modes per config.
 */

/* ------------------------------------------------------------
 * Render capabilities and configuration
 * ------------------------------------------------------------ */
typedef enum dom_render_backend_e {
    DOM_RENDER_BACKEND_SOFTWARE = 0,  /* universal fallback */
    DOM_RENDER_BACKEND_DX9,
    DOM_RENDER_BACKEND_DX11,
    DOM_RENDER_BACKEND_DX12,
    DOM_RENDER_BACKEND_GL1,
    DOM_RENDER_BACKEND_GL2,
    DOM_RENDER_BACKEND_VK1
} dom_render_backend;

typedef enum dom_render_mode_e {
    DOM_RENDER_MODE_VECTOR_ONLY = 0,  /* CAD / outline */
    DOM_RENDER_MODE_FULL              /* full textured graphics */
} dom_render_mode;

typedef struct dom_render_caps_s {
    int supports_textures;
    int supports_blending;
    int supports_linear_filter;
    int supports_aniso;
} dom_render_caps;

typedef void (*dom_present_fn)(void *user,
                               const dom_u32 *pixels,
                               int width,
                               int height,
                               int pitch_bytes);

typedef struct dom_render_config_s {
    dom_render_backend backend; /* compile-time choice, but tracked for completeness */
    dom_render_mode    mode;    /* runtime choice: vector/full */
    dom_i32 width;
    dom_i32 height;
    dom_i32 fullscreen;
    void *platform_window;  /* native window handle (opaque to renderer) */
    dom_present_fn present; /* software backend present callback (optional) */
    void *present_user;     /* user data for present callback */
} dom_render_config;

typedef struct DomRenderState {
    DomColor clear_color;
    DomColor default_color;
    DomSpriteId default_sprite;
} DomRenderState;

void dom_render_state_init(DomRenderState *s);

/* ------------------------------------------------------------
 * Command buffer
 * ------------------------------------------------------------ */
void dom_render_cmd_init(DomRenderCommandBuffer *cb);
dom_err_t dom_render_cmd_push(DomRenderCommandBuffer *cb,
                              const DomRenderCmd *cmd);

/* ------------------------------------------------------------
 * Backend selection
 * ------------------------------------------------------------ */
struct DomRenderBackendAPI;

typedef struct DomRenderer {
    dom_render_backend backend;
    dom_render_mode mode;
    dom_render_config config;
    dom_render_caps caps;
    void *backend_state;       /* owned by backend */
    void *platform_window;     /* native window handle (opaque to renderer) */
    dom_u32 width;
    dom_u32 height;
    DomRenderCommandBuffer cmd;
    DomRenderState state;
    const struct DomRenderBackendAPI *api;
} DomRenderer;
typedef DomRenderer dom_renderer;

/* ------------------------------------------------------------
 * Public API
 * ------------------------------------------------------------ */
dom_err_t dom_render_create(DomRenderer *r,
                            dom_render_backend backend,
                            const dom_render_config *cfg,
                            dom_render_caps *out_caps);

void dom_render_destroy(DomRenderer *r);

void dom_render_resize(DomRenderer *r, dom_u32 width, dom_u32 height);

void dom_render_begin(DomRenderer *r, DomColor clear_color);

dom_err_t dom_render_rect(DomRenderer *r, const DomRect *rc, DomColor c);
dom_err_t dom_render_line(DomRenderer *r,
                          dom_i32 x0, dom_i32 y0,
                          dom_i32 x1, dom_i32 y1,
                          DomColor c);
dom_err_t dom_render_poly(DomRenderer *r,
                          const DomVec2i *pts,
                          dom_u32 count,
                          DomColor c);
dom_err_t dom_render_sprite(DomRenderer *r,
                            DomSpriteId id,
                            dom_i32 x,
                            dom_i32 y);
dom_err_t dom_render_text(DomRenderer *r,
                          DomFontId font,
                          DomColor color,
                          const char *text,
                          dom_i32 x,
                          dom_i32 y);

dom_err_t dom_render_submit(DomRenderer *r,
                            const DomDrawCommand *cmds,
                            dom_u32 count);
void dom_render_present(DomRenderer *r);

/* New canonical renderer API wrapper (malloc-owning) */
int dom_renderer_create(const dom_render_config *cfg,
                        dom_renderer           **out_renderer,
                        dom_render_caps        *out_caps);
void dom_renderer_destroy(dom_renderer *r);
void dom_renderer_submit(dom_renderer *r,
                         const DomDrawCommand *cmds,
                         unsigned count);

/* ------------------------------------------------------------
 * Backend API (implemented by individual backends)
 * ------------------------------------------------------------ */
typedef struct DomRenderBackendAPI {
    dom_err_t (*init)(DomRenderer *r,
                      const dom_render_config *cfg,
                      dom_render_caps *out_caps);
    void      (*shutdown)(DomRenderer *r);
    void      (*resize)(DomRenderer *r, dom_u32 w, dom_u32 h);
    void      (*submit)(DomRenderer *r,
                        const DomDrawCommand *cmds,
                        dom_u32 count);
    void      (*present)(DomRenderer *r);
} DomRenderBackendAPI;

const DomRenderBackendAPI *dom_render_backend_dx9(void);
const DomRenderBackendAPI *dom_render_backend_null(void);
const DomRenderBackendAPI *dom_render_backend_vector2d(void);
const DomRenderBackendAPI *dom_render_backend_software(void);

#ifdef __cplusplus
}
#endif

#endif /* DOM_RENDER_API_H */
