#include "quartz_gfx.h"

#include <stdlib.h>
#include <string.h>

#include "domino/sys.h"

#if defined(__APPLE__)
#include <CoreGraphics/CoreGraphics.h>
#endif

quartz_state_t g_quartz;

typedef struct quartz_cmd_clear_payload_t {
    uint8_t r;
    uint8_t g;
    uint8_t b;
    uint8_t a;
} quartz_cmd_clear_payload_t;

typedef struct quartz_lines_header_t {
    uint16_t vertex_count;
    uint16_t reserved;
} quartz_lines_header_t;

typedef struct quartz_line_vertex_t {
    float    x;
    float    y;
    float    z;
    uint32_t color;
} quartz_line_vertex_t;

typedef struct quartz_camera_payload_t {
    float offset_x;
    float offset_y;
} quartz_camera_payload_t;

typedef struct quartz_sprite_t {
    float    x;
    float    y;
    float    w;
    float    h;
    uint32_t color_rgba; /* 0xAARRGGBB */
} quartz_sprite_t;

static bool      quartz_init(const dgfx_desc* desc);
static void      quartz_shutdown(void);
static dgfx_caps quartz_get_caps(void);
static void      quartz_resize(int width, int height);
static void      quartz_begin_frame(void);
static void      quartz_execute(const dgfx_cmd_buffer* cmd);
static void      quartz_end_frame(void);

static void quartz_build_caps(void);
static bool quartz_create_bitmap_context(void);
static void quartz_cmd_clear(const uint8_t* payload, size_t payload_size);
static void quartz_cmd_set_viewport(const uint8_t* payload);
static void quartz_cmd_set_camera(const uint8_t* payload);
static void quartz_cmd_set_pipeline(const uint8_t* payload);
static void quartz_cmd_set_texture(const uint8_t* payload);
static void quartz_cmd_draw_sprites(const uint8_t* payload, size_t payload_size);
static void quartz_cmd_draw_lines(const uint8_t* payload, size_t payload_size);
static void quartz_cmd_draw_meshes(const uint8_t* payload, size_t payload_size);
static void quartz_cmd_draw_text(const uint8_t* payload, size_t payload_size);

static const dgfx_backend_vtable g_quartz_vtable = {
    quartz_init,
    quartz_shutdown,
    quartz_get_caps,
    quartz_resize,
    quartz_begin_frame,
    quartz_execute,
    quartz_end_frame
};

const dgfx_backend_vtable* dgfx_quartz_get_vtable(void)
{
    return &g_quartz_vtable;
}

#if defined(__APPLE__)
extern CGContextRef dsys_cocoa_get_window_context(void* ns_window)
    __attribute__((weak_import));
#endif

static CGContextRef quartz_get_window_context(void)
{
#if defined(__APPLE__)
    if (dsys_cocoa_get_window_context) {
        return dsys_cocoa_get_window_context(g_quartz.ns_window);
    }
#endif
    return NULL;
}

static void quartz_build_caps(void)
{
    memset(&g_quartz.caps, 0, sizeof(g_quartz.caps));
    g_quartz.caps.name = "quartz";
    g_quartz.caps.supports_2d = true;
    g_quartz.caps.supports_3d = false;
    g_quartz.caps.supports_text = false;
    g_quartz.caps.supports_rt = false;
    g_quartz.caps.supports_alpha = true;
    g_quartz.caps.max_texture_size = 4096;
}

static bool quartz_create_bitmap_context(void)
{
#if !defined(__APPLE__)
    return false;
#else
    size_t width;
    size_t height;
    size_t bpp;
    size_t bpc;
    size_t stride;
    void* data;
    CGColorSpaceRef cs;
    CGContextRef ctx;

    width = (size_t)g_quartz.width;
    height = (size_t)g_quartz.height;
    if (width == 0u || height == 0u) {
        return false;
    }

    bpp = 32u;
    bpc = 8u;
    stride = width * (bpp / 8u);
    data = malloc(stride * height);
    if (!data) {
        return false;
    }

    cs = g_quartz.color_space;
    if (!cs) {
        cs = CGColorSpaceCreateDeviceRGB();
        if (!cs) {
            free(data);
            return false;
        }
    }

    ctx = CGBitmapContextCreate(
        data,
        width,
        height,
        bpc,
        stride,
        cs,
        kCGImageAlphaPremultipliedLast | kCGBitmapByteOrder32Big);
    if (!ctx) {
        if (!g_quartz.color_space) {
            CGColorSpaceRelease(cs);
        }
        free(data);
        return false;
    }

    g_quartz.color_space = cs;
    g_quartz.bitmap_ctx = ctx;
    g_quartz.bitmap_data = data;
    g_quartz.bitmap_stride = stride;
    g_quartz.bitmap_image = NULL;
    return true;
#endif
}

static bool quartz_init(const dgfx_desc* desc)
{
    if (!desc || !desc->window) {
        return false;
    }

    memset(&g_quartz, 0, sizeof(g_quartz));

    g_quartz.window = desc->window;
    g_quartz.ns_window = dsys_window_get_native_handle(desc->window);
    if (!g_quartz.ns_window) {
        return false;
    }
    g_quartz.width = (desc->width > 0) ? desc->width : 800;
    g_quartz.height = (desc->height > 0) ? desc->height : 600;
    g_quartz.fullscreen = 0;
    g_quartz.depth = 32;

    if (!quartz_create_bitmap_context()) {
        quartz_shutdown();
        return false;
    }

    g_quartz.camera_offset_x = 0.0f;
    g_quartz.camera_offset_y = 0.0f;

    quartz_build_caps();

    g_quartz.frame_in_progress = 0;

    return true;
}

static void quartz_shutdown(void)
{
#if defined(__APPLE__)
    if (g_quartz.bitmap_ctx) {
        CGContextRelease(g_quartz.bitmap_ctx);
        g_quartz.bitmap_ctx = NULL;
    }
    if (g_quartz.bitmap_image) {
        CGImageRelease(g_quartz.bitmap_image);
        g_quartz.bitmap_image = NULL;
    }
    if (g_quartz.color_space) {
        CGColorSpaceRelease(g_quartz.color_space);
        g_quartz.color_space = NULL;
    }
#endif
    if (g_quartz.bitmap_data) {
        free(g_quartz.bitmap_data);
        g_quartz.bitmap_data = NULL;
    }

    memset(&g_quartz, 0, sizeof(g_quartz));
}

static dgfx_caps quartz_get_caps(void)
{
    return g_quartz.caps;
}

static void quartz_resize(int width, int height)
{
    if (width <= 0 || height <= 0) {
        return;
    }

    g_quartz.width = width;
    g_quartz.height = height;

#if defined(__APPLE__)
    if (g_quartz.bitmap_ctx) {
        CGContextRelease(g_quartz.bitmap_ctx);
        g_quartz.bitmap_ctx = NULL;
    }
    if (g_quartz.bitmap_image) {
        CGImageRelease(g_quartz.bitmap_image);
        g_quartz.bitmap_image = NULL;
    }
#endif
    if (g_quartz.bitmap_data) {
        free(g_quartz.bitmap_data);
        g_quartz.bitmap_data = NULL;
    }

    quartz_create_bitmap_context();
}

static void quartz_begin_frame(void)
{
#if defined(__APPLE__)
    if (!g_quartz.bitmap_ctx) {
        return;
    }

    CGContextSaveGState(g_quartz.bitmap_ctx);
    CGContextSetRGBFillColor(g_quartz.bitmap_ctx, 0.0f, 0.0f, 0.0f, 1.0f);
    CGContextFillRect(
        g_quartz.bitmap_ctx,
        CGRectMake(0.0f, 0.0f, (CGFloat)g_quartz.width, (CGFloat)g_quartz.height));
    CGContextRestoreGState(g_quartz.bitmap_ctx);

    g_quartz.frame_in_progress = 1;
#endif
}

static void quartz_end_frame(void)
{
#if defined(__APPLE__)
    CGContextRef window_ctx;

    if (!g_quartz.frame_in_progress) {
        return;
    }
    if (!g_quartz.bitmap_ctx) {
        g_quartz.frame_in_progress = 0;
        return;
    }

    if (g_quartz.bitmap_image) {
        CGImageRelease(g_quartz.bitmap_image);
        g_quartz.bitmap_image = NULL;
    }

    g_quartz.bitmap_image = CGBitmapContextCreateImage(g_quartz.bitmap_ctx);
    if (!g_quartz.bitmap_image) {
        g_quartz.frame_in_progress = 0;
        return;
    }

    window_ctx = quartz_get_window_context();
    if (window_ctx) {
        CGRect dst;
        dst = CGRectMake(
            0.0f,
            0.0f,
            (CGFloat)g_quartz.width,
            (CGFloat)g_quartz.height);

        CGContextSaveGState(window_ctx);
        CGContextDrawImage(window_ctx, dst, g_quartz.bitmap_image);
        CGContextRestoreGState(window_ctx);
    }

    g_quartz.frame_in_progress = 0;
#else
    (void)g_quartz;
#endif
}

static void quartz_cmd_clear(const uint8_t* payload, size_t payload_size)
{
#if defined(__APPLE__)
    quartz_cmd_clear_payload_t clr;
    CGFloat r;
    CGFloat g;
    CGFloat b;
    CGFloat a;

    if (!g_quartz.bitmap_ctx) {
        return;
    }

    r = 0.0f;
    g = 0.0f;
    b = 0.0f;
    a = 1.0f;

    if (payload && payload_size >= sizeof(quartz_cmd_clear_payload_t)) {
        memcpy(&clr, payload, sizeof(clr));
        r = (CGFloat)clr.r / 255.0f;
        g = (CGFloat)clr.g / 255.0f;
        b = (CGFloat)clr.b / 255.0f;
        a = (CGFloat)clr.a / 255.0f;
    }

    CGContextSaveGState(g_quartz.bitmap_ctx);
    CGContextSetRGBFillColor(g_quartz.bitmap_ctx, r, g, b, a);
    CGContextFillRect(
        g_quartz.bitmap_ctx,
        CGRectMake(0.0f, 0.0f, (CGFloat)g_quartz.width, (CGFloat)g_quartz.height));
    CGContextRestoreGState(g_quartz.bitmap_ctx);
#else
    (void)payload;
    (void)payload_size;
#endif
}

static void quartz_cmd_set_viewport(const uint8_t* payload)
{
    (void)payload;
    /* Viewport handling not implemented; Quartz draws to full bitmap. */
}

static void quartz_cmd_set_camera(const uint8_t* payload)
{
    if (!payload) {
        return;
    }

    {
        const quartz_camera_payload_t* cam;
        cam = (const quartz_camera_payload_t*)payload;
        g_quartz.camera_offset_x = cam->offset_x;
        g_quartz.camera_offset_y = cam->offset_y;
    }
}

static void quartz_cmd_set_pipeline(const uint8_t* payload)
{
    (void)payload;
#if defined(__APPLE__)
    if (!g_quartz.bitmap_ctx) {
        return;
    }
    /* Basic defaults; future pipeline identifiers can map to state here. */
    CGContextSetLineWidth(g_quartz.bitmap_ctx, 1.0f);
    CGContextSetLineJoin(g_quartz.bitmap_ctx, kCGLineJoinMiter);
    CGContextSetLineCap(g_quartz.bitmap_ctx, kCGLineCapButt);
    CGContextSetBlendMode(g_quartz.bitmap_ctx, kCGBlendModeNormal);
#endif
}

static void quartz_cmd_set_texture(const uint8_t* payload)
{
    (void)payload;
    /* Texture binding is not implemented in the Quartz backend MVP. */
}

static void quartz_cmd_draw_sprites(const uint8_t* payload, size_t payload_size)
{
#if defined(__APPLE__)
    size_t count;
    size_t i;

    if (!payload || payload_size < sizeof(quartz_sprite_t)) {
        return;
    }
    if (!g_quartz.bitmap_ctx) {
        return;
    }

    count = payload_size / sizeof(quartz_sprite_t);

    for (i = 0u; i < count; ++i) {
        const quartz_sprite_t* spr;
        CGFloat r;
        CGFloat g;
        CGFloat b;
        CGFloat a;
        CGRect rect;

        spr = ((const quartz_sprite_t*)payload) + i;

        a = (CGFloat)((spr->color_rgba >> 24) & 0xffu) / 255.0f;
        r = (CGFloat)((spr->color_rgba >> 16) & 0xffu) / 255.0f;
        g = (CGFloat)((spr->color_rgba >> 8) & 0xffu) / 255.0f;
        b = (CGFloat)((spr->color_rgba >> 0) & 0xffu) / 255.0f;

        rect = CGRectMake(
            (CGFloat)(spr->x + g_quartz.camera_offset_x),
            (CGFloat)(spr->y + g_quartz.camera_offset_y),
            (CGFloat)spr->w,
            (CGFloat)spr->h);

        CGContextSaveGState(g_quartz.bitmap_ctx);
        CGContextSetRGBFillColor(g_quartz.bitmap_ctx, r, g, b, a);
        CGContextFillRect(g_quartz.bitmap_ctx, rect);
        CGContextRestoreGState(g_quartz.bitmap_ctx);
    }
#else
    (void)payload;
    (void)payload_size;
#endif
}

static void quartz_cmd_draw_lines(const uint8_t* payload, size_t payload_size)
{
#if defined(__APPLE__)
    quartz_lines_header_t header;
    const quartz_line_vertex_t* verts;
    size_t required;
    size_t i;

    if (!payload || !g_quartz.bitmap_ctx) {
        return;
    }
    if (payload_size < sizeof(header)) {
        return;
    }

    memcpy(&header, payload, sizeof(header));
    required = sizeof(header) + ((size_t)header.vertex_count * sizeof(quartz_line_vertex_t));
    if (payload_size < required) {
        return;
    }
    if (header.vertex_count < 2u) {
        return;
    }

    verts = (const quartz_line_vertex_t*)(payload + sizeof(header));

    for (i = 0u; i + 1u < (size_t)header.vertex_count; i += 2u) {
        const quartz_line_vertex_t* v0;
        const quartz_line_vertex_t* v1;
        CGFloat r;
        CGFloat g;
        CGFloat b;
        CGFloat a;

        v0 = &verts[i];
        v1 = &verts[i + 1u];

        a = (CGFloat)((v0->color >> 24) & 0xffu) / 255.0f;
        r = (CGFloat)((v0->color >> 16) & 0xffu) / 255.0f;
        g = (CGFloat)((v0->color >> 8) & 0xffu) / 255.0f;
        b = (CGFloat)((v0->color >> 0) & 0xffu) / 255.0f;

        CGContextSaveGState(g_quartz.bitmap_ctx);
        CGContextSetRGBStrokeColor(g_quartz.bitmap_ctx, r, g, b, a);
        CGContextSetLineWidth(g_quartz.bitmap_ctx, 1.0f);
        CGContextBeginPath(g_quartz.bitmap_ctx);
        CGContextMoveToPoint(
            g_quartz.bitmap_ctx,
            (CGFloat)(v0->x + g_quartz.camera_offset_x),
            (CGFloat)(v0->y + g_quartz.camera_offset_y));
        CGContextAddLineToPoint(
            g_quartz.bitmap_ctx,
            (CGFloat)(v1->x + g_quartz.camera_offset_x),
            (CGFloat)(v1->y + g_quartz.camera_offset_y));
        CGContextStrokePath(g_quartz.bitmap_ctx);
        CGContextRestoreGState(g_quartz.bitmap_ctx);
    }
#else
    (void)payload;
    (void)payload_size;
#endif
}

static void quartz_cmd_draw_meshes(const uint8_t* payload, size_t payload_size)
{
    (void)payload;
    (void)payload_size;
    /* 3D meshes are not supported in the Quartz backend MVP. */
}

static void quartz_cmd_draw_text(const uint8_t* payload, size_t payload_size)
{
    (void)payload;
    (void)payload_size;
    /* Text rendering is not implemented in the Quartz backend MVP. */
}

static void quartz_execute(const dgfx_cmd_buffer* cmd_buf)
{
    const uint8_t* ptr;
    const uint8_t* end;
    size_t header_size;

    if (!cmd_buf || !cmd_buf->data || cmd_buf->size == 0u) {
        return;
    }
    if (!g_quartz.frame_in_progress) {
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
            quartz_cmd_clear(payload, payload_size);
            break;
        case DGFX_CMD_SET_VIEWPORT:
            quartz_cmd_set_viewport(payload);
            break;
        case DGFX_CMD_SET_CAMERA:
            quartz_cmd_set_camera(payload);
            break;
        case DGFX_CMD_SET_PIPELINE:
            quartz_cmd_set_pipeline(payload);
            break;
        case DGFX_CMD_SET_TEXTURE:
            quartz_cmd_set_texture(payload);
            break;
        case DGFX_CMD_DRAW_SPRITES:
            quartz_cmd_draw_sprites(payload, payload_size);
            break;
        case DGFX_CMD_DRAW_MESHES:
            quartz_cmd_draw_meshes(payload, payload_size);
            break;
        case DGFX_CMD_DRAW_LINES:
            quartz_cmd_draw_lines(payload, payload_size);
            break;
        case DGFX_CMD_DRAW_TEXT:
            quartz_cmd_draw_text(payload, payload_size);
            break;
        default:
            break;
        }

        ptr += total_size;
    }
}