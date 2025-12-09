#include "vga_gfx.h"
#include "vga_hw.h"

#include <stdlib.h>
#include <string.h>

vga_state_t g_vga;

typedef struct vga_cmd_clear_payload_t {
    uint8_t r;
    uint8_t g;
    uint8_t b;
    uint8_t a;
} vga_cmd_clear_payload_t;

typedef struct vga_lines_header_t {
    uint16_t vertex_count;
    uint16_t reserved;
} vga_lines_header_t;

typedef struct vga_line_vertex_t {
    float    x;
    float    y;
    float    z;
    uint32_t color;
} vga_line_vertex_t;

typedef struct vga_camera_payload_t {
    float view[16];
    float proj[16];
    float world[16];
} vga_camera_payload_t;

typedef struct vga_sprite_t {
    int32_t x;
    int32_t y;
    int32_t w;
    int32_t h;
    uint32_t color_rgba;
} vga_sprite_t;

static bool      vga_init(const dgfx_desc* desc);
static void      vga_shutdown(void);
static dgfx_caps vga_get_caps(void);
static void      vga_resize(int width, int height);
static void      vga_begin_frame(void);
static void      vga_execute(const dgfx_cmd_buffer* cmd_buf);
static void      vga_end_frame(void);

static void vga_build_caps(void);
static void vga_init_matrices_and_viewport(void);
static int  vga_round_to_int(float v);

static void vga_cmd_clear(const uint8_t* payload, size_t payload_size);
static void vga_cmd_set_viewport(const uint8_t* payload);
static void vga_cmd_set_camera(const uint8_t* payload);
static void vga_cmd_set_pipeline(const uint8_t* payload);
static void vga_cmd_set_texture(const uint8_t* payload);
static void vga_cmd_draw_sprites(const uint8_t* payload, size_t payload_size);
static void vga_cmd_draw_lines(const uint8_t* payload, size_t payload_size);
static void vga_cmd_draw_meshes(const uint8_t* payload, size_t payload_size);
static void vga_cmd_draw_text(const uint8_t* payload, size_t payload_size);

static const dgfx_backend_vtable g_vga_vtable = {
    vga_init,
    vga_shutdown,
    vga_get_caps,
    vga_resize,
    vga_begin_frame,
    vga_execute,
    vga_end_frame
};

const dgfx_backend_vtable* dgfx_vga_get_vtable(void)
{
    return &g_vga_vtable;
}

static void vga_build_caps(void)
{
    memset(&g_vga.caps, 0, sizeof(g_vga.caps));
    g_vga.caps.name = "vga";
    g_vga.caps.supports_2d = g_vga.config.features.enable_2d ? true : false;
    g_vga.caps.supports_3d = g_vga.config.features.enable_3d ? true : false;
    g_vga.caps.supports_text = false;
    g_vga.caps.supports_rt = g_vga.config.features.enable_raster ? true : false;
    g_vga.caps.supports_alpha = false;
    g_vga.caps.max_texture_size = 0;
}

static void vga_init_matrices_and_viewport(void)
{
    int i;
    for (i = 0; i < 16; ++i) {
        g_vga.view[i] = 0.0f;
        g_vga.proj[i] = 0.0f;
        g_vga.world[i] = 0.0f;
    }
    g_vga.view[0] = g_vga.view[5] = g_vga.view[10] = g_vga.view[15] = 1.0f;
    g_vga.proj[0] = g_vga.proj[5] = g_vga.proj[10] = g_vga.proj[15] = 1.0f;
    g_vga.world[0] = g_vga.world[5] = g_vga.world[10] = g_vga.world[15] = 1.0f;

    g_vga.vp_x = 0;
    g_vga.vp_y = 0;
    g_vga.vp_w = g_vga.width;
    g_vga.vp_h = g_vga.height;
    g_vga.camera2d_x = 0;
    g_vga.camera2d_y = 0;
}

static bool vga_init(const dgfx_desc* desc)
{
    dgfx_soft_format requested_fmt;

    if (!desc) {
        return false;
    }

    if (vga_hw_init() != 0) {
        return false;
    }

    memset(&g_vga, 0, sizeof(g_vga));

    if (vga_hw_set_mode_13h(&g_vga.mode) != 0) {
        vga_shutdown();
        return false;
    }

    g_vga.width = g_vga.mode.width;
    g_vga.height = g_vga.mode.height;

    dgfx_soft_config_get_default(&g_vga.config);
    dgfx_soft_config_load_from_env(&g_vga.config);
    dgfx_soft_config_load_from_file(&g_vga.config, NULL);
    if (g_vga.config.profile == DGFX_SOFT_PROFILE_NULL) {
        g_vga.config.profile = DGFX_SOFT_PROFILE_BALANCED;
    }
    requested_fmt = DGFX_SOFT_FMT_8_INDEXED;
    dgfx_soft_config_apply_profile(&g_vga.config, g_vga.config.profile);
    g_vga.config.color_format = requested_fmt;

    if (!soft_fb_create(&g_vga.fb,
                        g_vga.width,
                        g_vga.height,
                        g_vga.config.color_format,
                        g_vga.config.depth_bits,
                        g_vga.config.stencil_bits)) {
        vga_shutdown();
        return false;
    }

    g_vga.depth = g_vga.fb.depth;
    g_vga.stencil = g_vga.fb.stencil;
    g_vga.vram_ptr = vga_hw_get_vram_ptr();

    vga_init_matrices_and_viewport();
    vga_build_caps();

    g_vga.frame_in_progress = 0;

    return true;
}

static void vga_shutdown(void)
{
    if (g_vga.fb.color || g_vga.fb.depth || g_vga.fb.stencil) {
        soft_fb_destroy(&g_vga.fb);
    }

    vga_hw_restore_text_mode();

    memset(&g_vga, 0, sizeof(g_vga));
}

static dgfx_caps vga_get_caps(void)
{
    return g_vga.caps;
}

static void vga_resize(int width, int height)
{
    (void)width;
    (void)height;
    /* VGA mode 13h is fixed; resizing would require a mode switch. */
}

static void vga_begin_frame(void)
{
    if (!g_vga.fb.color) {
        return;
    }

    g_vga.frame_in_progress = 1;

    soft_raster_clear_color(&g_vga.fb, 0u, 0u, 0u, 255u);
    if (g_vga.config.features.enable_depth && g_vga.fb.depth) {
        soft_raster_clear_depth(&g_vga.fb, 1.0f);
    }
    if (g_vga.config.features.enable_stencil && g_vga.fb.stencil) {
        soft_raster_clear_stencil(&g_vga.fb, 0u);
    }
}

static void vga_end_frame(void)
{
    if (!g_vga.frame_in_progress) {
        return;
    }
    if (!g_vga.fb.color) {
        g_vga.frame_in_progress = 0;
        return;
    }

    vga_hw_blit_13h(
        g_vga.fb.color,
        (uint16_t)g_vga.width,
        (uint16_t)g_vga.height,
        (uint16_t)g_vga.fb.stride_bytes);

    g_vga.frame_in_progress = 0;
}

static void vga_cmd_clear(const uint8_t* payload, size_t payload_size)
{
    vga_cmd_clear_payload_t clr;
    uint8_t r = 0u;
    uint8_t g = 0u;
    uint8_t b = 0u;
    uint8_t a = 255u;

    if (payload && payload_size >= sizeof(clr)) {
        memcpy(&clr, payload, sizeof(clr));
        r = clr.r;
        g = clr.g;
        b = clr.b;
        a = clr.a;
    }

    soft_raster_clear_color(&g_vga.fb, r, g, b, a);
    if (g_vga.config.features.enable_depth && g_vga.fb.depth) {
        soft_raster_clear_depth(&g_vga.fb, 1.0f);
    }
    if (g_vga.config.features.enable_stencil && g_vga.fb.stencil) {
        soft_raster_clear_stencil(&g_vga.fb, 0u);
    }
}

static void vga_cmd_set_viewport(const uint8_t* payload)
{
    (void)payload;
    g_vga.vp_x = 0;
    g_vga.vp_y = 0;
    g_vga.vp_w = g_vga.fb.width;
    g_vga.vp_h = g_vga.fb.height;
}

static void vga_cmd_set_camera(const uint8_t* payload)
{
    if (payload) {
        const vga_camera_payload_t* cam = (const vga_camera_payload_t*)payload;
        memcpy(g_vga.view, cam->view, sizeof(g_vga.view));
        memcpy(g_vga.proj, cam->proj, sizeof(g_vga.proj));
        memcpy(g_vga.world, cam->world, sizeof(g_vga.world));
    }
}

static void vga_cmd_set_pipeline(const uint8_t* payload)
{
    (void)payload;
}

static void vga_cmd_set_texture(const uint8_t* payload)
{
    (void)payload;
}

static void vga_cmd_draw_sprites(const uint8_t* payload, size_t payload_size)
{
    size_t count;
    size_t i;

    if (!payload || payload_size < sizeof(vga_sprite_t)) {
        return;
    }
    if (!g_vga.config.features.enable_2d) {
        return;
    }

    count = payload_size / sizeof(vga_sprite_t);
    for (i = 0u; i < count; ++i) {
        const vga_sprite_t* spr = ((const vga_sprite_t*)payload) + i;
        int x = spr->x + g_vga.camera2d_x;
        int y = spr->y + g_vga.camera2d_y;
        soft_raster_fill_rect_2d(&g_vga.fb, x, y, spr->w, spr->h, spr->color_rgba);
    }
}

static int vga_round_to_int(float v)
{
    return (int)((v >= 0.0f) ? (v + 0.5f) : (v - 0.5f));
}

static void vga_cmd_draw_lines(const uint8_t* payload, size_t payload_size)
{
    vga_lines_header_t header;
    const vga_line_vertex_t* verts;
    size_t required;
    size_t i;

    if (!payload || payload_size < sizeof(header)) {
        return;
    }
    if (!g_vga.config.features.enable_vector) {
        return;
    }

    memcpy(&header, payload, sizeof(header));
    required = sizeof(header) + ((size_t)header.vertex_count * sizeof(vga_line_vertex_t));
    if (payload_size < required || header.vertex_count < 2u) {
        return;
    }

    verts = (const vga_line_vertex_t*)(payload + sizeof(header));
    for (i = 0u; (i + 1u) < (size_t)header.vertex_count; i += 2u) {
        int x0 = vga_round_to_int(verts[i].x) + g_vga.camera2d_x;
        int y0 = vga_round_to_int(verts[i].y) + g_vga.camera2d_y;
        int x1 = vga_round_to_int(verts[i + 1u].x) + g_vga.camera2d_x;
        int y1 = vga_round_to_int(verts[i + 1u].y) + g_vga.camera2d_y;
        soft_raster_draw_line_2d(&g_vga.fb, x0, y0, x1, y1, verts[i].color);
    }
}

static void vga_cmd_draw_meshes(const uint8_t* payload, size_t payload_size)
{
    (void)payload;
    (void)payload_size;
    /* Future: decode mesh payload and rasterize triangles. */
}

static void vga_cmd_draw_text(const uint8_t* payload, size_t payload_size)
{
    (void)payload;
    (void)payload_size;
    /* Text rendering stub for v1. */
}

static void vga_execute(const dgfx_cmd_buffer* cmd_buf)
{
    const uint8_t* ptr;
    const uint8_t* end;
    size_t header_size;

    if (!cmd_buf || !cmd_buf->data || cmd_buf->size == 0u) {
        return;
    }
    if (!g_vga.frame_in_progress) {
        return;
    }
    if (!g_vga.fb.color) {
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
            vga_cmd_clear(payload, payload_size);
            break;
        case DGFX_CMD_SET_VIEWPORT:
            vga_cmd_set_viewport(payload);
            break;
        case DGFX_CMD_SET_CAMERA:
            vga_cmd_set_camera(payload);
            break;
        case DGFX_CMD_SET_PIPELINE:
            vga_cmd_set_pipeline(payload);
            break;
        case DGFX_CMD_SET_TEXTURE:
            vga_cmd_set_texture(payload);
            break;
        case DGFX_CMD_DRAW_SPRITES:
            vga_cmd_draw_sprites(payload, payload_size);
            break;
        case DGFX_CMD_DRAW_MESHES:
            vga_cmd_draw_meshes(payload, payload_size);
            break;
        case DGFX_CMD_DRAW_LINES:
            vga_cmd_draw_lines(payload, payload_size);
            break;
        case DGFX_CMD_DRAW_TEXT:
            vga_cmd_draw_text(payload, payload_size);
            break;
        default:
            break;
        }

        ptr += total_size;
    }
}
