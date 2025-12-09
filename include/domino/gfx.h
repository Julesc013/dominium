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
 * Domino rendering IR (dgfx_*) - opaque NULL backend stub
 *------------------------------------------------------------*/
typedef struct dgfx_context dgfx_context;

typedef enum dgfx_backend {
    DGFX_BACKEND_NULL = 0,
    DGFX_BACKEND_SOFT8,
    DGFX_BACKEND_GL2,
    DGFX_BACKEND_DX9,
    DGFX_BACKEND_VK1,
    DGFX_BACKEND_DX7,
    DGFX_BACKEND_DX11,
    DGFX_BACKEND_METAL,
    DGFX_BACKEND_QUARTZ,
    DGFX_BACKEND_QUICKDRAW,
    DGFX_BACKEND_GDI
} dgfx_backend;

typedef struct dgfx_caps {
    const char* name;
    bool        supports_2d;
    bool        supports_3d;
    bool        supports_text;
    bool        supports_rt;
    bool        supports_alpha;
    int32_t     max_texture_size;
} dgfx_caps;

typedef struct dgfx_desc {
    dgfx_backend backend;
    dsys_window* window;
    int32_t      width;
    int32_t      height;
    int          vsync;
} dgfx_desc;

typedef enum dgfx_opcode {
    DGFX_CMD_CLEAR = 0,
    DGFX_CMD_SET_VIEWPORT,
    DGFX_CMD_SET_CAMERA,
    DGFX_CMD_SET_PIPELINE,
    DGFX_CMD_SET_TEXTURE,
    DGFX_CMD_DRAW_SPRITES,
    DGFX_CMD_DRAW_MESHES,
    DGFX_CMD_DRAW_LINES,
    DGFX_CMD_DRAW_TEXT
} dgfx_opcode;

typedef struct dgfx_cmd {
    dgfx_opcode op;
    uint16_t    payload_size;
} dgfx_cmd;

typedef struct dgfx_cmd_buffer {
    uint8_t* data;
    uint16_t size;
    uint16_t capacity;
} dgfx_cmd_buffer;

typedef struct dgfx_backend_vtable {
    /* lifecycle */
    bool       (*init)(const dgfx_desc* desc);
    void       (*shutdown)(void);
    dgfx_caps  (*get_caps)(void);

    /* resize / framebuffer */
    void       (*resize)(int width, int height);

    /* frame */
    void       (*begin_frame)(void);
    void       (*execute)(const dgfx_cmd_buffer* buf);
    void       (*end_frame)(void);
} dgfx_backend_vtable;

dgfx_context* dgfx_init(const dgfx_desc* desc);
void          dgfx_shutdown(dgfx_context* ctx);
dgfx_caps     dgfx_get_caps(dgfx_context* ctx);
void          dgfx_resize(dgfx_context* ctx, int32_t width, int32_t height);
void          dgfx_cmd_buffer_reset(dgfx_cmd_buffer* buf);
bool          dgfx_cmd_emit(dgfx_cmd_buffer* buf,
                            dgfx_opcode op,
                            const void* payload,
                            uint16_t payload_size);
void          dgfx_begin_frame(dgfx_context* ctx);
void          dgfx_execute(dgfx_context* ctx, const dgfx_cmd_buffer* buf);
void          dgfx_end_frame(dgfx_context* ctx);

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
