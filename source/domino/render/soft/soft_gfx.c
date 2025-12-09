#include "soft_gfx.h"

#include <stdlib.h>
#include <string.h>

#include "domino/sys.h"
#include "soft_raster.h"
#include "soft_blit.h"

soft_state_t g_soft;

typedef struct soft_cmd_clear_payload_t {
    uint8_t r;
    uint8_t g;
    uint8_t b;
    uint8_t a;
} soft_cmd_clear_payload_t;

typedef struct soft_lines_header_t {
    uint16_t vertex_count;
    uint16_t reserved;
} soft_lines_header_t;

typedef struct soft_line_vertex_t {
    float    x;
    float    y;
    float    z;
    uint32_t color;
} soft_line_vertex_t;

typedef struct soft_camera_payload_t {
    float view[16];
    float proj[16];
    float world[16];
} soft_camera_payload_t;

typedef struct soft_sprite_t {
    int32_t x;
    int32_t y;
    int32_t w;
    int32_t h;
    uint32_t color_rgba;
} soft_sprite_t;

static bool      soft_init(const dgfx_desc* desc);
static void      soft_shutdown(void);
static dgfx_caps soft_get_caps(void);
static void      soft_resize(int width, int height);
static void      soft_begin_frame(void);
static void      soft_execute(const dgfx_cmd_buffer* cmd_buf);
static void      soft_end_frame(void);

static void soft_build_caps(void);
static void soft_init_matrices(void);

static void soft_cmd_clear(const uint8_t* payload, size_t payload_size);
static void soft_cmd_set_viewport(const uint8_t* payload);
static void soft_cmd_set_camera(const uint8_t* payload);
static void soft_cmd_set_pipeline(const uint8_t* payload);
static void soft_cmd_set_texture(const uint8_t* payload);
static void soft_cmd_draw_sprites(const uint8_t* payload, size_t payload_size);
static void soft_cmd_draw_lines(const uint8_t* payload, size_t payload_size);
static void soft_cmd_draw_meshes(const uint8_t* payload, size_t payload_size);
static void soft_cmd_draw_text(const uint8_t* payload, size_t payload_size);

static const dgfx_backend_vtable g_soft_vtable = {
    soft_init,
    soft_shutdown,
    soft_get_caps,
    soft_resize,
    soft_begin_frame,
    soft_execute,
    soft_end_frame
};

const dgfx_backend_vtable* dgfx_soft_get_vtable(void)
{
    return &g_soft_vtable;
}

static void soft_init_matrices(void)
{
    int i;
    for (i = 0; i < 16; ++i) {
        g_soft.view[i] = 0.0f;
        g_soft.proj[i] = 0.0f;
        g_soft.world[i] = 0.0f;
    }
    g_soft.view[0] = g_soft.view[5] = g_soft.view[10] = g_soft.view[15] = 1.0f;
    g_soft.proj[0] = g_soft.proj[5] = g_soft.proj[10] = g_soft.proj[15] = 1.0f;
    g_soft.world[0] = g_soft.world[5] = g_soft.world[10] = g_soft.world[15] = 1.0f;
}

static void soft_build_caps(void)
{
    memset(&g_soft.caps, 0, sizeof(g_soft.caps));
    g_soft.caps.name = "soft";

    if (g_soft.config.profile == DGFX_SOFT_PROFILE_NULL) {
        return;
    }

    g_soft.caps.supports_2d = g_soft.config.features.enable_2d ? true : false;
    g_soft.caps.supports_3d = g_soft.config.features.enable_3d ? true : false;
    g_soft.caps.supports_text = false;
    g_soft.caps.supports_rt = g_soft.config.features.enable_raster ? true : false;
    g_soft.caps.supports_alpha = true;
    g_soft.caps.max_texture_size = 2048;
}

static bool soft_init(const dgfx_desc* desc)
{
    if (!desc) {
        return false;
    }

    memset(&g_soft, 0, sizeof(g_soft));

    g_soft.native_window = desc->window ? dsys_window_get_native_handle(desc->window) : NULL;
    g_soft.width = (desc->width > 0) ? desc->width : 640;
    g_soft.height = (desc->height > 0) ? desc->height : 480;
    g_soft.fullscreen = 0;

    dgfx_soft_config_get_default(&g_soft.config);
    dgfx_soft_config_load_from_env(&g_soft.config);
    dgfx_soft_config_load_from_file(&g_soft.config, NULL);
    {
        dgfx_soft_format requested_fmt = g_soft.config.color_format;
        dgfx_soft_config_apply_profile(&g_soft.config, g_soft.config.profile);
        g_soft.config.color_format = requested_fmt;
    }

    soft_build_caps();

    if (g_soft.config.profile != DGFX_SOFT_PROFILE_NULL) {
        if (!soft_fb_create(&g_soft.fb,
                            g_soft.width,
                            g_soft.height,
                            g_soft.config.color_format,
                            g_soft.config.depth_bits,
                            g_soft.config.stencil_bits)) {
            soft_shutdown();
            return false;
        }
    }

    g_soft.vp_x = 0;
    g_soft.vp_y = 0;
    g_soft.vp_w = g_soft.width;
    g_soft.vp_h = g_soft.height;

    soft_init_matrices();

    g_soft.frame_in_progress = 0;

    return true;
}

static void soft_shutdown(void)
{
    if (g_soft.config.profile != DGFX_SOFT_PROFILE_NULL) {
        soft_fb_destroy(&g_soft.fb);
    }
    memset(&g_soft, 0, sizeof(g_soft));
}

static dgfx_caps soft_get_caps(void)
{
    return g_soft.caps;
}

static void soft_resize(int width, int height)
{
    if (width <= 0 || height <= 0) {
        return;
    }
    if (!g_soft.config.allow_resize) {
        return;
    }

    g_soft.width = width;
    g_soft.height = height;

    if (g_soft.config.profile == DGFX_SOFT_PROFILE_NULL) {
        return;
    }

    soft_fb_destroy(&g_soft.fb);
    soft_fb_create(&g_soft.fb,
                   width,
                   height,
                   g_soft.config.color_format,
                   g_soft.config.depth_bits,
                   g_soft.config.stencil_bits);

    g_soft.vp_x = 0;
    g_soft.vp_y = 0;
    g_soft.vp_w = width;
    g_soft.vp_h = height;
}

static void soft_begin_frame(void)
{
    if (g_soft.config.profile == DGFX_SOFT_PROFILE_NULL) {
        g_soft.frame_in_progress = 1;
        return;
    }

    g_soft.frame_in_progress = 1;

    soft_raster_clear_color(&g_soft.fb, 0, 0, 0, 255);
    if (g_soft.config.features.enable_depth) {
        soft_raster_clear_depth(&g_soft.fb, 1.0f);
    }
    if (g_soft.config.features.enable_stencil) {
        soft_raster_clear_stencil(&g_soft.fb, 0);
    }
}

static void soft_end_frame(void)
{
    soft_present_fn present;

    if (!g_soft.frame_in_progress) {
        return;
    }

    if (g_soft.config.profile != DGFX_SOFT_PROFILE_NULL) {
        present = soft_blit_get_present_callback();
        if (present) {
            present(g_soft.native_window, &g_soft.fb);
        }
    }

    g_soft.frame_in_progress = 0;
}

static void soft_cmd_clear(const uint8_t* payload, size_t payload_size)
{
    soft_cmd_clear_payload_t clr;
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

    soft_raster_clear_color(&g_soft.fb, r, g, b, a);
    if (g_soft.config.features.enable_depth) {
        soft_raster_clear_depth(&g_soft.fb, 1.0f);
    }
    if (g_soft.config.features.enable_stencil) {
        soft_raster_clear_stencil(&g_soft.fb, 0u);
    }
}

static void soft_cmd_set_viewport(const uint8_t* payload)
{
    (void)payload;
    g_soft.vp_x = 0;
    g_soft.vp_y = 0;
    g_soft.vp_w = g_soft.width;
    g_soft.vp_h = g_soft.height;
}

static void soft_cmd_set_camera(const uint8_t* payload)
{
    if (payload) {
        const soft_camera_payload_t* cam = (const soft_camera_payload_t*)payload;
        memcpy(g_soft.view, cam->view, sizeof(g_soft.view));
        memcpy(g_soft.proj, cam->proj, sizeof(g_soft.proj));
        memcpy(g_soft.world, cam->world, sizeof(g_soft.world));
    }
}

static void soft_cmd_set_pipeline(const uint8_t* payload)
{
    (void)payload;
}

static void soft_cmd_set_texture(const uint8_t* payload)
{
    (void)payload;
}

static void soft_cmd_draw_sprites(const uint8_t* payload, size_t payload_size)
{
    size_t count;
    size_t i;

    if (!payload || payload_size < sizeof(soft_sprite_t)) {
        return;
    }
    if (!g_soft.config.features.enable_2d) {
        return;
    }

    count = payload_size / sizeof(soft_sprite_t);
    for (i = 0u; i < count; ++i) {
        const soft_sprite_t* spr = ((const soft_sprite_t*)payload) + i;
        int x = spr->x + g_soft.camera2d_x;
        int y = spr->y + g_soft.camera2d_y;
        soft_raster_fill_rect_2d(&g_soft.fb, x, y, spr->w, spr->h, spr->color_rgba);
    }
}

static int soft_round_to_int(float v)
{
    return (int)((v >= 0.0f) ? (v + 0.5f) : (v - 0.5f));
}

static void soft_cmd_draw_lines(const uint8_t* payload, size_t payload_size)
{
    soft_lines_header_t header;
    const soft_line_vertex_t* verts;
    size_t required;
    size_t i;

    if (!payload || payload_size < sizeof(header)) {
        return;
    }
    if (!g_soft.config.features.enable_vector) {
        return;
    }

    memcpy(&header, payload, sizeof(header));
    required = sizeof(header) + ((size_t)header.vertex_count * sizeof(soft_line_vertex_t));
    if (payload_size < required || header.vertex_count < 2u) {
        return;
    }

    verts = (const soft_line_vertex_t*)(payload + sizeof(header));
    for (i = 0u; (i + 1u) < (size_t)header.vertex_count; i += 2u) {
        int x0 = soft_round_to_int(verts[i].x) + g_soft.camera2d_x;
        int y0 = soft_round_to_int(verts[i].y) + g_soft.camera2d_y;
        int x1 = soft_round_to_int(verts[i + 1u].x) + g_soft.camera2d_x;
        int y1 = soft_round_to_int(verts[i + 1u].y) + g_soft.camera2d_y;
        soft_raster_draw_line_2d(&g_soft.fb, x0, y0, x1, y1, verts[i].color);
    }
}

static void soft_cmd_draw_meshes(const uint8_t* payload, size_t payload_size)
{
    (void)payload;
    (void)payload_size;
    /* v1 stub; 3D meshes will be decoded and rasterized in a later revision. */
}

static void soft_cmd_draw_text(const uint8_t* payload, size_t payload_size)
{
    (void)payload;
    (void)payload_size;
    /* Text rendering is a stub for now. */
}

static void soft_execute(const dgfx_cmd_buffer* cmd_buf)
{
    const uint8_t* ptr;
    const uint8_t* end;
    size_t header_size;

    if (!cmd_buf || !cmd_buf->data || cmd_buf->size == 0u) {
        return;
    }
    if (!g_soft.frame_in_progress) {
        return;
    }
    if (g_soft.config.profile == DGFX_SOFT_PROFILE_NULL) {
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
            soft_cmd_clear(payload, payload_size);
            break;
        case DGFX_CMD_SET_VIEWPORT:
            soft_cmd_set_viewport(payload);
            break;
        case DGFX_CMD_SET_CAMERA:
            soft_cmd_set_camera(payload);
            break;
        case DGFX_CMD_SET_PIPELINE:
            soft_cmd_set_pipeline(payload);
            break;
        case DGFX_CMD_SET_TEXTURE:
            soft_cmd_set_texture(payload);
            break;
        case DGFX_CMD_DRAW_SPRITES:
            soft_cmd_draw_sprites(payload, payload_size);
            break;
        case DGFX_CMD_DRAW_MESHES:
            soft_cmd_draw_meshes(payload, payload_size);
            break;
        case DGFX_CMD_DRAW_LINES:
            soft_cmd_draw_lines(payload, payload_size);
            break;
        case DGFX_CMD_DRAW_TEXT:
            soft_cmd_draw_text(payload, payload_size);
            break;
        default:
            break;
        }

        ptr += total_size;
    }
}
