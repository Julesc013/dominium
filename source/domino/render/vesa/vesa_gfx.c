#include "vesa_gfx.h"

#include <stdlib.h>
#include <string.h>

#include "vesa_bios.h"
#include "domino/sys.h"

vesa_state_t g_vesa;

typedef struct vesa_cmd_clear_payload_t {
    uint8_t r;
    uint8_t g;
    uint8_t b;
    uint8_t a;
} vesa_cmd_clear_payload_t;

typedef struct vesa_lines_header_t {
    uint16_t vertex_count;
    uint16_t reserved;
} vesa_lines_header_t;

typedef struct vesa_line_vertex_t {
    float    x;
    float    y;
    float    z;
    uint32_t color;
} vesa_line_vertex_t;

typedef struct vesa_camera_payload_t {
    float view[16];
    float proj[16];
    float world[16];
} vesa_camera_payload_t;

typedef struct vesa_sprite_t {
    int32_t x;
    int32_t y;
    int32_t w;
    int32_t h;
    uint32_t color_rgba;
} vesa_sprite_t;

static bool      vesa_init(const dgfx_desc* desc);
static void      vesa_shutdown(void);
static dgfx_caps vesa_get_caps(void);
static void      vesa_resize(int width, int height);
static void      vesa_begin_frame(void);
static void      vesa_execute(const dgfx_cmd_buffer* cmd_buf);
static void      vesa_end_frame(void);

static void vesa_build_caps(void);
static void vesa_init_matrices_and_viewport(void);
static int  vesa_round_to_int(float v);

static void vesa_cmd_clear(const uint8_t* payload, size_t payload_size);
static void vesa_cmd_set_viewport(const uint8_t* payload);
static void vesa_cmd_set_camera(const uint8_t* payload);
static void vesa_cmd_set_pipeline(const uint8_t* payload);
static void vesa_cmd_set_texture(const uint8_t* payload);
static void vesa_cmd_draw_sprites(const uint8_t* payload, size_t payload_size);
static void vesa_cmd_draw_lines(const uint8_t* payload, size_t payload_size);
static void vesa_cmd_draw_meshes(const uint8_t* payload, size_t payload_size);
static void vesa_cmd_draw_text(const uint8_t* payload, size_t payload_size);

static const dgfx_backend_vtable g_vesa_vtable = {
    vesa_init,
    vesa_shutdown,
    vesa_get_caps,
    vesa_resize,
    vesa_begin_frame,
    vesa_execute,
    vesa_end_frame
};

const dgfx_backend_vtable* dgfx_vesa_get_vtable(void)
{
    return &g_vesa_vtable;
}

static void vesa_build_caps(void)
{
    memset(&g_vesa.caps, 0, sizeof(g_vesa.caps));
    g_vesa.caps.name = "vesa";

    g_vesa.caps.supports_2d = g_vesa.config.features.enable_2d ? true : false;
    g_vesa.caps.supports_3d = g_vesa.config.features.enable_3d ? true : false;
    g_vesa.caps.supports_text = false;
    g_vesa.caps.supports_rt = g_vesa.config.features.enable_raster ? true : false;
    g_vesa.caps.supports_alpha = true;
    g_vesa.caps.max_texture_size = 2048;
}

static void vesa_init_matrices_and_viewport(void)
{
    int i;
    for (i = 0; i < 16; ++i) {
        g_vesa.view[i] = 0.0f;
        g_vesa.proj[i] = 0.0f;
        g_vesa.world[i] = 0.0f;
    }
    g_vesa.view[0] = g_vesa.view[5] = g_vesa.view[10] = g_vesa.view[15] = 1.0f;
    g_vesa.proj[0] = g_vesa.proj[5] = g_vesa.proj[10] = g_vesa.proj[15] = 1.0f;
    g_vesa.world[0] = g_vesa.world[5] = g_vesa.world[10] = g_vesa.world[15] = 1.0f;

    g_vesa.vp_x = 0;
    g_vesa.vp_y = 0;
    g_vesa.vp_w = g_vesa.width;
    g_vesa.vp_h = g_vesa.height;

    g_vesa.camera2d_x = 0;
    g_vesa.camera2d_y = 0;
}

static bool vesa_init(const dgfx_desc* desc)
{
    uint16_t req_w;
    uint16_t req_h;
    uint8_t req_bpp;
    void* lfb;

    if (!desc) {
        return false;
    }

    memset(&g_vesa, 0, sizeof(g_vesa));

    req_w = (uint16_t)((desc->width > 0) ? desc->width : 640);
    req_h = (uint16_t)((desc->height > 0) ? desc->height : 480);
    req_bpp = 32u;

    dgfx_soft_config_get_default(&g_vesa.config);
    dgfx_soft_config_load_from_env(&g_vesa.config);
    dgfx_soft_config_load_from_file(&g_vesa.config, NULL);
    if (g_vesa.config.profile == DGFX_SOFT_PROFILE_NULL) {
        g_vesa.config.profile = DGFX_SOFT_PROFILE_BALANCED;
    }
    dgfx_soft_config_apply_profile(&g_vesa.config, g_vesa.config.profile);

    if (vesa_bios_init() != 0) {
        return false;
    }

    if (vesa_bios_find_mode(req_w, req_h, req_bpp, &g_vesa.mode) != 0) {
        req_bpp = 16u;
        if (vesa_bios_find_mode(req_w, req_h, req_bpp, &g_vesa.mode) != 0) {
            return false;
        }
    }

    if (vesa_bios_set_mode(&g_vesa.mode, 1) != 0) {
        vesa_bios_restore_mode();
        return false;
    }

    lfb = vesa_bios_map_lfb(&g_vesa.mode);
    if (!lfb) {
        vesa_bios_restore_mode();
        return false;
    }

    g_vesa.width = g_vesa.mode.width;
    g_vesa.height = g_vesa.mode.height;

    if (g_vesa.mode.bpp <= 8u) {
        g_vesa.config.color_format = DGFX_SOFT_FMT_8_INDEXED;
    } else if (g_vesa.mode.bpp <= 16u) {
        g_vesa.config.color_format = DGFX_SOFT_FMT_16_565;
    } else {
        g_vesa.config.color_format = DGFX_SOFT_FMT_32_ARGB;
    }

    memset(&g_vesa.fb, 0, sizeof(g_vesa.fb));
    g_vesa.fb.width = g_vesa.width;
    g_vesa.fb.height = g_vesa.height;
    g_vesa.fb.format = g_vesa.config.color_format;
    g_vesa.fb.color = (uint8_t*)lfb;
    g_vesa.fb.depth_bits = g_vesa.config.depth_bits;
    g_vesa.fb.stencil_bits = g_vesa.config.stencil_bits;
    g_vesa.fb.stride_bytes = g_vesa.mode.pitch ? g_vesa.mode.pitch : (int)(g_vesa.width * (g_vesa.mode.bpp / 8u));
    g_vesa.fb.depth_stride = 0;
    g_vesa.fb.stencil_stride = 0;

    if (g_vesa.config.features.enable_depth && g_vesa.config.depth_bits > 0u) {
        size_t depth_stride;
        size_t depth_size;
        depth_stride = (size_t)g_vesa.width * sizeof(float);
        depth_size = depth_stride * (size_t)g_vesa.height;
        g_vesa.depth = (uint8_t*)malloc(depth_size);
        if (!g_vesa.depth) {
            vesa_shutdown();
            return false;
        }
        memset(g_vesa.depth, 0, depth_size);
        g_vesa.fb.depth = g_vesa.depth;
        g_vesa.fb.depth_stride = (int)depth_stride;
    }

    if (g_vesa.config.features.enable_stencil && g_vesa.config.stencil_bits > 0u) {
        size_t stencil_stride;
        size_t stencil_size;
        stencil_stride = (size_t)g_vesa.width;
        stencil_size = stencil_stride * (size_t)g_vesa.height;
        g_vesa.stencil = (uint8_t*)malloc(stencil_size);
        if (!g_vesa.stencil) {
            vesa_shutdown();
            return false;
        }
        memset(g_vesa.stencil, 0, stencil_size);
        g_vesa.fb.stencil = g_vesa.stencil;
        g_vesa.fb.stencil_stride = (int)stencil_stride;
    }

    vesa_init_matrices_and_viewport();
    vesa_build_caps();

    g_vesa.frame_in_progress = 0;
    return true;
}

static void vesa_shutdown(void)
{
    if (g_vesa.depth) {
        free(g_vesa.depth);
        g_vesa.depth = NULL;
    }
    if (g_vesa.stencil) {
        free(g_vesa.stencil);
        g_vesa.stencil = NULL;
    }

    vesa_bios_restore_mode();

    memset(&g_vesa, 0, sizeof(g_vesa));
}

static dgfx_caps vesa_get_caps(void)
{
    return g_vesa.caps;
}

static void vesa_resize(int width, int height)
{
    (void)width;
    (void)height;
    /* VESA modes require reprogramming the BIOS; not supported in v1. */
}

static void vesa_begin_frame(void)
{
    if (!g_vesa.fb.color) {
        return;
    }

    g_vesa.frame_in_progress = 1;

    soft_raster_clear_color(&g_vesa.fb, 0u, 0u, 0u, 255u);
    if (g_vesa.config.features.enable_depth && g_vesa.fb.depth) {
        soft_raster_clear_depth(&g_vesa.fb, 1.0f);
    }
    if (g_vesa.config.features.enable_stencil && g_vesa.fb.stencil) {
        soft_raster_clear_stencil(&g_vesa.fb, 0u);
    }
}

static void vesa_end_frame(void)
{
    if (!g_vesa.frame_in_progress) {
        return;
    }
    g_vesa.frame_in_progress = 0;
}

static void vesa_cmd_clear(const uint8_t* payload, size_t payload_size)
{
    vesa_cmd_clear_payload_t clr;
    uint8_t r;
    uint8_t g;
    uint8_t b;
    uint8_t a;

    r = 0u;
    g = 0u;
    b = 0u;
    a = 255u;

    if (payload && payload_size >= sizeof(clr)) {
        memcpy(&clr, payload, sizeof(clr));
        r = clr.r;
        g = clr.g;
        b = clr.b;
        a = clr.a;
    }

    soft_raster_clear_color(&g_vesa.fb, r, g, b, a);
    if (g_vesa.config.features.enable_depth && g_vesa.fb.depth) {
        soft_raster_clear_depth(&g_vesa.fb, 1.0f);
    }
    if (g_vesa.config.features.enable_stencil && g_vesa.fb.stencil) {
        soft_raster_clear_stencil(&g_vesa.fb, 0u);
    }
}

static void vesa_cmd_set_viewport(const uint8_t* payload)
{
    (void)payload;
    g_vesa.vp_x = 0;
    g_vesa.vp_y = 0;
    g_vesa.vp_w = g_vesa.width;
    g_vesa.vp_h = g_vesa.height;
}

static void vesa_cmd_set_camera(const uint8_t* payload)
{
    if (payload) {
        const vesa_camera_payload_t* cam = (const vesa_camera_payload_t*)payload;
        memcpy(g_vesa.view, cam->view, sizeof(g_vesa.view));
        memcpy(g_vesa.proj, cam->proj, sizeof(g_vesa.proj));
        memcpy(g_vesa.world, cam->world, sizeof(g_vesa.world));
    }
}

static void vesa_cmd_set_pipeline(const uint8_t* payload)
{
    (void)payload;
}

static void vesa_cmd_set_texture(const uint8_t* payload)
{
    (void)payload;
}

static int vesa_round_to_int(float v)
{
    return (int)((v >= 0.0f) ? (v + 0.5f) : (v - 0.5f));
}

static void vesa_cmd_draw_sprites(const uint8_t* payload, size_t payload_size)
{
    size_t count;
    size_t i;

    if (!payload || payload_size < sizeof(vesa_sprite_t)) {
        return;
    }
    if (!g_vesa.config.features.enable_2d) {
        return;
    }

    count = payload_size / sizeof(vesa_sprite_t);
    for (i = 0u; i < count; ++i) {
        const vesa_sprite_t* spr = ((const vesa_sprite_t*)payload) + i;
        int x = spr->x + g_vesa.camera2d_x;
        int y = spr->y + g_vesa.camera2d_y;
        soft_raster_fill_rect_2d(&g_vesa.fb, x, y, spr->w, spr->h, spr->color_rgba);
    }
}

static void vesa_cmd_draw_lines(const uint8_t* payload, size_t payload_size)
{
    vesa_lines_header_t header;
    const vesa_line_vertex_t* verts;
    size_t required;
    size_t i;

    if (!payload || payload_size < sizeof(header)) {
        return;
    }
    if (!g_vesa.config.features.enable_vector) {
        return;
    }

    memcpy(&header, payload, sizeof(header));
    required = sizeof(header) + ((size_t)header.vertex_count * sizeof(vesa_line_vertex_t));
    if (payload_size < required || header.vertex_count < 2u) {
        return;
    }

    verts = (const vesa_line_vertex_t*)(payload + sizeof(header));
    for (i = 0u; (i + 1u) < (size_t)header.vertex_count; i += 2u) {
        int x0 = vesa_round_to_int(verts[i].x) + g_vesa.camera2d_x;
        int y0 = vesa_round_to_int(verts[i].y) + g_vesa.camera2d_y;
        int x1 = vesa_round_to_int(verts[i + 1u].x) + g_vesa.camera2d_x;
        int y1 = vesa_round_to_int(verts[i + 1u].y) + g_vesa.camera2d_y;
        soft_raster_draw_line_2d(&g_vesa.fb, x0, y0, x1, y1, verts[i].color);
    }
}

static void vesa_cmd_draw_meshes(const uint8_t* payload, size_t payload_size)
{
    (void)payload;
    (void)payload_size;
    /* Future work: decode mesh payload and feed soft_raster_draw_triangle. */
}

static void vesa_cmd_draw_text(const uint8_t* payload, size_t payload_size)
{
    (void)payload;
    (void)payload_size;
    /* Text rendering stub for v1. */
}

static void vesa_execute(const dgfx_cmd_buffer* cmd_buf)
{
    const uint8_t* ptr;
    const uint8_t* end;
    size_t header_size;

    if (!cmd_buf || !cmd_buf->data || cmd_buf->size == 0u) {
        return;
    }
    if (!g_vesa.frame_in_progress) {
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
            vesa_cmd_clear(payload, payload_size);
            break;
        case DGFX_CMD_SET_VIEWPORT:
            vesa_cmd_set_viewport(payload);
            break;
        case DGFX_CMD_SET_CAMERA:
            vesa_cmd_set_camera(payload);
            break;
        case DGFX_CMD_SET_PIPELINE:
            vesa_cmd_set_pipeline(payload);
            break;
        case DGFX_CMD_SET_TEXTURE:
            vesa_cmd_set_texture(payload);
            break;
        case DGFX_CMD_DRAW_SPRITES:
            vesa_cmd_draw_sprites(payload, payload_size);
            break;
        case DGFX_CMD_DRAW_MESHES:
            vesa_cmd_draw_meshes(payload, payload_size);
            break;
        case DGFX_CMD_DRAW_LINES:
            vesa_cmd_draw_lines(payload, payload_size);
            break;
        case DGFX_CMD_DRAW_TEXT:
            vesa_cmd_draw_text(payload, payload_size);
            break;
        default:
            break;
        }

        ptr += total_size;
    }
}
