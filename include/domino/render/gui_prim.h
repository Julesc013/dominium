#ifndef DOMINO_RENDER_GUI_PRIM_H_INCLUDED
#define DOMINO_RENDER_GUI_PRIM_H_INCLUDED

/* Minimal vector-style GUI primitives built on dgfx sprites/text. */

#include "domino/gfx.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct dgui_color {
    uint8_t r, g, b, a;
} dgui_color;

typedef struct dgui_rect {
    int x, y, w, h;
} dgui_rect;

typedef struct dgui_text_prim {
    int     x;
    int     y;
    dgui_color color;
    const char* text;
} dgui_text_prim;

typedef struct dgui_rect_prim {
    dgui_rect  rect;
    dgui_color fill;
    dgui_color stroke;
    int        stroke_width;
    int        corner_radius;
} dgui_rect_prim;

/* Utility helpers emit into a canvas */
void dgui_draw_rect(struct dcvs_t* c, const dgui_rect_prim* r);
void dgui_draw_text(struct dcvs_t* c, const dgui_text_prim* t);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINO_RENDER_GUI_PRIM_H_INCLUDED */
