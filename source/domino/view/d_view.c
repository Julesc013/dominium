#include <string.h>

#include "d_view.h"

#define D_VIEW_MAX 32u

static d_view_desc g_views[D_VIEW_MAX];
static u32 g_view_count = 0u;
static d_view_id g_view_next_id = 1u;

static void d_view_make_identity(float *m) {
    int i;
    if (!m) {
        return;
    }
    for (i = 0; i < 16; ++i) {
        m[i] = (i % 5 == 0) ? 1.0f : 0.0f;
    }
}

static int d_view_emit_clear(dgfx_cmd_buffer *buf) {
    u32 rgba = 0u;
    if (!buf) {
        return -1;
    }
    return dgfx_cmd_emit(buf, (uint16_t)DGFX_CMD_CLEAR, &rgba, (uint16_t)sizeof(u32)) ? 0 : -1;
}

static int d_view_emit_viewport(dgfx_cmd_buffer *buf, const d_view_desc *view) {
    dgfx_viewport_t vp;
    if (!buf || !view) {
        return -1;
    }
    vp.x = d_q16_16_to_int(view->vp_x);
    vp.y = d_q16_16_to_int(view->vp_y);
    vp.w = d_q16_16_to_int(view->vp_w);
    vp.h = d_q16_16_to_int(view->vp_h);
    return dgfx_cmd_emit(buf, (uint16_t)DGFX_CMD_SET_VIEWPORT, &vp, (uint16_t)sizeof(dgfx_viewport_t)) ? 0 : -1;
}

static int d_view_emit_camera(dgfx_cmd_buffer *buf) {
    dgfx_camera_t cam;
    if (!buf) {
        return -1;
    }
    d_view_make_identity(cam.view);
    d_view_make_identity(cam.proj);
    d_view_make_identity(cam.world);
    return dgfx_cmd_emit(buf, (uint16_t)DGFX_CMD_SET_CAMERA, &cam, (uint16_t)sizeof(dgfx_camera_t)) ? 0 : -1;
}

static void dview_render_world(d_world *w, d_view_desc *view, d_view_frame *frame) {
    (void)w;
    (void)view;
    (void)frame;
    /* TODO: hook world rendering once world draw is available. */
}

static void dview_render_ui(d_view_desc *view, d_view_frame *frame) {
    (void)view;
    (void)frame;
    /* TODO: hook UI overlay rendering once DUI integrates. */
}

d_view_id d_view_create(const d_view_desc *desc) {
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

int d_view_destroy(d_view_id id) {
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

d_view_desc *d_view_get(d_view_id id) {
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
    if (!view || !frame || !frame->cmd_buffer) {
        return -1;
    }

    frame->view = view;
    dgfx_cmd_buffer_reset(frame->cmd_buffer);

    if (d_view_emit_clear(frame->cmd_buffer) != 0) {
        return -1;
    }
    if (d_view_emit_viewport(frame->cmd_buffer, view) != 0) {
        return -1;
    }
    if (d_view_emit_camera(frame->cmd_buffer) != 0) {
        return -1;
    }

    dview_render_world(w, view, frame);
    dview_render_ui(view, frame);
    return 0;
}
