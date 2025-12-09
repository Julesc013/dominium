#include "domino/gfx.h"

#include <stdlib.h>
#include <string.h>
#include "domino/canvas.h"
#include "domino/sys.h"

static const dgfx_backend_vtable *g_dgfx = NULL;
static dgfx_caps g_caps;
static dcvs *g_frame_canvas = NULL;

/* Forward decl for soft backend vtable */
extern const dgfx_backend_vtable *dgfx_soft_get_vtable(void);

static const dgfx_backend_vtable *dgfx_choose_backend(dgfx_backend_t backend)
{
    switch (backend) {
    case DGFX_BACKEND_SOFT:
    case DGFX_BACKEND_SOFT8:
        return dgfx_soft_get_vtable();
    default:
        /* Temporary fallback to software until HW backends are rebuilt. */
        return dgfx_soft_get_vtable();
    }
}

bool dgfx_init(const dgfx_desc *desc)
{
    dgfx_desc local;
    const dgfx_backend_vtable *vt;

    memset(&local, 0, sizeof(local));
    if (desc) {
        local = *desc;
    }
    if (local.width == 0) local.width = 800;
    if (local.height == 0) local.height = 600;
    if (local.native_window == NULL && local.window) {
        local.native_window = dsys_window_get_native_handle(local.window);
    }

    vt = dgfx_choose_backend(local.backend);
    if (!vt || !vt->init || !vt->init(&local)) {
        return false;
    }

    g_dgfx = vt;
    if (g_dgfx->get_caps) {
        g_caps = g_dgfx->get_caps();
    } else {
        memset(&g_caps, 0, sizeof(g_caps));
    }

    g_frame_canvas = dcvs_create(64u * 1024u);
    if (!g_frame_canvas) {
        if (g_dgfx && g_dgfx->shutdown) {
            g_dgfx->shutdown();
        }
        g_dgfx = NULL;
        return false;
    }

    return true;
}

void dgfx_shutdown(void)
{
    if (g_frame_canvas) {
        dcvs_destroy(g_frame_canvas);
        g_frame_canvas = NULL;
    }
    if (g_dgfx && g_dgfx->shutdown) {
        g_dgfx->shutdown();
    }
    g_dgfx = NULL;
    memset(&g_caps, 0, sizeof(g_caps));
}

dgfx_caps dgfx_get_caps(void)
{
    return g_caps;
}

void dgfx_resize(int width, int height)
{
    if (g_dgfx && g_dgfx->resize) {
        g_dgfx->resize(width, height);
    }
}

void dgfx_begin_frame(void)
{
    if (g_frame_canvas) {
        dcvs_reset(g_frame_canvas);
    }
    if (g_dgfx && g_dgfx->begin_frame) {
        g_dgfx->begin_frame();
    }
}

void dgfx_execute(const dgfx_cmd_buffer *cmd)
{
    if (g_dgfx && g_dgfx->execute) {
        g_dgfx->execute(cmd);
    }
}

void dgfx_end_frame(void)
{
    if (g_dgfx && g_dgfx->end_frame) {
        g_dgfx->end_frame();
    }
}

dgfx_cmd_buffer *dgfx_get_frame_cmd_buffer(void)
{
    if (!g_frame_canvas) {
        return NULL;
    }
    return (dgfx_cmd_buffer *)dcvs_get_cmd_buffer(g_frame_canvas);
}

struct dcvs_t *dgfx_get_frame_canvas(void)
{
    return g_frame_canvas;
}
