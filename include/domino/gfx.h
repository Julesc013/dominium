/* Domino minimal graphics IR (C89). */
#ifndef D_GFX_H
#define D_GFX_H
#ifndef DOMINO_GFX_H_INCLUDED
#define DOMINO_GFX_H_INCLUDED
#endif

#include "domino/core/types.h"
#include "domino/core/fixed.h"

#ifdef __cplusplus
extern "C" {
#endif

/* Minimal IR opcodes for this prompt. Extend later, but don't break these. */
typedef enum d_gfx_opcode_e {
    D_GFX_OP_CLEAR = 0,
    D_GFX_OP_SET_VIEWPORT,
    D_GFX_OP_SET_CAMERA,
    D_GFX_OP_DRAW_RECT,
    D_GFX_OP_DRAW_TEXT
} d_gfx_opcode;

/* Simple color type: ARGB 8-8-8-8 */
typedef struct d_gfx_color_s {
    u8 a, r, g, b;
} d_gfx_color;

/* Viewport in pixels for now. */
typedef struct d_gfx_viewport_s {
    i32 x;
    i32 y;
    i32 w;
    i32 h;
} d_gfx_viewport;

/* Camera parameters – minimal for now. */
typedef struct d_gfx_camera_s {
    q16_16 pos_x, pos_y, pos_z;
    q16_16 dir_x, dir_y, dir_z;
    q16_16 up_x,  up_y,  up_z;
    q16_16 fov;          /* or ignored in this prompt */
} d_gfx_camera;

/* Command buffer element types */

typedef struct d_gfx_cmd_clear_s {
    d_gfx_color color;
} d_gfx_clear_cmd;

typedef struct d_gfx_cmd_set_viewport_s {
    d_gfx_viewport vp;
} d_gfx_set_viewport_cmd;

typedef struct d_gfx_cmd_set_camera_s {
    d_gfx_camera cam;
} d_gfx_set_camera_cmd;

typedef struct d_gfx_cmd_draw_rect_s {
    i32 x, y, w, h;
    d_gfx_color color;
} d_gfx_draw_rect_cmd;

typedef struct d_gfx_cmd_draw_text_s {
    i32 x, y;
    const char *text;    /* pointer is valid only during frame; backend may copy if needed */
    d_gfx_color color;
} d_gfx_draw_text_cmd;

typedef struct d_gfx_cmd_s {
    d_gfx_opcode opcode;
    union {
        d_gfx_clear_cmd        clear;
        d_gfx_set_viewport_cmd viewport;
        d_gfx_set_camera_cmd   camera;
        d_gfx_draw_rect_cmd    rect;
        d_gfx_draw_text_cmd    text;
    } u;
} d_gfx_cmd;

/* Command buffer opaque handle */
typedef struct d_gfx_cmd_buffer_s {
    d_gfx_cmd *cmds;
    u32        count;
    u32        capacity;
} d_gfx_cmd_buffer;

/* Minimal API */

/* Initialize graphics system for a named backend (e.g. "soft"). */
int d_gfx_init(const char *backend_name);

/* Shutdown graphics system. */
void d_gfx_shutdown(void);

/* Allocate / reset command buffer for current frame. */
d_gfx_cmd_buffer *d_gfx_cmd_buffer_begin(void);
void              d_gfx_cmd_buffer_end(d_gfx_cmd_buffer *buf);

/* Append commands. These are helpers; you may also expose a raw append if needed. */
void d_gfx_cmd_clear(d_gfx_cmd_buffer *buf, d_gfx_color color);
void d_gfx_cmd_set_viewport(d_gfx_cmd_buffer *buf, const d_gfx_viewport *vp);
void d_gfx_cmd_set_camera(d_gfx_cmd_buffer *buf, const d_gfx_camera *cam);
void d_gfx_cmd_draw_rect(d_gfx_cmd_buffer *buf, const d_gfx_draw_rect_cmd *rect);
void d_gfx_cmd_draw_text(d_gfx_cmd_buffer *buf, const d_gfx_draw_text_cmd *text);

/* Submit the command buffer to currently active backend. */
void d_gfx_submit(d_gfx_cmd_buffer *buf);

/* Present the rendered frame (swap buffers / blit). */
void d_gfx_present(void);

/* Optional helper: query current backbuffer size (soft backend only). */
void d_gfx_get_surface_size(i32 *out_w, i32 *out_h);

/* ------------------------------------------------------------
 * Legacy dgfx compatibility (thin wrappers over the minimal API)
 * ------------------------------------------------------------ */

typedef d_gfx_cmd_buffer dgfx_cmd_buffer;
typedef d_gfx_viewport   dgfx_viewport_t;
typedef d_gfx_camera     dgfx_camera_t;

typedef enum dgfx_backend_t {
    DGFX_BACKEND_SOFT = 0,
    DGFX_BACKEND_NULL = 100,
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
    DGFX_BACKEND_COUNT
} dgfx_backend_t;

typedef enum dgfx_cmd_opcode_t {
    DGFX_CMD_NOP = 0,
    DGFX_CMD_CLEAR = D_GFX_OP_CLEAR,
    DGFX_CMD_SET_VIEWPORT = D_GFX_OP_SET_VIEWPORT,
    DGFX_CMD_SET_CAMERA = D_GFX_OP_SET_CAMERA,
    DGFX_CMD_SET_PIPELINE,
    DGFX_CMD_SET_TEXTURE,
    DGFX_CMD_DRAW_SPRITES = D_GFX_OP_DRAW_RECT,
    DGFX_CMD_DRAW_LINES,
    DGFX_CMD_DRAW_MESHES,
    DGFX_CMD_DRAW_TEXT = D_GFX_OP_DRAW_TEXT
} dgfx_cmd_opcode_t;

typedef struct dgfx_sprite_t {
    i32 x;
    i32 y;
    i32 w;
    i32 h;
    u32 color_rgba;
} dgfx_sprite_t;

typedef struct dgfx_text_draw_t {
    i32 x;
    i32 y;
    u32 color_rgba;
    const char *utf8_text;
} dgfx_text_draw_t;

typedef struct dgfx_line_segment_t {
    i32 x0, y0;
    i32 x1, y1;
    u32 color_rgba;
    i32 thickness;
} dgfx_line_segment_t;

typedef struct dgfx_desc_t {
    dgfx_backend_t backend;
    void *native_window; /* ignored by the minimal slice */
    int width;
    int height;
    int fullscreen;
    int vsync;
    void *window;
} dgfx_desc;

int               dgfx_init(const dgfx_desc *desc);
void              dgfx_shutdown(void);
void              dgfx_begin_frame(void);
void              dgfx_execute(const dgfx_cmd_buffer *cmd);
void              dgfx_end_frame(void);
dgfx_cmd_buffer  *dgfx_get_frame_cmd_buffer(void);
void              dgfx_cmd_buffer_reset(dgfx_cmd_buffer *buf);
int               dgfx_cmd_emit(dgfx_cmd_buffer *buf,
                                u16 opcode,
                                const void *payload,
                                u16 payload_size);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* D_GFX_H */
