/*
FILE: source/domino/render/dx11/dx11_gfx.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / render/dx11/dx11_gfx
RESPONSIBILITY: Implements `dx11_gfx`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
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
#include <d3d11.h>
#include <dxgi.h>
#include <stddef.h>
#include <stdlib.h>
#include <string.h>

#include "dx11_gfx.h"
#include "domino/sys.h"

#define DX11_DYNAMIC_VB_SIZE (64 * 1024)

typedef struct dx11_cmd_clear_payload_t {
    uint8_t r;
    uint8_t g;
    uint8_t b;
    uint8_t a;
} dx11_cmd_clear_payload_t;

typedef struct dx11_lines_header_t {
    uint16_t vertex_count;
    uint16_t reserved;
} dx11_lines_header_t;

typedef struct dx11_line_vertex_t {
    float    x;
    float    y;
    float    z;
    uint32_t color;
} dx11_line_vertex_t;

typedef struct dx11_sprite_vertex_t {
    float    x;
    float    y;
    float    z;
    float    u;
    float    v;
    uint32_t color;
} dx11_sprite_vertex_t;

typedef struct dx11_camera_cb_t {
    float view[16];
    float proj[16];
    float world[16];
} dx11_camera_cb_t;

dx11_state_t g_dx11;

static bool      dx11_init(const dgfx_desc* desc);
static void      dx11_shutdown(void);
static dgfx_caps dx11_get_caps(void);
static void      dx11_resize(int width, int height);
static void      dx11_begin_frame(void);
static void      dx11_execute(const dgfx_cmd_buffer* cmd_buf);
static void      dx11_end_frame(void);

static void dx11_build_caps(void);
static bool dx11_create_backbuffer_targets(void);
static bool dx11_create_common_resources(void);
static bool dx11_create_dynamic_buffer(UINT size, UINT bind_flags, ID3D11Buffer** out_buf);
static void dx11_release_resource(IUnknown** res);

static void dx11_cmd_clear(const uint8_t* payload, size_t payload_size);
static void dx11_cmd_set_viewport(const uint8_t* payload);
static void dx11_cmd_set_camera(const uint8_t* payload);
static void dx11_cmd_set_pipeline(const uint8_t* payload);
static void dx11_cmd_set_texture(const uint8_t* payload);
static void dx11_cmd_draw_sprites(const uint8_t* payload, size_t payload_size);
static void dx11_cmd_draw_lines(const uint8_t* payload, size_t payload_size);
static void dx11_cmd_draw_meshes(const uint8_t* payload, size_t payload_size);
static void dx11_cmd_draw_text(const uint8_t* payload, size_t payload_size);

static const dgfx_backend_vtable g_dx11_vtable = {
    dx11_init,
    dx11_shutdown,
    dx11_get_caps,
    dx11_resize,
    dx11_begin_frame,
    dx11_execute,
    dx11_end_frame
};

const dgfx_backend_vtable* dgfx_dx11_get_vtable(void)
{
    return &g_dx11_vtable;
}

static void dx11_build_caps(void)
{
    memset(&g_dx11.caps, 0, sizeof(g_dx11.caps));
    g_dx11.caps.name = "dx11";
    g_dx11.caps.supports_2d = true;
    g_dx11.caps.supports_3d = true;
    g_dx11.caps.supports_text = false;
    g_dx11.caps.supports_rt = true;
    g_dx11.caps.supports_alpha = true;
    g_dx11.caps.max_texture_size = 16384;
}

static void dx11_release_resource(IUnknown** res)
{
    if (res && *res) {
        (*res)->lpVtbl->Release(*res);
        *res = NULL;
    }
}

static bool dx11_create_dynamic_buffer(UINT size, UINT bind_flags, ID3D11Buffer** out_buf)
{
    HRESULT hr;
    D3D11_BUFFER_DESC desc;

    if (!g_dx11.device || !out_buf) {
        return false;
    }

    memset(&desc, 0, sizeof(desc));
    desc.ByteWidth = size;
    desc.Usage = D3D11_USAGE_DYNAMIC;
    desc.BindFlags = bind_flags;
    desc.CPUAccessFlags = D3D11_CPU_ACCESS_WRITE;

    hr = g_dx11.device->lpVtbl->CreateBuffer(g_dx11.device, &desc, NULL, out_buf);
    return SUCCEEDED(hr);
}

static bool dx11_create_backbuffer_targets(void)
{
    HRESULT hr;
    ID3D11Texture2D* backbuffer;
    D3D11_TEXTURE2D_DESC depth_desc;

    if (!g_dx11.device || !g_dx11.swap_chain) {
        return false;
    }

    backbuffer = NULL;
    hr = g_dx11.swap_chain->lpVtbl->GetBuffer(
        g_dx11.swap_chain,
        0,
        &IID_ID3D11Texture2D,
        (void**)&backbuffer);
    if (FAILED(hr)) {
        return false;
    }

    hr = g_dx11.device->lpVtbl->CreateRenderTargetView(
        g_dx11.device,
        (ID3D11Resource*)backbuffer,
        NULL,
        &g_dx11.rtv);
    backbuffer->lpVtbl->Release(backbuffer);
    if (FAILED(hr)) {
        return false;
    }

    memset(&depth_desc, 0, sizeof(depth_desc));
    depth_desc.Width = (UINT)g_dx11.width;
    depth_desc.Height = (UINT)g_dx11.height;
    depth_desc.MipLevels = 1;
    depth_desc.ArraySize = 1;
    depth_desc.Format = DXGI_FORMAT_D24_UNORM_S8_UINT;
    depth_desc.SampleDesc.Count = 1;
    depth_desc.SampleDesc.Quality = 0;
    depth_desc.Usage = D3D11_USAGE_DEFAULT;
    depth_desc.BindFlags = D3D11_BIND_DEPTH_STENCIL;

    hr = g_dx11.device->lpVtbl->CreateTexture2D(
        g_dx11.device,
        &depth_desc,
        NULL,
        &g_dx11.depth_tex);
    if (FAILED(hr)) {
        return false;
    }

    hr = g_dx11.device->lpVtbl->CreateDepthStencilView(
        g_dx11.device,
        (ID3D11Resource*)g_dx11.depth_tex,
        NULL,
        &g_dx11.dsv);
    if (FAILED(hr)) {
        return false;
    }

    g_dx11.context->lpVtbl->OMSetRenderTargets(
        g_dx11.context,
        1,
        &g_dx11.rtv,
        g_dx11.dsv);

    return true;
}

static bool dx11_create_common_resources(void)
{
    HRESULT hr;

    if (!g_dx11.device) {
        return false;
    }

    /* Alpha blend state */
    {
        D3D11_BLEND_DESC bd;
        memset(&bd, 0, sizeof(bd));
        bd.RenderTarget[0].BlendEnable = TRUE;
        bd.RenderTarget[0].SrcBlend = D3D11_BLEND_SRC_ALPHA;
        bd.RenderTarget[0].DestBlend = D3D11_BLEND_INV_SRC_ALPHA;
        bd.RenderTarget[0].BlendOp = D3D11_BLEND_OP_ADD;
        bd.RenderTarget[0].SrcBlendAlpha = D3D11_BLEND_ONE;
        bd.RenderTarget[0].DestBlendAlpha = D3D11_BLEND_ZERO;
        bd.RenderTarget[0].BlendOpAlpha = D3D11_BLEND_OP_ADD;
        bd.RenderTarget[0].RenderTargetWriteMask = D3D11_COLOR_WRITE_ENABLE_ALL;

        hr = g_dx11.device->lpVtbl->CreateBlendState(
            g_dx11.device,
            &bd,
            &g_dx11.blend_alpha);
        if (FAILED(hr)) {
            goto fail;
        }
    }

    /* Rasterizer state */
    {
        D3D11_RASTERIZER_DESC rd;
        memset(&rd, 0, sizeof(rd));
        rd.FillMode = D3D11_FILL_SOLID;
        rd.CullMode = D3D11_CULL_BACK;
        rd.DepthClipEnable = TRUE;

        hr = g_dx11.device->lpVtbl->CreateRasterizerState(
            g_dx11.device,
            &rd,
            &g_dx11.rs_solid);
        if (FAILED(hr)) {
            goto fail;
        }
    }

    /* Depth-stencil state */
    {
        D3D11_DEPTH_STENCIL_DESC dd;
        memset(&dd, 0, sizeof(dd));
        dd.DepthEnable = TRUE;
        dd.DepthWriteMask = D3D11_DEPTH_WRITE_MASK_ALL;
        dd.DepthFunc = D3D11_COMPARISON_LESS;
        dd.StencilEnable = FALSE;

        hr = g_dx11.device->lpVtbl->CreateDepthStencilState(
            g_dx11.device,
            &dd,
            &g_dx11.ds_default);
        if (FAILED(hr)) {
            goto fail;
        }
    }

    /* Constant buffer for camera/world matrices */
    {
        D3D11_BUFFER_DESC cbd;
        memset(&cbd, 0, sizeof(cbd));
        cbd.ByteWidth = 64u * 3u;
        cbd.Usage = D3D11_USAGE_DYNAMIC;
        cbd.BindFlags = D3D11_BIND_CONSTANT_BUFFER;
        cbd.CPUAccessFlags = D3D11_CPU_ACCESS_WRITE;
        hr = g_dx11.device->lpVtbl->CreateBuffer(
            g_dx11.device,
            &cbd,
            NULL,
            &g_dx11.cb_camera);
        if (FAILED(hr)) {
            goto fail;
        }
    }

    /* Dynamic vertex buffer shared by sprites/lines */
    if (!dx11_create_dynamic_buffer(
            DX11_DYNAMIC_VB_SIZE,
            D3D11_BIND_VERTEX_BUFFER,
            &g_dx11.vb_sprite)) {
        goto fail;
    }

    return true;

fail:
    dx11_release_resource((IUnknown**)&g_dx11.cb_camera);
    dx11_release_resource((IUnknown**)&g_dx11.vb_mesh);
    dx11_release_resource((IUnknown**)&g_dx11.ib_mesh);
    dx11_release_resource((IUnknown**)&g_dx11.vb_sprite);
    dx11_release_resource((IUnknown**)&g_dx11.il_mesh);
    dx11_release_resource((IUnknown**)&g_dx11.il_sprite);
    dx11_release_resource((IUnknown**)&g_dx11.vs_mesh);
    dx11_release_resource((IUnknown**)&g_dx11.ps_mesh);
    dx11_release_resource((IUnknown**)&g_dx11.vs_sprite);
    dx11_release_resource((IUnknown**)&g_dx11.ps_sprite);
    dx11_release_resource((IUnknown**)&g_dx11.ds_default);
    dx11_release_resource((IUnknown**)&g_dx11.rs_solid);
    dx11_release_resource((IUnknown**)&g_dx11.blend_alpha);
    return false;
}

static bool dx11_init(const dgfx_desc* desc)
{
    HRESULT hr;
    DXGI_SWAP_CHAIN_DESC scd;
    UINT flags;

    memset(&g_dx11, 0, sizeof(g_dx11));

    if (!desc || !desc->window) {
        return false;
    }

    g_dx11.hwnd = (HWND)dsys_window_get_native_handle(desc->window);
    if (!g_dx11.hwnd) {
        return false;
    }
    g_dx11.hinstance = GetModuleHandleA(NULL);
    g_dx11.width = (desc->width > 0) ? desc->width : 800;
    g_dx11.height = (desc->height > 0) ? desc->height : 600;
    g_dx11.fullscreen = 0;
    g_dx11.vsync = desc->vsync ? 1 : 0;

    memset(&scd, 0, sizeof(scd));
    scd.BufferCount = 1;
    scd.BufferDesc.Width = (UINT)g_dx11.width;
    scd.BufferDesc.Height = (UINT)g_dx11.height;
    scd.BufferDesc.Format = DXGI_FORMAT_R8G8B8A8_UNORM;
    scd.BufferDesc.RefreshRate.Numerator = 0;
    scd.BufferDesc.RefreshRate.Denominator = 1;
    scd.BufferUsage = DXGI_USAGE_RENDER_TARGET_OUTPUT;
    scd.OutputWindow = g_dx11.hwnd;
    scd.SampleDesc.Count = 1;
    scd.SampleDesc.Quality = 0;
    scd.Windowed = TRUE;
    scd.SwapEffect = DXGI_SWAP_EFFECT_DISCARD;

    flags = 0u;
#if defined(_DEBUG)
    flags |= D3D11_CREATE_DEVICE_DEBUG;
#endif

    hr = D3D11CreateDeviceAndSwapChain(
        NULL,
        D3D_DRIVER_TYPE_HARDWARE,
        NULL,
        flags,
        NULL,
        0,
        D3D11_SDK_VERSION,
        &scd,
        &g_dx11.swap_chain,
        &g_dx11.device,
        NULL,
        &g_dx11.context);
    if (FAILED(hr)) {
        dx11_shutdown();
        return false;
    }

    if (!dx11_create_backbuffer_targets()) {
        dx11_shutdown();
        return false;
    }

    if (!dx11_create_common_resources()) {
        dx11_shutdown();
        return false;
    }

    dx11_build_caps();
    g_dx11.frame_in_progress = 0;
    return true;
}

static void dx11_shutdown(void)
{
    dx11_release_resource((IUnknown**)&g_dx11.cb_camera);
    dx11_release_resource((IUnknown**)&g_dx11.vb_mesh);
    dx11_release_resource((IUnknown**)&g_dx11.ib_mesh);
    dx11_release_resource((IUnknown**)&g_dx11.vb_sprite);

    dx11_release_resource((IUnknown**)&g_dx11.il_mesh);
    dx11_release_resource((IUnknown**)&g_dx11.il_sprite);
    dx11_release_resource((IUnknown**)&g_dx11.vs_mesh);
    dx11_release_resource((IUnknown**)&g_dx11.ps_mesh);
    dx11_release_resource((IUnknown**)&g_dx11.vs_sprite);
    dx11_release_resource((IUnknown**)&g_dx11.ps_sprite);

    dx11_release_resource((IUnknown**)&g_dx11.ds_default);
    dx11_release_resource((IUnknown**)&g_dx11.rs_solid);
    dx11_release_resource((IUnknown**)&g_dx11.blend_alpha);

    dx11_release_resource((IUnknown**)&g_dx11.dsv);
    dx11_release_resource((IUnknown**)&g_dx11.depth_tex);
    dx11_release_resource((IUnknown**)&g_dx11.rtv);

    dx11_release_resource((IUnknown**)&g_dx11.swap_chain);
    dx11_release_resource((IUnknown**)&g_dx11.context);
    dx11_release_resource((IUnknown**)&g_dx11.device);

    memset(&g_dx11, 0, sizeof(g_dx11));
}

static dgfx_caps dx11_get_caps(void)
{
    return g_dx11.caps;
}

static void dx11_resize(int width, int height)
{
    HRESULT hr;

    if (!g_dx11.device || !g_dx11.swap_chain) {
        return;
    }
    if (width <= 0 || height <= 0) {
        return;
    }
    if (width == g_dx11.width && height == g_dx11.height) {
        return;
    }

    g_dx11.width = width;
    g_dx11.height = height;

    dx11_release_resource((IUnknown**)&g_dx11.dsv);
    dx11_release_resource((IUnknown**)&g_dx11.depth_tex);
    dx11_release_resource((IUnknown**)&g_dx11.rtv);

    hr = g_dx11.swap_chain->lpVtbl->ResizeBuffers(
        g_dx11.swap_chain,
        0,
        (UINT)g_dx11.width,
        (UINT)g_dx11.height,
        DXGI_FORMAT_UNKNOWN,
        0);
    if (FAILED(hr)) {
        return;
    }

    dx11_create_backbuffer_targets();
}

static void dx11_begin_frame(void)
{
    float clear_color[4];
    D3D11_VIEWPORT vp;

    if (!g_dx11.context || !g_dx11.rtv || !g_dx11.dsv) {
        return;
    }

    clear_color[0] = 0.0f;
    clear_color[1] = 0.0f;
    clear_color[2] = 0.0f;
    clear_color[3] = 1.0f;

    g_dx11.context->lpVtbl->OMSetRenderTargets(
        g_dx11.context,
        1,
        &g_dx11.rtv,
        g_dx11.dsv);

    g_dx11.context->lpVtbl->RSSetState(g_dx11.context, g_dx11.rs_solid);
    g_dx11.context->lpVtbl->OMSetDepthStencilState(
        g_dx11.context,
        g_dx11.ds_default,
        0);

    vp.TopLeftX = 0.0f;
    vp.TopLeftY = 0.0f;
    vp.Width = (float)g_dx11.width;
    vp.Height = (float)g_dx11.height;
    vp.MinDepth = 0.0f;
    vp.MaxDepth = 1.0f;
    g_dx11.context->lpVtbl->RSSetViewports(g_dx11.context, 1, &vp);

    g_dx11.context->lpVtbl->ClearRenderTargetView(
        g_dx11.context,
        g_dx11.rtv,
        clear_color);
    g_dx11.context->lpVtbl->ClearDepthStencilView(
        g_dx11.context,
        g_dx11.dsv,
        D3D11_CLEAR_DEPTH | D3D11_CLEAR_STENCIL,
        1.0f,
        0);

    g_dx11.frame_in_progress = 1;
}

static void dx11_end_frame(void)
{
    if (!g_dx11.swap_chain) {
        return;
    }

    g_dx11.swap_chain->lpVtbl->Present(
        g_dx11.swap_chain,
        g_dx11.vsync ? 1u : 0u,
        0u);
    g_dx11.frame_in_progress = 0;
}

static void dx11_cmd_clear(const uint8_t* payload, size_t payload_size)
{
    dx11_cmd_clear_payload_t clr;
    float color[4];

    if (!g_dx11.context || !g_dx11.rtv || !g_dx11.dsv) {
        return;
    }

    color[0] = 0.0f;
    color[1] = 0.0f;
    color[2] = 0.0f;
    color[3] = 1.0f;

    if (payload && payload_size >= sizeof(dx11_cmd_clear_payload_t)) {
        memcpy(&clr, payload, sizeof(clr));
        color[0] = (float)clr.r / 255.0f;
        color[1] = (float)clr.g / 255.0f;
        color[2] = (float)clr.b / 255.0f;
        color[3] = (float)clr.a / 255.0f;
    }

    g_dx11.context->lpVtbl->ClearRenderTargetView(
        g_dx11.context,
        g_dx11.rtv,
        color);
    g_dx11.context->lpVtbl->ClearDepthStencilView(
        g_dx11.context,
        g_dx11.dsv,
        D3D11_CLEAR_DEPTH | D3D11_CLEAR_STENCIL,
        1.0f,
        0);
}

static void dx11_cmd_set_viewport(const uint8_t* payload)
{
    D3D11_VIEWPORT vp;

    (void)payload;
    if (!g_dx11.context) {
        return;
    }

    vp.TopLeftX = 0.0f;
    vp.TopLeftY = 0.0f;
    vp.Width = (float)g_dx11.width;
    vp.Height = (float)g_dx11.height;
    vp.MinDepth = 0.0f;
    vp.MaxDepth = 1.0f;

    g_dx11.context->lpVtbl->RSSetViewports(g_dx11.context, 1, &vp);
}

static void dx11_cmd_set_camera(const uint8_t* payload)
{
    D3D11_MAPPED_SUBRESOURCE map;
    dx11_camera_cb_t* cb;
    size_t i;

    (void)payload;
    if (!g_dx11.context || !g_dx11.cb_camera) {
        return;
    }

    if (FAILED(g_dx11.context->lpVtbl->Map(
            g_dx11.context,
            (ID3D11Resource*)g_dx11.cb_camera,
            0,
            D3D11_MAP_WRITE_DISCARD,
            0,
            &map))) {
        return;
    }

    cb = (dx11_camera_cb_t*)map.pData;
    if (!cb) {
        g_dx11.context->lpVtbl->Unmap(
            g_dx11.context,
            (ID3D11Resource*)g_dx11.cb_camera,
            0);
        return;
    }

    for (i = 0u; i < 16u; ++i) {
        cb->view[i] = 0.0f;
        cb->proj[i] = 0.0f;
        cb->world[i] = 0.0f;
    }
    cb->view[0] = cb->view[5] = cb->view[10] = cb->view[15] = 1.0f;
    cb->proj[0] = cb->proj[5] = cb->proj[10] = cb->proj[15] = 1.0f;
    cb->world[0] = cb->world[5] = cb->world[10] = cb->world[15] = 1.0f;

    g_dx11.context->lpVtbl->Unmap(
        g_dx11.context,
        (ID3D11Resource*)g_dx11.cb_camera,
        0);

    g_dx11.context->lpVtbl->VSSetConstantBuffers(
        g_dx11.context,
        0,
        1,
        &g_dx11.cb_camera);
}

static void dx11_cmd_set_pipeline(const uint8_t* payload)
{
    float blend_factor[4];
    UINT sample_mask;

    (void)payload;
    if (!g_dx11.context) {
        return;
    }

    blend_factor[0] = 1.0f;
    blend_factor[1] = 1.0f;
    blend_factor[2] = 1.0f;
    blend_factor[3] = 1.0f;
    sample_mask = 0xffffffffu;

    g_dx11.context->lpVtbl->OMSetBlendState(
        g_dx11.context,
        g_dx11.blend_alpha,
        blend_factor,
        sample_mask);
    g_dx11.context->lpVtbl->RSSetState(
        g_dx11.context,
        g_dx11.rs_solid);
    g_dx11.context->lpVtbl->OMSetDepthStencilState(
        g_dx11.context,
        g_dx11.ds_default,
        0);
}

static void dx11_cmd_set_texture(const uint8_t* payload)
{
    (void)payload;
    /* Texture binding will be added once the IR carries texture IDs. */
}

static void dx11_cmd_draw_sprites(const uint8_t* payload, size_t payload_size)
{
    dx11_sprite_vertex_t verts[6];
    D3D11_MAPPED_SUBRESOURCE map;
    ID3D11Buffer* vb;
    UINT stride;
    UINT offset;

    (void)payload;
    (void)payload_size;
    if (!g_dx11.context || !g_dx11.vb_sprite) {
        return;
    }

    /* Simple quad centered at origin in clip space. */
    verts[0].x = -0.5f; verts[0].y = -0.5f; verts[0].z = 0.0f;
    verts[0].u = 0.0f;  verts[0].v = 1.0f;  verts[0].color = 0xffffffffu;
    verts[1].x = -0.5f; verts[1].y =  0.5f; verts[1].z = 0.0f;
    verts[1].u = 0.0f;  verts[1].v = 0.0f;  verts[1].color = 0xffffffffu;
    verts[2].x =  0.5f; verts[2].y =  0.5f; verts[2].z = 0.0f;
    verts[2].u = 1.0f;  verts[2].v = 0.0f;  verts[2].color = 0xffffffffu;

    verts[3] = verts[0];
    verts[4] = verts[2];
    verts[5].x =  0.5f; verts[5].y = -0.5f; verts[5].z = 0.0f;
    verts[5].u = 1.0f;  verts[5].v = 1.0f;  verts[5].color = 0xffffffffu;

    if (FAILED(g_dx11.context->lpVtbl->Map(
            g_dx11.context,
            (ID3D11Resource*)g_dx11.vb_sprite,
            0,
            D3D11_MAP_WRITE_DISCARD,
            0,
            &map))) {
        return;
    }

    memcpy(map.pData, verts, sizeof(verts));

    g_dx11.context->lpVtbl->Unmap(
        g_dx11.context,
        (ID3D11Resource*)g_dx11.vb_sprite,
        0);

    vb = g_dx11.vb_sprite;
    stride = (UINT)sizeof(dx11_sprite_vertex_t);
    offset = 0u;

    g_dx11.context->lpVtbl->IASetInputLayout(g_dx11.context, g_dx11.il_sprite);
    g_dx11.context->lpVtbl->IASetVertexBuffers(
        g_dx11.context,
        0,
        1,
        &vb,
        &stride,
        &offset);
    g_dx11.context->lpVtbl->IASetPrimitiveTopology(
        g_dx11.context,
        D3D11_PRIMITIVE_TOPOLOGY_TRIANGLELIST);

    g_dx11.context->lpVtbl->VSSetShader(
        g_dx11.context,
        g_dx11.vs_sprite,
        NULL,
        0);
    g_dx11.context->lpVtbl->PSSetShader(
        g_dx11.context,
        g_dx11.ps_sprite,
        NULL,
        0);

    g_dx11.context->lpVtbl->Draw(
        g_dx11.context,
        6,
        0);
}

static void dx11_cmd_draw_lines(const uint8_t* payload, size_t payload_size)
{
    dx11_lines_header_t header;
    const dx11_line_vertex_t* src;
    UINT count;
    UINT max_count;
    D3D11_MAPPED_SUBRESOURCE map;
    ID3D11Buffer* vb;
    UINT stride;
    UINT offset;
    D3D11_BUFFER_DESC vb_desc;

    if (!g_dx11.context || !g_dx11.vb_sprite || !payload) {
        return;
    }
    if (payload_size < sizeof(header)) {
        return;
    }

    memcpy(&header, payload, sizeof(header));
    src = (const dx11_line_vertex_t*)(payload + sizeof(header));
    if (header.vertex_count == 0u) {
        return;
    }
    if (payload_size < sizeof(header) + ((size_t)header.vertex_count * sizeof(dx11_line_vertex_t))) {
        return;
    }

    vb = g_dx11.vb_sprite;
    g_dx11.vb_sprite->lpVtbl->GetDesc(g_dx11.vb_sprite, &vb_desc);
    stride = (UINT)sizeof(dx11_line_vertex_t);
    max_count = vb_desc.ByteWidth / stride;
    count = (header.vertex_count > max_count) ? max_count : header.vertex_count;
    if (count == 0u) {
        return;
    }

    if (FAILED(g_dx11.context->lpVtbl->Map(
            g_dx11.context,
            (ID3D11Resource*)vb,
            0,
            D3D11_MAP_WRITE_DISCARD,
            0,
            &map))) {
        return;
    }

    memcpy(map.pData, src, (size_t)count * sizeof(dx11_line_vertex_t));

    g_dx11.context->lpVtbl->Unmap(
        g_dx11.context,
        (ID3D11Resource*)vb,
        0);

    offset = 0u;
    g_dx11.context->lpVtbl->IASetInputLayout(g_dx11.context, g_dx11.il_sprite);
    g_dx11.context->lpVtbl->IASetVertexBuffers(
        g_dx11.context,
        0,
        1,
        &vb,
        &stride,
        &offset);
    g_dx11.context->lpVtbl->IASetPrimitiveTopology(
        g_dx11.context,
        D3D11_PRIMITIVE_TOPOLOGY_LINELIST);

    g_dx11.context->lpVtbl->VSSetShader(
        g_dx11.context,
        g_dx11.vs_sprite,
        NULL,
        0);
    g_dx11.context->lpVtbl->PSSetShader(
        g_dx11.context,
        g_dx11.ps_sprite,
        NULL,
        0);

    g_dx11.context->lpVtbl->Draw(
        g_dx11.context,
        count,
        0);
}

static void dx11_cmd_draw_meshes(const uint8_t* payload, size_t payload_size)
{
    (void)payload;
    (void)payload_size;
    /* Mesh rendering is stubbed until the IR is finalized. */
}

static void dx11_cmd_draw_text(const uint8_t* payload, size_t payload_size)
{
    (void)payload;
    (void)payload_size;
    /* Text rendering is not implemented in the DX11 backend MVP. */
}

static void dx11_execute(const dgfx_cmd_buffer* cmd_buf)
{
    const uint8_t* ptr;
    const uint8_t* end;
    size_t header_size;

    if (!cmd_buf || !cmd_buf->data || cmd_buf->size == 0u) {
        return;
    }
    if (!g_dx11.device || !g_dx11.context) {
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
            dx11_cmd_clear(payload, payload_size);
            break;
        case DGFX_CMD_SET_VIEWPORT:
            dx11_cmd_set_viewport(payload);
            break;
        case DGFX_CMD_SET_CAMERA:
            dx11_cmd_set_camera(payload);
            break;
        case DGFX_CMD_SET_PIPELINE:
            dx11_cmd_set_pipeline(payload);
            break;
        case DGFX_CMD_SET_TEXTURE:
            dx11_cmd_set_texture(payload);
            break;
        case DGFX_CMD_DRAW_SPRITES:
            dx11_cmd_draw_sprites(payload, payload_size);
            break;
        case DGFX_CMD_DRAW_MESHES:
            dx11_cmd_draw_meshes(payload, payload_size);
            break;
        case DGFX_CMD_DRAW_LINES:
            dx11_cmd_draw_lines(payload, payload_size);
            break;
        case DGFX_CMD_DRAW_TEXT:
            dx11_cmd_draw_text(payload, payload_size);
            break;
        default:
            break;
        }

        ptr += total_size;
    }
}
