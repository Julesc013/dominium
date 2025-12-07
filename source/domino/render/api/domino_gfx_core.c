#include "domino_gfx_internal.h"

#include <stdlib.h>
#include <string.h>

#include "../soft/soft_internal.h"

/*------------------------------------------------------------
 * Soft backend forward declarations
 *------------------------------------------------------------*/
int  domino_gfx_soft_create(domino_sys_context* sys,
                            const domino_gfx_desc* desc,
                            domino_gfx_device** out_dev);

/*------------------------------------------------------------
 * Backend selection
 *------------------------------------------------------------*/
static domino_gfx_backend domino_gfx_choose_backend(domino_sys_context* sys,
                                                    const domino_gfx_desc* desc)
{
    domino_gfx_backend backend = DOMINO_GFX_BACKEND_SOFT;
    (void)sys;
    if (desc && desc->backend != DOMINO_GFX_BACKEND_AUTO) {
        return desc->backend;
    }
    /* For now, prefer software; future passes can probe sys for GPU support. */
    return backend;
}

/*------------------------------------------------------------
 * Public API
 *------------------------------------------------------------*/
int domino_gfx_create_device(domino_sys_context* sys,
                             const domino_gfx_desc* desc,
                             domino_gfx_device** out_dev)
{
    domino_gfx_desc local_desc;
    domino_gfx_backend backend;
    if (!out_dev) return -1;
    *out_dev = NULL;

    memset(&local_desc, 0, sizeof(local_desc));
    local_desc.backend = DOMINO_GFX_BACKEND_AUTO;
    local_desc.profile_hint = DOMINO_GFX_PROFILE_FIXED;
    local_desc.width = 640;
    local_desc.height = 480;
    local_desc.fullscreen = 0;
    local_desc.vsync = 0;
    local_desc.framebuffer_fmt = DOMINO_PIXFMT_A8R8G8B8;

    if (desc) {
        local_desc = *desc;
        if (local_desc.width == 0) local_desc.width = 640;
        if (local_desc.height == 0) local_desc.height = 480;
        if (local_desc.framebuffer_fmt == 0) {
            local_desc.framebuffer_fmt = DOMINO_PIXFMT_A8R8G8B8;
        }
    }

    backend = domino_gfx_choose_backend(sys, &local_desc);
    switch (backend) {
    case DOMINO_GFX_BACKEND_SOFT:
    case DOMINO_GFX_BACKEND_AUTO: /* auto resolves to soft for now */
        return domino_gfx_soft_create(sys, &local_desc, out_dev);
    default:
        /* TODO: implement GPU backends */
        return domino_gfx_soft_create(sys, &local_desc, out_dev);
    }
}

void domino_gfx_destroy_device(domino_gfx_device* dev)
{
    if (!dev) return;
    if (dev->vt && dev->vt->destroy) {
        dev->vt->destroy(dev);
    }
}

int domino_gfx_begin_frame(domino_gfx_device* dev)
{
    if (!dev || !dev->vt || !dev->vt->begin_frame) return -1;
    return dev->vt->begin_frame(dev);
}

int domino_gfx_end_frame(domino_gfx_device* dev)
{
    if (!dev || !dev->vt || !dev->vt->end_frame) return -1;
    return dev->vt->end_frame(dev);
}

int domino_gfx_clear(domino_gfx_device* dev,
                     float r, float g, float b, float a)
{
    if (!dev || !dev->vt || !dev->vt->clear) return -1;
    return dev->vt->clear(dev, r, g, b, a);
}

int domino_gfx_draw_filled_rect(domino_gfx_device* dev,
                                const domino_gfx_rect* rect,
                                float r, float g, float b, float a)
{
    if (!dev || !dev->vt || !dev->vt->draw_rect) return -1;
    return dev->vt->draw_rect(dev, rect, r, g, b, a);
}

int domino_gfx_texture_create(domino_gfx_device* dev,
                              const domino_gfx_texture_desc* desc,
                              domino_gfx_texture** out_tex)
{
    if (!dev || !dev->vt || !dev->vt->tex_create) return -1;
    return dev->vt->tex_create(dev, desc, out_tex);
}

void domino_gfx_texture_destroy(domino_gfx_texture* tex)
{
    if (!tex) return;
    /* Texture destruction is backend-specific; stored on the object */
    free(tex);
}

int domino_gfx_texture_update(domino_gfx_texture* tex,
                              int x, int y, int w, int h,
                              const void* pixels, int pitch_bytes)
{
    (void)x; (void)y; (void)w; (void)h; (void)pixels; (void)pitch_bytes;
    if (!tex) return -1;
    /* stubbed for now */
    return -1;
}

int domino_gfx_draw_texture(domino_gfx_device* dev,
                            domino_gfx_texture* tex,
                            const domino_gfx_rect* dst_rect,
                            const domino_gfx_uv_rect* src_uv)
{
    if (!dev || !dev->vt || !dev->vt->draw_texture) return -1;
    return dev->vt->draw_texture(dev, tex, dst_rect, src_uv);
}

int domino_gfx_font_draw_text(domino_gfx_device* dev,
                              domino_gfx_font* font,
                              float x, float y,
                              const char* text,
                              float r, float g, float b, float a)
{
    if (!dev || !dev->vt || !dev->vt->draw_text) return -1;
    return dev->vt->draw_text(dev, font, x, y, text, r, g, b, a);
}
