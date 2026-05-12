/*
FILE: source/domino/render/gui_prim.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / render/gui_prim
RESPONSIBILITY: Implements `gui_prim`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include "domino/render/gui_prim.h"
#include "domino/canvas.h"
#include <string.h>

static uint32_t dgui_pack(const dgui_color* c) {
    return ((uint32_t)(c->a) << 24) |
           ((uint32_t)(c->r) << 16) |
           ((uint32_t)(c->g) << 8)  |
           ((uint32_t)(c->b));
}

void dgui_draw_rect(struct dcvs_t* c, const dgui_rect_prim* r) {
    dgfx_sprite_t spr;
    if (!c || !r) return;
    spr.x = r->rect.x;
    spr.y = r->rect.y;
    spr.w = r->rect.w;
    spr.h = r->rect.h;
    spr.color_rgba = dgui_pack(&r->fill);
    dcvs_draw_sprite(c, &spr);
}

void dgui_draw_text(struct dcvs_t* c, const dgui_text_prim* t) {
    dgfx_text_draw_t txt;
    if (!c || !t || !t->text) return;
    txt.x = t->x;
    txt.y = t->y;
    txt.color_rgba = dgui_pack(&t->color);
    txt.utf8_text = t->text;
    dcvs_draw_text(c, &txt);
}
