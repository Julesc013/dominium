#ifndef DOMINO_GFX_H_INCLUDED
#define DOMINO_GFX_H_INCLUDED

/* Domino Render API - C89 friendly */

#include <stddef.h>
#include <stdint.h>
#include "domino/sys.h"

#ifdef __cplusplus
extern "C" {
#endif

/*------------------------------------------------------------
 * New Domino rendering ABI (dgfx_*)
 *------------------------------------------------------------*/
typedef struct dsys_context dsys_context;
typedef struct dom_canvas   dom_canvas;
typedef struct dgfx_device  dgfx_device;

typedef enum dgfx_backend {
    DGFX_BACKEND_DEFAULT = 0,
    DGFX_BACKEND_SOFTWARE,
    DGFX_BACKEND_NULL,
    DGFX_BACKEND_EXTERNAL
} dgfx_backend;

typedef enum dgfx_present_mode {
    DGFX_PRESENT_VSYNC = 0,
    DGFX_PRESENT_IMMEDIATE = 1
} dgfx_present_mode;

typedef struct dgfx_device_desc {
    uint32_t      struct_size;
    uint32_t      struct_version;
    dsys_context* sys;
    dgfx_backend  backend;
    uint32_t      width;
    uint32_t      height;
    uint32_t      framebuffer_format;
    int           fullscreen;
    int           vsync;
    dgfx_present_mode present_mode;
} dgfx_device_desc;

int           dgfx_create_device(const dgfx_device_desc* desc, dgfx_device** out_device);
void          dgfx_destroy_device(dgfx_device* device);
dgfx_backend  dgfx_get_backend(dgfx_device* device);
int           dgfx_resize(dgfx_device* device, uint32_t width, uint32_t height);
int           dgfx_begin_frame(dgfx_device* device);
int           dgfx_end_frame(dgfx_device* device);
int           dgfx_get_canvas(dgfx_device* device, dom_canvas** out_canvas);

/*------------------------------------------------------------
 * Legacy Domino Render API (domino_gfx_*)
 *------------------------------------------------------------*/
/*------------------------------------------------------------
 * Core types
 *------------------------------------------------------------*/
typedef struct domino_gfx_device  domino_gfx_device;
typedef struct domino_gfx_texture domino_gfx_texture;
typedef struct domino_gfx_font    domino_gfx_font;

typedef enum {
    DOMINO_GFX_BACKEND_AUTO = 0,
    DOMINO_GFX_BACKEND_SOFT,
    DOMINO_GFX_BACKEND_GL1,
    DOMINO_GFX_BACKEND_GL2,
    DOMINO_GFX_BACKEND_GLES,
    DOMINO_GFX_BACKEND_DX7,
    DOMINO_GFX_BACKEND_DX9,
    DOMINO_GFX_BACKEND_DX11,
    DOMINO_GFX_BACKEND_VK1,
    DOMINO_GFX_BACKEND_METAL
} domino_gfx_backend;

typedef enum {
    DOMINO_GFX_PROFILE_TINY,
    DOMINO_GFX_PROFILE_FIXED,
    DOMINO_GFX_PROFILE_PROGRAMMABLE
} domino_gfx_profile;

typedef enum {
    DOMINO_PIXFMT_INDEXED8,
    DOMINO_PIXFMT_RGB565,
    DOMINO_PIXFMT_X8R8G8B8,
    DOMINO_PIXFMT_A8R8G8B8
} domino_pixfmt;

typedef struct domino_gfx_desc {
    domino_gfx_backend backend;
    domino_gfx_profile profile_hint;

    int width;
    int height;
    int fullscreen;
    int vsync;

    domino_pixfmt framebuffer_fmt;
} domino_gfx_desc;

typedef struct domino_gfx_rect {
    float x, y, w, h;
} domino_gfx_rect;

typedef struct domino_gfx_uv_rect {
    float u0, v0, u1, v1;
} domino_gfx_uv_rect;

typedef struct domino_gfx_texture_desc {
    int width;
    int height;
    domino_pixfmt format;
    const void* initial_pixels; /* nullable */
} domino_gfx_texture_desc;

/*------------------------------------------------------------
 * Lifecycle
 *------------------------------------------------------------*/
int domino_gfx_create_device(domino_sys_context* sys,
                             const domino_gfx_desc* desc,
                             domino_gfx_device** out_dev);

void domino_gfx_destroy_device(domino_gfx_device* dev);

/*------------------------------------------------------------
 * Frame control
 *------------------------------------------------------------*/
int domino_gfx_begin_frame(domino_gfx_device* dev);
int domino_gfx_end_frame(domino_gfx_device* dev);

/*------------------------------------------------------------
 * Clear / primitive 2D
 *------------------------------------------------------------*/
int domino_gfx_clear(domino_gfx_device* dev,
                     float r, float g, float b, float a);

int domino_gfx_draw_filled_rect(domino_gfx_device* dev,
                                const domino_gfx_rect* rect,
                                float r, float g, float b, float a);

/*------------------------------------------------------------
 * Textures
 *------------------------------------------------------------*/
int domino_gfx_texture_create(domino_gfx_device* dev,
                              const domino_gfx_texture_desc* desc,
                              domino_gfx_texture** out_tex);

void domino_gfx_texture_destroy(domino_gfx_texture* tex);

int domino_gfx_texture_update(domino_gfx_texture* tex,
                              int x, int y, int w, int h,
                              const void* pixels, int pitch_bytes);

/*------------------------------------------------------------
 * Blit / text
 *------------------------------------------------------------*/
int domino_gfx_draw_texture(domino_gfx_device* dev,
                            domino_gfx_texture* tex,
                            const domino_gfx_rect* dst_rect,
                            const domino_gfx_uv_rect* src_uv);

int domino_gfx_font_draw_text(domino_gfx_device* dev,
                              domino_gfx_font* font,
                              float x, float y,
                              const char* text,
                              float r, float g, float b, float a);

#ifdef __cplusplus
}
#endif

#endif /* DOMINO_GFX_H_INCLUDED */
