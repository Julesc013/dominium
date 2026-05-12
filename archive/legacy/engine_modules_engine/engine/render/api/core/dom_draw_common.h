/*
FILE: source/domino/render/api/core/dom_draw_common.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / render/api/core/dom_draw_common
RESPONSIBILITY: Defines internal contract for `dom_draw_common`; shared within its subsystem; does NOT define a public API (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (internal header).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOM_DRAW_COMMON_H
#define DOM_DRAW_COMMON_H

/*
 * Shared draw-command definitions for all renderers.
 * Pure C89, no platform headers. Deterministic and backend-agnostic.
 */

#ifdef __cplusplus
extern "C" {
#endif

#include "dom_core_types.h"
#include "dom_core_err.h"

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

typedef enum DomDrawCmdType {
    DOM_CMD_NONE = 0,
    DOM_CMD_CLEAR,
    DOM_CMD_RECT,
    DOM_CMD_LINE,
    DOM_CMD_POLY,
    DOM_CMD_SPRITE,
    DOM_CMD_TILEMAP,
    DOM_CMD_TEXT,
    DOM_CMD_TRIANGLE
} DomDrawCmdType;

typedef struct DomCmdClear {
    DomColor color;
} DomCmdClear;

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

typedef struct DomCmdTriangle {
    dom_i32 x0, y0, x1, y1, x2, y2; /* screen pixels */
    dom_i32 z0, z1, z2;             /* optional depth */
    dom_u32 color;                  /* fallback 0xAARRGGBB */
    dom_u32 texture_id;
    dom_i32 u0_q16_16, v0_q16_16;
    dom_i32 u1_q16_16, v1_q16_16;
    dom_i32 u2_q16_16, v2_q16_16;
} DomCmdTriangle;

#define DOM_CMD_TEXT_MAX 256
typedef struct DomCmdText {
    DomFontId font;
    DomColor color;
    char text[DOM_CMD_TEXT_MAX];
    dom_i32 x;
    dom_i32 y;
} DomCmdText;

typedef struct DomDrawCommand {
    DomDrawCmdType type;
    union {
        DomCmdClear  clear;
        DomCmdRect   rect;
        DomCmdLine   line;
        DomCmdPoly   poly;
        DomCmdSprite sprite;
        DomCmdText   text;
        DomCmdTriangle tri;
    } u;
} DomDrawCommand;

#define DOM_DRAW_COMMAND_MAX 1024
typedef struct DomDrawCommandBuffer {
    dom_u32 count;
    DomDrawCommand cmds[DOM_DRAW_COMMAND_MAX];
} DomDrawCommandBuffer;

void dom_draw_cmd_buffer_init(DomDrawCommandBuffer *cb);
dom_err_t dom_draw_cmd_buffer_push(DomDrawCommandBuffer *cb,
                                   const DomDrawCommand *cmd);
void dom_draw_cmd_buffer_sort_triangles(DomDrawCommandBuffer *cb);

/* Compatibility aliases for existing render code */
typedef DomDrawCmdType DomRenderCmdKind;
typedef DomDrawCommand DomRenderCmd;
typedef DomDrawCommandBuffer DomRenderCommandBuffer;

enum { DOM_RENDER_CMD_MAX = DOM_DRAW_COMMAND_MAX };

#ifdef __cplusplus
}
#endif

#endif /* DOM_DRAW_COMMON_H */
