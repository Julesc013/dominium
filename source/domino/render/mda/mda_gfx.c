#include "mda_gfx.h"

#include <stdlib.h>
#include <string.h>

#include "mda_hw.h"

mda_state_t g_mda;

typedef struct mda_cmd_clear_payload_t {
    uint8_t r;
    uint8_t g;
    uint8_t b;
    uint8_t a;
} mda_cmd_clear_payload_t;

typedef struct mda_lines_header_t {
    uint16_t vertex_count;
    uint16_t reserved;
} mda_lines_header_t;

typedef struct mda_line_vertex_t {
    float    x;
    float    y;
    float    z;
    uint32_t color;
} mda_line_vertex_t;

typedef struct mda_sprite_t {
    int32_t  x;
    int32_t  y;
    int32_t  w;
    int32_t  h;
    uint32_t color_rgba;
} mda_sprite_t;

typedef struct mda_camera_payload_t {
    int32_t offset_x;
    int32_t offset_y;
} mda_camera_payload_t;

static void      mda_init_matrices_and_viewport(void);
static void      mda_build_caps(void);

static bool      mda_init(const dgfx_desc* desc);
static void      mda_shutdown(void);
static dgfx_caps mda_get_caps(void);
static void      mda_resize(int width, int height);
static void      mda_begin_frame(void);
static void      mda_execute(const dgfx_cmd_buffer* cmd_buf);
static void      mda_end_frame(void);

static void mda_cmd_clear(const uint8_t* payload, size_t payload_size);
static void mda_cmd_set_viewport(const uint8_t* payload);
static void mda_cmd_set_camera(const uint8_t* payload);
static void mda_cmd_set_pipeline(const uint8_t* payload);
static void mda_cmd_set_texture(const uint8_t* payload);
static void mda_cmd_draw_sprites(const uint8_t* payload, size_t payload_size);
static void mda_cmd_draw_lines(const uint8_t* payload, size_t payload_size);
static void mda_cmd_draw_meshes(const uint8_t* payload, size_t payload_size);
static void mda_cmd_draw_text(const uint8_t* payload, size_t payload_size);

static int mda_round_to_int(float v);

static const dgfx_backend_vtable g_mda_vtable = {
    mda_init,
    mda_shutdown,
    mda_get_caps,
    mda_resize,
    mda_begin_frame,
    mda_execute,
    mda_end_frame
};

const dgfx_backend_vtable* dgfx_mda_get_vtable(void)
{
    return &g_mda_vtable;
}

static void mda_init_matrices_and_viewport(void)
{
    int i;
    for (i = 0; i < 16; ++i) {
        g_mda.view[i] = 0.0f;
        g_mda.proj[i] = 0.0f;
        g_mda.world[i] = 0.0f;
    }
    g_mda.view[0] = g_mda.view[5] = g_mda.view[10] = g_mda.view[15] = 1.0f;
    g_mda.proj[0] = g_mda.proj[5] = g_mda.proj[10] = g_mda.proj[15] = 1.0f;
    g_mda.world[0] = g_mda.world[5] = g_mda.world[10] = g_mda.world[15] = 1.0f;

    g_mda.vp_x = 0;
    g_mda.vp_y = 0;
    g_mda.vp_w = g_mda.width;
    g_mda.vp_h = g_mda.height;
    g_mda.camera2d_x = 0;
    g_mda.camera2d_y = 0;
}

static void mda_build_caps(void)
{
    memset(&g_mda.caps, 0, sizeof(g_mda.caps));
    g_mda.caps.name = "mda";
    g_mda.caps.supports_2d = g_mda.config.features.enable_2d ? true : false;
    g_mda.caps.supports_3d = g_mda.config.features.enable_3d ? true : false;
    g_mda.caps.supports_text = false;
    g_mda.caps.supports_rt = g_mda.config.features.enable_raster ? true : false;
    g_mda.caps.supports_alpha = false;
    g_mda.caps.max_texture_size = 0;
}

static bool mda_init(const dgfx_desc* desc)
{
    (void)desc;

    if (mda_hw_init() != 0) {
        return false;
    }

    memset(&g_mda, 0, sizeof(g_mda));

    if (mda_hw_set_mode_720x350(&g_mda.mode) != 0) {
        mda_shutdown();
        return false;
    }

    g_mda.width = g_mda.mode.width;
    g_mda.height = g_mda.mode.height;

    dgfx_soft_config_get_default(&g_mda.config);
    g_mda.config.color_format = DGFX_SOFT_FMT_8_INDEXED; /* 8bpp grayscale buffer */

    if (g_mda.config.profile == DGFX_SOFT_PROFILE_NULL) {
        g_mda.config.profile = DGFX_SOFT_PROFILE_BALANCED;
    }
    dgfx_soft_config_apply_profile(&g_mda.config, g_mda.config.profile);
    g_mda.config.color_format = DGFX_SOFT_FMT_8_INDEXED;
    g_mda.config.allow_resize = 0u;

    if (!soft_fb_create(&g_mda.fb,
                        g_mda.width,
                        g_mda.height,
                        g_mda.config.color_format,
                        g_mda.config.depth_bits,
                        g_mda.config.stencil_bits)) {
        mda_shutdown();
        return false;
    }
    g_mda.depth = g_mda.fb.depth;
    g_mda.stencil = g_mda.fb.stencil;

    mda_init_matrices_and_viewport();
    mda_build_caps();

    g_mda.frame_in_progress = 0;
    return true;
}

static void mda_shutdown(void)
{
    soft_fb_destroy(&g_mda.fb);

    mda_hw_restore_text_mode();
    memset(&g_mda, 0, sizeof(g_mda));
}

static dgfx_caps mda_get_caps(void)
{
    return g_mda.caps;
}

static void mda_resize(int width, int height)
{
    (void)width;
    (void)height;
    /* MDA graphics mode is fixed at 720x350. */
}

static void mda_begin_frame(void)
{
    if (!g_mda.fb.color) {
        return;
    }

    g_mda.frame_in_progress = 1;
    soft_raster_clear_color(&g_mda.fb, 0, 0, 0, 255);
    if (g_mda.fb.depth && g_mda.config.features.enable_depth) {
        soft_raster_clear_depth(&g_mda.fb, 1.0f);
    }
    if (g_mda.fb.stencil && g_mda.config.features.enable_stencil) {
        soft_raster_clear_stencil(&g_mda.fb, 0u);
    }
}

static void mda_end_frame(void)
{
    if (!g_mda.frame_in_progress) {
        return;
    }
    if (!g_mda.fb.color) {
        g_mda.frame_in_progress = 0;
        return;
    }

    mda_hw_blit_720x350(
        g_mda.fb.color,
        (uint16_t)g_mda.width,
        (uint16_t)g_mda.height,
        (uint16_t)g_mda.fb.stride_bytes);

    g_mda.frame_in_progress = 0;
}

static void mda_cmd_clear(const uint8_t* payload, size_t payload_size)
{
    uint8_t r = 0u;
    uint8_t g = 0u;
    uint8_t b = 0u;
    uint8_t a = 255u;

    if (payload && payload_size >= sizeof(mda_cmd_clear_payload_t)) {
        mda_cmd_clear_payload_t clr;
        memcpy(&clr, payload, sizeof(clr));
        r = clr.r;
        g = clr.g;
        b = clr.b;
        a = clr.a;
    }

    soft_raster_clear_color(&g_mda.fb, r, g, b, a);
    if (g_mda.fb.depth && g_mda.config.features.enable_depth) {
        soft_raster_clear_depth(&g_mda.fb, 1.0f);
    }
    if (g_mda.fb.stencil && g_mda.config.features.enable_stencil) {
        soft_raster_clear_stencil(&g_mda.fb, 0u);
    }
}

static void mda_cmd_set_viewport(const uint8_t* payload)
{
    (void)payload;
    g_mda.vp_x = 0;
    g_mda.vp_y = 0;
    g_mda.vp_w = g_mda.width;
    g_mda.vp_h = g_mda.height;
}

static void mda_cmd_set_camera(const uint8_t* payload)
{
    if (payload) {
        const mda_camera_payload_t* cam = (const mda_camera_payload_t*)payload;
        g_mda.camera2d_x = cam->offset_x;
        g_mda.camera2d_y = cam->offset_y;
    }
}

static void mda_cmd_set_pipeline(const uint8_t* payload)
{
    (void)payload;
    /* Pipeline selection is not modeled for the MDA backend. */
}

static void mda_cmd_set_texture(const uint8_t* payload)
{
    (void)payload;
    /* Texturing is not supported in the MDA backend. */
}

static void mda_cmd_draw_sprites(const uint8_t* payload, size_t payload_size)
{
    size_t count;
    size_t i;

    if (!payload || payload_size < sizeof(mda_sprite_t)) {
        return;
    }
    if (!g_mda.config.features.enable_2d) {
        return;
    }

    count = payload_size / sizeof(mda_sprite_t);
    for (i = 0u; i < count; ++i) {
        const mda_sprite_t* spr = ((const mda_sprite_t*)payload) + i;
        int x = spr->x + g_mda.camera2d_x;
        int y = spr->y + g_mda.camera2d_y;
        soft_raster_fill_rect_2d(&g_mda.fb, x, y, spr->w, spr->h, spr->color_rgba);
    }
}

static int mda_round_to_int(float v)
{
    return (int)((v >= 0.0f) ? (v + 0.5f) : (v - 0.5f));
}

static void mda_cmd_draw_lines(const uint8_t* payload, size_t payload_size)
{
    mda_lines_header_t header;
    const mda_line_vertex_t* verts;
    size_t required;
    size_t i;

    if (!payload || payload_size < sizeof(header)) {
        return;
    }
    if (!g_mda.config.features.enable_vector) {
        return;
    }

    memcpy(&header, payload, sizeof(header));
    required = sizeof(header) + ((size_t)header.vertex_count * sizeof(mda_line_vertex_t));
    if (payload_size < required || header.vertex_count < 2u) {
        return;
    }

    verts = (const mda_line_vertex_t*)(payload + sizeof(header));
    for (i = 0u; (i + 1u) < (size_t)header.vertex_count; i += 2u) {
        int x0 = mda_round_to_int(verts[i].x) + g_mda.camera2d_x;
        int y0 = mda_round_to_int(verts[i].y) + g_mda.camera2d_y;
        int x1 = mda_round_to_int(verts[i + 1u].x) + g_mda.camera2d_x;
        int y1 = mda_round_to_int(verts[i + 1u].y) + g_mda.camera2d_y;
        soft_raster_draw_line_2d(&g_mda.fb, x0, y0, x1, y1, verts[i].color);
    }
}

static void mda_cmd_draw_meshes(const uint8_t* payload, size_t payload_size)
{
    (void)payload;
    (void)payload_size;
    /* CPU triangles are stubbed for the MDA backend v1. */
}

static void mda_cmd_draw_text(const uint8_t* payload, size_t payload_size)
{
    (void)payload;
    (void)payload_size;
    /* Text rendering is not implemented in the MDA backend. */
}

static void mda_execute(const dgfx_cmd_buffer* cmd_buf)
{
    const uint8_t* ptr;
    const uint8_t* end;
    size_t header_size;

    if (!cmd_buf || !cmd_buf->data || cmd_buf->size == 0u) {
        return;
    }
    if (!g_mda.frame_in_progress) {
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
            mda_cmd_clear(payload, payload_size);
            break;
        case DGFX_CMD_SET_VIEWPORT:
            mda_cmd_set_viewport(payload);
            break;
        case DGFX_CMD_SET_CAMERA:
            mda_cmd_set_camera(payload);
            break;
        case DGFX_CMD_SET_PIPELINE:
            mda_cmd_set_pipeline(payload);
            break;
        case DGFX_CMD_SET_TEXTURE:
            mda_cmd_set_texture(payload);
            break;
        case DGFX_CMD_DRAW_SPRITES:
            mda_cmd_draw_sprites(payload, payload_size);
            break;
        case DGFX_CMD_DRAW_MESHES:
            mda_cmd_draw_meshes(payload, payload_size);
            break;
        case DGFX_CMD_DRAW_LINES:
            mda_cmd_draw_lines(payload, payload_size);
            break;
        case DGFX_CMD_DRAW_TEXT:
            mda_cmd_draw_text(payload, payload_size);
            break;
        default:
            break;
        }

        ptr += total_size;
    }
}
