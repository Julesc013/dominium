#include "soft_gfx.h"

#include <stdlib.h>
#include <string.h>
#include "soft_raster.h"
#include "soft_blit.h"

soft_state_t g_soft;

static bool      soft_init(const dgfx_desc *desc);
static void      soft_shutdown(void);
static dgfx_caps soft_get_caps(void);
static void      soft_resize(int width, int height);
static void      soft_begin_frame(void);
static void      soft_execute(const dgfx_cmd_buffer *cmd);
static void      soft_end_frame(void);

static void soft_build_caps(void);
static void soft_cmd_clear(const uint8_t *payload, uint32_t payload_size);
static void soft_cmd_set_viewport(const uint8_t *payload, uint32_t payload_size);
static void soft_cmd_set_camera(const uint8_t *payload, uint32_t payload_size);
static void soft_cmd_draw_sprites(const uint8_t *payload, uint32_t payload_size);
static void soft_cmd_draw_lines(const uint8_t *payload, uint32_t payload_size);
static void soft_cmd_draw_meshes(const uint8_t *payload, uint32_t payload_size);
static void soft_cmd_draw_text(const uint8_t *payload, uint32_t payload_size);

static const dgfx_backend_vtable g_soft_vtable = {
    soft_init,
    soft_shutdown,
    soft_get_caps,
    soft_resize,
    soft_begin_frame,
    soft_execute,
    soft_end_frame
};

const dgfx_backend_vtable *dgfx_soft_get_vtable(void)
{
    return &g_soft_vtable;
}

static void soft_build_caps(void)
{
    memset(&g_soft.caps, 0, sizeof(g_soft.caps));
    g_soft.caps.supports_2d = g_soft.config.features.enable_2d ? 1 : 0;
    g_soft.caps.supports_3d = g_soft.config.features.enable_3d ? 1 : 0;
    g_soft.caps.supports_vector = g_soft.config.features.enable_vector ? 1 : 0;
    g_soft.caps.supports_raster = g_soft.config.features.enable_raster ? 1 : 0;
    g_soft.caps.supports_text = 1;
    g_soft.caps.max_viewports = 16;
    g_soft.caps.max_render_targets = 1;
    g_soft.caps.name = "soft";
}

static void soft_init_view_state(void)
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

    g_soft.vp.x = 0;
    g_soft.vp.y = 0;
    g_soft.vp.w = g_soft.width;
    g_soft.vp.h = g_soft.height;
}

static bool soft_init(const dgfx_desc *desc)
{
    int width;
    int height;

    width = (desc && desc->width > 0) ? desc->width : 800;
    height = (desc && desc->height > 0) ? desc->height : 600;

    memset(&g_soft, 0, sizeof(g_soft));
    g_soft.width = width;
    g_soft.height = height;

    dgfx_soft_config_get_default(&g_soft.config);
    dgfx_soft_config_apply_profile(&g_soft.config, g_soft.config.profile);

    if (!soft_fb_create(&g_soft.fb,
                        g_soft.width,
                        g_soft.height,
                        g_soft.config.color_format,
                        g_soft.config.depth_bits,
                        g_soft.config.stencil_bits)) {
        soft_shutdown();
        return false;
    }

    g_soft.depth_mem = g_soft.fb.depth;
    g_soft.stencil_mem = g_soft.fb.stencil;

    soft_build_caps();
    soft_init_view_state();

    g_soft.frame_in_progress = 0;
    return true;
}

static void soft_shutdown(void)
{
    soft_fb_destroy(&g_soft.fb);
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

    soft_fb_destroy(&g_soft.fb);
    g_soft.width = width;
    g_soft.height = height;
    if (soft_fb_create(&g_soft.fb,
                       width,
                       height,
                       g_soft.config.color_format,
                       g_soft.config.depth_bits,
                       g_soft.config.stencil_bits)) {
        g_soft.depth_mem = g_soft.fb.depth;
        g_soft.stencil_mem = g_soft.fb.stencil;
        g_soft.vp.x = 0;
        g_soft.vp.y = 0;
        g_soft.vp.w = width;
        g_soft.vp.h = height;
    }
}

static void soft_begin_frame(void)
{
    if (!g_soft.fb.color) {
        g_soft.frame_in_progress = 0;
        return;
    }
    g_soft.frame_in_progress = 1;
    soft_raster_clear_color(&g_soft.fb, 0u, 0u, 0u, 255u);
    if (g_soft.config.features.enable_depth) {
        soft_raster_clear_depth(&g_soft.fb, 1.0f);
    }
    if (g_soft.config.features.enable_stencil) {
        soft_raster_clear_stencil(&g_soft.fb, 0u);
    }
}

static void soft_end_frame(void)
{
    soft_present_fn present;
    present = soft_blit_get_present_callback();
    if (present) {
        present(NULL, &g_soft.fb);
    }
    g_soft.frame_in_progress = 0;
}

static void soft_cmd_clear(const uint8_t *payload, uint32_t payload_size)
{
    uint32_t rgba;

    rgba = 0xff000000u; /* opaque black */
    if (payload && payload_size >= sizeof(uint32_t)) {
        memcpy(&rgba, payload, sizeof(uint32_t));
    }

    soft_raster_clear_color(&g_soft.fb,
                            (uint8_t)((rgba >> 16) & 0xffu),
                            (uint8_t)((rgba >> 8) & 0xffu),
                            (uint8_t)(rgba & 0xffu),
                            (uint8_t)((rgba >> 24) & 0xffu));

    if (g_soft.config.features.enable_depth) {
        soft_raster_clear_depth(&g_soft.fb, 1.0f);
    }
    if (g_soft.config.features.enable_stencil) {
        soft_raster_clear_stencil(&g_soft.fb, 0u);
    }
}

static void soft_cmd_set_viewport(const uint8_t *payload, uint32_t payload_size)
{
    (void)payload_size;
    if (!payload || payload_size < sizeof(dgfx_viewport_t)) {
        return;
    }
    memcpy(&g_soft.vp, payload, sizeof(dgfx_viewport_t));
}

static void soft_cmd_set_camera(const uint8_t *payload, uint32_t payload_size)
{
    if (!payload || payload_size < sizeof(dgfx_camera_t)) {
        return;
    }
    {
        const dgfx_camera_t *cam = (const dgfx_camera_t *)payload;
        memcpy(g_soft.view, cam->view, sizeof(g_soft.view));
        memcpy(g_soft.proj, cam->proj, sizeof(g_soft.proj));
        memcpy(g_soft.world, cam->world, sizeof(g_soft.world));
    }
}

static void soft_cmd_draw_sprites(const uint8_t *payload, uint32_t payload_size)
{
    uint32_t count;
    uint32_t i;
    const dgfx_sprite_t *sprites;

    if (!payload || payload_size < sizeof(dgfx_sprite_t)) {
        return;
    }
    if (!g_soft.config.features.enable_2d) {
        return;
    }

    count = payload_size / (uint32_t)sizeof(dgfx_sprite_t);
    sprites = (const dgfx_sprite_t *)payload;

    for (i = 0u; i < count; ++i) {
        const dgfx_sprite_t *spr;
        int x0;
        int y0;
        int x1;
        int y1;
        int w;
        int h;

        spr = sprites + i;
        x0 = spr->x + g_soft.vp.x;
        y0 = spr->y + g_soft.vp.y;
        x1 = x0 + spr->w;
        y1 = y0 + spr->h;

        if (x0 < g_soft.vp.x) x0 = g_soft.vp.x;
        if (y0 < g_soft.vp.y) y0 = g_soft.vp.y;
        if (x1 > g_soft.vp.x + g_soft.vp.w) x1 = g_soft.vp.x + g_soft.vp.w;
        if (y1 > g_soft.vp.y + g_soft.vp.h) y1 = g_soft.vp.y + g_soft.vp.h;

        w = x1 - x0;
        h = y1 - y0;
        if (w > 0 && h > 0) {
            soft_raster_fill_rect_2d(&g_soft.fb, x0, y0, w, h, spr->color_rgba);
        }
    }
}

static void soft_cmd_draw_lines(const uint8_t *payload, uint32_t payload_size)
{
    uint32_t count;
    uint32_t i;
    const dgfx_line_segment_t *lines;

    if (!payload || payload_size < sizeof(dgfx_line_segment_t)) {
        return;
    }
    if (!g_soft.config.features.enable_vector) {
        return;
    }

    count = payload_size / (uint32_t)sizeof(dgfx_line_segment_t);
    lines = (const dgfx_line_segment_t *)payload;

    for (i = 0u; i < count; ++i) {
        const dgfx_line_segment_t *ln;
        int x0;
        int y0;
        int x1;
        int y1;
        ln = lines + i;
        x0 = ln->x0 + g_soft.vp.x;
        y0 = ln->y0 + g_soft.vp.y;
        x1 = ln->x1 + g_soft.vp.x;
        y1 = ln->y1 + g_soft.vp.y;
        soft_raster_draw_line_2d(&g_soft.fb, x0, y0, x1, y1, ln->color_rgba);
    }
}

static void soft_cmd_draw_meshes(const uint8_t *payload, uint32_t payload_size)
{
    uint32_t count;
    uint32_t i;
    const dgfx_mesh_draw_t *meshes;

    if (!payload || payload_size < sizeof(dgfx_mesh_draw_t)) {
        return;
    }
    if (!g_soft.config.features.enable_3d && !g_soft.config.features.enable_raster) {
        return;
    }

    count = payload_size / (uint32_t)sizeof(dgfx_mesh_draw_t);
    meshes = (const dgfx_mesh_draw_t *)payload;

    for (i = 0u; i < count; ++i) {
        const dgfx_mesh_draw_t *m;
        uint32_t tri;

        m = meshes + i;
        if (!m->positions || !m->indices || m->index_count < 3u) {
            continue;
        }

        for (tri = 0u; tri + 2u < m->index_count; tri += 3u) {
            uint32_t i0;
            uint32_t i1;
            uint32_t i2;
            soft_vertex vtx0;
            soft_vertex vtx1;
            soft_vertex vtx2;
            const float *p0;
            const float *p1;
            const float *p2;
            uint32_t color;

            i0 = m->indices[tri + 0u];
            i1 = m->indices[tri + 1u];
            i2 = m->indices[tri + 2u];
            if (i0 >= m->vertex_count || i1 >= m->vertex_count || i2 >= m->vertex_count) {
                continue;
            }

            p0 = m->positions + (size_t)i0 * 3u;
            p1 = m->positions + (size_t)i1 * 3u;
            p2 = m->positions + (size_t)i2 * 3u;

            color = 0xffffffffu;

            vtx0.x = p0[0] + (float)g_soft.vp.x;
            vtx0.y = p0[1] + (float)g_soft.vp.y;
            vtx0.z = p0[2];
            vtx0.w = 1.0f;
            vtx0.u = 0.0f;
            vtx0.v = 0.0f;
            vtx0.rgba = color;

            vtx1.x = p1[0] + (float)g_soft.vp.x;
            vtx1.y = p1[1] + (float)g_soft.vp.y;
            vtx1.z = p1[2];
            vtx1.w = 1.0f;
            vtx1.u = 0.0f;
            vtx1.v = 0.0f;
            vtx1.rgba = color;

            vtx2.x = p2[0] + (float)g_soft.vp.x;
            vtx2.y = p2[1] + (float)g_soft.vp.y;
            vtx2.z = p2[2];
            vtx2.w = 1.0f;
            vtx2.u = 0.0f;
            vtx2.v = 0.0f;
            vtx2.rgba = color;

            soft_raster_draw_triangle(&g_soft.fb, &vtx0, &vtx1, &vtx2,
                                      g_soft.config.features.enable_depth ? 1 : 0);
        }
    }
}

static void soft_cmd_draw_text(const uint8_t *payload, uint32_t payload_size)
{
    (void)payload_size;
    if (!payload) {
        return;
    }
    {
        const dgfx_text_draw_t *t = (const dgfx_text_draw_t *)payload;
        int x = t->x + g_soft.vp.x;
        int y = t->y + g_soft.vp.y;
        if (!g_soft.caps.supports_text) {
            return;
        }
        if (!t->utf8_text) {
            return;
        }
        soft_raster_draw_text_stub(&g_soft.fb, x, y, t->color_rgba, t->utf8_text);
    }
}

static void soft_execute(const dgfx_cmd_buffer *cmd)
{
    const uint8_t *ptr;
    const uint8_t *end;

    if (!cmd || !cmd->data || cmd->size == 0u) {
        return;
    }
    if (!g_soft.frame_in_progress) {
        return;
    }

    ptr = cmd->data;
    end = cmd->data + cmd->size;

    while (ptr + sizeof(dgfx_cmd_header) <= end) {
        const dgfx_cmd_header *hdr;
        const uint8_t *payload;
        const uint8_t *next;
        uint32_t payload_size;
        uint32_t cmd_size;

        hdr = (const dgfx_cmd_header *)ptr;
        cmd_size = hdr->size;
        if (cmd_size < sizeof(dgfx_cmd_header)) {
            cmd_size = (uint32_t)sizeof(dgfx_cmd_header) + (uint32_t)hdr->payload_size;
        }

        next = ptr + cmd_size;
        if (next > end) {
            break;
        }

        payload = ptr + sizeof(dgfx_cmd_header);
        payload_size = cmd_size - (uint32_t)sizeof(dgfx_cmd_header);

        switch (hdr->opcode) {
        case DGFX_CMD_CLEAR:
            soft_cmd_clear(payload, payload_size);
            break;
        case DGFX_CMD_SET_VIEWPORT:
            soft_cmd_set_viewport(payload, payload_size);
            break;
        case DGFX_CMD_SET_CAMERA:
            soft_cmd_set_camera(payload, payload_size);
            break;
        case DGFX_CMD_SET_PIPELINE:
            /* pipeline state not modeled yet */
            break;
        case DGFX_CMD_SET_TEXTURE:
            /* textures not modeled yet */
            break;
        case DGFX_CMD_DRAW_SPRITES:
            soft_cmd_draw_sprites(payload, payload_size);
            break;
        case DGFX_CMD_DRAW_LINES:
            soft_cmd_draw_lines(payload, payload_size);
            break;
        case DGFX_CMD_DRAW_MESHES:
            soft_cmd_draw_meshes(payload, payload_size);
            break;
        case DGFX_CMD_DRAW_TEXT:
            soft_cmd_draw_text(payload, payload_size);
            break;
        default:
            break;
        }

        ptr = next;
    }
}

#if 0
#include "domino/canvas.h"
/* Minimal smoke test for the software backend */
static void soft_backend_smoke_test(void)
{
    dgfx_desc desc;
    dgfx_viewport_t vp_main;
    dgfx_viewport_t vp_ui;
    dgfx_sprite_t ui_rect;
    dgfx_line_segment_t line;
    dgfx_mesh_draw_t mesh;
    float tri_positions[9];
    uint32_t tri_indices[3];
    dcvs *canvas;
    const dgfx_cmd_buffer *buf;

    memset(&desc, 0, sizeof(desc));
    desc.backend = DGFX_BACKEND_SOFT;
    desc.width = 320;
    desc.height = 200;

    if (!dgfx_init(&desc)) {
        return;
    }

    canvas = dgfx_get_frame_canvas();
    if (!canvas) {
        dgfx_shutdown();
        return;
    }

    dgfx_begin_frame();

    dcvs_clear(canvas, 0xff202040u);

    vp_main.x = 0; vp_main.y = 0; vp_main.w = 320; vp_main.h = 150;
    dcvs_set_viewport(canvas, &vp_main);

    tri_positions[0] = 50.0f; tri_positions[1] = 50.0f; tri_positions[2] = 0.2f;
    tri_positions[3] = 150.0f; tri_positions[4] = 60.0f; tri_positions[5] = 0.3f;
    tri_positions[6] = 100.0f; tri_positions[7] = 140.0f; tri_positions[8] = 0.1f;
    tri_indices[0] = 0u; tri_indices[1] = 1u; tri_indices[2] = 2u;
    memset(&mesh, 0, sizeof(mesh));
    mesh.positions = tri_positions;
    mesh.indices = tri_indices;
    mesh.vertex_count = 3u;
    mesh.index_count = 3u;
    dcvs_draw_mesh(canvas, &mesh);

    vp_ui.x = 0; vp_ui.y = 150; vp_ui.w = 320; vp_ui.h = 50;
    dcvs_set_viewport(canvas, &vp_ui);

    ui_rect.x = 10; ui_rect.y = 160; ui_rect.w = 80; ui_rect.h = 30;
    ui_rect.color_rgba = 0xff00ff00u;
    dcvs_draw_sprite(canvas, &ui_rect);

    line.x0 = 0; line.y0 = 150; line.x1 = 319; line.y1 = 150;
    line.color_rgba = 0xffffffffu;
    line.thickness = 1;
    dcvs_draw_line(canvas, &line);

    buf = dcvs_get_cmd_buffer(canvas);
    dgfx_execute(buf);
    dgfx_end_frame();
    dgfx_shutdown();
}
#endif
