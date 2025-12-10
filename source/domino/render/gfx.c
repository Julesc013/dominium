#include "domino/gfx.h"

#include <stdlib.h>
#include <string.h>
#include "domino/canvas.h"
#include "domino/sys.h"
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
        return dgfx_soft_get_vtable();
    case DGFX_BACKEND_DX7: {
        extern const dgfx_backend_vtable *dgfx_dx7_get_vtable(void);
        return dgfx_dx7_get_vtable();
    }
    case DGFX_BACKEND_DX9: {
        extern const dgfx_backend_vtable *dgfx_dx9_get_vtable(void);
        return dgfx_dx9_get_vtable();
    }
    case DGFX_BACKEND_DX11: {
        extern const dgfx_backend_vtable *dgfx_dx11_get_vtable(void);
        return dgfx_dx11_get_vtable();
    }
    case DGFX_BACKEND_VK1: {
        extern const dgfx_backend_vtable *dgfx_vk1_get_vtable(void);
        return dgfx_vk1_get_vtable();
    }
    case DGFX_BACKEND_GL1: {
        extern const dgfx_backend_vtable *dgfx_gl1_get_vtable(void);
        return dgfx_gl1_get_vtable();
    }
    case DGFX_BACKEND_GL2: {
        extern const dgfx_backend_vtable *dgfx_gl2_get_vtable(void);
        return dgfx_gl2_get_vtable();
    }
    case DGFX_BACKEND_QUICKDRAW: {
        extern const dgfx_backend_vtable *dgfx_quickdraw_get_vtable(void);
        return dgfx_quickdraw_get_vtable();
    }
    case DGFX_BACKEND_QUARTZ: {
        extern const dgfx_backend_vtable *dgfx_quartz_get_vtable(void);
        return dgfx_quartz_get_vtable();
    }
    case DGFX_BACKEND_METAL: {
        extern const dgfx_backend_vtable *dgfx_metal_get_vtable(void);
        return dgfx_metal_get_vtable();
    }
    case DGFX_BACKEND_GDI: {
        extern const dgfx_backend_vtable *dgfx_gdi_get_vtable(void);
        return dgfx_gdi_get_vtable();
    }
    case DGFX_BACKEND_VESA: {
        extern const dgfx_backend_vtable *dgfx_vesa_get_vtable(void);
        return dgfx_vesa_get_vtable();
    }
    case DGFX_BACKEND_VGA: {
        extern const dgfx_backend_vtable *dgfx_vga_get_vtable(void);
        return dgfx_vga_get_vtable();
    }
    case DGFX_BACKEND_CGA: {
        extern const dgfx_backend_vtable *dgfx_cga_get_vtable(void);
        return dgfx_cga_get_vtable();
    }
    case DGFX_BACKEND_EGA: {
        extern const dgfx_backend_vtable *dgfx_ega_get_vtable(void);
        return dgfx_ega_get_vtable();
    }
    case DGFX_BACKEND_XGA: {
        extern const dgfx_backend_vtable *dgfx_xga_get_vtable(void);
        return dgfx_xga_get_vtable();
    }
    case DGFX_BACKEND_HERC: {
        extern const dgfx_backend_vtable *dgfx_herc_get_vtable(void);
        return dgfx_herc_get_vtable();
    }
    case DGFX_BACKEND_MDA: {
        extern const dgfx_backend_vtable *dgfx_mda_get_vtable(void);
        return dgfx_mda_get_vtable();
    }
    case DGFX_BACKEND_X11: {
        extern const dgfx_backend_vtable *dgfx_x11_get_vtable(void);
        return dgfx_x11_get_vtable();
    }
    case DGFX_BACKEND_COCOA: {
        extern const dgfx_backend_vtable *dgfx_cocoa_get_vtable(void);
        return dgfx_cocoa_get_vtable();
    }
    case DGFX_BACKEND_SDL1: {
        extern const dgfx_backend_vtable *dgfx_sdl1_get_vtable(void);
        return dgfx_sdl1_get_vtable();
    }
    case DGFX_BACKEND_SDL2: {
        extern const dgfx_backend_vtable *dgfx_sdl2_get_vtable(void);
        return dgfx_sdl2_get_vtable();
    }
    case DGFX_BACKEND_WAYLAND: {
        extern const dgfx_backend_vtable *dgfx_wayland_get_vtable(void);
        return dgfx_wayland_get_vtable();
    }
    case DGFX_BACKEND_NULL: {
        extern const dgfx_backend_vtable *dgfx_null_get_vtable(void);
        return dgfx_null_get_vtable();
    }
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
