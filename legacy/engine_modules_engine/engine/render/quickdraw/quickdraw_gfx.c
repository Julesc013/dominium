/*
FILE: source/domino/render/quickdraw/quickdraw_gfx.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / render/quickdraw/quickdraw_gfx
RESPONSIBILITY: Implements `quickdraw_gfx`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include "quickdraw_gfx.h"

#if defined(DOMINIUM_GFX_QUICKDRAW)

#include <QuickDraw.h>
#include <QDOffscreen.h>
#include <MacWindows.h>
#include <stddef.h>
#include <string.h>

#include "domino/sys.h"

typedef struct quickdraw_camera_state_t {
    int32_t offset_x;
    int32_t offset_y;
} quickdraw_camera_state_t;

typedef struct quickdraw_cmd_clear_payload_t {
    uint8_t r;
    uint8_t g;
    uint8_t b;
    uint8_t a;
} quickdraw_cmd_clear_payload_t;

typedef struct quickdraw_sprite_t {
    int32_t  x;
    int32_t  y;
    int32_t  w;
    int32_t  h;
    uint32_t color_rgba;
} quickdraw_sprite_t;

typedef struct quickdraw_lines_header_t {
    uint16_t vertex_count;
    uint16_t reserved;
} quickdraw_lines_header_t;

typedef struct quickdraw_line_vertex_t {
    float    x;
    float    y;
    float    z;
    uint32_t color;
} quickdraw_line_vertex_t;

quickdraw_state_t g_quickdraw;
static quickdraw_camera_state_t g_quickdraw_camera;

static bool      quickdraw_init(const dgfx_desc* desc);
static void      quickdraw_shutdown(void);
static dgfx_caps quickdraw_get_caps(void);
static void      quickdraw_resize(int width, int height);
static void      quickdraw_begin_frame(void);
static void      quickdraw_execute(const dgfx_cmd_buffer* cmd_buf);
static void      quickdraw_end_frame(void);

static bool quickdraw_setup_ports(void);
static void quickdraw_init_state(void);
static void quickdraw_build_caps(void);

static void quickdraw_cmd_clear(const uint8_t* payload, size_t payload_size);
static void quickdraw_cmd_set_viewport(const uint8_t* payload);
static void quickdraw_cmd_set_camera(const uint8_t* payload);
static void quickdraw_cmd_set_pipeline(const uint8_t* payload);
static void quickdraw_cmd_set_texture(const uint8_t* payload);
static void quickdraw_cmd_draw_sprites(const uint8_t* payload, size_t payload_size);
static void quickdraw_cmd_draw_lines(const uint8_t* payload, size_t payload_size);
static void quickdraw_cmd_draw_meshes(const uint8_t* payload, size_t payload_size);
static void quickdraw_cmd_draw_text(const uint8_t* payload, size_t payload_size);

static void quickdraw_color_from_rgba(uint32_t rgba, RGBColor* out);

static const dgfx_backend_vtable g_quickdraw_vtable = {
    quickdraw_init,
    quickdraw_shutdown,
    quickdraw_get_caps,
    quickdraw_resize,
    quickdraw_begin_frame,
    quickdraw_execute,
    quickdraw_end_frame
};

const dgfx_backend_vtable* dgfx_quickdraw_get_vtable(void)
{
    return &g_quickdraw_vtable;
}

static void quickdraw_color_from_rgba(uint32_t rgba, RGBColor* out)
{
    uint16_t r;
    uint16_t g;
    uint16_t b;

    if (!out) {
        return;
    }

    r = (uint16_t)((rgba >> 16) & 0xffu);
    g = (uint16_t)((rgba >> 8) & 0xffu);
    b = (uint16_t)((rgba >> 0) & 0xffu);

    out->red = (r << 8) | r;
    out->green = (g << 8) | g;
    out->blue = (b << 8) | b;
}

static void quickdraw_build_caps(void)
{
    memset(&g_quickdraw.caps, 0, sizeof(g_quickdraw.caps));
    g_quickdraw.caps.name = "quickdraw";
    g_quickdraw.caps.supports_2d = true;
    g_quickdraw.caps.supports_3d = false;
    g_quickdraw.caps.supports_text = false;
    g_quickdraw.caps.supports_rt = false;
    g_quickdraw.caps.supports_alpha = false;
    g_quickdraw.caps.max_texture_size = 1024;
}

static bool quickdraw_setup_ports(void)
{
    CGrafPtr window_port;
    GWorldPtr offscreen;
    Rect bounds;

    if (!g_quickdraw.window) {
        return false;
    }

    window_port = GetWindowPort(g_quickdraw.window);
    if (!window_port) {
        return false;
    }
    g_quickdraw.window_port = window_port;

    SetRect(&bounds, 0, 0, g_quickdraw.width, g_quickdraw.height);

    g_quickdraw.depth = 32;

    if (NewGWorld(&offscreen, g_quickdraw.depth, &bounds, NULL, NULL, keepLocal) != noErr) {
        return false;
    }

    g_quickdraw.offscreen_gworld = offscreen;
    g_quickdraw.offscreen_port = (CGrafPtr)offscreen;
    LockPixels(GetGWorldPixMap(offscreen));

    return true;
}

static void quickdraw_init_state(void)
{
    RGBColor black;
    RGBColor white;

    black.red = 0;
    black.green = 0;
    black.blue = 0;

    white.red = 0xffff;
    white.green = 0xffff;
    white.blue = 0xffff;

    if (g_quickdraw.offscreen_port) {
        SetGWorld((CGrafPtr)g_quickdraw.offscreen_gworld, NULL);
        RGBBackColor(&black);
        RGBForeColor(&white);
        PenSize(1, 1);
    }
}

static bool quickdraw_init(const dgfx_desc* desc)
{
    if (!desc || !desc->window) {
        return false;
    }

    memset(&g_quickdraw, 0, sizeof(g_quickdraw));
    memset(&g_quickdraw_camera, 0, sizeof(g_quickdraw_camera));

    g_quickdraw.native_window = dsys_window_get_native_handle(desc->window);
    g_quickdraw.width = (desc->width > 0) ? desc->width : 640;
    g_quickdraw.height = (desc->height > 0) ? desc->height : 480;
    g_quickdraw.fullscreen = 0;

    g_quickdraw.window = (WindowPtr)g_quickdraw.native_window;
    if (!quickdraw_setup_ports()) {
        quickdraw_shutdown();
        return false;
    }

    quickdraw_init_state();
    quickdraw_build_caps();
    g_quickdraw.frame_in_progress = 0;

    return true;
}

static void quickdraw_shutdown(void)
{
    if (g_quickdraw.offscreen_gworld) {
        UnlockPixels(GetGWorldPixMap(g_quickdraw.offscreen_gworld));
        DisposeGWorld(g_quickdraw.offscreen_gworld);
    }

    memset(&g_quickdraw, 0, sizeof(g_quickdraw));
    memset(&g_quickdraw_camera, 0, sizeof(g_quickdraw_camera));
}

static dgfx_caps quickdraw_get_caps(void)
{
    return g_quickdraw.caps;
}

static void quickdraw_resize(int width, int height)
{
    Rect bounds;

    if (width <= 0 || height <= 0) {
        return;
    }

    g_quickdraw.width = width;
    g_quickdraw.height = height;

    if (g_quickdraw.offscreen_gworld) {
        UnlockPixels(GetGWorldPixMap(g_quickdraw.offscreen_gworld));
        DisposeGWorld(g_quickdraw.offscreen_gworld);
        g_quickdraw.offscreen_gworld = NULL;
        g_quickdraw.offscreen_port = NULL;
    }

    SetRect(&bounds, 0, 0, g_quickdraw.width, g_quickdraw.height);

    if (NewGWorld(&g_quickdraw.offscreen_gworld,
                  g_quickdraw.depth,
                  &bounds,
                  NULL,
                  NULL,
                  keepLocal) == noErr) {
        g_quickdraw.offscreen_port = (CGrafPtr)g_quickdraw.offscreen_gworld;
        LockPixels(GetGWorldPixMap(g_quickdraw.offscreen_gworld));
        quickdraw_init_state();
    }
}

static void quickdraw_begin_frame(void)
{
    RGBColor clear_color;

    clear_color.red = 0;
    clear_color.green = 0;
    clear_color.blue = 0;

    if (!g_quickdraw.offscreen_port) {
        return;
    }

    SetGWorld((CGrafPtr)g_quickdraw.offscreen_gworld, NULL);
    RGBBackColor(&clear_color);
    {
        Rect r;
        GetPortBounds(g_quickdraw.offscreen_port, &r);
        EraseRect(&r);
    }

    g_quickdraw.frame_in_progress = 1;
}

static void quickdraw_end_frame(void)
{
    BitMap* src_bits;
    BitMap* dst_bits;
    Rect src_rect;
    Rect dst_rect;

    if (!g_quickdraw.frame_in_progress) {
        return;
    }
    if (!g_quickdraw.offscreen_port || !g_quickdraw.window_port) {
        g_quickdraw.frame_in_progress = 0;
        return;
    }

    GetPortBounds(g_quickdraw.offscreen_port, &src_rect);
    GetPortBounds(g_quickdraw.window_port, &dst_rect);

    src_bits = (BitMap*)*GetGWorldPixMap(g_quickdraw.offscreen_gworld);
    dst_bits = GetPortBitMapForCopyBits(g_quickdraw.window_port);

    SetGWorld(g_quickdraw.window_port, NULL);
    CopyBits(src_bits, dst_bits, &src_rect, &dst_rect, srcCopy, NULL);

    g_quickdraw.frame_in_progress = 0;
}

static void quickdraw_cmd_clear(const uint8_t* payload, size_t payload_size)
{
    RGBColor color;
    quickdraw_cmd_clear_payload_t clr;
    Rect r;

    color.red = 0;
    color.green = 0;
    color.blue = 0;

    if (payload && payload_size >= sizeof(clr)) {
        memcpy(&clr, payload, sizeof(clr));
        quickdraw_color_from_rgba(
            ((uint32_t)clr.r << 16) |
            ((uint32_t)clr.g << 8) |
            ((uint32_t)clr.b << 0),
            &color);
    }

    if (!g_quickdraw.offscreen_port) {
        return;
    }

    SetGWorld((CGrafPtr)g_quickdraw.offscreen_gworld, NULL);
    RGBBackColor(&color);

    GetPortBounds(g_quickdraw.offscreen_port, &r);
    EraseRect(&r);
}

static void quickdraw_cmd_set_viewport(const uint8_t* payload)
{
    (void)payload;
}

static void quickdraw_cmd_set_camera(const uint8_t* payload)
{
    (void)payload;
    g_quickdraw_camera.offset_x = 0;
    g_quickdraw_camera.offset_y = 0;
}

static void quickdraw_cmd_set_pipeline(const uint8_t* payload)
{
    RGBColor pen;

    (void)payload;
    if (!g_quickdraw.offscreen_port) {
        return;
    }

    pen.red = 0xffff;
    pen.green = 0xffff;
    pen.blue = 0xffff;

    SetGWorld((CGrafPtr)g_quickdraw.offscreen_gworld, NULL);
    PenSize(1, 1);
    RGBForeColor(&pen);
}

static void quickdraw_cmd_set_texture(const uint8_t* payload)
{
    (void)payload;
}

static void quickdraw_cmd_draw_sprites(const uint8_t* payload, size_t payload_size)
{
    size_t count;
    size_t i;
    const quickdraw_sprite_t* sprites;

    if (!payload || payload_size < sizeof(quickdraw_sprite_t)) {
        return;
    }
    if (!g_quickdraw.offscreen_port) {
        return;
    }

    sprites = (const quickdraw_sprite_t*)payload;
    count = payload_size / sizeof(quickdraw_sprite_t);

    SetGWorld((CGrafPtr)g_quickdraw.offscreen_gworld, NULL);

    for (i = 0; i < count; ++i) {
        RGBColor c;
        Rect r;

        quickdraw_color_from_rgba(sprites[i].color_rgba, &c);
        RGBForeColor(&c);
        SetRect(&r,
                sprites[i].x + g_quickdraw_camera.offset_x,
                sprites[i].y + g_quickdraw_camera.offset_y,
                sprites[i].x + sprites[i].w + g_quickdraw_camera.offset_x,
                sprites[i].y + sprites[i].h + g_quickdraw_camera.offset_y);
        PaintRect(&r);
    }
}

static void quickdraw_cmd_draw_lines(const uint8_t* payload, size_t payload_size)
{
    quickdraw_lines_header_t header;
    size_t required;
    const quickdraw_line_vertex_t* verts;
    size_t i;

    if (!payload || payload_size < sizeof(header)) {
        return;
    }
    if (!g_quickdraw.offscreen_port) {
        return;
    }

    memcpy(&header, payload, sizeof(header));
    required = sizeof(header) + ((size_t)header.vertex_count * sizeof(quickdraw_line_vertex_t));
    if (payload_size < required || header.vertex_count < 2u) {
        return;
    }

    verts = (const quickdraw_line_vertex_t*)(payload + sizeof(header));

    SetGWorld((CGrafPtr)g_quickdraw.offscreen_gworld, NULL);

    for (i = 1u; i < (size_t)header.vertex_count; i += 2u) {
        const quickdraw_line_vertex_t* v0;
        const quickdraw_line_vertex_t* v1;
        RGBColor c;

        v0 = &verts[i - 1u];
        v1 = &verts[i];
        quickdraw_color_from_rgba(v0->color, &c);
        RGBForeColor(&c);

        MoveTo((int)(v0->x + (float)g_quickdraw_camera.offset_x),
               (int)(v0->y + (float)g_quickdraw_camera.offset_y));
        LineTo((int)(v1->x + (float)g_quickdraw_camera.offset_x),
               (int)(v1->y + (float)g_quickdraw_camera.offset_y));
    }
}

static void quickdraw_cmd_draw_meshes(const uint8_t* payload, size_t payload_size)
{
    (void)payload;
    (void)payload_size;
}

static void quickdraw_cmd_draw_text(const uint8_t* payload, size_t payload_size)
{
    (void)payload;
    (void)payload_size;
}

static void quickdraw_execute(const dgfx_cmd_buffer* cmd_buf)
{
    const uint8_t* ptr;
    const uint8_t* end;
    size_t header_size;

    if (!cmd_buf || !cmd_buf->data || cmd_buf->size == 0u) {
        return;
    }
    if (!g_quickdraw.offscreen_port || !g_quickdraw.frame_in_progress) {
        return;
    }

    header_size = sizeof(dgfx_cmd);
    ptr = cmd_buf->data;
    end = cmd_buf->data + cmd_buf->size;

    SetGWorld((CGrafPtr)g_quickdraw.offscreen_gworld, NULL);

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
            quickdraw_cmd_clear(payload, payload_size);
            break;
        case DGFX_CMD_SET_VIEWPORT:
            quickdraw_cmd_set_viewport(payload);
            break;
        case DGFX_CMD_SET_CAMERA:
            quickdraw_cmd_set_camera(payload);
            break;
        case DGFX_CMD_SET_PIPELINE:
            quickdraw_cmd_set_pipeline(payload);
            break;
        case DGFX_CMD_SET_TEXTURE:
            quickdraw_cmd_set_texture(payload);
            break;
        case DGFX_CMD_DRAW_SPRITES:
            quickdraw_cmd_draw_sprites(payload, payload_size);
            break;
        case DGFX_CMD_DRAW_MESHES:
            quickdraw_cmd_draw_meshes(payload, payload_size);
            break;
        case DGFX_CMD_DRAW_LINES:
            quickdraw_cmd_draw_lines(payload, payload_size);
            break;
        case DGFX_CMD_DRAW_TEXT:
            quickdraw_cmd_draw_text(payload, payload_size);
            break;
        default:
            break;
        }

        ptr += total_size;
    }
}

#else /* DOMINIUM_GFX_QUICKDRAW */

quickdraw_state_t g_quickdraw;

const dgfx_backend_vtable* dgfx_quickdraw_get_vtable(void)
{
    return NULL;
}

#endif /* DOMINIUM_GFX_QUICKDRAW */
