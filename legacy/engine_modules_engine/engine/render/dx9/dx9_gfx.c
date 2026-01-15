/*
FILE: source/domino/render/dx9/dx9_gfx.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / render/dx9/dx9_gfx
RESPONSIBILITY: Implements `dx9_gfx`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#define COBJMACROS
#ifndef WIN32_LEAN_AND_MEAN
#define WIN32_LEAN_AND_MEAN
#endif

#include <windows.h>
#include <d3d9.h>
#include <stddef.h>
#include <stdlib.h>
#include <string.h>

#include "dx9_gfx.h"
#include "domino/sys.h"

#define DX9_SAFE_RELEASE(x) \
    do { if (x) { (x)->lpVtbl->Release(x); (x) = NULL; } } while (0)

typedef struct dx9_cmd_clear_payload_t {
    uint8_t r;
    uint8_t g;
    uint8_t b;
    uint8_t a;
} dx9_cmd_clear_payload_t;

typedef struct dx9_lines_header_t {
    uint16_t vertex_count;
    uint16_t reserved;
} dx9_lines_header_t;

typedef struct dx9_line_vertex_t {
    float    x;
    float    y;
    float    z;
    uint32_t color;
} dx9_line_vertex_t;

typedef struct dx9_tl_vertex_t {
    float    x;
    float    y;
    float    z;
    float    rhw;
    D3DCOLOR color;
    float    u;
    float    v;
} dx9_tl_vertex_t;

typedef struct dx9_mesh_vertex_t {
    float    x;
    float    y;
    float    z;
    float    nx;
    float    ny;
    float    nz;
    float    u;
    float    v;
    D3DCOLOR color;
} dx9_mesh_vertex_t;

#define DX9_LINE_FVF (D3DFVF_XYZRHW | D3DFVF_DIFFUSE)
#define DX9_TL_FVF   (D3DFVF_XYZRHW | D3DFVF_DIFFUSE | D3DFVF_TEX1)
#define DX9_MESH_FVF (D3DFVF_XYZ | D3DFVF_NORMAL | D3DFVF_TEX1 | D3DFVF_DIFFUSE)

dx9_state_t g_dx9;

static IDirect3DTexture9* g_dx9_current_texture = NULL;
static int dx9_device_lost = 0;

static bool      dx9_init(const dgfx_desc* desc);
static void      dx9_shutdown(void);
static dgfx_caps dx9_get_caps(void);
static void      dx9_resize(int width, int height);
static void      dx9_begin_frame(void);
static void      dx9_execute(const dgfx_cmd_buffer* cmd_buf);
static void      dx9_end_frame(void);

static void dx9_build_caps(void);
static void dx9_apply_default_state(void);
static void dx9_check_device(void);

static void dx9_cmd_clear(const uint8_t* payload, size_t payload_size);
static void dx9_cmd_set_viewport(const uint8_t* payload);
static void dx9_cmd_set_camera(const uint8_t* payload);
static void dx9_cmd_set_pipeline(const uint8_t* payload);
static void dx9_cmd_set_texture(const uint8_t* payload);
static void dx9_cmd_draw_sprites(const uint8_t* payload, size_t payload_size);
static void dx9_cmd_draw_lines(const uint8_t* payload, size_t payload_size);
static void dx9_cmd_draw_meshes(const uint8_t* payload, size_t payload_size);
static void dx9_cmd_draw_text(const uint8_t* payload, size_t payload_size);

static const dgfx_backend_vtable g_dx9_vtable = {
    dx9_init,
    dx9_shutdown,
    dx9_get_caps,
    dx9_resize,
    dx9_begin_frame,
    dx9_execute,
    dx9_end_frame
};

const dgfx_backend_vtable* dgfx_dx9_get_vtable(void)
{
    return &g_dx9_vtable;
}

static void dx9_build_caps(void)
{
    memset(&g_dx9.caps, 0, sizeof(g_dx9.caps));
    g_dx9.caps.name = "dx9";
    g_dx9.caps.supports_2d = true;
    g_dx9.caps.supports_3d = true;
    g_dx9.caps.supports_text = false;
    g_dx9.caps.supports_rt = false;
    g_dx9.caps.supports_alpha = true;
    g_dx9.caps.max_texture_size = 4096;
}

static void dx9_apply_default_state(void)
{
    if (!g_dx9.device) {
        return;
    }

    g_dx9.device->lpVtbl->SetRenderState(
        g_dx9.device, D3DRS_ZENABLE, D3DZB_TRUE);
    g_dx9.device->lpVtbl->SetRenderState(
        g_dx9.device, D3DRS_CULLMODE, D3DCULL_CCW);
    g_dx9.device->lpVtbl->SetRenderState(
        g_dx9.device, D3DRS_LIGHTING, FALSE);
    g_dx9.device->lpVtbl->SetRenderState(
        g_dx9.device, D3DRS_ALPHABLENDENABLE, TRUE);
    g_dx9.device->lpVtbl->SetRenderState(
        g_dx9.device, D3DRS_SRCBLEND, D3DBLEND_SRCALPHA);
    g_dx9.device->lpVtbl->SetRenderState(
        g_dx9.device, D3DRS_DESTBLEND, D3DBLEND_INVSRCALPHA);
}

static bool dx9_init(const dgfx_desc* desc)
{
    HRESULT hr;
    DWORD behavior_flags;
    D3DPRESENT_PARAMETERS* pp;

    memset(&g_dx9, 0, sizeof(g_dx9));
    dx9_device_lost = 0;

    if (!desc || !desc->window) {
        return false;
    }

    g_dx9.hwnd = (HWND)dsys_window_get_native_handle(desc->window);
    if (!g_dx9.hwnd) {
        return false;
    }
    g_dx9.hinstance = GetModuleHandleA(NULL);
    g_dx9.width = (desc->width > 0) ? desc->width : 800;
    g_dx9.height = (desc->height > 0) ? desc->height : 600;
    g_dx9.fullscreen = 0;

    g_dx9.d3d = Direct3DCreate9(D3D_SDK_VERSION);
    if (!g_dx9.d3d) {
        return false;
    }

    memset(&g_dx9.pp, 0, sizeof(g_dx9.pp));
    pp = &g_dx9.pp;
    pp->Windowed = TRUE;
    pp->hDeviceWindow = g_dx9.hwnd;
    pp->SwapEffect = D3DSWAPEFFECT_DISCARD;
    pp->BackBufferCount = 1;
    pp->BackBufferWidth = (UINT)g_dx9.width;
    pp->BackBufferHeight = (UINT)g_dx9.height;
    pp->BackBufferFormat = D3DFMT_UNKNOWN;
    pp->MultiSampleType = D3DMULTISAMPLE_NONE;
    pp->EnableAutoDepthStencil = TRUE;
    pp->AutoDepthStencilFormat = D3DFMT_D24S8;
    pp->PresentationInterval = desc->vsync ? D3DPRESENT_INTERVAL_ONE
                                           : D3DPRESENT_INTERVAL_IMMEDIATE;

    behavior_flags = D3DCREATE_HARDWARE_VERTEXPROCESSING | D3DCREATE_FPU_PRESERVE;
    hr = g_dx9.d3d->lpVtbl->CreateDevice(
        g_dx9.d3d,
        D3DADAPTER_DEFAULT,
        D3DDEVTYPE_HAL,
        g_dx9.hwnd,
        behavior_flags,
        pp,
        &g_dx9.device);

    if (FAILED(hr)) {
        pp->AutoDepthStencilFormat = D3DFMT_D16;
        hr = g_dx9.d3d->lpVtbl->CreateDevice(
            g_dx9.d3d,
            D3DADAPTER_DEFAULT,
            D3DDEVTYPE_HAL,
            g_dx9.hwnd,
            behavior_flags,
            pp,
            &g_dx9.device);
    }

    if (FAILED(hr)) {
        behavior_flags = D3DCREATE_SOFTWARE_VERTEXPROCESSING | D3DCREATE_FPU_PRESERVE;
        hr = g_dx9.d3d->lpVtbl->CreateDevice(
            g_dx9.d3d,
            D3DADAPTER_DEFAULT,
            D3DDEVTYPE_HAL,
            g_dx9.hwnd,
            behavior_flags,
            pp,
            &g_dx9.device);
    }

    if (FAILED(hr)) {
        dx9_shutdown();
        return false;
    }

    dx9_apply_default_state();

    g_dx9.scene_active = 0;
    dx9_build_caps();
    return true;
}

static void dx9_shutdown(void)
{
    DX9_SAFE_RELEASE(g_dx9.device);
    DX9_SAFE_RELEASE(g_dx9.d3d);
    g_dx9_current_texture = NULL;
    dx9_device_lost = 0;
    memset(&g_dx9, 0, sizeof(g_dx9));
}

static dgfx_caps dx9_get_caps(void)
{
    return g_dx9.caps;
}

static void dx9_resize(int width, int height)
{
    HRESULT hr;

    if (!g_dx9.device || !g_dx9.d3d) {
        return;
    }
    if (width <= 0 || height <= 0) {
        return;
    }
    if (width == g_dx9.width && height == g_dx9.height) {
        return;
    }

    g_dx9.width = width;
    g_dx9.height = height;
    g_dx9.pp.BackBufferWidth = (UINT)width;
    g_dx9.pp.BackBufferHeight = (UINT)height;

    hr = g_dx9.device->lpVtbl->Reset(g_dx9.device, &g_dx9.pp);
    if (FAILED(hr)) {
        dx9_device_lost = 1;
        return;
    }

    dx9_apply_default_state();
    g_dx9.scene_active = 0;
    dx9_device_lost = 0;
}

static void dx9_check_device(void)
{
    HRESULT hr;

    if (!g_dx9.device) {
        return;
    }
    if (!dx9_device_lost) {
        return;
    }

    hr = g_dx9.device->lpVtbl->TestCooperativeLevel(g_dx9.device);
    if (hr == D3DERR_DEVICENOTRESET) {
        hr = g_dx9.device->lpVtbl->Reset(g_dx9.device, &g_dx9.pp);
        if (SUCCEEDED(hr)) {
            dx9_apply_default_state();
            g_dx9.scene_active = 0;
            dx9_device_lost = 0;
        }
    }
}

static void dx9_begin_frame(void)
{
    HRESULT hr;

    dx9_check_device();
    if (!g_dx9.device || dx9_device_lost) {
        return;
    }

    hr = g_dx9.device->lpVtbl->Clear(
        g_dx9.device,
        0,
        NULL,
        D3DCLEAR_TARGET | D3DCLEAR_ZBUFFER,
        D3DCOLOR_XRGB(0, 0, 0),
        1.0f,
        0);
    if (FAILED(hr)) {
        if (hr == D3DERR_DEVICELOST) {
            dx9_device_lost = 1;
        }
        return;
    }

    if (!g_dx9.scene_active) {
        hr = g_dx9.device->lpVtbl->BeginScene(g_dx9.device);
        if (SUCCEEDED(hr)) {
            g_dx9.scene_active = 1;
        } else if (hr == D3DERR_DEVICELOST) {
            dx9_device_lost = 1;
        }
    }
}

static void dx9_end_frame(void)
{
    HRESULT hr;

    if (!g_dx9.device) {
        return;
    }
    if (dx9_device_lost) {
        dx9_check_device();
        return;
    }

    if (g_dx9.scene_active) {
        g_dx9.device->lpVtbl->EndScene(g_dx9.device);
        g_dx9.scene_active = 0;
    }

    hr = g_dx9.device->lpVtbl->Present(g_dx9.device, NULL, NULL, NULL, NULL);
    if (hr == D3DERR_DEVICELOST) {
        dx9_device_lost = 1;
    }
}

static void dx9_cmd_clear(const uint8_t* payload, size_t payload_size)
{
    dx9_cmd_clear_payload_t clr;
    float r;
    float g;
    float b;
    float a;

    if (!g_dx9.device) {
        return;
    }

    r = 0.0f;
    g = 0.0f;
    b = 0.0f;
    a = 1.0f;

    if (payload && payload_size >= sizeof(dx9_cmd_clear_payload_t)) {
        memcpy(&clr, payload, sizeof(clr));
        r = (float)clr.r / 255.0f;
        g = (float)clr.g / 255.0f;
        b = (float)clr.b / 255.0f;
        a = (float)clr.a / 255.0f;
    }

    g_dx9.device->lpVtbl->Clear(
        g_dx9.device,
        0,
        NULL,
        D3DCLEAR_TARGET | D3DCLEAR_ZBUFFER,
        D3DCOLOR_COLORVALUE(r, g, b, a),
        1.0f,
        0);
}

static void dx9_cmd_set_viewport(const uint8_t* payload)
{
    int32_t x;
    int32_t y;
    int32_t w;
    int32_t h;
    D3DVIEWPORT9 vp;

    (void)payload;
    if (!g_dx9.device) {
        return;
    }

    x = 0;
    y = 0;
    w = g_dx9.width;
    h = g_dx9.height;

    vp.X = (DWORD)x;
    vp.Y = (DWORD)y;
    vp.Width = (DWORD)w;
    vp.Height = (DWORD)h;
    vp.MinZ = 0.0f;
    vp.MaxZ = 1.0f;

    g_dx9.device->lpVtbl->SetViewport(g_dx9.device, &vp);
}

static void dx9_cmd_set_camera(const uint8_t* payload)
{
    (void)payload;
    /* Camera transforms are not defined in the current IR; stubbed out. */
}

static void dx9_cmd_set_pipeline(const uint8_t* payload)
{
    (void)payload;
    /* Basic alpha blending defaults; future pipeline IDs will map here. */
    dx9_apply_default_state();
}

static void dx9_cmd_set_texture(const uint8_t* payload)
{
    (void)payload;
    if (!g_dx9.device) {
        return;
    }

    g_dx9.device->lpVtbl->SetTexture(
        g_dx9.device,
        0,
        (IDirect3DBaseTexture9*)g_dx9_current_texture);
}

static void dx9_cmd_draw_sprites(const uint8_t* payload, size_t payload_size)
{
    (void)payload;
    (void)payload_size;
    if (!g_dx9.device) {
        return;
    }

    /* Sprite batching not yet implemented. */
}

static void dx9_cmd_draw_lines(const uint8_t* payload, size_t payload_size)
{
    dx9_lines_header_t header;
    size_t required;
    const dx9_line_vertex_t* src;
    dx9_tl_vertex_t stack[256];
    dx9_tl_vertex_t* verts;
    uint16_t count;
    size_t i;

    if (!g_dx9.device || !payload) {
        return;
    }
    if (payload_size < sizeof(header)) {
        return;
    }

    memcpy(&header, payload, sizeof(header));
    count = header.vertex_count;
    required = sizeof(header) + ((size_t)count * sizeof(dx9_line_vertex_t));
    if (payload_size < required || count == 0u) {
        return;
    }

    src = (const dx9_line_vertex_t*)(payload + sizeof(header));

    if (count <= (uint16_t)(sizeof(stack) / sizeof(stack[0]))) {
        verts = stack;
    } else {
        verts = (dx9_tl_vertex_t*)malloc((size_t)count * sizeof(dx9_tl_vertex_t));
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
        verts[i].u = 0.0f;
        verts[i].v = 0.0f;
    }

    g_dx9.device->lpVtbl->SetTexture(g_dx9.device, 0, NULL);
    g_dx9.device->lpVtbl->SetFVF(g_dx9.device, DX9_LINE_FVF);
    g_dx9.device->lpVtbl->DrawPrimitiveUP(
        g_dx9.device,
        D3DPT_LINELIST,
        count / 2u,
        verts,
        sizeof(dx9_tl_vertex_t));

    if (verts != stack) {
        free(verts);
    }
}

static void dx9_cmd_draw_meshes(const uint8_t* payload, size_t payload_size)
{
    (void)payload;
    (void)payload_size;
    if (!g_dx9.device) {
        return;
    }

    /* 3D mesh rendering will be wired once the IR is finalized. */
}

static void dx9_cmd_draw_text(const uint8_t* payload, size_t payload_size)
{
    (void)payload;
    (void)payload_size;
    /* Text rendering is not implemented in the DX9 backend MVP. */
}

static void dx9_execute(const dgfx_cmd_buffer* cmd_buf)
{
    const uint8_t* ptr;
    const uint8_t* end;
    size_t header_size;

    dx9_check_device();
    if (!cmd_buf || !cmd_buf->data || cmd_buf->size == 0u) {
        return;
    }
    if (!g_dx9.device || dx9_device_lost) {
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
            dx9_cmd_clear(payload, payload_size);
            break;
        case DGFX_CMD_SET_VIEWPORT:
            dx9_cmd_set_viewport(payload);
            break;
        case DGFX_CMD_SET_CAMERA:
            dx9_cmd_set_camera(payload);
            break;
        case DGFX_CMD_SET_PIPELINE:
            dx9_cmd_set_pipeline(payload);
            break;
        case DGFX_CMD_SET_TEXTURE:
            dx9_cmd_set_texture(payload);
            break;
        case DGFX_CMD_DRAW_SPRITES:
            dx9_cmd_draw_sprites(payload, payload_size);
            break;
        case DGFX_CMD_DRAW_MESHES:
            dx9_cmd_draw_meshes(payload, payload_size);
            break;
        case DGFX_CMD_DRAW_LINES:
            dx9_cmd_draw_lines(payload, payload_size);
            break;
        case DGFX_CMD_DRAW_TEXT:
            dx9_cmd_draw_text(payload, payload_size);
            break;
        default:
            break;
        }

        ptr += total_size;
    }
}
