#define COBJMACROS
#ifndef WIN32_LEAN_AND_MEAN
#define WIN32_LEAN_AND_MEAN
#endif

#include <windows.h>
#include <ddraw.h>
#include <d3d.h>
#include <stddef.h>
#include <stdlib.h>
#include <string.h>

#include "dx7_gfx.h"
#include "domino/sys.h"

#ifndef D3DRGBA
#define D3DRGBA(r, g, b, a) \
    ((D3DCOLOR)((((DWORD)((a) * 255.0f)) << 24) | \
                (((DWORD)((r) * 255.0f)) << 16) | \
                (((DWORD)((g) * 255.0f)) << 8)  | \
                ((DWORD)((b) * 255.0f))))
#endif

#define DX7_SAFE_RELEASE(x) \
    do { if (x) { (x)->lpVtbl->Release(x); (x) = NULL; } } while (0)

typedef struct dx7_cmd_clear_payload_t {
    uint8_t r;
    uint8_t g;
    uint8_t b;
    uint8_t a;
} dx7_cmd_clear_payload_t;

typedef struct dx7_lines_header_t {
    uint16_t vertex_count;
    uint16_t reserved;
} dx7_lines_header_t;

typedef struct dx7_line_vertex_t {
    float    x;
    float    y;
    float    z;
    uint32_t color;
} dx7_line_vertex_t;

typedef struct dx7_tl_vertex_t {
    float    x;
    float    y;
    float    z;
    float    rhw;
    uint32_t color;
    float    tu;
    float    tv;
} dx7_tl_vertex_t;

#define DX7_TL_FVF (D3DFVF_XYZRHW | D3DFVF_DIFFUSE | D3DFVF_TEX1)

dx7_state_t g_dx7;

static bool dx7_create_dd_device(void);
static bool dx7_create_d3d_device(void);
static void dx7_build_caps(void);
static void dx7_cmd_clear(const uint8_t* payload, size_t payload_size);
static void dx7_cmd_set_viewport(const uint8_t* payload);
static void dx7_cmd_set_camera(const uint8_t* payload);
static void dx7_cmd_set_pipeline(const uint8_t* payload);
static void dx7_cmd_set_texture(const uint8_t* payload);
static void dx7_cmd_draw_sprites(const uint8_t* payload, size_t payload_size);
static void dx7_cmd_draw_lines(const uint8_t* payload, size_t payload_size);
static void dx7_cmd_draw_meshes(const uint8_t* payload, size_t payload_size);
static void dx7_cmd_draw_text(const uint8_t* payload, size_t payload_size);

static bool dx7_init(const dgfx_desc* desc);
static void dx7_shutdown(void);
static dgfx_caps dx7_get_caps(void);
static void dx7_resize(int width, int height);
static void dx7_begin_frame(void);
static void dx7_execute(const dgfx_cmd_buffer* cmd_buf);
static void dx7_end_frame(void);

static const dgfx_backend_vtable g_dx7_vtable = {
    dx7_init,
    dx7_shutdown,
    dx7_get_caps,
    dx7_resize,
    dx7_begin_frame,
    dx7_execute,
    dx7_end_frame
};

const dgfx_backend_vtable* dgfx_dx7_get_vtable(void)
{
    return &g_dx7_vtable;
}

static bool dx7_init(const dgfx_desc* desc)
{
    memset(&g_dx7, 0, sizeof(g_dx7));

    if (!desc || !desc->window) {
        return false;
    }

    g_dx7.hwnd = (HWND)dsys_window_get_native_handle(desc->window);
    if (!g_dx7.hwnd) {
        return false;
    }

    g_dx7.width = (desc->width > 0) ? desc->width : 800;
    g_dx7.height = (desc->height > 0) ? desc->height : 600;
    g_dx7.fullscreen = 0;
    g_dx7.hinstance = GetModuleHandleA(NULL);

    if (!dx7_create_dd_device()) {
        dx7_shutdown();
        return false;
    }
    if (!dx7_create_d3d_device()) {
        dx7_shutdown();
        return false;
    }

    dx7_build_caps();
    return true;
}

static void dx7_shutdown(void)
{
    DX7_SAFE_RELEASE(g_dx7.viewport);
    DX7_SAFE_RELEASE(g_dx7.d3d_device);
    DX7_SAFE_RELEASE(g_dx7.d3d);
    DX7_SAFE_RELEASE(g_dx7.backbuffer);
    DX7_SAFE_RELEASE(g_dx7.primary);
    DX7_SAFE_RELEASE(g_dx7.clipper);
    DX7_SAFE_RELEASE(g_dx7.dd);

    memset(&g_dx7, 0, sizeof(g_dx7));
}

static dgfx_caps dx7_get_caps(void)
{
    return g_dx7.caps;
}

static void dx7_resize(int width, int height)
{
    if (width <= 0 || height <= 0) {
        return;
    }
    if (width == g_dx7.width && height == g_dx7.height) {
        return;
    }

    g_dx7.width = width;
    g_dx7.height = height;

    DX7_SAFE_RELEASE(g_dx7.viewport);
    DX7_SAFE_RELEASE(g_dx7.d3d_device);
    DX7_SAFE_RELEASE(g_dx7.d3d);
    DX7_SAFE_RELEASE(g_dx7.backbuffer);
    DX7_SAFE_RELEASE(g_dx7.primary);
    DX7_SAFE_RELEASE(g_dx7.clipper);

    if (!dx7_create_dd_device()) {
        dx7_shutdown();
        return;
    }
    if (!dx7_create_d3d_device()) {
        dx7_shutdown();
    }
}

static void dx7_begin_frame(void)
{
    D3DVIEWPORT7 vp;

    if (!g_dx7.d3d_device || !g_dx7.viewport) {
        return;
    }

    memset(&vp, 0, sizeof(vp));
    vp.dwX = 0;
    vp.dwY = 0;
    vp.dwWidth = (DWORD)g_dx7.width;
    vp.dwHeight = (DWORD)g_dx7.height;
    vp.dvMinZ = 0.0f;
    vp.dvMaxZ = 1.0f;
    g_dx7.viewport->lpVtbl->SetViewport(g_dx7.viewport, &vp);

    g_dx7.d3d_device->lpVtbl->Clear(
        g_dx7.d3d_device,
        0,
        NULL,
        D3DCLEAR_TARGET,
        D3DRGBA(0.0f, 0.0f, 0.0f, 1.0f),
        1.0f,
        0);

    g_dx7.d3d_device->lpVtbl->BeginScene(g_dx7.d3d_device);
}

static void dx7_end_frame(void)
{
    if (!g_dx7.d3d_device || !g_dx7.primary) {
        return;
    }

    g_dx7.d3d_device->lpVtbl->EndScene(g_dx7.d3d_device);

    if (g_dx7.fullscreen) {
        g_dx7.primary->lpVtbl->Flip(g_dx7.primary, NULL, DDFLIP_WAIT);
    } else {
        RECT client;
        RECT screen;
        POINT p;

        GetClientRect(g_dx7.hwnd, &client);
        p.x = 0;
        p.y = 0;
        ClientToScreen(g_dx7.hwnd, &p);

        screen.left = p.x;
        screen.top = p.y;
        screen.right = p.x + client.right;
        screen.bottom = p.y + client.bottom;

        g_dx7.primary->lpVtbl->Blt(
            g_dx7.primary,
            &screen,
            g_dx7.backbuffer,
            NULL,
            DDBLT_WAIT,
            NULL);
    }
}

static bool dx7_create_dd_device(void)
{
    HRESULT hr;

    hr = DirectDrawCreateEx(NULL, (void**)&g_dx7.dd, &IID_IDirectDraw7, NULL);
    if (FAILED(hr)) {
        return false;
    }

    if (g_dx7.fullscreen) {
        DDSURFACEDESC2 desc;
        DDSCAPS2 caps;

        hr = g_dx7.dd->lpVtbl->SetCooperativeLevel(
            g_dx7.dd,
            g_dx7.hwnd,
            DDSCL_EXCLUSIVE | DDSCL_FULLSCREEN | DDSCL_ALLOWREBOOT);
        if (FAILED(hr)) {
            return false;
        }

        hr = g_dx7.dd->lpVtbl->SetDisplayMode(
            g_dx7.dd,
            (DWORD)g_dx7.width,
            (DWORD)g_dx7.height,
            32,
            0,
            0);
        if (FAILED(hr)) {
            return false;
        }

        memset(&desc, 0, sizeof(desc));
        desc.dwSize = sizeof(desc);
        desc.dwFlags = DDSD_CAPS | DDSD_BACKBUFFERCOUNT;
        desc.ddsCaps.dwCaps = DDSCAPS_PRIMARYSURFACE | DDSCAPS_FLIP | DDSCAPS_COMPLEX;
        desc.dwBackBufferCount = 1;

        hr = g_dx7.dd->lpVtbl->CreateSurface(g_dx7.dd, &desc, &g_dx7.primary, NULL);
        if (FAILED(hr)) {
            return false;
        }

        memset(&caps, 0, sizeof(caps));
        caps.dwCaps = DDSCAPS_BACKBUFFER;
        hr = g_dx7.primary->lpVtbl->GetAttachedSurface(g_dx7.primary, &caps, &g_dx7.backbuffer);
        if (FAILED(hr)) {
            return false;
        }
    } else {
        DDSURFACEDESC2 desc;

        hr = g_dx7.dd->lpVtbl->SetCooperativeLevel(
            g_dx7.dd,
            g_dx7.hwnd,
            DDSCL_NORMAL);
        if (FAILED(hr)) {
            return false;
        }

        memset(&desc, 0, sizeof(desc));
        desc.dwSize = sizeof(desc);
        desc.dwFlags = DDSD_CAPS;
        desc.ddsCaps.dwCaps = DDSCAPS_PRIMARYSURFACE;
        hr = g_dx7.dd->lpVtbl->CreateSurface(g_dx7.dd, &desc, &g_dx7.primary, NULL);
        if (FAILED(hr)) {
            return false;
        }

        memset(&desc, 0, sizeof(desc));
        desc.dwSize = sizeof(desc);
        desc.dwFlags = DDSD_CAPS | DDSD_WIDTH | DDSD_HEIGHT;
        desc.ddsCaps.dwCaps = DDSCAPS_OFFSCREENPLAIN | DDSCAPS_3DDEVICE;
        desc.dwWidth = (DWORD)g_dx7.width;
        desc.dwHeight = (DWORD)g_dx7.height;

        hr = g_dx7.dd->lpVtbl->CreateSurface(g_dx7.dd, &desc, &g_dx7.backbuffer, NULL);
        if (FAILED(hr)) {
            return false;
        }

        hr = g_dx7.dd->lpVtbl->CreateClipper(g_dx7.dd, 0, &g_dx7.clipper, NULL);
        if (FAILED(hr)) {
            return false;
        }

        g_dx7.clipper->lpVtbl->SetHWnd(g_dx7.clipper, 0, g_dx7.hwnd);
        g_dx7.primary->lpVtbl->SetClipper(g_dx7.primary, g_dx7.clipper);
    }

    return true;
}

static bool dx7_create_d3d_device(void)
{
    HRESULT hr;
    D3DVIEWPORT7 vp;

    hr = g_dx7.dd->lpVtbl->QueryInterface(g_dx7.dd, &IID_IDirect3D7, (void**)&g_dx7.d3d);
    if (FAILED(hr)) {
        return false;
    }

    hr = g_dx7.d3d->lpVtbl->CreateDevice(
        g_dx7.d3d,
        &IID_IDirect3DHALDevice,
        g_dx7.backbuffer,
        &g_dx7.d3d_device);
    if (FAILED(hr)) {
        hr = g_dx7.d3d->lpVtbl->CreateDevice(
            g_dx7.d3d,
            &IID_IDirect3DRGBDevice,
            g_dx7.backbuffer,
            &g_dx7.d3d_device);
        if (FAILED(hr)) {
            return false;
        }
    }

    hr = g_dx7.d3d_device->lpVtbl->CreateViewport(g_dx7.d3d_device, &g_dx7.viewport, NULL);
    if (FAILED(hr)) {
        return false;
    }
    hr = g_dx7.d3d_device->lpVtbl->AddViewport(g_dx7.d3d_device, g_dx7.viewport);
    if (FAILED(hr)) {
        return false;
    }

    memset(&vp, 0, sizeof(vp));
    vp.dwX = 0;
    vp.dwY = 0;
    vp.dwWidth = (DWORD)g_dx7.width;
    vp.dwHeight = (DWORD)g_dx7.height;
    vp.dvMinZ = 0.0f;
    vp.dvMaxZ = 1.0f;
    hr = g_dx7.viewport->lpVtbl->SetViewport(g_dx7.viewport, &vp);
    if (FAILED(hr)) {
        return false;
    }

    hr = g_dx7.d3d_device->lpVtbl->SetRenderTarget(g_dx7.d3d_device, g_dx7.backbuffer, 0);
    if (FAILED(hr)) {
        return false;
    }

    g_dx7.d3d_device->lpVtbl->SetRenderState(g_dx7.d3d_device, D3DRENDERSTATE_ZENABLE, D3DZB_FALSE);
    g_dx7.d3d_device->lpVtbl->SetRenderState(g_dx7.d3d_device, D3DRENDERSTATE_LIGHTING, FALSE);
    g_dx7.d3d_device->lpVtbl->SetRenderState(g_dx7.d3d_device, D3DRENDERSTATE_CULLMODE, D3DCULL_NONE);

    return true;
}

static void dx7_build_caps(void)
{
    memset(&g_dx7.caps, 0, sizeof(g_dx7.caps));
    g_dx7.caps.name = "dx7";
    g_dx7.caps.supports_2d = true;
    g_dx7.caps.supports_3d = true;
    g_dx7.caps.supports_text = false;
    g_dx7.caps.supports_rt = false;
    g_dx7.caps.supports_alpha = true;
    g_dx7.caps.max_texture_size = 1024;
}

static void dx7_cmd_clear(const uint8_t* payload, size_t payload_size)
{
    dx7_cmd_clear_payload_t clr;
    float r = 0.0f;
    float g = 0.0f;
    float b = 0.0f;
    float a = 1.0f;

    if (!g_dx7.d3d_device) {
        return;
    }

    if (payload && payload_size >= sizeof(dx7_cmd_clear_payload_t)) {
        memcpy(&clr, payload, sizeof(clr));
        r = (float)clr.r / 255.0f;
        g = (float)clr.g / 255.0f;
        b = (float)clr.b / 255.0f;
        a = (float)clr.a / 255.0f;
    }

    g_dx7.d3d_device->lpVtbl->Clear(
        g_dx7.d3d_device,
        0,
        NULL,
        D3DCLEAR_TARGET,
        D3DRGBA(r, g, b, a),
        1.0f,
        0);
}

static void dx7_cmd_set_viewport(const uint8_t* payload)
{
    (void)payload;
    /* No custom viewports defined in the current IR; handled via resize/begin_frame. */
}

static void dx7_cmd_set_camera(const uint8_t* payload)
{
    (void)payload;
    /* Camera transforms are not yet defined in the IR; stubbed out. */
}

static void dx7_cmd_set_pipeline(const uint8_t* payload)
{
    (void)payload;
    /* Pipeline state is not defined for the DX7 backend MVP; keep defaults. */
}

static void dx7_cmd_set_texture(const uint8_t* payload)
{
    (void)payload;
    /* Texture binding is not implemented in the MVP. */
}

static void dx7_cmd_draw_sprites(const uint8_t* payload, size_t payload_size)
{
    (void)payload;
    (void)payload_size;
    /* Sprites not implemented yet. */
}

static void dx7_cmd_draw_lines(const uint8_t* payload, size_t payload_size)
{
    dx7_lines_header_t header;
    size_t required;
    const dx7_line_vertex_t* src;
    dx7_tl_vertex_t stack[256];
    dx7_tl_vertex_t* verts;
    uint16_t count;
    size_t i;

    if (!g_dx7.d3d_device || !payload) {
        return;
    }
    if (payload_size < sizeof(header)) {
        return;
    }

    memcpy(&header, payload, sizeof(header));
    count = header.vertex_count;
    required = sizeof(header) + ((size_t)count * sizeof(dx7_line_vertex_t));
    if (payload_size < required || count == 0u) {
        return;
    }

    src = (const dx7_line_vertex_t*)(payload + sizeof(header));

    if (count <= (uint16_t)(sizeof(stack) / sizeof(stack[0]))) {
        verts = stack;
    } else {
        verts = (dx7_tl_vertex_t*)malloc((size_t)count * sizeof(dx7_tl_vertex_t));
        if (!verts) {
            return;
        }
    }

    for (i = 0; i < (size_t)count; ++i) {
        verts[i].x = src[i].x;
        verts[i].y = src[i].y;
        verts[i].z = src[i].z;
        verts[i].rhw = 1.0f;
        verts[i].color = src[i].color;
        verts[i].tu = 0.0f;
        verts[i].tv = 0.0f;
    }

    g_dx7.d3d_device->lpVtbl->SetTexture(g_dx7.d3d_device, 0, NULL);
    g_dx7.d3d_device->lpVtbl->SetRenderState(g_dx7.d3d_device, D3DRENDERSTATE_ALPHABLENDENABLE, TRUE);
    g_dx7.d3d_device->lpVtbl->SetTextureStageState(g_dx7.d3d_device, 0, D3DTSS_COLOROP, D3DTOP_SELECTARG1);
    g_dx7.d3d_device->lpVtbl->SetTextureStageState(g_dx7.d3d_device, 0, D3DTSS_ALPHAOP, D3DTOP_SELECTARG1);

    g_dx7.d3d_device->lpVtbl->DrawPrimitive(
        g_dx7.d3d_device,
        D3DPT_LINELIST,
        DX7_TL_FVF,
        verts,
        count,
        D3DDP_WAIT);

    if (verts != stack) {
        free(verts);
    }
}

static void dx7_cmd_draw_meshes(const uint8_t* payload, size_t payload_size)
{
    (void)payload;
    (void)payload_size;
    /* 3D meshes not implemented yet. */
}

static void dx7_cmd_draw_text(const uint8_t* payload, size_t payload_size)
{
    (void)payload;
    (void)payload_size;
    /* Text rendering is stubbed in the DX7 backend MVP. */
}

static void dx7_execute(const dgfx_cmd_buffer* cmd_buf)
{
    const uint8_t* ptr;
    const uint8_t* end;
    size_t header_size;

    if (!cmd_buf || !cmd_buf->data || cmd_buf->size == 0u) {
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
            dx7_cmd_clear(payload, payload_size);
            break;
        case DGFX_CMD_SET_VIEWPORT:
            dx7_cmd_set_viewport(payload);
            break;
        case DGFX_CMD_SET_CAMERA:
            dx7_cmd_set_camera(payload);
            break;
        case DGFX_CMD_SET_PIPELINE:
            dx7_cmd_set_pipeline(payload);
            break;
        case DGFX_CMD_SET_TEXTURE:
            dx7_cmd_set_texture(payload);
            break;
        case DGFX_CMD_DRAW_SPRITES:
            dx7_cmd_draw_sprites(payload, payload_size);
            break;
        case DGFX_CMD_DRAW_MESHES:
            dx7_cmd_draw_meshes(payload, payload_size);
            break;
        case DGFX_CMD_DRAW_LINES:
            dx7_cmd_draw_lines(payload, payload_size);
            break;
        case DGFX_CMD_DRAW_TEXT:
            dx7_cmd_draw_text(payload, payload_size);
            break;
        default:
            break;
        }

        ptr += total_size;
    }
}
