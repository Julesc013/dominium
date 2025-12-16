/*
FILE: source/domino/render/api/core/dom_render_debug.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / render/api/core/dom_render_debug
RESPONSIBILITY: Implements `dom_render_debug`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
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
