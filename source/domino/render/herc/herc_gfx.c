#include "herc_gfx.h"

#include <stdlib.h>
#include <string.h>

#include "domino/sys.h"
#include "herc_hw.h"

herc_state_t g_herc;

typedef struct herc_cmd_clear_payload_t {
    uint8_t r;
    uint8_t g;
    uint8_t b;
    uint8_t a;
} herc_cmd_clear_payload_t;

typedef struct herc_lines_header_t {
    uint16_t vertex_count;
    uint16_t reserved;
} herc_lines_header_t;

typedef struct herc_line_vertex_t {
    float    x;
    float    y;
    float    z;
    uint32_t color;
} herc_line_vertex_t;

typedef struct herc_camera_payload_t {
    float view[16];
    float proj[16];
    float world[16];
} herc_camera_payload_t;

typedef struct herc_sprite_t {
    int32_t  x;
    int32_t  y;
    int32_t  w;
    int32_t  h;
    uint32_t color_rgba;
} herc_sprite_t;

static bool      herc_init(const dgfx_desc* desc);
static void      herc_shutdown(void);
static dgfx_caps herc_get_caps(void);
static void      herc_resize(int width, int height);
static void      herc_begin_frame(void);
static void      herc_execute(const dgfx_cmd_buffer* cmd_buf);
static void      herc_end_frame(void);

static void herc_init_matrices(void);
static void herc_build_caps(void);
static int  herc_round_to_int(float v);

static void herc_cmd_clear(const uint8_t* payload, size_t payload_size);
static void herc_cmd_set_viewport(const uint8_t* payload);
static void herc_cmd_set_camera(const uint8_t* payload);
static void herc_cmd_set_pipeline(const uint8_t* payload);
static void herc_cmd_set_texture(const uint8_t* payload);
static void herc_cmd_draw_sprites(const uint8_t* payload, size_t payload_size);
static void herc_cmd_draw_lines(const uint8_t* payload, size_t payload_size);
static void herc_cmd_draw_meshes(const uint8_t* payload, size_t payload_size);
static void herc_cmd_draw_text(const uint8_t* payload, size_t payload_size);

static const dgfx_backend_vtable g_herc_vtable = {
    herc_init,
    herc_shutdown,
    herc_get_caps,
    herc_resize,
    herc_begin_frame,
    herc_execute,
    herc_end_frame
};

const dgfx_backend_vtable* dgfx_herc_get_vtable(void)
{
    return &g_herc_vtable;
}

static void herc_init_matrices(void)
{
    int i;
    for (i = 0; i < 16; ++i) {
        g_herc.view[i] = 0.0f;
        g_herc.proj[i] = 0.0f;
        g_herc.world[i] = 0.0f;
    }
    g_herc.view[0] = g_herc.view[5] = g_herc.view[10] = g_herc.view[15] = 1.0f;
    g_herc.proj[0] = g_herc.proj[5] = g_herc.proj[10] = g_herc.proj[15] = 1.0f;
    g_herc.world[0] = g_herc.world[5] = g_herc.world[10] = g_herc.world[15] = 1.0f;
}

static void herc_build_caps(void)
{
    memset(&g_herc.caps, 0, sizeof(g_herc.caps));
    g_herc.caps.name = "herc";

    if (g_herc.config.profile == DGFX_SOFT_PROFILE_NULL) {
        return;
    }

    g_herc.caps.supports_2d = g_herc.config.features.enable_2d ? true : false;
    g_herc.caps.supports_3d = g_herc.config.features.enable_3d ? true : false;
    g_herc.caps.supports_text = false;
    g_herc.caps.supports_rt = g_herc.config.features.enable_raster ? true : false;
    g_herc.caps.supports_alpha = false;
    g_herc.caps.max_texture_size = 0;
}

static bool herc_init(const dgfx_desc* desc)
{
    (void)desc;

    if (herc_hw_init() != 0) {
        return false;
    }

    memset(&g_herc, 0, sizeof(g_herc));

    if (herc_hw_set_mode_720x348(&g_herc.mode) != 0) {
        herc_shutdown();
        return false;
    }

    g_herc.width = g_herc.mode.width;
    g_herc.height = g_herc.mode.height;

    dgfx_soft_config_get_default(&g_herc.config);
    dgfx_soft_config_load_from_env(&g_herc.config);
    dgfx_soft_config_load_from_file(&g_herc.config, NULL);
    if (g_herc.config.profile == DGFX_SOFT_PROFILE_NULL) {
        g_herc.config.profile = DGFX_SOFT_PROFILE_BALANCED;
    }
    dgfx_soft_config_apply_profile(&g_herc.config, g_herc.config.profile);
    g_herc.config.color_format = DGFX_SOFT_FMT_8_INDEXED;

    if (!soft_fb_create(&g_herc.fb,
                        g_herc.width,
                        g_herc.height,
                        g_herc.config.color_format,
                        g_herc.config.depth_bits,
                        g_herc.config.stencil_bits)) {
        herc_shutdown();
        return false;
    }

    g_herc.depth = g_herc.fb.depth;
    g_herc.stencil = g_herc.fb.stencil;

    g_herc.vp_x = 0;
    g_herc.vp_y = 0;
    g_herc.vp_w = g_herc.width;
    g_herc.vp_h = g_herc.height;

    g_herc.camera2d_x = 0;
    g_herc.camera2d_y = 0;

    herc_init_matrices();
    herc_build_caps();

    g_herc.frame_in_progress = 0;

    return true;
}

static void herc_shutdown(void)
{
    soft_fb_destroy(&g_herc.fb);
    g_herc.depth = NULL;
    g_herc.stencil = NULL;

    herc_hw_restore_text_mode();

    memset(&g_herc, 0, sizeof(g_herc));
}

static dgfx_caps herc_get_caps(void)
{
    return g_herc.caps;
}

static void herc_resize(int width, int height)
{
    (void)width;
    (void)height;
    /* Hercules graphics mode is fixed; no dynamic resize in v1. */
}

static void herc_begin_frame(void)
{
    if (g_herc.config.profile == DGFX_SOFT_PROFILE_NULL) {
        g_herc.frame_in_progress = 1;
        return;
    }
    if (!g_herc.fb.color) {
        g_herc.frame_in_progress = 0;
        return;
    }

    g_herc.frame_in_progress = 1;

    soft_raster_clear_color(&g_herc.fb, 0u, 0u, 0u, 255u);
    if (g_herc.config.features.enable_depth) {
        soft_raster_clear_depth(&g_herc.fb, 1.0f);
    }
    if (g_herc.config.features.enable_stencil) {
        soft_raster_clear_stencil(&g_herc.fb, 0u);
    }
}

static void herc_end_frame(void)
{
    if (!g_herc.frame_in_progress) {
        return;
    }

    if (g_herc.config.profile != DGFX_SOFT_PROFILE_NULL && g_herc.fb.color) {
        herc_hw_blit_720x348(
            g_herc.fb.color,
            (uint16_t)g_herc.width,
            (uint16_t)g_herc.height,
            (uint16_t)g_herc.fb.stride_bytes);
    }

    g_herc.frame_in_progress = 0;
}

static void herc_cmd_clear(const uint8_t* payload, size_t payload_size)
{
    herc_cmd_clear_payload_t clr;
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

    soft_raster_clear_color(&g_herc.fb, r, g, b, a);
    if (g_herc.config.features.enable_depth) {
        soft_raster_clear_depth(&g_herc.fb, 1.0f);
    }
    if (g_herc.config.features.enable_stencil) {
        soft_raster_clear_stencil(&g_herc.fb, 0u);
    }
}

static void herc_cmd_set_viewport(const uint8_t* payload)
{
    (void)payload;
    g_herc.vp_x = 0;
    g_herc.vp_y = 0;
    g_herc.vp_w = g_herc.width;
    g_herc.vp_h = g_herc.height;
}

static void herc_cmd_set_camera(const uint8_t* payload)
{
    if (payload) {
        const herc_camera_payload_t* cam = (const herc_camera_payload_t*)payload;
        memcpy(g_herc.view, cam->view, sizeof(g_herc.view));
        memcpy(g_herc.proj, cam->proj, sizeof(g_herc.proj));
        memcpy(g_herc.world, cam->world, sizeof(g_herc.world));
    }
}

static void herc_cmd_set_pipeline(const uint8_t* payload)
{
    (void)payload;
}

static void herc_cmd_set_texture(const uint8_t* payload)
{
    (void)payload;
}

static void herc_cmd_draw_sprites(const uint8_t* payload, size_t payload_size)
{
    size_t count;
    size_t i;

    if (!payload || payload_size < sizeof(herc_sprite_t)) {
        return;
    }
    if (!g_herc.config.features.enable_2d) {
        return;
    }

    count = payload_size / sizeof(herc_sprite_t);
    for (i = 0u; i < count; ++i) {
        const herc_sprite_t* spr = ((const herc_sprite_t*)payload) + i;
        int x = spr->x + g_herc.camera2d_x;
        int y = spr->y + g_herc.camera2d_y;
        soft_raster_fill_rect_2d(&g_herc.fb, x, y, spr->w, spr->h, spr->color_rgba);
    }
}

static int herc_round_to_int(float v)
{
    return (int)((v >= 0.0f) ? (v + 0.5f) : (v - 0.5f));
}

static void herc_cmd_draw_lines(const uint8_t* payload, size_t payload_size)
{
    herc_lines_header_t header;
    const herc_line_vertex_t* verts;
    size_t required;
    size_t i;

    if (!payload || payload_size < sizeof(header)) {
        return;
    }
    if (!g_herc.config.features.enable_vector) {
        return;
    }

    memcpy(&header, payload, sizeof(header));
    required = sizeof(header) + ((size_t)header.vertex_count * sizeof(herc_line_vertex_t));
    if (payload_size < required || header.vertex_count < 2u) {
        return;
    }

    verts = (const herc_line_vertex_t*)(payload + sizeof(header));

    for (i = 0u; (i + 1u) < (size_t)header.vertex_count; i += 2u) {
        int x0 = herc_round_to_int(verts[i].x) + g_herc.camera2d_x;
        int y0 = herc_round_to_int(verts[i].y) + g_herc.camera2d_y;
        int x1 = herc_round_to_int(verts[i + 1u].x) + g_herc.camera2d_x;
        int y1 = herc_round_to_int(verts[i + 1u].y) + g_herc.camera2d_y;
        soft_raster_draw_line_2d(&g_herc.fb, x0, y0, x1, y1, verts[i].color);
    }
}

static void herc_cmd_draw_meshes(const uint8_t* payload, size_t payload_size)
{
    (void)payload;
    (void)payload_size;
    /* Future: decode meshes and rasterize via soft_raster_draw_triangle. */
}

static void herc_cmd_draw_text(const uint8_t* payload, size_t payload_size)
{
    (void)payload;
    (void)payload_size;
    /* Text rendering is not implemented in the Hercules backend v1. */
}

static void herc_execute(const dgfx_cmd_buffer* cmd_buf)
{
    const uint8_t* ptr;
    const uint8_t* end;
    size_t header_size;

    if (!cmd_buf || !cmd_buf->data || cmd_buf->size == 0u) {
        return;
    }
    if (!g_herc.frame_in_progress) {
        return;
    }
    if (g_herc.config.profile == DGFX_SOFT_PROFILE_NULL) {
        return;
    }
    if (!g_herc.fb.color) {
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
            herc_cmd_clear(payload, payload_size);
            break;
        case DGFX_CMD_SET_VIEWPORT:
            herc_cmd_set_viewport(payload);
            break;
        case DGFX_CMD_SET_CAMERA:
            herc_cmd_set_camera(payload);
            break;
        case DGFX_CMD_SET_PIPELINE:
            herc_cmd_set_pipeline(payload);
            break;
        case DGFX_CMD_SET_TEXTURE:
            herc_cmd_set_texture(payload);
            break;
        case DGFX_CMD_DRAW_SPRITES:
            herc_cmd_draw_sprites(payload, payload_size);
            break;
        case DGFX_CMD_DRAW_MESHES:
            herc_cmd_draw_meshes(payload, payload_size);
            break;
        case DGFX_CMD_DRAW_LINES:
            herc_cmd_draw_lines(payload, payload_size);
            break;
        case DGFX_CMD_DRAW_TEXT:
            herc_cmd_draw_text(payload, payload_size);
            break;
        default:
            break;
        }

        ptr += total_size;
    }
}
