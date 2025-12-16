/*
FILE: source/domino/render/cga/cga_gfx.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / render/cga/cga_gfx
RESPONSIBILITY: Implements `cga_gfx`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include "cga_gfx.h"

#include <stdlib.h>
#include <string.h>

#include "domino/sys.h"
#include "cga_hw.h"

cga_state_t g_cga;

typedef struct cga_cmd_clear_payload_t {
    uint8_t r;
    uint8_t g;
    uint8_t b;
    uint8_t a;
} cga_cmd_clear_payload_t;

typedef struct cga_lines_header_t {
    uint16_t vertex_count;
    uint16_t reserved;
} cga_lines_header_t;

typedef struct cga_line_vertex_t {
    float    x;
    float    y;
    float    z;
    uint32_t color;
} cga_line_vertex_t;

typedef struct cga_sprite_t {
    int32_t  x;
    int32_t  y;
    int32_t  w;
    int32_t  h;
    uint32_t color_rgba;
} cga_sprite_t;

typedef struct cga_camera_payload_t {
    int32_t offset_x;
    int32_t offset_y;
} cga_camera_payload_t;

static bool      cga_init(const dgfx_desc* desc);
static void      cga_shutdown(void);
static dgfx_caps cga_get_caps(void);
static void      cga_resize(int width, int height);
static void      cga_begin_frame(void);
static void      cga_execute(const dgfx_cmd_buffer* cmd_buf);
static void      cga_end_frame(void);

static void cga_build_caps(void);
static void cga_clear(uint8_t color_idx);
static uint8_t cga_quantize_rgba(uint32_t rgba);
static void cga_fill_rect(int x, int y, int w, int h, uint8_t color_idx);
static void cga_draw_line(int x0, int y0, int x1, int y1, uint8_t color_idx);
static int cga_round_to_int(float v);

static void cga_cmd_clear(const uint8_t* payload, size_t payload_size);
static void cga_cmd_set_viewport(const uint8_t* payload);
static void cga_cmd_set_camera(const uint8_t* payload);
static void cga_cmd_set_pipeline(const uint8_t* payload);
static void cga_cmd_set_texture(const uint8_t* payload);
static void cga_cmd_draw_sprites(const uint8_t* payload, size_t payload_size);
static void cga_cmd_draw_lines(const uint8_t* payload, size_t payload_size);
static void cga_cmd_draw_meshes(const uint8_t* payload, size_t payload_size);
static void cga_cmd_draw_text(const uint8_t* payload, size_t payload_size);

static const dgfx_backend_vtable g_cga_vtable = {
    cga_init,
    cga_shutdown,
    cga_get_caps,
    cga_resize,
    cga_begin_frame,
    cga_execute,
    cga_end_frame
};

const dgfx_backend_vtable* dgfx_cga_get_vtable(void)
{
    return &g_cga_vtable;
}

static void cga_build_caps(void)
{
    memset(&g_cga.caps, 0, sizeof(g_cga.caps));
    g_cga.caps.name = "cga";
    g_cga.caps.supports_2d = true;
    g_cga.caps.supports_3d = false;
    g_cga.caps.supports_text = false;
    g_cga.caps.supports_rt = false;
    g_cga.caps.supports_alpha = false;
    g_cga.caps.max_texture_size = 0;
}

static bool cga_init(const dgfx_desc* desc)
{
    (void)desc;

    if (cga_hw_init() != 0) {
        return false;
    }

    memset(&g_cga, 0, sizeof(g_cga));

    if (cga_hw_set_mode_320x200_4col(0u, &g_cga.mode) != 0) {
        cga_shutdown();
        return false;
    }

    g_cga.width = g_cga.mode.width;
    g_cga.height = g_cga.mode.height;
    g_cga.stride_bytes = g_cga.width;

    g_cga.color = (uint8_t*)malloc((size_t)g_cga.stride_bytes * (size_t)g_cga.height);
    if (!g_cga.color) {
        cga_shutdown();
        return false;
    }
    memset(g_cga.color, 0, (size_t)g_cga.stride_bytes * (size_t)g_cga.height);

    g_cga.camera_offset_x = 0;
    g_cga.camera_offset_y = 0;

    cga_build_caps();

    g_cga.frame_in_progress = 0;

    return true;
}

static void cga_shutdown(void)
{
    if (g_cga.color) {
        free(g_cga.color);
        g_cga.color = NULL;
    }
    if (g_cga.depth) {
        free(g_cga.depth);
        g_cga.depth = NULL;
    }
    if (g_cga.stencil) {
        free(g_cga.stencil);
        g_cga.stencil = NULL;
    }

    cga_hw_restore_text_mode();

    memset(&g_cga, 0, sizeof(g_cga));
}

static dgfx_caps cga_get_caps(void)
{
    return g_cga.caps;
}

static void cga_resize(int width, int height)
{
    (void)width;
    (void)height;
    /* CGA mode is fixed; no dynamic resize in v1. */
}

static void cga_begin_frame(void)
{
    if (!g_cga.color) {
        return;
    }

    cga_clear(0u);
    g_cga.frame_in_progress = 1;
}

static void cga_end_frame(void)
{
    if (!g_cga.frame_in_progress) {
        return;
    }
    if (!g_cga.color) {
        g_cga.frame_in_progress = 0;
        return;
    }

    cga_hw_blit_320x200_4col(
        g_cga.color,
        (uint16_t)g_cga.width,
        (uint16_t)g_cga.height,
        (uint16_t)g_cga.stride_bytes);

    g_cga.frame_in_progress = 0;
}

static uint8_t cga_quantize_rgba(uint32_t rgba)
{
    uint8_t r;
    uint8_t g;
    uint8_t b;
    int intensity;

    r = (uint8_t)((rgba >> 16) & 0xffu);
    g = (uint8_t)((rgba >> 8) & 0xffu);
    b = (uint8_t)(rgba & 0xffu);

    intensity = (int)((r * 30 + g * 59 + b * 11) / 100);
    if (intensity < 0) intensity = 0;
    if (intensity > 255) intensity = 255;

    return (uint8_t)(intensity >> 6);
}

static void cga_clear(uint8_t color_idx)
{
    if (!g_cga.color) {
        return;
    }
    memset(g_cga.color, color_idx, (size_t)g_cga.stride_bytes * (size_t)g_cga.height);
}

static void cga_fill_rect(int x, int y, int w, int h, uint8_t color_idx)
{
    int x0;
    int y0;
    int x1;
    int y1;
    int iy;

    if (!g_cga.color || w <= 0 || h <= 0) {
        return;
    }

    x0 = x;
    y0 = y;
    x1 = x + w;
    y1 = y + h;

    if (x0 < 0) x0 = 0;
    if (y0 < 0) y0 = 0;
    if (x1 > g_cga.width)  x1 = g_cga.width;
    if (y1 > g_cga.height) y1 = g_cga.height;

    for (iy = y0; iy < y1; ++iy) {
        uint8_t* row;
        int ix;

        row = g_cga.color + (size_t)iy * (size_t)g_cga.stride_bytes;
        for (ix = x0; ix < x1; ++ix) {
            row[ix] = color_idx;
        }
    }
}

static int cga_round_to_int(float v)
{
    return (int)((v >= 0.0f) ? (v + 0.5f) : (v - 0.5f));
}

static void cga_draw_line(int x0, int y0, int x1, int y1, uint8_t color_idx)
{
    int dx;
    int dy;
    int sx;
    int sy;
    int err;
    int e2;

    if (!g_cga.color) {
        return;
    }

    dx = (x1 > x0) ? (x1 - x0) : (x0 - x1);
    dy = (y1 > y0) ? (y1 - y0) : (y0 - y1);
    sx = (x0 < x1) ? 1 : -1;
    sy = (y0 < y1) ? 1 : -1;
    err = dx - dy;

    for (;;) {
        if (x0 >= 0 && x0 < g_cga.width && y0 >= 0 && y0 < g_cga.height) {
            g_cga.color[(size_t)y0 * (size_t)g_cga.stride_bytes + (size_t)x0] = color_idx;
        }

        if (x0 == x1 && y0 == y1) {
            break;
        }

        e2 = err << 1;

        if (e2 > -dy) {
            err -= dy;
            x0 += sx;
        }
        if (e2 < dx) {
            err += dx;
            y0 += sy;
        }
    }
}

static void cga_cmd_clear(const uint8_t* payload, size_t payload_size)
{
    uint8_t color_idx;
    color_idx = 0u;

    if (payload && payload_size >= sizeof(cga_cmd_clear_payload_t)) {
        cga_cmd_clear_payload_t clr;
        memcpy(&clr, payload, sizeof(clr));
        color_idx = cga_quantize_rgba(
            ((uint32_t)clr.r << 16) |
            ((uint32_t)clr.g << 8) |
            ((uint32_t)clr.b));
    }

    cga_clear(color_idx);
}

static void cga_cmd_set_viewport(const uint8_t* payload)
{
    (void)payload;
    /* Viewport not modeled in the CGA backend v1. */
}

static void cga_cmd_set_camera(const uint8_t* payload)
{
    if (payload) {
        const cga_camera_payload_t* cam;
        cam = (const cga_camera_payload_t*)payload;
        g_cga.camera_offset_x = cam->offset_x;
        g_cga.camera_offset_y = cam->offset_y;
    }
}

static void cga_cmd_set_pipeline(const uint8_t* payload)
{
    (void)payload;
    /* Pipelines are not modeled in this backend. */
}

static void cga_cmd_set_texture(const uint8_t* payload)
{
    (void)payload;
    /* Textures are not implemented for CGA. */
}

static void cga_cmd_draw_sprites(const uint8_t* payload, size_t payload_size)
{
    size_t count;
    size_t i;

    if (!payload || payload_size < sizeof(cga_sprite_t)) {
        return;
    }
    if (!g_cga.color) {
        return;
    }

    count = payload_size / sizeof(cga_sprite_t);

    for (i = 0u; i < count; ++i) {
        const cga_sprite_t* spr;
        uint8_t idx;
        int x;
        int y;

        spr = ((const cga_sprite_t*)payload) + i;
        idx = cga_quantize_rgba(spr->color_rgba);
        x = spr->x + g_cga.camera_offset_x;
        y = spr->y + g_cga.camera_offset_y;

        cga_fill_rect(x, y, spr->w, spr->h, idx);
    }
}

static void cga_cmd_draw_lines(const uint8_t* payload, size_t payload_size)
{
    cga_lines_header_t header;
    size_t required;
    const cga_line_vertex_t* verts;
    size_t i;

    if (!payload || payload_size < sizeof(header)) {
        return;
    }
    if (!g_cga.color) {
        return;
    }

    memcpy(&header, payload, sizeof(header));
    required = sizeof(header) + ((size_t)header.vertex_count * sizeof(cga_line_vertex_t));
    if (payload_size < required || header.vertex_count < 2u) {
        return;
    }

    verts = (const cga_line_vertex_t*)(payload + sizeof(header));

    for (i = 1u; i < (size_t)header.vertex_count; i += 2u) {
        const cga_line_vertex_t* v0;
        const cga_line_vertex_t* v1;
        uint8_t idx;
        int x0;
        int y0;
        int x1;
        int y1;

        v0 = &verts[i - 1u];
        v1 = &verts[i];
        idx = cga_quantize_rgba(v0->color);

        x0 = cga_round_to_int(v0->x) + g_cga.camera_offset_x;
        y0 = cga_round_to_int(v0->y) + g_cga.camera_offset_y;
        x1 = cga_round_to_int(v1->x) + g_cga.camera_offset_x;
        y1 = cga_round_to_int(v1->y) + g_cga.camera_offset_y;

        cga_draw_line(x0, y0, x1, y1, idx);
    }
}

static void cga_cmd_draw_meshes(const uint8_t* payload, size_t payload_size)
{
    (void)payload;
    (void)payload_size;
    /* 3D mesh path is not implemented in the CGA backend MVP. */
}

static void cga_cmd_draw_text(const uint8_t* payload, size_t payload_size)
{
    (void)payload;
    (void)payload_size;
    /* Text rendering is not implemented for CGA. */
}

static void cga_execute(const dgfx_cmd_buffer* cmd_buf)
{
    const uint8_t* ptr;
    const uint8_t* end;
    size_t header_size;

    if (!cmd_buf || !cmd_buf->data || cmd_buf->size == 0u) {
        return;
    }
    if (!g_cga.color || !g_cga.frame_in_progress) {
        return;
    }

    header_size = sizeof(dgfx_cmd);
    ptr = cmd_buf->data;
    end = cmd_buf->data + cmd_buf->size;

    while (ptr + header_size <= end) {
        const dgfx_cmd* cmd;
        const uint8_t* payload;
        size_t payload_size;
        size_t total_size;

        cmd = (const dgfx_cmd*)ptr;
        payload_size = cmd->payload_size;
        total_size = header_size + payload_size;
        if (ptr + total_size > end) {
            break;
        }
        payload = ptr + header_size;

        switch (cmd->opcode) {
        case DGFX_CMD_CLEAR:
            cga_cmd_clear(payload, payload_size);
            break;
        case DGFX_CMD_SET_VIEWPORT:
            cga_cmd_set_viewport(payload);
            break;
        case DGFX_CMD_SET_CAMERA:
            cga_cmd_set_camera(payload);
            break;
        case DGFX_CMD_SET_PIPELINE:
            cga_cmd_set_pipeline(payload);
            break;
        case DGFX_CMD_SET_TEXTURE:
            cga_cmd_set_texture(payload);
            break;
        case DGFX_CMD_DRAW_SPRITES:
            cga_cmd_draw_sprites(payload, payload_size);
            break;
        case DGFX_CMD_DRAW_MESHES:
            cga_cmd_draw_meshes(payload, payload_size);
            break;
        case DGFX_CMD_DRAW_LINES:
            cga_cmd_draw_lines(payload, payload_size);
            break;
        case DGFX_CMD_DRAW_TEXT:
            cga_cmd_draw_text(payload, payload_size);
            break;
        default:
            break;
        }

        ptr += total_size;
    }
}
