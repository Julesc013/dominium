#ifndef DOM_RENDER_API_H
#define DOM_RENDER_API_H

/*
 * Dominium rendering API (MVP)
 * - Backend-agnostic, integer-only command buffer.
 * - No simulation or game logic here.
 * - C89/C++98 friendly.
 */

#ifdef __cplusplus
extern "C" {
#endif

#include "dom_core_types.h"
#include "dom_core_err.h"

/* ------------------------------------------------------------
 * Basic types
 * ------------------------------------------------------------ */
typedef struct DomVec2i {
    dom_i32 x;
    dom_i32 y;
} DomVec2i;

typedef struct DomRect {
    dom_i32 x;
    dom_i32 y;
    dom_i32 w;
    dom_i32 h;
} DomRect;

typedef dom_u32 DomColor;      /* 0xAARRGGBB */
typedef dom_u32 DomSpriteId;
typedef dom_u32 DomFontId;

typedef struct DomRenderState {
    DomColor clear_color;
    DomColor default_color;
    DomSpriteId default_sprite;
} DomRenderState;

void dom_render_state_init(DomRenderState *s);

/* ------------------------------------------------------------
 * Command buffer
 * ------------------------------------------------------------ */
typedef enum DomRenderCmdKind {
    DOM_CMD_NONE = 0,
    DOM_CMD_RECT,
    DOM_CMD_LINE,
    DOM_CMD_POLY,
    DOM_CMD_SPRITE,
    DOM_CMD_TEXT
} DomRenderCmdKind;

typedef struct DomCmdRect {
    DomRect rect;
    DomColor color;
} DomCmdRect;

typedef struct DomCmdLine {
    dom_i32 x0, y0, x1, y1;
    DomColor color;
} DomCmdLine;

#define DOM_CMD_POLY_MAX 16
typedef struct DomCmdPoly {
    dom_u32 count;
    DomVec2i pts[DOM_CMD_POLY_MAX];
    DomColor color;
} DomCmdPoly;

typedef struct DomCmdSprite {
    DomSpriteId id;
    dom_i32 x;
    dom_i32 y;
} DomCmdSprite;

#define DOM_CMD_TEXT_MAX 256
typedef struct DomCmdText {
    DomFontId font;
    DomColor color;
    char text[DOM_CMD_TEXT_MAX];
    dom_i32 x;
    dom_i32 y;
} DomCmdText;

typedef struct DomRenderCmd {
    DomRenderCmdKind kind;
    union {
        DomCmdRect   rect;
        DomCmdLine   line;
        DomCmdPoly   poly;
        DomCmdSprite sprite;
        DomCmdText   text;
    } u;
} DomRenderCmd;

#define DOM_RENDER_CMD_MAX 8192
typedef struct DomRenderCommandBuffer {
    dom_u32 count;
    DomRenderCmd cmds[DOM_RENDER_CMD_MAX];
} DomRenderCommandBuffer;

void dom_render_cmd_init(DomRenderCommandBuffer *cb);
dom_err_t dom_render_cmd_push(DomRenderCommandBuffer *cb,
                              const DomRenderCmd *cmd);

/* ------------------------------------------------------------
 * Backend selection
 * ------------------------------------------------------------ */
typedef enum DomRenderBackendKind {
    DOM_RENDER_BACKEND_NULL = 0,
    DOM_RENDER_BACKEND_DX9,
    DOM_RENDER_BACKEND_VECTOR2D /* stub, future GL1/GL2 mapper */
} DomRenderBackendKind;

struct DomRenderBackendAPI;

typedef struct DomRenderer {
    DomRenderBackendKind backend;
    void *backend_state;       /* owned by backend */
    void *platform_window;     /* native window handle (opaque to renderer) */
    dom_u32 width;
    dom_u32 height;
    DomRenderCommandBuffer cmd;
    DomRenderState state;
    const struct DomRenderBackendAPI *api;
} DomRenderer;

/* ------------------------------------------------------------
 * Public API
 * ------------------------------------------------------------ */
dom_err_t dom_render_create(DomRenderer *r,
                            DomRenderBackendKind backend,
                            dom_u32 width,
                            dom_u32 height,
                            void *platform_window);

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

dom_err_t dom_render_submit(DomRenderer *r);
void dom_render_present(DomRenderer *r);

/* ------------------------------------------------------------
 * Backend API (implemented by individual backends)
 * ------------------------------------------------------------ */
typedef struct DomRenderBackendAPI {
    dom_err_t (*init)(DomRenderer *r);
    void      (*shutdown)(DomRenderer *r);
    void      (*resize)(DomRenderer *r, dom_u32 w, dom_u32 h);
    void      (*submit)(DomRenderer *r, const DomRenderCommandBuffer *cb);
    void      (*present)(DomRenderer *r);
} DomRenderBackendAPI;

const DomRenderBackendAPI *dom_render_backend_dx9(void);
const DomRenderBackendAPI *dom_render_backend_null(void);
const DomRenderBackendAPI *dom_render_backend_vector2d(void);

#ifdef __cplusplus
}
#endif

#endif /* DOM_RENDER_API_H */
