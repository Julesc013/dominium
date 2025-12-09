#include "gdi_gfx.h"

#ifndef WIN32_LEAN_AND_MEAN
#define WIN32_LEAN_AND_MEAN
#endif
#include <windows.h>
#include <string.h>
#include "domino/sys.h"

gdi_state_t g_gdi;

typedef struct gdi_cmd_clear_payload_t {
    uint8_t r;
    uint8_t g;
    uint8_t b;
    uint8_t a;
} gdi_cmd_clear_payload_t;

typedef struct gdi_lines_header_t {
    uint16_t vertex_count;
    uint16_t reserved;
} gdi_lines_header_t;

typedef struct gdi_line_vertex_t {
    float    x;
    float    y;
    float    z;
    uint32_t color;
} gdi_line_vertex_t;

typedef struct gdi_sprite_t {
    int32_t  x;
    int32_t  y;
    int32_t  w;
    int32_t  h;
    uint32_t color_rgba;
} gdi_sprite_t;

typedef struct gdi_camera_payload_t {
    int32_t offset_x;
    int32_t offset_y;
} gdi_camera_payload_t;

static bool      gdi_init(const dgfx_desc* desc);
static void      gdi_shutdown(void);
static dgfx_caps gdi_get_caps(void);
static void      gdi_resize(int width, int height);
static void      gdi_begin_frame(void);
static void      gdi_execute(const dgfx_cmd_buffer* cmd_buf);
static void      gdi_end_frame(void);

static bool gdi_create_offscreen(void);
static void gdi_init_state(void);
static void gdi_build_caps(void);

static void gdi_cmd_clear(const uint8_t* payload, size_t payload_size);
static void gdi_cmd_set_viewport(const uint8_t* payload);
static void gdi_cmd_set_camera(const uint8_t* payload);
static void gdi_cmd_set_pipeline(const uint8_t* payload);
static void gdi_cmd_set_texture(const uint8_t* payload);
static void gdi_cmd_draw_sprites(const uint8_t* payload, size_t payload_size);
static void gdi_cmd_draw_lines(const uint8_t* payload, size_t payload_size);
static void gdi_cmd_draw_meshes(const uint8_t* payload, size_t payload_size);
static void gdi_cmd_draw_text(const uint8_t* payload, size_t payload_size);

static int gdi_round_to_int(float v)
{
    return (int)((v >= 0.0f) ? (v + 0.5f) : (v - 0.5f));
}

static const dgfx_backend_vtable g_gdi_vtable = {
    gdi_init,
    gdi_shutdown,
    gdi_get_caps,
    gdi_resize,
    gdi_begin_frame,
    gdi_execute,
    gdi_end_frame
};

const dgfx_backend_vtable* dgfx_gdi_get_vtable(void)
{
    return &g_gdi_vtable;
}

static bool gdi_create_offscreen(void)
{
    BITMAPINFO bmi;
    HBITMAP dib;
    void* bits;
    HDC mem_dc;
    int width;
    int height;

    if (!g_gdi.hwnd_dc) {
        return false;
    }

    width = g_gdi.width;
    height = g_gdi.height;

    mem_dc = CreateCompatibleDC(g_gdi.hwnd_dc);
    if (!mem_dc) {
        return false;
    }

    memset(&bmi, 0, sizeof(bmi));
    bmi.bmiHeader.biSize = sizeof(BITMAPINFOHEADER);
    bmi.bmiHeader.biWidth = width;
    bmi.bmiHeader.biHeight = -height; /* top-down */
    bmi.bmiHeader.biPlanes = 1;
    bmi.bmiHeader.biBitCount = (WORD)g_gdi.dib_bpp;
    bmi.bmiHeader.biCompression = BI_RGB;
    bmi.bmiHeader.biSizeImage = 0;

    dib = CreateDIBSection(
        g_gdi.hwnd_dc,
        &bmi,
        DIB_RGB_COLORS,
        &bits,
        NULL,
        0);
    if (!dib || !bits) {
        DeleteDC(mem_dc);
        return false;
    }

    SelectObject(mem_dc, dib);

    g_gdi.mem_dc = mem_dc;
    g_gdi.dib_bitmap = dib;
    g_gdi.dib_bits = bits;
    g_gdi.dib_pitch = width * (g_gdi.dib_bpp / 8);

    return true;
}

static void gdi_init_state(void)
{
    g_gdi.camera_offset_x = 0;
    g_gdi.camera_offset_y = 0;
    g_gdi.current_color_rgba = 0xffffffffu;
}

static void gdi_build_caps(void)
{
    memset(&g_gdi.caps, 0, sizeof(g_gdi.caps));
    g_gdi.caps.name = "gdi";
    g_gdi.caps.supports_2d = true;
    g_gdi.caps.supports_3d = false;
    g_gdi.caps.supports_text = false;
    g_gdi.caps.supports_rt = false;
    g_gdi.caps.supports_alpha = false;
    g_gdi.caps.max_texture_size = 4096;
}

static bool gdi_init(const dgfx_desc* desc)
{
    if (!desc || !desc->window) {
        return false;
    }

    memset(&g_gdi, 0, sizeof(g_gdi));

    g_gdi.width = (desc->width > 0) ? desc->width : 800;
    g_gdi.height = (desc->height > 0) ? desc->height : 600;
    g_gdi.fullscreen = 0;
    g_gdi.dib_bpp = 32;

    g_gdi.native_window = dsys_window_get_native_handle(desc->window);
    g_gdi.hwnd = (HWND)g_gdi.native_window;
    if (!g_gdi.hwnd) {
        return false;
    }

    g_gdi.hwnd_dc = GetDC(g_gdi.hwnd);
    if (!g_gdi.hwnd_dc) {
        return false;
    }

    if (!gdi_create_offscreen()) {
        gdi_shutdown();
        return false;
    }

    gdi_init_state();
    gdi_build_caps();

    g_gdi.frame_in_progress = 0;
    return true;
}

static void gdi_shutdown(void)
{
    if (g_gdi.mem_dc) {
        if (g_gdi.dib_bitmap) {
            SelectObject(g_gdi.mem_dc, (HBITMAP)NULL);
            DeleteObject(g_gdi.dib_bitmap);
        }
        DeleteDC(g_gdi.mem_dc);
    }

    if (g_gdi.hwnd_dc && g_gdi.hwnd) {
        ReleaseDC(g_gdi.hwnd, g_gdi.hwnd_dc);
    }

    memset(&g_gdi, 0, sizeof(g_gdi));
}

static dgfx_caps gdi_get_caps(void)
{
    return g_gdi.caps;
}

static void gdi_resize(int width, int height)
{
    if (width <= 0 || height <= 0) {
        return;
    }

    g_gdi.width = width;
    g_gdi.height = height;

    if (g_gdi.mem_dc) {
        if (g_gdi.dib_bitmap) {
            SelectObject(g_gdi.mem_dc, (HBITMAP)NULL);
            DeleteObject(g_gdi.dib_bitmap);
            g_gdi.dib_bitmap = NULL;
        }
        DeleteDC(g_gdi.mem_dc);
        g_gdi.mem_dc = NULL;
    }

    g_gdi.dib_bits = NULL;
    g_gdi.dib_pitch = 0;
    g_gdi.frame_in_progress = 0;

    gdi_create_offscreen();
}

static void gdi_begin_frame(void)
{
    RECT r;
    HBRUSH brush;

    g_gdi.frame_in_progress = 0;

    if (!g_gdi.mem_dc || !g_gdi.dib_bits) {
        if (!gdi_create_offscreen()) {
            return;
        }
    }

    r.left = 0;
    r.top = 0;
    r.right = g_gdi.width;
    r.bottom = g_gdi.height;

    brush = CreateSolidBrush(RGB(0, 0, 0));
    if (brush) {
        FillRect(g_gdi.mem_dc, &r, brush);
        DeleteObject(brush);
    }

    g_gdi.frame_in_progress = 1;
}

static void gdi_end_frame(void)
{
    if (!g_gdi.frame_in_progress) {
        return;
    }
    if (!g_gdi.hwnd_dc || !g_gdi.mem_dc) {
        g_gdi.frame_in_progress = 0;
        return;
    }

    BitBlt(
        g_gdi.hwnd_dc,
        0,
        0,
        g_gdi.width,
        g_gdi.height,
        g_gdi.mem_dc,
        0,
        0,
        SRCCOPY);

    g_gdi.frame_in_progress = 0;
}

static void gdi_cmd_clear(const uint8_t* payload, size_t payload_size)
{
    gdi_cmd_clear_payload_t clr;
    RECT rect;
    HBRUSH brush;
    BYTE r;
    BYTE g;
    BYTE b;

    if (!g_gdi.mem_dc) {
        return;
    }

    r = 0u;
    g = 0u;
    b = 0u;

    if (payload && payload_size >= sizeof(gdi_cmd_clear_payload_t)) {
        memcpy(&clr, payload, sizeof(clr));
        r = clr.r;
        g = clr.g;
        b = clr.b;
    }

    rect.left = 0;
    rect.top = 0;
    rect.right = g_gdi.width;
    rect.bottom = g_gdi.height;

    brush = CreateSolidBrush(RGB(r, g, b));
    if (brush) {
        FillRect(g_gdi.mem_dc, &rect, brush);
        DeleteObject(brush);
    }
}

static void gdi_cmd_set_viewport(const uint8_t* payload)
{
    (void)payload;
    /* Viewport handling not implemented; drawing uses full framebuffer. */
}

static void gdi_cmd_set_camera(const uint8_t* payload)
{
    if (payload) {
        const gdi_camera_payload_t* cam;
        cam = (const gdi_camera_payload_t*)payload;
        g_gdi.camera_offset_x = cam->offset_x;
        g_gdi.camera_offset_y = cam->offset_y;
    }
}

static void gdi_cmd_set_pipeline(const uint8_t* payload)
{
    (void)payload;
    /* Pipelines are not modeled in the GDI backend MVP. */
}

static void gdi_cmd_set_texture(const uint8_t* payload)
{
    (void)payload;
    /* Textures are not implemented in the GDI backend MVP. */
}

static void gdi_cmd_draw_sprites(const uint8_t* payload, size_t payload_size)
{
    size_t count;
    size_t i;

    if (!payload || payload_size < sizeof(gdi_sprite_t)) {
        return;
    }
    if (!g_gdi.mem_dc) {
        return;
    }

    count = payload_size / sizeof(gdi_sprite_t);
    for (i = 0u; i < count; ++i) {
        const gdi_sprite_t* spr;
        RECT rect;
        HBRUSH brush;
        BYTE r;
        BYTE g;
        BYTE b;

        spr = ((const gdi_sprite_t*)payload) + i;
        r = (BYTE)((spr->color_rgba >> 16) & 0xffu);
        g = (BYTE)((spr->color_rgba >> 8) & 0xffu);
        b = (BYTE)(spr->color_rgba & 0xffu);

        rect.left = spr->x + g_gdi.camera_offset_x;
        rect.top = spr->y + g_gdi.camera_offset_y;
        rect.right = rect.left + spr->w;
        rect.bottom = rect.top + spr->h;

        brush = CreateSolidBrush(RGB(r, g, b));
        if (brush) {
            FillRect(g_gdi.mem_dc, &rect, brush);
            DeleteObject(brush);
        }
    }
}

static void gdi_cmd_draw_lines(const uint8_t* payload, size_t payload_size)
{
    gdi_lines_header_t header;
    const gdi_line_vertex_t* verts;
    size_t count;
    size_t required;
    size_t i;

    if (!payload || payload_size < sizeof(header)) {
        return;
    }
    if (!g_gdi.mem_dc) {
        return;
    }

    memcpy(&header, payload, sizeof(header));
    verts = (const gdi_line_vertex_t*)(payload + sizeof(header));
    count = header.vertex_count;
    required = sizeof(header) + (count * sizeof(gdi_line_vertex_t));
    if (payload_size < required || count == 0u) {
        return;
    }

    for (i = 0u; (i + 1u) < count; i += 2u) {
        uint32_t color;
        BYTE r;
        BYTE g;
        BYTE b;
        HPEN pen;
        HPEN old_pen;
        int x0;
        int y0;
        int x1;
        int y1;

        color = verts[i].color;
        r = (BYTE)((color >> 16) & 0xffu);
        g = (BYTE)((color >> 8) & 0xffu);
        b = (BYTE)(color & 0xffu);

        pen = CreatePen(PS_SOLID, 1, RGB(r, g, b));
        if (!pen) {
            continue;
        }

        old_pen = (HPEN)SelectObject(g_gdi.mem_dc, pen);

        x0 = gdi_round_to_int(verts[i].x) + g_gdi.camera_offset_x;
        y0 = gdi_round_to_int(verts[i].y) + g_gdi.camera_offset_y;
        x1 = gdi_round_to_int(verts[i + 1u].x) + g_gdi.camera_offset_x;
        y1 = gdi_round_to_int(verts[i + 1u].y) + g_gdi.camera_offset_y;

        MoveToEx(g_gdi.mem_dc, x0, y0, NULL);
        LineTo(g_gdi.mem_dc, x1, y1);

        SelectObject(g_gdi.mem_dc, old_pen);
        DeleteObject(pen);
    }
}

static void gdi_cmd_draw_meshes(const uint8_t* payload, size_t payload_size)
{
    (void)payload;
    (void)payload_size;
    /* 3D meshes are not supported in the GDI backend. */
}

static void gdi_cmd_draw_text(const uint8_t* payload, size_t payload_size)
{
    (void)payload;
    (void)payload_size;
    /* Text drawing is not implemented in the GDI backend MVP. */
}

static void gdi_execute(const dgfx_cmd_buffer* cmd_buf)
{
    const uint8_t* ptr;
    const uint8_t* end;
    size_t header_size;

    if (!cmd_buf || !cmd_buf->data || cmd_buf->size == 0u) {
        return;
    }
    if (!g_gdi.mem_dc || !g_gdi.frame_in_progress) {
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
            gdi_cmd_clear(payload, payload_size);
            break;
        case DGFX_CMD_SET_VIEWPORT:
            gdi_cmd_set_viewport(payload);
            break;
        case DGFX_CMD_SET_CAMERA:
            gdi_cmd_set_camera(payload);
            break;
        case DGFX_CMD_SET_PIPELINE:
            gdi_cmd_set_pipeline(payload);
            break;
        case DGFX_CMD_SET_TEXTURE:
            gdi_cmd_set_texture(payload);
            break;
        case DGFX_CMD_DRAW_SPRITES:
            gdi_cmd_draw_sprites(payload, payload_size);
            break;
        case DGFX_CMD_DRAW_MESHES:
            gdi_cmd_draw_meshes(payload, payload_size);
            break;
        case DGFX_CMD_DRAW_LINES:
            gdi_cmd_draw_lines(payload, payload_size);
            break;
        case DGFX_CMD_DRAW_TEXT:
            gdi_cmd_draw_text(payload, payload_size);
            break;
        default:
            break;
        }

        ptr += total_size;
    }
}
