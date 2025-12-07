#include "dom_render_debug.h"

void dom_render_debug_draw_crosshair(DomRenderer *r, DomColor color)
{
    dom_i32 cx;
    dom_i32 cy;
    if (!r) {
        return;
    }
    cx = (dom_i32)(r->width / 2u);
    cy = (dom_i32)(r->height / 2u);
    /* Horizontal */
    dom_render_line(r, 0, cy, (dom_i32)r->width, cy, color);
    /* Vertical */
    dom_render_line(r, cx, 0, cx, (dom_i32)r->height, color);
}

void dom_render_debug_draw_grid(DomRenderer *r, dom_i32 spacing, DomColor color)
{
    dom_i32 x;
    dom_i32 y;
    if (!r || spacing <= 0) {
        return;
    }
    for (x = 0; x < (dom_i32)r->width; x += spacing) {
        dom_render_line(r, x, 0, x, (dom_i32)r->height, color);
    }
    for (y = 0; y < (dom_i32)r->height; y += spacing) {
        dom_render_line(r, 0, y, (dom_i32)r->width, y, color);
    }
}
