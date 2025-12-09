#include "xga_gfx.h"
#include "xga_hw.h"

#include <stdlib.h>
#include <string.h>

xga_state_t g_xga;

typedef struct xga_cmd_clear_payload_t {
    uint8_t r;
    uint8_t g;
    uint8_t b;
    uint8_t a;
} xga_cmd_clear_payload_t;

typedef struct xga_lines_header_t {
    uint16_t vertex_count;
    uint16_t reserved;
} xga_lines_header_t;

typedef struct xga_line_vertex_t {
    float    x;
    float    y;
    float    z;
    uint32_t color;
} xga_line_vertex_t;

typedef struct xga_camera_payload_t {
    float view[16];
    float proj[16];
    float world[16];
} xga_camera_payload_t;

typedef struct xga_sprite_t {
    int32_t x;
    int32_t y;
    int32_t w;
    int32_t h;
    uint32_t color_rgba;
} xga_sprite_t;

static bool      xga_init(const dgfx_desc* desc);
static void      xga_shutdown(void);
static dgfx_caps xga_get_caps(void);
static void      xga_resize(int width, int height);
static void      xga_begin_frame(void);
static void      xga_execute(const dgfx_cmd_buffer* cmd_buf);
static void      xga_end_frame(void);

static void xga_build_caps(void);
static void xga_init_matrices_and_viewport(void);
static int  xga_round_to_int(float v);

static void xga_cmd_clear(const uint8_t* payload, size_t payload_size);
static void xga_cmd_set_viewport(const uint8_t* payload);
static void xga_cmd_set_camera(const uint8_t* payload);
static void xga_cmd_set_pipeline(const uint8_t* payload);
static void xga_cmd_set_texture(const uint8_t* payload);
static void xga_cmd_draw_sprites(const uint8_t* payload, size_t payload_size);
static void xga_cmd_draw_lines(const uint8_t* payload, size_t payload_size);
static void xga_cmd_draw_meshes(const uint8_t* payload, size_t payload_size);
static void xga_cmd_draw_text(const uint8_t* payload, size_t payload_size);

static const dgfx_backend_vtable g_xga_vtable = {
    xga_init,
    xga_shutdown,
    xga_get_caps,
    xga_resize,
    xga_begin_frame,
    xga_execute,
    xga_end_frame
};

const dgfx_backend_vtable* dgfx_xga_get_vtable(void)
{
    return &g_xga_vtable;
}

static void xga_build_caps(void)
{
    memset(&g_xga.caps, 0, sizeof(g_xga.caps));
    g_xga.caps.name = "xga";
    g_xga.caps.supports_2d = true;
    g_xga.caps.supports_3d = true; /* CPU rasterizer */
    g_xga.caps.supports_text = false;
    g_xga.caps.supports_rt = true;
    g_xga.caps.supports_alpha = false;
    g_xga.caps.max_texture_size = 0;
}

static void xga_init_matrices_and_viewport(void)
{
    int i;
    for (i = 0; i < 16; ++i) {
        g_xga.view[i] = 0.0f;
        g_xga.proj[i] = 0.0f;
        g_xga.world[i] = 0.0f;
    }
    g_xga.view[0] = g_xga.view[5] = g_xga.view[10] = g_xga.view[15] = 1.0f;
    g_xga.proj[0] = g_xga.proj[5] = g_xga.proj[10] = g_xga.proj[15] = 1.0f;
    g_xga.world[0] = g_xga.world[5] = g_xga.world[10] = g_xga.world[15] = 1.0f;

    g_xga.vp_x = 0;
    g_xga.vp_y = 0;
    g_xga.vp_w = g_xga.width;
    g_xga.vp_h = g_xga.height;
    g_xga.camera2d_x = 0;
    g_xga.camera2d_y = 0;
}

static bool xga_init(const dgfx_desc* desc)
{
    uint16_t req_w;
    uint16_t req_h;

    if (!desc) {
        return false;
    }

    if (xga_hw_init() != 0) {
        return false;
    }

    memset(&g_xga, 0, sizeof(g_xga));

    req_w = (uint16_t)((desc->width > 0) ? desc->width : 640);
    req_h = (uint16_t)((desc->height > 0) ? desc->height : 480);

    if (xga_hw_set_mode(req_w, req_h, &g_xga.mode) != 0) {
        xga_shutdown();
        return false;
    }

    g_xga.width = g_xga.mode.width;
    g_xga.height = g_xga.mode.height;

    dgfx_soft_config_get_default(&g_xga.config);
    g_xga.config.color_format = DGFX_SOFT_FMT_8_INDEXED;
    if (g_xga.config.profile == DGFX_SOFT_PROFILE_NULL) {
        g_xga.config.profile = DGFX_SOFT_PROFILE_BALANCED;
    }
    dgfx_soft_config_apply_profile(&g_xga.config, g_xga.config.profile);

    if (!soft_fb_create(&g_xga.fb,
                        g_xga.width,
                        g_xga.height,
                        g_xga.config.color_format,
                        g_xga.config.depth_bits,
                        g_xga.config.stencil_bits)) {
        xga_shutdown();
        return false;
    }

    g_xga.depth = g_xga.fb.depth;
    g_xga.stencil = g_xga.fb.stencil;

    xga_init_matrices_and_viewport();
    xga_build_caps();

    g_xga.frame_in_progress = 0;

    return true;
}

static void xga_shutdown(void)
{
    if (g_xga.fb.color || g_xga.fb.depth || g_xga.fb.stencil) {
        soft_fb_destroy(&g_xga.fb);
    }

    xga_hw_restore_mode();

    memset(&g_xga, 0, sizeof(g_xga));
}

static dgfx_caps xga_get_caps(void)
{
    return g_xga.caps;
}

static void xga_resize(int width, int height)
{
    (void)width;
    (void)height;
    /* v1: XGA modes are discrete; resizing would require reinitialization. */
}

static void xga_begin_frame(void)
{
    if (!g_xga.fb.color) {
        return;
    }

    g_xga.frame_in_progress = 1;

    soft_raster_clear_color(&g_xga.fb, 0u, 0u, 0u, 255u);

    if (g_xga.config.features.enable_depth && g_xga.fb.depth) {
        soft_raster_clear_depth(&g_xga.fb, 1.0f);
    }
    if (g_xga.config.features.enable_stencil && g_xga.fb.stencil) {
        soft_raster_clear_stencil(&g_xga.fb, 0u);
    }
}

static void xga_end_frame(void)
{
    if (!g_xga.frame_in_progress) {
        return;
    }
    if (!g_xga.fb.color) {
        g_xga.frame_in_progress = 0;
        return;
    }

    xga_hw_blit(
        g_xga.fb.color,
        (uint16_t)g_xga.width,
        (uint16_t)g_xga.height,
        (uint16_t)g_xga.fb.stride_bytes,
        &g_xga.mode);

    g_xga.frame_in_progress = 0;
}

static void xga_cmd_clear(const uint8_t* payload, size_t payload_size)
{
    xga_cmd_clear_payload_t clr;
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

    soft_raster_clear_color(&g_xga.fb, r, g, b, a);
    if (g_xga.config.features.enable_depth && g_xga.fb.depth) {
        soft_raster_clear_depth(&g_xga.fb, 1.0f);
    }
    if (g_xga.config.features.enable_stencil && g_xga.fb.stencil) {
        soft_raster_clear_stencil(&g_xga.fb, 0u);
    }
}

static void xga_cmd_set_viewport(const uint8_t* payload)
{
    (void)payload;
    g_xga.vp_x = 0;
    g_xga.vp_y = 0;
    g_xga.vp_w = g_xga.fb.width;
    g_xga.vp_h = g_xga.fb.height;
}

static void xga_cmd_set_camera(const uint8_t* payload)
{
    if (payload) {
        const xga_camera_payload_t* cam = (const xga_camera_payload_t*)payload;
        memcpy(g_xga.view, cam->view, sizeof(g_xga.view));
        memcpy(g_xga.proj, cam->proj, sizeof(g_xga.proj));
        memcpy(g_xga.world, cam->world, sizeof(g_xga.world));
    }
}

static void xga_cmd_set_pipeline(const uint8_t* payload)
{
    (void)payload;
}

static void xga_cmd_set_texture(const uint8_t* payload)
{
    (void)payload;
}

static void xga_cmd_draw_sprites(const uint8_t* payload, size_t payload_size)
{
    size_t count;
    size_t i;

    if (!payload || payload_size < sizeof(xga_sprite_t)) {
        return;
    }
    if (!g_xga.config.features.enable_2d) {
        return;
    }

    count = payload_size / sizeof(xga_sprite_t);
    for (i = 0u; i < count; ++i) {
        const xga_sprite_t* spr = ((const xga_sprite_t*)payload) + i;
        int x = spr->x + g_xga.camera2d_x;
        int y = spr->y + g_xga.camera2d_y;
        soft_raster_fill_rect_2d(&g_xga.fb, x, y, spr->w, spr->h, spr->color_rgba);
    }
}

static int xga_round_to_int(float v)
{
    return (int)((v >= 0.0f) ? (v + 0.5f) : (v - 0.5f));
}

static void xga_cmd_draw_lines(const uint8_t* payload, size_t payload_size)
{
    xga_lines_header_t header;
    const xga_line_vertex_t* verts;
    size_t required;
    size_t i;

    if (!payload || payload_size < sizeof(header)) {
        return;
    }
    if (!g_xga.config.features.enable_vector) {
        return;
    }

    memcpy(&header, payload, sizeof(header));
    required = sizeof(header) + ((size_t)header.vertex_count * sizeof(xga_line_vertex_t));
    if (payload_size < required || header.vertex_count < 2u) {
        return;
    }

    verts = (const xga_line_vertex_t*)(payload + sizeof(header));
    for (i = 0u; (i + 1u) < (size_t)header.vertex_count; i += 2u) {
        int x0 = xga_round_to_int(verts[i].x) + g_xga.camera2d_x;
        int y0 = xga_round_to_int(verts[i].y) + g_xga.camera2d_y;
        int x1 = xga_round_to_int(verts[i + 1u].x) + g_xga.camera2d_x;
        int y1 = xga_round_to_int(verts[i + 1u].y) + g_xga.camera2d_y;
        soft_raster_draw_line_2d(&g_xga.fb, x0, y0, x1, y1, verts[i].color);
    }
}

static void xga_cmd_draw_meshes(const uint8_t* payload, size_t payload_size)
{
    (void)payload;
    (void)payload_size;
    /* Future work: decode mesh payloads and rasterize triangles. */
}

static void xga_cmd_draw_text(const uint8_t* payload, size_t payload_size)
{
    (void)payload;
    (void)payload_size;
    /* Text rendering is not implemented in the XGA backend MVP. */
}

static void xga_execute(const dgfx_cmd_buffer* cmd_buf)
{
    const uint8_t* ptr;
    const uint8_t* end;
    size_t header_size;

    if (!cmd_buf || !cmd_buf->data || cmd_buf->size == 0u) {
        return;
    }
    if (!g_xga.frame_in_progress) {
        return;
    }
    if (!g_xga.fb.color) {
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
            xga_cmd_clear(payload, payload_size);
            break;
        case DGFX_CMD_SET_VIEWPORT:
            xga_cmd_set_viewport(payload);
            break;
        case DGFX_CMD_SET_CAMERA:
            xga_cmd_set_camera(payload);
            break;
        case DGFX_CMD_SET_PIPELINE:
            xga_cmd_set_pipeline(payload);
            break;
        case DGFX_CMD_SET_TEXTURE:
            xga_cmd_set_texture(payload);
            break;
        case DGFX_CMD_DRAW_SPRITES:
            xga_cmd_draw_sprites(payload, payload_size);
            break;
        case DGFX_CMD_DRAW_MESHES:
            xga_cmd_draw_meshes(payload, payload_size);
            break;
        case DGFX_CMD_DRAW_LINES:
            xga_cmd_draw_lines(payload, payload_size);
            break;
        case DGFX_CMD_DRAW_TEXT:
            xga_cmd_draw_text(payload, payload_size);
            break;
        default:
            break;
        }

        ptr += total_size;
    }
}
