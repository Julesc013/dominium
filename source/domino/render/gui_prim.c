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
