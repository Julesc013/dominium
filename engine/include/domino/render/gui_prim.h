/*
FILE: include/domino/render/gui_prim.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino API / render/gui_prim
RESPONSIBILITY: Defines the public contract for `gui_prim` (types/constants/function signatures); does NOT provide implementation.
ALLOWED DEPENDENCIES: `include/domino/**` plus C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `source/**` private headers; keep contracts freestanding and layer-respecting.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: Public header; see `docs/SPEC_ABI_TEMPLATES.md` where ABI stability matters.
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOMINO_RENDER_GUI_PRIM_H_INCLUDED
#define DOMINO_RENDER_GUI_PRIM_H_INCLUDED

/* Minimal vector-style GUI primitives built on dgfx sprites/text. */

#include "domino/gfx.h"

#ifdef __cplusplus
extern "C" {
#endif

/* dgui_color: Public type used by `gui_prim`. */
typedef struct dgui_color {
    uint8_t r, g, b, a;
} dgui_color;

/* dgui_rect: Public type used by `gui_prim`. */
typedef struct dgui_rect {
    int x, y, w, h;
} dgui_rect;

/* dgui_text_prim: Public type used by `gui_prim`. */
typedef struct dgui_text_prim {
    int     x;
    int     y;
    dgui_color color;
    const char* text;
} dgui_text_prim;

/* dgui_rect_prim: Public type used by `gui_prim`. */
typedef struct dgui_rect_prim {
    dgui_rect  rect;
    dgui_color fill;
    dgui_color stroke;
    int        stroke_width;
    int        corner_radius;
} dgui_rect_prim;

/* Utility helpers emit into a canvas */
void dgui_draw_rect(struct dcvs_t* c, const dgui_rect_prim* r);
/* Purpose: Text dgui draw.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 */
void dgui_draw_text(struct dcvs_t* c, const dgui_text_prim* t);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINO_RENDER_GUI_PRIM_H_INCLUDED */
