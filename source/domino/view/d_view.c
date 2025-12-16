/*
FILE: source/domino/view/d_view.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / view/d_view
RESPONSIBILITY: Implements `d_view`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include <string.h>

#include "d_view.h"

#define D_VIEW_MAX 32u
#define D_VIEW_DEFAULT_WIDTH 800
#define D_VIEW_DEFAULT_HEIGHT 600

static d_view_desc g_views[D_VIEW_MAX];
static u32 g_view_count = 0u;
static d_view_id g_view_next_id = 1u;

static i32 d_view_q16_mul_int(q16_16 v, i32 m)
{
    i64 tmp;
    tmp = (i64)v * (i64)m;
    return (i32)(tmp >> 16);
}

static void d_view_map_viewport(const d_view_desc *view, d_gfx_viewport *out)
{
    i32 width = 0;
    i32 height = 0;
    if (!view || !out) {
        return;
    }
    d_gfx_get_surface_size(&width, &height);
    if (width <= 0) width = D_VIEW_DEFAULT_WIDTH;
    if (height <= 0) height = D_VIEW_DEFAULT_HEIGHT;

    out->x = d_view_q16_mul_int(view->vp_x, width);
    out->y = d_view_q16_mul_int(view->vp_y, height);
    out->w = d_view_q16_mul_int(view->vp_w, width);
    out->h = d_view_q16_mul_int(view->vp_h, height);
    if (out->w <= 0) out->w = width;
    if (out->h <= 0) out->h = height;
}

static void dview_render_world(d_world *w, d_view_desc *view, d_view_frame *frame)
{
    (void)w;
    (void)view;
    (void)frame;
    /* TODO: hook world rendering once world draw is available. */
}

d_view_id d_view_create(const d_view_desc *desc)
{
    d_view_id id;
    if (!desc) {
        return (d_view_id)0;
    }
    if (g_view_count >= D_VIEW_MAX) {
        return (d_view_id)0;
    }

    id = g_view_next_id++;
    g_views[g_view_count] = *desc;
    g_views[g_view_count].id = id;
    g_view_count += 1u;
    return id;
}

int d_view_destroy(d_view_id id)
{
    u32 i;
    for (i = 0u; i < g_view_count; ++i) {
        if (g_views[i].id == id) {
            if (i != g_view_count - 1u) {
                g_views[i] = g_views[g_view_count - 1u];
            }
            g_view_count -= 1u;
            return 0;
        }
    }
    return -1;
}

d_view_desc *d_view_get(d_view_id id)
{
    u32 i;
    for (i = 0u; i < g_view_count; ++i) {
        if (g_views[i].id == id) {
            return &g_views[i];
        }
    }
    return (d_view_desc *)0;
}

int d_view_render(
    d_world      *w,
    d_view_desc  *view,
    d_view_frame *frame
) {
    d_gfx_viewport vp;
    d_gfx_color clear_color;

    if (!view || !frame || !frame->cmd_buffer) {
        return -1;
    }

    frame->view = view;
    frame->cmd_buffer->count = 0u;

    clear_color.a = 0xffu;
    clear_color.r = 0x12u;
    clear_color.g = 0x12u;
    clear_color.b = 0x20u;
    d_gfx_cmd_clear(frame->cmd_buffer, clear_color);

    d_view_map_viewport(view, &vp);
    d_gfx_cmd_set_viewport(frame->cmd_buffer, &vp);
    {
        d_gfx_camera cam;
        cam.pos_x = view->camera.pos_x;
        cam.pos_y = view->camera.pos_y;
        cam.pos_z = view->camera.pos_z;
        cam.dir_x = view->camera.dir_x;
        cam.dir_y = view->camera.dir_y;
        cam.dir_z = view->camera.dir_z;
        cam.up_x = view->camera.up_x;
        cam.up_y = view->camera.up_y;
        cam.up_z = view->camera.up_z;
        cam.fov = view->camera.fov;
        d_gfx_cmd_set_camera(frame->cmd_buffer, &cam);
    }

    dview_render_world(w, view, frame);
    return 0;
}
