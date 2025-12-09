#ifndef DOMINO_GFX_H_INCLUDED
#define DOMINO_GFX_H_INCLUDED

/* Domino Render API - C89 friendly */

#include <stddef.h>
#include <stdint.h>
#include "domino/sys.h"

#ifdef __cplusplus
extern "C" {
#endif

/*
 * Domino Graphics IR (dgfx_*)
 * ----------------------------
 * This header exposes the public command IR, capabilities, and backend
 * dispatch table used by both the canvas recorder and the software backend.
 * The layout intentionally stays POD-only for determinism and portability.
 */

/* Backend selector */
typedef enum dgfx_backend_t {
    DGFX_BACKEND_SOFT = 0,
    DGFX_BACKEND_DX7,
    DGFX_BACKEND_DX9,
    DGFX_BACKEND_DX11,
    DGFX_BACKEND_VK1,
    DGFX_BACKEND_GL1,
    DGFX_BACKEND_GL2,
    DGFX_BACKEND_QUICKDRAW,
    DGFX_BACKEND_QUARTZ,
    DGFX_BACKEND_METAL,
    DGFX_BACKEND_GDI,
    DGFX_BACKEND_VESA,
    DGFX_BACKEND_VGA,
    DGFX_BACKEND_CGA,
    DGFX_BACKEND_EGA,
    DGFX_BACKEND_XGA,
    DGFX_BACKEND_HERC,
    DGFX_BACKEND_MDA,
    DGFX_BACKEND_X11,
    DGFX_BACKEND_COCOA,
    DGFX_BACKEND_SDL1,
    DGFX_BACKEND_SDL2,
    DGFX_BACKEND_WAYLAND,
    DGFX_BACKEND_NULL,
    DGFX_BACKEND_COUNT,
    /* Legacy alias kept for compatibility; maps to SOFT. */
    DGFX_BACKEND_SOFT8 = DGFX_BACKEND_SOFT
} dgfx_backend_t;

/* Legacy name preserved for existing code */
typedef dgfx_backend_t dgfx_backend;

/* Command opcodes */
typedef enum dgfx_cmd_opcode_t {
    DGFX_CMD_NOP = 0,
    DGFX_CMD_CLEAR,
    DGFX_CMD_SET_VIEWPORT,
    DGFX_CMD_SET_CAMERA,
    DGFX_CMD_SET_PIPELINE,
    DGFX_CMD_SET_TEXTURE,
    DGFX_CMD_DRAW_SPRITES,
    DGFX_CMD_DRAW_LINES,
    DGFX_CMD_DRAW_MESHES,
    DGFX_CMD_DRAW_TEXT
} dgfx_cmd_opcode_t;
typedef dgfx_cmd_opcode_t dgfx_opcode; /* legacy alias */

/* Command header */
typedef struct dgfx_cmd_header_t {
    uint16_t opcode;        /* dgfx_cmd_opcode_t */
    uint16_t payload_size;  /* payload bytes following the header */
    uint32_t size;          /* total size in bytes: header + payload */
} dgfx_cmd_header;

typedef dgfx_cmd_header dgfx_cmd;

/* IR payload structs */
typedef struct dgfx_viewport_t {
    int32_t x;
    int32_t y;
    int32_t w;
    int32_t h;
} dgfx_viewport_t;

typedef struct dgfx_camera_t {
    float view[16];
    float proj[16];
    float world[16];
} dgfx_camera_t;

typedef struct dgfx_sprite_t {
    int32_t x;
    int32_t y;
    int32_t w;
    int32_t h;
    uint32_t color_rgba;
    /* texture handle can be layered later */
} dgfx_sprite_t;

typedef struct dgfx_line_segment_t {
    int32_t x0, y0;
    int32_t x1, y1;
    uint32_t color_rgba;
    int32_t thickness;
} dgfx_line_segment_t;

typedef struct dgfx_mesh_draw_t {
    const float *positions;   /* xyz positions */
    const float *normals;     /* optional */
    const float *uvs;         /* optional */
    const uint32_t *indices;  /* triangles */
    uint32_t vertex_count;
    uint32_t index_count;
    uint32_t flags;
    uint32_t reserved;
} dgfx_mesh_draw_t;

typedef struct dgfx_text_draw_t {
    int32_t x;
    int32_t y;
    uint32_t color_rgba;
    const char *utf8_text; /* null-terminated */
} dgfx_text_draw_t;

/* Caps and descriptor */
typedef struct dgfx_caps_t {
    int supports_2d;
    int supports_3d;
    int supports_vector;
    int supports_raster;
    int supports_text;

    int max_viewports;
    int max_render_targets;

    int reserved[8];

    /* Legacy capability fields kept for ABI stability */
    const char* name;
    bool        supports_rt;
    bool        supports_alpha;
    int32_t     max_texture_size;
} dgfx_caps;

typedef struct dgfx_desc_t {
    dgfx_backend_t backend;
    void *native_window; /* may be NULL for headless/soft */
    int width;
    int height;
    int fullscreen;
    int vsync;

    /* Legacy field preserved for older callers */
    dsys_window* window;
} dgfx_desc;

/* Command buffer */
typedef struct dgfx_cmd_buffer_t {
    uint8_t *data;
    uint32_t size;     /* number of bytes used */
    uint32_t capacity; /* total buffer capacity */
} dgfx_cmd_buffer;

/* Backend vtable */
typedef struct dgfx_backend_vtable_t {
    bool      (*init)(const dgfx_desc *desc);
    void      (*shutdown)(void);
    dgfx_caps (*get_caps)(void);

    void      (*resize)(int width, int height);

    void      (*begin_frame)(void);
    void      (*execute)(const dgfx_cmd_buffer *cmd);
    void      (*end_frame)(void);
} dgfx_backend_vtable;

/* Front-end API */
bool      dgfx_init(const dgfx_desc *desc);
void      dgfx_shutdown(void);
dgfx_caps dgfx_get_caps(void);

void      dgfx_resize(int width, int height);

void      dgfx_begin_frame(void);
void      dgfx_execute(const dgfx_cmd_buffer *cmd);
void      dgfx_end_frame(void);

dgfx_cmd_buffer *dgfx_get_frame_cmd_buffer(void);

/* Convenience: retrieve the reusable frame canvas */
struct dcvs_t;
struct dcvs_t *dgfx_get_frame_canvas(void);

/* Legacy helpers kept for callers that still build buffers manually */
void          dgfx_cmd_buffer_reset(dgfx_cmd_buffer* buf);
bool          dgfx_cmd_emit(dgfx_cmd_buffer* buf,
                            uint16_t opcode,
                            const void* payload,
                            uint16_t payload_size);

/*------------------------------------------------------------
 * Legacy Domino Render API (domino_gfx_*)
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

int domino_gfx_create_device(domino_sys_context* sys,
                             const domino_gfx_desc* desc,
                             domino_gfx_device** out_dev);

void domino_gfx_destroy_device(domino_gfx_device* dev);

int domino_gfx_begin_frame(domino_gfx_device* dev);
int domino_gfx_end_frame(domino_gfx_device* dev);

int domino_gfx_clear(domino_gfx_device* dev,
                     float r, float g, float b, float a);

int domino_gfx_draw_filled_rect(domino_gfx_device* dev,
                                const domino_gfx_rect* rect,
                                float r, float g, float b, float a);

int domino_gfx_texture_create(domino_gfx_device* dev,
                              const domino_gfx_texture_desc* desc,
                              domino_gfx_texture** out_tex);

void domino_gfx_texture_destroy(domino_gfx_texture* tex);

int domino_gfx_texture_update(domino_gfx_texture* tex,
                              int x, int y, int w, int h,
                              const void* pixels, int pitch_bytes);

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
