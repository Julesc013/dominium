#include "ega_gfx.h"

#include <stdlib.h>
#include <string.h>

#include "ega_hw.h"

ega_state_t g_ega;

typedef struct ega_cmd_clear_payload_t {
    uint8_t r;
    uint8_t g;
    uint8_t b;
    uint8_t a;
} ega_cmd_clear_payload_t;

typedef struct ega_lines_header_t {
    uint16_t vertex_count;
    uint16_t reserved;
} ega_lines_header_t;

typedef struct ega_line_vertex_t {
    float    x;
    float    y;
    float    z;
    uint32_t color;
} ega_line_vertex_t;

typedef struct ega_camera_payload_t {
    float view[16];
    float proj[16];
    float world[16];
} ega_camera_payload_t;

typedef struct ega_sprite_t {
    int32_t x;
    int32_t y;
    int32_t w;
    int32_t h;
    uint32_t color_rgba;
} ega_sprite_t;

static bool      ega_init(const dgfx_desc* desc);
static void      ega_shutdown(void);
static dgfx_caps ega_get_caps(void);
static void      ega_resize(int width, int height);
static void      ega_begin_frame(void);
static void      ega_execute(const dgfx_cmd_buffer* cmd_buf);
static void      ega_end_frame(void);

static void ega_build_caps(void);
static void ega_init_matrices_and_viewport(void);
static int  ega_round_to_int(float v);

static void ega_cmd_clear(const uint8_t* payload, size_t payload_size);
static void ega_cmd_set_viewport(const uint8_t* payload);
static void ega_cmd_set_camera(const uint8_t* payload);
static void ega_cmd_set_pipeline(const uint8_t* payload);
static void ega_cmd_set_texture(const uint8_t* payload);
static void ega_cmd_draw_sprites(const uint8_t* payload, size_t payload_size);
static void ega_cmd_draw_lines(const uint8_t* payload, size_t payload_size);
static void ega_cmd_draw_meshes(const uint8_t* payload, size_t payload_size);
static void ega_cmd_draw_text(const uint8_t* payload, size_t payload_size);

static const dgfx_backend_vtable g_ega_vtable = {
    ega_init,
    ega_shutdown,
    ega_get_caps,
    ega_resize,
    ega_begin_frame,
    ega_execute,
    ega_end_frame
};

const dgfx_backend_vtable* dgfx_ega_get_vtable(void)
{
    return &g_ega_vtable;
}

static void ega_build_caps(void)
{
    memset(&g_ega.caps, 0, sizeof(g_ega.caps));
    g_ega.caps.name = "ega";
    g_ega.caps.supports_2d = true;
    g_ega.caps.supports_3d = true;
    g_ega.caps.supports_text = false;
    g_ega.caps.supports_rt = false;
    g_ega.caps.supports_alpha = false;
    g_ega.caps.max_texture_size = 0;
}

static void ega_init_matrices_and_viewport(void)
{
    int i;
    for (i = 0; i < 16; ++i) {
        g_ega.view[i] = 0.0f;
        g_ega.proj[i] = 0.0f;
        g_ega.world[i] = 0.0f;
    }
    g_ega.view[0] = g_ega.view[5] = g_ega.view[10] = g_ega.view[15] = 1.0f;
    g_ega.proj[0] = g_ega.proj[5] = g_ega.proj[10] = g_ega.proj[15] = 1.0f;
    g_ega.world[0] = g_ega.world[5] = g_ega.world[10] = g_ega.world[15] = 1.0f;

    g_ega.vp_x = 0;
    g_ega.vp_y = 0;
    g_ega.vp_w = g_ega.width;
    g_ega.vp_h = g_ega.height;
    g_ega.camera2d_x = 0;
    g_ega.camera2d_y = 0;
}

static bool ega_init(const dgfx_desc* desc)
{
    (void)desc;

    if (ega_hw_init() != 0) {
        return false;
    }

    memset(&g_ega, 0, sizeof(g_ega));

    if (ega_hw_set_mode_640x350_16(&g_ega.mode) != 0) {
        ega_shutdown();
        return false;
    }

    g_ega.width = g_ega.mode.width;
    g_ega.height = g_ega.mode.height;

    dgfx_soft_config_get_default(&g_ega.config);
    g_ega.config.color_format = DGFX_SOFT_FMT_8_INDEXED;
    if (g_ega.config.profile == DGFX_SOFT_PROFILE_NULL) {
        g_ega.config.profile = DGFX_SOFT_PROFILE_BALANCED;
    }
    dgfx_soft_config_apply_profile(&g_ega.config, g_ega.config.profile);
    g_ega.config.color_format = DGFX_SOFT_FMT_8_INDEXED;

    if (!soft_fb_create(&g_ega.fb,
                        g_ega.width,
                        g_ega.height,
                        g_ega.config.color_format,
                        g_ega.config.depth_bits,
                        g_ega.config.stencil_bits)) {
        ega_shutdown();
        return false;
    }

    g_ega.depth = g_ega.fb.depth;
    g_ega.stencil = g_ega.fb.stencil;

    ega_init_matrices_and_viewport();
    ega_build_caps();

    g_ega.frame_in_progress = 0;

    return true;
}

static void ega_shutdown(void)
{
    soft_fb_destroy(&g_ega.fb);
    g_ega.depth = NULL;
    g_ega.stencil = NULL;

    ega_hw_restore_text_mode();

    memset(&g_ega, 0, sizeof(g_ega));
}

static dgfx_caps ega_get_caps(void)
{
    return g_ega.caps;
}

static void ega_resize(int width, int height)
{
    (void)width;
    (void)height;
}

static void ega_begin_frame(void)
{
    if (!g_ega.fb.color) {
        return;
    }

    g_ega.frame_in_progress = 1;

    soft_raster_clear_color(&g_ega.fb, 0u, 0u, 0u, 255u);
    if (g_ega.config.features.enable_depth && g_ega.fb.depth) {
        soft_raster_clear_depth(&g_ega.fb, 1.0f);
    }
    if (g_ega.config.features.enable_stencil && g_ega.fb.stencil) {
        soft_raster_clear_stencil(&g_ega.fb, 0u);
    }
}

static void ega_end_frame(void)
{
    if (!g_ega.frame_in_progress) {
        return;
    }
    if (!g_ega.fb.color) {
        g_ega.frame_in_progress = 0;
        return;
    }

    ega_hw_blit_640x350_16(
        g_ega.fb.color,
        (uint16_t)g_ega.width,
        (uint16_t)g_ega.height,
        (uint16_t)g_ega.fb.stride_bytes);

    g_ega.frame_in_progress = 0;
}

static void ega_cmd_clear(const uint8_t* payload, size_t payload_size)
{
    uint8_t r = 0u;
    uint8_t g = 0u;
    uint8_t b = 0u;
    uint8_t a = 255u;

    if (payload && payload_size >= sizeof(ega_cmd_clear_payload_t)) {
        ega_cmd_clear_payload_t clr;
        memcpy(&clr, payload, sizeof(clr));
        r = clr.r;
        g = clr.g;
        b = clr.b;
        a = clr.a;
    }

    soft_raster_clear_color(&g_ega.fb, r, g, b, a);
    if (g_ega.config.features.enable_depth && g_ega.fb.depth) {
        soft_raster_clear_depth(&g_ega.fb, 1.0f);
    }
    if (g_ega.config.features.enable_stencil && g_ega.fb.stencil) {
        soft_raster_clear_stencil(&g_ega.fb, 0u);
    }
}

static void ega_cmd_set_viewport(const uint8_t* payload)
{
    (void)payload;
    g_ega.vp_x = 0;
    g_ega.vp_y = 0;
    g_ega.vp_w = g_ega.fb.width;
    g_ega.vp_h = g_ega.fb.height;
}

static void ega_cmd_set_camera(const uint8_t* payload)
{
    if (payload) {
        const ega_camera_payload_t* cam = (const ega_camera_payload_t*)payload;
        memcpy(g_ega.view, cam->view, sizeof(g_ega.view));
        memcpy(g_ega.proj, cam->proj, sizeof(g_ega.proj));
        memcpy(g_ega.world, cam->world, sizeof(g_ega.world));
    }
}

static void ega_cmd_set_pipeline(const uint8_t* payload)
{
    (void)payload;
}

static void ega_cmd_set_texture(const uint8_t* payload)
{
    (void)payload;
}

static int ega_round_to_int(float v)
{
    return (int)((v >= 0.0f) ? (v + 0.5f) : (v - 0.5f));
}

static void ega_cmd_draw_sprites(const uint8_t* payload, size_t payload_size)
{
    size_t count;
    size_t i;

    if (!payload || payload_size < sizeof(ega_sprite_t)) {
        return;
    }

    count = payload_size / sizeof(ega_sprite_t);
    for (i = 0u; i < count; ++i) {
        const ega_sprite_t* spr = ((const ega_sprite_t*)payload) + i;
        int x = spr->x + g_ega.camera2d_x;
        int y = spr->y + g_ega.camera2d_y;
        soft_raster_fill_rect_2d(&g_ega.fb, x, y, spr->w, spr->h, spr->color_rgba);
    }
}

static void ega_cmd_draw_lines(const uint8_t* payload, size_t payload_size)
{
    ega_lines_header_t header;
    size_t required;
    const ega_line_vertex_t* verts;
    size_t i;

    if (!payload || payload_size < sizeof(header)) {
        return;
    }

    memcpy(&header, payload, sizeof(header));
    required = sizeof(header) + ((size_t)header.vertex_count * sizeof(ega_line_vertex_t));
    if (payload_size < required || header.vertex_count < 2u) {
        return;
    }

    verts = (const ega_line_vertex_t*)(payload + sizeof(header));
    for (i = 0u; (i + 1u) < (size_t)header.vertex_count; i += 2u) {
        int x0 = ega_round_to_int(verts[i].x) + g_ega.camera2d_x;
        int y0 = ega_round_to_int(verts[i].y) + g_ega.camera2d_y;
        int x1 = ega_round_to_int(verts[i + 1u].x) + g_ega.camera2d_x;
        int y1 = ega_round_to_int(verts[i + 1u].y) + g_ega.camera2d_y;
        soft_raster_draw_line_2d(&g_ega.fb, x0, y0, x1, y1, verts[i].color);
    }
}

static void ega_cmd_draw_meshes(const uint8_t* payload, size_t payload_size)
{
    (void)payload;
    (void)payload_size;
}

static void ega_cmd_draw_text(const uint8_t* payload, size_t payload_size)
{
    (void)payload;
    (void)payload_size;
}

static void ega_execute(const dgfx_cmd_buffer* cmd_buf)
{
    const uint8_t* ptr;
    const uint8_t* end;
    size_t header_size;

    if (!cmd_buf || !cmd_buf->data || cmd_buf->size == 0u) {
        return;
    }
    if (!g_ega.fb.color || !g_ega.frame_in_progress) {
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

        switch (cmd->op) {
        case DGFX_CMD_CLEAR:
            ega_cmd_clear(payload, payload_size);
            break;
        case DGFX_CMD_SET_VIEWPORT:
            ega_cmd_set_viewport(payload);
            break;
        case DGFX_CMD_SET_CAMERA:
            ega_cmd_set_camera(payload);
            break;
        case DGFX_CMD_SET_PIPELINE:
            ega_cmd_set_pipeline(payload);
            break;
        case DGFX_CMD_SET_TEXTURE:
            ega_cmd_set_texture(payload);
            break;
        case DGFX_CMD_DRAW_SPRITES:
            ega_cmd_draw_sprites(payload, payload_size);
            break;
        case DGFX_CMD_DRAW_MESHES:
            ega_cmd_draw_meshes(payload, payload_size);
            break;
        case DGFX_CMD_DRAW_LINES:
            ega_cmd_draw_lines(payload, payload_size);
            break;
        case DGFX_CMD_DRAW_TEXT:
            ega_cmd_draw_text(payload, payload_size);
            break;
        default:
            break;
        }

        ptr += total_size;
    }
}
