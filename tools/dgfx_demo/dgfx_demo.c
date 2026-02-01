/*
FILE: source/tools/dgfx_demo/dgfx_demo.c
MODULE: Repository
LAYER / SUBSYSTEM: source/tools/dgfx_demo
RESPONSIBILITY: Owns documentation for this translation unit.
ALLOWED DEPENDENCIES: Project-local headers; C89/C++98 standard headers.
FORBIDDEN DEPENDENCIES: N/A.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/specs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A.
EXTENSION POINTS: Extend via public headers and relevant `docs/specs/SPEC_*.md` without cross-layer coupling.
*/
#include "dgfx_demo.h"

#include <math.h>
#include <string.h>
#include <stdio.h>
#include <stdint.h>

#include "domino/canvas.h"

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

static const float demo_cube_positions[] = {
    -1.0f, -1.0f, -1.0f,
     1.0f, -1.0f, -1.0f,
     1.0f,  1.0f, -1.0f,
    -1.0f,  1.0f, -1.0f,
    -1.0f, -1.0f,  1.0f,
     1.0f, -1.0f,  1.0f,
     1.0f,  1.0f,  1.0f,
    -1.0f,  1.0f,  1.0f
};

static const uint32_t demo_cube_indices[] = {
    0, 1, 2, 0, 2, 3,      /* back */
    4, 5, 6, 4, 6, 7,      /* front */
    0, 1, 5, 0, 5, 4,      /* bottom */
    2, 3, 7, 2, 7, 6,      /* top */
    1, 2, 6, 1, 6, 5,      /* right */
    0, 3, 7, 0, 7, 4       /* left */
};

static float demo_cube_main_positions[24];
static float demo_cube_minimap_positions[24];

static void demo_mat4_identity(float m[16]);
static void demo_mat4_mul(float out[16], const float a[16], const float b[16]);
static void demo_mat4_perspective(float m[16], float fov_y_rad, float aspect, float z_near, float z_far);
static void demo_mat4_ortho(float m[16], float left, float right, float bottom, float top, float z_near, float z_far);
static void demo_mat4_look_at(float m[16],
                              float eye_x, float eye_y, float eye_z,
                              float at_x, float at_y, float at_z,
                              float up_x, float up_y, float up_z);
static void demo_mat4_rotate_y(float m[16], float radians);

static void demo_transform_positions(float *out24,
                                     const float *in24,
                                     const float mvp[16],
                                     const dgfx_viewport_t *vp);

static void dgfx_demo_make_perspective_camera(dgfx_camera_t *cam, int frame, int w, int h);
static void dgfx_demo_make_topdown_camera(dgfx_camera_t *cam, int w, int h);
static void dgfx_demo_make_2d_camera(dgfx_camera_t *cam);
static void dgfx_demo_record_frame(dcvs *c, int frame_index, int width, int height);

int dgfx_run_demo_single_frame(dgfx_backend_t backend)
{
    dgfx_desc desc;
    dcvs *c;
    const dgfx_cmd_buffer *buf;

    memset(&desc, 0, sizeof(desc));
    desc.backend = backend;
    desc.width = 800;
    desc.height = 600;
    desc.fullscreen = 0;
    desc.vsync = 0;
    desc.native_window = NULL;

    if (!dgfx_init(&desc)) {
        return 1;
    }

    c = dcvs_create(64u * 1024u);
    if (!c) {
        dgfx_shutdown();
        return 2;
    }

    dgfx_begin_frame();
    dcvs_reset(c);
    dgfx_demo_record_frame(c, 0, desc.width, desc.height);
    buf = dcvs_get_cmd_buffer(c);
    dgfx_execute(buf);
    dgfx_end_frame();

    dcvs_destroy(c);
    dgfx_shutdown();

    return 0;
}

int dgfx_run_demo(dgfx_backend_t backend)
{
    dgfx_desc desc;
    dcvs *c;
    const dgfx_cmd_buffer *buf;
    int frame;
    const int max_frames = 300;

    memset(&desc, 0, sizeof(desc));
    desc.backend = backend;
    desc.width = 800;
    desc.height = 600;
    desc.fullscreen = 0;
    desc.vsync = 0;
    desc.native_window = NULL;

    if (!dgfx_init(&desc)) {
        return 1;
    }

    c = dcvs_create(64u * 1024u);
    if (!c) {
        dgfx_shutdown();
        return 2;
    }

    for (frame = 0; frame < max_frames; ++frame) {
        dgfx_begin_frame();
        dcvs_reset(c);

        dgfx_demo_record_frame(c, frame, desc.width, desc.height);

        buf = dcvs_get_cmd_buffer(c);
        dgfx_execute(buf);
        dgfx_end_frame();
    }

    dcvs_destroy(c);
    dgfx_shutdown();
    return 0;
}

static void dgfx_demo_record_frame(dcvs *c, int frame_index, int width, int height)
{
    uint32_t clear_color;
    dgfx_viewport_t vp_main;
    dgfx_viewport_t vp_minimap;
    dgfx_viewport_t vp_ui;
    dgfx_camera_t cam_main;
    dgfx_camera_t cam_minimap;
    dgfx_camera_t cam_ui;
    dgfx_mesh_draw_t mesh;
    float world[16];
    float temp[16];
    float mvp[16];
    dgfx_sprite_t bar;
    dgfx_line_segment_t line;
    char text_buf[64];
    dgfx_text_draw_t txt;

    clear_color = 0x202020FFu;
    dcvs_clear(c, clear_color);

    /* Main viewport: 3D cube */
    vp_main.x = 0;
    vp_main.y = 0;
    vp_main.w = (width * 2) / 3;
    vp_main.h = (height * 3) / 4;
    dcvs_set_viewport(c, &vp_main);

    dgfx_demo_make_perspective_camera(&cam_main, frame_index, vp_main.w, vp_main.h);
    dcvs_set_camera(c, &cam_main);

    memcpy(world, cam_main.world, sizeof(world));
    demo_mat4_mul(temp, cam_main.view, world);
    demo_mat4_mul(mvp, cam_main.proj, temp);
    demo_transform_positions(demo_cube_main_positions, demo_cube_positions, mvp, &vp_main);

    memset(&mesh, 0, sizeof(mesh));
    mesh.positions = demo_cube_main_positions;
    mesh.indices = demo_cube_indices;
    mesh.vertex_count = 8u;
    mesh.index_count = (uint32_t)(sizeof(demo_cube_indices) / sizeof(demo_cube_indices[0]));
    dcvs_draw_mesh(c, &mesh);

    /* Minimap viewport */
    vp_minimap.x = (width * 2) / 3;
    vp_minimap.y = 0;
    vp_minimap.w = width - vp_minimap.x;
    vp_minimap.h = height / 2;
    dcvs_set_viewport(c, &vp_minimap);

    dgfx_demo_make_topdown_camera(&cam_minimap, vp_minimap.w, vp_minimap.h);
    dcvs_set_camera(c, &cam_minimap);

    memcpy(world, cam_minimap.world, sizeof(world));
    demo_mat4_mul(temp, cam_minimap.view, world);
    demo_mat4_mul(mvp, cam_minimap.proj, temp);
    demo_transform_positions(demo_cube_minimap_positions, demo_cube_positions, mvp, &vp_minimap);

    mesh.positions = demo_cube_minimap_positions;
    dcvs_draw_mesh(c, &mesh);

    /* Simple cross lines for minimap */
    line.color_rgba = 0xFFAA00FFu;
    line.thickness = 1;
    line.x0 = 0;
    line.y0 = vp_minimap.h / 2;
    line.x1 = vp_minimap.w;
    line.y1 = vp_minimap.h / 2;
    dcvs_draw_line(c, &line);
    line.x0 = vp_minimap.w / 2;
    line.y0 = 0;
    line.x1 = vp_minimap.w / 2;
    line.y1 = vp_minimap.h;
    dcvs_draw_line(c, &line);

    /* UI overlay */
    vp_ui.x = 0;
    vp_ui.y = (height * 3) / 4;
    vp_ui.w = width;
    vp_ui.h = height - vp_ui.y;
    dcvs_set_viewport(c, &vp_ui);

    dgfx_demo_make_2d_camera(&cam_ui);
    dcvs_set_camera(c, &cam_ui);

    bar.x = 10;
    bar.y = 10;
    bar.w = vp_ui.w - 20;
    bar.h = vp_ui.h - 20;
    bar.color_rgba = 0x404080FFu;
    dcvs_draw_sprite(c, &bar);

    line.x0 = 10;
    line.y0 = 10;
    line.x1 = vp_ui.w - 10;
    line.y1 = vp_ui.h - 10;
    line.color_rgba = 0xFFFFFFFFu;
    line.thickness = 1;
    dcvs_draw_line(c, &line);

    sprintf(text_buf, "Frame: %d", frame_index);
    txt.x = 20;
    txt.y = 20;
    txt.color_rgba = 0xFFFFFFFFu;
    txt.utf8_text = text_buf;
    dcvs_draw_text(c, &txt);
}

static void demo_mat4_identity(float m[16])
{
    int i;
    for (i = 0; i < 16; ++i) {
        m[i] = 0.0f;
    }
    m[0] = m[5] = m[10] = m[15] = 1.0f;
}

static void demo_mat4_mul(float out[16], const float a[16], const float b[16])
{
    int r, c;
    for (c = 0; c < 4; ++c) {
        for (r = 0; r < 4; ++r) {
            out[c * 4 + r] =
                a[0 * 4 + r] * b[c * 4 + 0] +
                a[1 * 4 + r] * b[c * 4 + 1] +
                a[2 * 4 + r] * b[c * 4 + 2] +
                a[3 * 4 + r] * b[c * 4 + 3];
        }
    }
}

static void demo_mat4_perspective(float m[16], float fov_y_rad, float aspect, float z_near, float z_far)
{
    float f;
    float inv_nf;

    demo_mat4_identity(m);
    if (aspect == 0.0f) {
        aspect = 1.0f;
    }
    f = 1.0f / (float)tan(fov_y_rad * 0.5f);
    inv_nf = 1.0f / (z_near - z_far);

    m[0] = f / aspect;
    m[5] = f;
    m[10] = (z_far + z_near) * inv_nf;
    m[11] = -1.0f;
    m[14] = (2.0f * z_far * z_near) * inv_nf;
    m[15] = 0.0f;
}

static void demo_mat4_ortho(float m[16], float left, float right, float bottom, float top, float z_near, float z_far)
{
    demo_mat4_identity(m);
    if (right != left) m[0] = 2.0f / (right - left);
    if (top != bottom) m[5] = 2.0f / (top - bottom);
    if (z_far != z_near) m[10] = -2.0f / (z_far - z_near);
    m[12] = -(right + left) / (right - left);
    m[13] = -(top + bottom) / (top - bottom);
    m[14] = -(z_far + z_near) / (z_far - z_near);
}

static void demo_mat4_look_at(float m[16],
                              float eye_x, float eye_y, float eye_z,
                              float at_x, float at_y, float at_z,
                              float up_x, float up_y, float up_z)
{
    float fx, fy, fz;
    float rx, ry, rz;
    float ux, uy, uz;
    float len;

    fx = at_x - eye_x;
    fy = at_y - eye_y;
    fz = at_z - eye_z;
    len = (float)sqrt(fx * fx + fy * fy + fz * fz);
    if (len != 0.0f) {
        fx /= len;
        fy /= len;
        fz /= len;
    }

    ux = up_x;
    uy = up_y;
    uz = up_z;
    len = (float)sqrt(ux * ux + uy * uy + uz * uz);
    if (len != 0.0f) {
        ux /= len;
        uy /= len;
        uz /= len;
    }

    rx = fy * uz - fz * uy;
    ry = fz * ux - fx * uz;
    rz = fx * uy - fy * ux;
    len = (float)sqrt(rx * rx + ry * ry + rz * rz);
    if (len != 0.0f) {
        rx /= len;
        ry /= len;
        rz /= len;
    }

    ux = ry * fz - rz * fy;
    uy = rz * fx - rx * fz;
    uz = rx * fy - ry * fx;

    m[0] = rx;  m[4] = ux;  m[8]  = -fx; m[12] = 0.0f;
    m[1] = ry;  m[5] = uy;  m[9]  = -fy; m[13] = 0.0f;
    m[2] = rz;  m[6] = uz;  m[10] = -fz; m[14] = 0.0f;
    m[3] = 0.0f; m[7] = 0.0f; m[11] = 0.0f; m[15] = 1.0f;

    {
        float t[16];
        demo_mat4_identity(t);
        t[12] = -eye_x;
        t[13] = -eye_y;
        t[14] = -eye_z;
        demo_mat4_mul(m, m, t);
    }
}

static void demo_mat4_rotate_y(float m[16], float radians)
{
    float c = (float)cos(radians);
    float s = (float)sin(radians);
    demo_mat4_identity(m);
    m[0] = c;
    m[2] = s;
    m[8] = -s;
    m[10] = c;
}

static void demo_transform_positions(float *out24,
                                     const float *in24,
                                     const float mvp[16],
                                     const dgfx_viewport_t *vp)
{
    int i;
    for (i = 0; i < 8; ++i) {
        float x = in24[i * 3 + 0];
        float y = in24[i * 3 + 1];
        float z = in24[i * 3 + 2];
        float cx = mvp[0] * x + mvp[4] * y + mvp[8]  * z + mvp[12];
        float cy = mvp[1] * x + mvp[5] * y + mvp[9]  * z + mvp[13];
        float cz = mvp[2] * x + mvp[6] * y + mvp[10] * z + mvp[14];
        float cw = mvp[3] * x + mvp[7] * y + mvp[11] * z + mvp[15];
        float ndc_x;
        float ndc_y;
        float ndc_z;
        float inv_w;

        if (cw != 0.0f) {
            inv_w = 1.0f / cw;
        } else {
            inv_w = 1.0f;
        }
        ndc_x = cx * inv_w;
        ndc_y = cy * inv_w;
        ndc_z = cz * inv_w;

        out24[i * 3 + 0] = (ndc_x * 0.5f + 0.5f) * (float)vp->w + (float)vp->x;
        out24[i * 3 + 1] = (1.0f - (ndc_y * 0.5f + 0.5f)) * (float)vp->h + (float)vp->y;
        out24[i * 3 + 2] = ndc_z;
    }
}

static void dgfx_demo_make_perspective_camera(dgfx_camera_t *cam, int frame, int w, int h)
{
    float angle;
    float radius;
    float eye_x;
    float eye_y;
    float eye_z;
    float view[16];
    float proj[16];
    float world[16];

    angle = (float)(frame % 360) * ((float)M_PI / 180.0f);
    radius = 4.0f;

    eye_x = radius * (float)cos(angle);
    eye_y = 2.0f;
    eye_z = radius * (float)sin(angle);

    demo_mat4_look_at(view, eye_x, eye_y, eye_z, 0.0f, 0.0f, 0.0f, 0.0f, 1.0f, 0.0f);
    demo_mat4_perspective(proj, 60.0f * ((float)M_PI / 180.0f), (float)w / (float)h, 0.1f, 100.0f);
    demo_mat4_rotate_y(world, angle * 0.5f);

    memcpy(cam->view, view, sizeof(cam->view));
    memcpy(cam->proj, proj, sizeof(cam->proj));
    memcpy(cam->world, world, sizeof(cam->world));
}

static void dgfx_demo_make_topdown_camera(dgfx_camera_t *cam, int w, int h)
{
    float view[16];
    float proj[16];
    float world[16];
    float size;

    size = (float)((w > h) ? w : h) / 100.0f;
    demo_mat4_look_at(view, 0.0f, 5.0f, 0.001f, 0.0f, 0.0f, 0.0f, 0.0f, 0.0f, 1.0f);
    demo_mat4_ortho(proj, -size, size, -size, size, 0.1f, 100.0f);
    demo_mat4_identity(world);

    memcpy(cam->view, view, sizeof(cam->view));
    memcpy(cam->proj, proj, sizeof(cam->proj));
    memcpy(cam->world, world, sizeof(cam->world));
}

static void dgfx_demo_make_2d_camera(dgfx_camera_t *cam)
{
    demo_mat4_identity(cam->view);
    demo_mat4_identity(cam->proj);
    demo_mat4_identity(cam->world);
}
