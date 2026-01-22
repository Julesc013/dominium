/*
Minimal renderer-driven GUI compositor for the client.
*/
#include "client_ui_compositor.h"

#include <string.h>

void dom_client_ui_compositor_init(dom_client_ui_compositor* ui)
{
    if (!ui) {
        return;
    }
    memset(ui, 0, sizeof(*ui));
    ui->show_overlay = 1;
}

void dom_client_ui_compositor_handle_event(dom_client_ui_compositor* ui, const dsys_event* ev)
{
    int key;
    if (!ui || !ev) {
        return;
    }
    if (ev->type != DSYS_EVENT_KEY_DOWN) {
        return;
    }
    key = ev->payload.key.key;
    if (key == 'h' || key == 'H') {
        ui->show_overlay = ui->show_overlay ? 0 : 1;
    }
}

void dom_client_ui_compositor_draw(dom_client_ui_compositor* ui,
                                   d_gfx_cmd_buffer* buf,
                                   int fb_w,
                                   int fb_h)
{
    d_gfx_viewport vp;
    d_gfx_draw_text_cmd text;
    d_gfx_color clear = { 0xff, 0x12, 0x12, 0x18 };
    d_gfx_color ink = { 0xff, 0xee, 0xee, 0xee };
    int width = (fb_w > 0) ? fb_w : 800;
    int height = (fb_h > 0) ? fb_h : 600;

    if (!buf) {
        return;
    }
    d_gfx_cmd_clear(buf, clear);
    vp.x = 0;
    vp.y = 0;
    vp.w = width;
    vp.h = height;
    d_gfx_cmd_set_viewport(buf, &vp);

    if (!ui || !ui->show_overlay) {
        return;
    }

    text.x = 16;
    text.y = 16;
    text.text = "Dominium client GUI";
    text.color = ink;
    d_gfx_cmd_draw_text(buf, &text);

    text.x = 16;
    text.y = 36;
    text.text = "H: toggle overlay  B: borderless";
    text.color = ink;
    d_gfx_cmd_draw_text(buf, &text);
}
