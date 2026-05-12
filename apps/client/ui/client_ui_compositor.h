/*
Client GUI compositor shell (renderer-driven, no OS widgets).
*/
#ifndef DOMINIUM_CLIENT_UI_COMPOSITOR_H
#define DOMINIUM_CLIENT_UI_COMPOSITOR_H

#include "domino/gfx.h"
#include "domino/system/dsys.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct dom_client_ui_compositor {
    int show_overlay;
    int has_summary;
    uint32_t package_count;
    uint32_t instance_count;
    int topology_supported;
    int snapshot_supported;
    int events_supported;
} dom_client_ui_compositor;

void dom_client_ui_compositor_init(dom_client_ui_compositor* ui);
void dom_client_ui_compositor_handle_event(dom_client_ui_compositor* ui, const dsys_event* ev);
void dom_client_ui_compositor_toggle_overlay(dom_client_ui_compositor* ui);
void dom_client_ui_compositor_set_summary(dom_client_ui_compositor* ui,
                                          uint32_t package_count,
                                          uint32_t instance_count,
                                          int topology_supported,
                                          int snapshot_supported,
                                          int events_supported);
void dom_client_ui_compositor_draw(dom_client_ui_compositor* ui,
                                   d_gfx_cmd_buffer* buf,
                                   int fb_w,
                                   int fb_h);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_CLIENT_UI_COMPOSITOR_H */
