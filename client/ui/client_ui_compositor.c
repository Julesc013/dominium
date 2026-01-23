/*
Minimal renderer-driven GUI compositor for the client.
*/
#include "client_ui_compositor.h"

#include <string.h>
#include <stdio.h>

void dom_client_ui_compositor_init(dom_client_ui_compositor* ui)
{
    if (!ui) {
        return;
    }
    memset(ui, 0, sizeof(*ui));
    ui->show_overlay = 1;
}

void dom_client_ui_compositor_toggle_overlay(dom_client_ui_compositor* ui)
{
    if (!ui) {
        return;
    }
    ui->show_overlay = ui->show_overlay ? 0 : 1;
}

void dom_client_ui_compositor_set_summary(dom_client_ui_compositor* ui,
                                          uint32_t package_count,
                                          uint32_t instance_count,
                                          int topology_supported,
                                          int snapshot_supported,
                                          int events_supported)
{
    if (!ui) {
        return;
    }
    ui->has_summary = 1;
    ui->package_count = package_count;
    ui->instance_count = instance_count;
    ui->topology_supported = topology_supported ? 1 : 0;
    ui->snapshot_supported = snapshot_supported ? 1 : 0;
    ui->events_supported = events_supported ? 1 : 0;
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
        dom_client_ui_compositor_toggle_overlay(ui);
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

    if (ui && ui->has_summary) {
        char line[128];
        snprintf(line, sizeof(line),
                 "packages=%u instances=%u",
                 (unsigned int)ui->package_count,
                 (unsigned int)ui->instance_count);
        text.x = 16;
        text.y = 56;
        text.text = line;
        text.color = ink;
        d_gfx_cmd_draw_text(buf, &text);

        snprintf(line, sizeof(line),
                 "topology=%s snapshot=%s events=%s",
                 ui->topology_supported ? "ok" : "unsupported",
                 ui->snapshot_supported ? "ok" : "unsupported",
                 ui->events_supported ? "ok" : "unsupported");
        text.x = 16;
        text.y = 76;
        text.text = line;
        text.color = ink;
        d_gfx_cmd_draw_text(buf, &text);
    }
}
