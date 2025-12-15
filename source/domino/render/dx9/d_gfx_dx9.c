#include "d_gfx_dx9.h"

#include "../d_gfx_internal.h"

#if defined(_WIN32)

#define CINTERFACE
#define COBJMACROS
#include <windows.h>
#include <d3d9.h>

#include <string.h>

typedef struct d_gfx_dx9_state_s {
    HWND hwnd;
    IDirect3D9* d3d;
    IDirect3DDevice9* dev;
    D3DPRESENT_PARAMETERS pp;
    int last_w;
    int last_h;
} d_gfx_dx9_state;

typedef struct d_gfx_dx9_tl_vertex_s {
    float x;
    float y;
    float z;
    float rhw;
    D3DCOLOR diffuse;
} d_gfx_dx9_tl_vertex;

#define D_GFX_DX9_FVF (D3DFVF_XYZRHW | D3DFVF_DIFFUSE)

static d_gfx_dx9_state g_dx9;

static D3DCOLOR d_gfx_dx9_pack_color(const d_gfx_color* c)
{
    if (!c) {
        return (D3DCOLOR)0xff000000u;
    }
    return (D3DCOLOR)(((u32)c->a << 24) | ((u32)c->r << 16) | ((u32)c->g << 8) | ((u32)c->b));
}

static void d_gfx_dx9_set_viewport(const d_gfx_viewport* vp);

static int d_gfx_dx9_get_client_size(HWND hwnd, int* out_w, int* out_h)
{
    RECT rc;
    int w;
    int h;

    if (!hwnd || !out_w || !out_h) {
        return 0;
    }

    if (!GetClientRect(hwnd, &rc)) {
        return 0;
    }

    w = (int)(rc.right - rc.left);
    h = (int)(rc.bottom - rc.top);
    if (w <= 0 || h <= 0) {
        return 0;
    }

    *out_w = w;
    *out_h = h;
    return 1;
}

static void d_gfx_dx9_apply_state(void)
{
    if (!g_dx9.dev) {
        return;
    }

    IDirect3DDevice9_SetRenderState(g_dx9.dev, D3DRS_LIGHTING, FALSE);
    IDirect3DDevice9_SetRenderState(g_dx9.dev, D3DRS_CULLMODE, D3DCULL_NONE);
    IDirect3DDevice9_SetRenderState(g_dx9.dev, D3DRS_ZENABLE, D3DZB_FALSE);
    IDirect3DDevice9_SetRenderState(g_dx9.dev, D3DRS_ALPHABLENDENABLE, FALSE);
    IDirect3DDevice9_SetRenderState(g_dx9.dev, D3DRS_SCISSORTESTENABLE, TRUE);
    IDirect3DDevice9_SetTexture(g_dx9.dev, 0, (IDirect3DBaseTexture9*)0);
    IDirect3DDevice9_SetFVF(g_dx9.dev, (DWORD)D_GFX_DX9_FVF);

    if (g_dx9.last_w > 0 && g_dx9.last_h > 0) {
        d_gfx_viewport vp;
        vp.x = 0;
        vp.y = 0;
        vp.w = (i32)g_dx9.last_w;
        vp.h = (i32)g_dx9.last_h;
        d_gfx_dx9_set_viewport(&vp);
    }
}

static int d_gfx_dx9_reset(int w, int h)
{
    HRESULT hr;

    if (!g_dx9.dev) {
        return 0;
    }
    if (w <= 0 || h <= 0) {
        return 0;
    }

    g_dx9.pp.BackBufferWidth = (UINT)w;
    g_dx9.pp.BackBufferHeight = (UINT)h;

    hr = IDirect3DDevice9_Reset(g_dx9.dev, &g_dx9.pp);
    if (FAILED(hr)) {
        return 0;
    }

    g_dx9.last_w = w;
    g_dx9.last_h = h;
    d_gfx_dx9_apply_state();
    return 1;
}

static void d_gfx_dx9_set_viewport(const d_gfx_viewport* vp)
{
    D3DVIEWPORT9 d3d_vp;
    RECT sc;

    if (!g_dx9.dev || !vp) {
        return;
    }

    if (vp->w <= 0 || vp->h <= 0) {
        return;
    }

    d3d_vp.X = (DWORD)vp->x;
    d3d_vp.Y = (DWORD)vp->y;
    d3d_vp.Width = (DWORD)vp->w;
    d3d_vp.Height = (DWORD)vp->h;
    d3d_vp.MinZ = 0.0f;
    d3d_vp.MaxZ = 1.0f;

    sc.left = vp->x;
    sc.top = vp->y;
    sc.right = vp->x + vp->w;
    sc.bottom = vp->y + vp->h;

    IDirect3DDevice9_SetViewport(g_dx9.dev, &d3d_vp);
    IDirect3DDevice9_SetScissorRect(g_dx9.dev, &sc);
}

static void d_gfx_dx9_draw_rect(const d_gfx_draw_rect_cmd* rc)
{
    const float half = -0.5f;
    const int x0i = rc ? rc->x : 0;
    const int y0i = rc ? rc->y : 0;
    const int x1i = rc ? (rc->x + rc->w) : 0;
    const int y1i = rc ? (rc->y + rc->h) : 0;
    const float x0 = (float)x0i + half;
    const float y0 = (float)y0i + half;
    const float x1 = (float)x1i + half;
    const float y1 = (float)y1i + half;
    const D3DCOLOR c = d_gfx_dx9_pack_color(rc ? &rc->color : (const d_gfx_color*)0);
    d_gfx_dx9_tl_vertex v[6];

    if (!g_dx9.dev || !rc) {
        return;
    }
    if (rc->w <= 0 || rc->h <= 0) {
        return;
    }

    v[0].x = x0; v[0].y = y0; v[0].z = 0.0f; v[0].rhw = 1.0f; v[0].diffuse = c;
    v[1].x = x1; v[1].y = y0; v[1].z = 0.0f; v[1].rhw = 1.0f; v[1].diffuse = c;
    v[2].x = x1; v[2].y = y1; v[2].z = 0.0f; v[2].rhw = 1.0f; v[2].diffuse = c;

    v[3].x = x0; v[3].y = y0; v[3].z = 0.0f; v[3].rhw = 1.0f; v[3].diffuse = c;
    v[4].x = x1; v[4].y = y1; v[4].z = 0.0f; v[4].rhw = 1.0f; v[4].diffuse = c;
    v[5].x = x0; v[5].y = y1; v[5].z = 0.0f; v[5].rhw = 1.0f; v[5].diffuse = c;

    (void)IDirect3DDevice9_DrawPrimitiveUP(g_dx9.dev,
                                          D3DPT_TRIANGLELIST,
                                          2,
                                          (const void*)v,
                                          (UINT)sizeof(d_gfx_dx9_tl_vertex));
}

static void d_gfx_dx9_stub_text(const d_gfx_draw_text_cmd* text)
{
    d_gfx_draw_rect_cmd r;
    size_t len;

    if (!text) {
        return;
    }

    len = text->text ? strlen(text->text) : 0u;
    r.x = text->x;
    r.y = text->y;
    r.w = (i32)(len ? (len * 8u) : 8u);
    r.h = 12;
    r.color = text->color;
    d_gfx_dx9_draw_rect(&r);
}

static int d_gfx_dx9_init(void)
{
    HRESULT hr;
    int w;
    int h;

    memset(&g_dx9, 0, sizeof(g_dx9));

    g_dx9.hwnd = (HWND)d_gfx_get_native_window();
    if (!g_dx9.hwnd) {
        return -1;
    }

    if (!d_gfx_dx9_get_client_size(g_dx9.hwnd, &w, &h)) {
        return -2;
    }

    g_dx9.d3d = Direct3DCreate9(D3D_SDK_VERSION);
    if (!g_dx9.d3d) {
        return -3;
    }

    memset(&g_dx9.pp, 0, sizeof(g_dx9.pp));
    g_dx9.pp.Windowed = TRUE;
    g_dx9.pp.SwapEffect = D3DSWAPEFFECT_DISCARD;
    g_dx9.pp.hDeviceWindow = g_dx9.hwnd;
    g_dx9.pp.BackBufferWidth = (UINT)w;
    g_dx9.pp.BackBufferHeight = (UINT)h;
    g_dx9.pp.BackBufferFormat = D3DFMT_UNKNOWN;
    g_dx9.pp.PresentationInterval = D3DPRESENT_INTERVAL_IMMEDIATE;

    hr = IDirect3D9_CreateDevice(g_dx9.d3d,
                                 D3DADAPTER_DEFAULT,
                                 D3DDEVTYPE_HAL,
                                 g_dx9.hwnd,
                                 D3DCREATE_SOFTWARE_VERTEXPROCESSING,
                                 &g_dx9.pp,
                                 &g_dx9.dev);
    if (FAILED(hr) || !g_dx9.dev) {
        IDirect3D9_Release(g_dx9.d3d);
        memset(&g_dx9, 0, sizeof(g_dx9));
        return -4;
    }

    g_dx9.last_w = w;
    g_dx9.last_h = h;
    d_gfx_dx9_apply_state();
    return 0;
}

static void d_gfx_dx9_shutdown(void)
{
    if (g_dx9.dev) {
        IDirect3DDevice9_Release(g_dx9.dev);
    }
    if (g_dx9.d3d) {
        IDirect3D9_Release(g_dx9.d3d);
    }
    memset(&g_dx9, 0, sizeof(g_dx9));
}

static void d_gfx_dx9_submit(const d_gfx_cmd_buffer* buf)
{
    HRESULT hr;
    u32 i;

    if (!g_dx9.dev) {
        return;
    }

    hr = IDirect3DDevice9_BeginScene(g_dx9.dev);
    if (FAILED(hr)) {
        return;
    }

    if (buf && buf->cmds) {
        for (i = 0u; i < buf->count; ++i) {
            const d_gfx_cmd* cmd = buf->cmds + i;
            switch (cmd->opcode) {
            case D_GFX_OP_CLEAR: {
                const D3DCOLOR c = d_gfx_dx9_pack_color(&cmd->u.clear.color);
                (void)IDirect3DDevice9_Clear(g_dx9.dev, 0, (const D3DRECT*)0, D3DCLEAR_TARGET, c, 1.0f, 0u);
                break;
            }
            case D_GFX_OP_SET_VIEWPORT:
                d_gfx_dx9_set_viewport(&cmd->u.viewport.vp);
                break;
            case D_GFX_OP_SET_CAMERA:
                /* ignored in minimal slice */
                break;
            case D_GFX_OP_DRAW_RECT:
                d_gfx_dx9_draw_rect(&cmd->u.rect);
                break;
            case D_GFX_OP_DRAW_TEXT:
                d_gfx_dx9_stub_text(&cmd->u.text);
                break;
            default:
                break;
            }
        }
    }

    (void)IDirect3DDevice9_EndScene(g_dx9.dev);
}

static void d_gfx_dx9_present(void)
{
    HRESULT hr;
    int w;
    int h;

    if (!g_dx9.dev || !g_dx9.hwnd) {
        return;
    }

    if (d_gfx_dx9_get_client_size(g_dx9.hwnd, &w, &h)) {
        if (w != g_dx9.last_w || h != g_dx9.last_h) {
            (void)d_gfx_dx9_reset(w, h);
        }
    }

    hr = IDirect3DDevice9_Present(g_dx9.dev, (const RECT*)0, (const RECT*)0, (HWND)0, (const RGNDATA*)0);
    if (FAILED(hr)) {
        HRESULT cl = IDirect3DDevice9_TestCooperativeLevel(g_dx9.dev);
        if (cl == D3DERR_DEVICENOTRESET) {
            if (d_gfx_dx9_get_client_size(g_dx9.hwnd, &w, &h)) {
                (void)d_gfx_dx9_reset(w, h);
            }
        }
    }
}

static d_gfx_backend_soft g_dx9_backend = {
    d_gfx_dx9_init,
    d_gfx_dx9_shutdown,
    d_gfx_dx9_submit,
    d_gfx_dx9_present
};

const d_gfx_backend_soft* d_gfx_dx9_register_backend(void)
{
    return &g_dx9_backend;
}

#else /* _WIN32 */

const d_gfx_backend_soft* d_gfx_dx9_register_backend(void)
{
    return (const d_gfx_backend_soft*)0;
}

#endif /* _WIN32 */
