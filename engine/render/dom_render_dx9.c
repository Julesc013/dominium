#define COBJMACROS
#ifndef WIN32_LEAN_AND_MEAN
#define WIN32_LEAN_AND_MEAN
#endif
#include <windows.h>
#include <d3d9.h>
#include <stdlib.h>
#include <string.h>

#include "dom_render_dx9.h"

typedef struct DomRenderDX9State {
    IDirect3D9 *d3d;
    IDirect3DDevice9 *device;
    D3DPRESENT_PARAMETERS pp;
} DomRenderDX9State;

typedef struct DomDX9Vertex {
    float x;
    float y;
    float z;
    float rhw;
    D3DCOLOR color;
} DomDX9Vertex;

#define DOM_DX9_FVF (D3DFVF_XYZRHW | D3DFVF_DIFFUSE)

static dom_err_t dom_render_dx9_init(DomRenderer *r)
{
    DomRenderDX9State *st;
    HRESULT hr;
    HWND hwnd;

    if (!r) {
        return DOM_ERR_INVALID_ARG;
    }

    st = (DomRenderDX9State *)malloc(sizeof(DomRenderDX9State));
    if (!st) {
        return DOM_ERR_OUT_OF_MEMORY;
    }
    memset(st, 0, sizeof(*st));

    hwnd = (HWND)r->platform_window;
    st->d3d = Direct3DCreate9(D3D_SDK_VERSION);
    if (!st->d3d) {
        free(st);
        return DOM_ERR_IO;
    }

    memset(&st->pp, 0, sizeof(st->pp));
    st->pp.Windowed = TRUE;
    st->pp.SwapEffect = D3DSWAPEFFECT_DISCARD;
    st->pp.BackBufferFormat = D3DFMT_X8R8G8B8;
    st->pp.BackBufferWidth = r->width;
    st->pp.BackBufferHeight = r->height;
    st->pp.PresentationInterval = D3DPRESENT_INTERVAL_IMMEDIATE;

    hr = IDirect3D9_CreateDevice(
        st->d3d,
        D3DADAPTER_DEFAULT,
        D3DDEVTYPE_HAL,
        hwnd,
        D3DCREATE_SOFTWARE_VERTEXPROCESSING,
        &st->pp,
        &st->device);

    if (FAILED(hr) || !st->device) {
        IDirect3D9_Release(st->d3d);
        free(st);
        return DOM_ERR_IO;
    }

    r->backend_state = st;
    return DOM_OK;
}

static void dom_render_dx9_shutdown(DomRenderer *r)
{
    DomRenderDX9State *st;
    if (!r || !r->backend_state) {
        return;
    }
    st = (DomRenderDX9State *)r->backend_state;
    if (st->device) {
        IDirect3DDevice9_Release(st->device);
    }
    if (st->d3d) {
        IDirect3D9_Release(st->d3d);
    }
    free(st);
    r->backend_state = 0;
}

static void dom_render_dx9_resize(DomRenderer *r, dom_u32 w, dom_u32 h)
{
    DomRenderDX9State *st;
    HRESULT hr;

    if (!r || !r->backend_state) {
        return;
    }

    st = (DomRenderDX9State *)r->backend_state;
    st->pp.BackBufferWidth = w;
    st->pp.BackBufferHeight = h;

    if (!st->device) {
        return;
    }

    hr = IDirect3DDevice9_Reset(st->device, &st->pp);
    if (FAILED(hr)) {
        /* leave device in whatever state it is; caller can recreate */
    }
}

static void dom_dx9_draw_line(IDirect3DDevice9 *dev,
                              float x0, float y0,
                              float x1, float y1,
                              D3DCOLOR color)
{
    DomDX9Vertex verts[2];
    verts[0].x = x0;
    verts[0].y = y0;
    verts[0].z = 0.0f;
    verts[0].rhw = 1.0f;
    verts[0].color = color;

    verts[1].x = x1;
    verts[1].y = y1;
    verts[1].z = 0.0f;
    verts[1].rhw = 1.0f;
    verts[1].color = color;

    IDirect3DDevice9_DrawPrimitiveUP(dev, D3DPT_LINELIST, 1, verts, sizeof(DomDX9Vertex));
}

static void dom_dx9_draw_rect(IDirect3DDevice9 *dev, const DomCmdRect *rc)
{
    float x0 = (float)rc->rect.x;
    float y0 = (float)rc->rect.y;
    float x1 = (float)(rc->rect.x + rc->rect.w);
    float y1 = (float)(rc->rect.y + rc->rect.h);
    D3DCOLOR c = (D3DCOLOR)rc->color;

    dom_dx9_draw_line(dev, x0, y0, x1, y0, c);
    dom_dx9_draw_line(dev, x1, y0, x1, y1, c);
    dom_dx9_draw_line(dev, x1, y1, x0, y1, c);
    dom_dx9_draw_line(dev, x0, y1, x0, y0, c);
}

static void dom_dx9_draw_poly(IDirect3DDevice9 *dev, const DomCmdPoly *poly)
{
    dom_u32 i;
    if (poly->count < 2) {
        return;
    }
    for (i = 0; i < poly->count; ++i) {
        DomVec2i a = poly->pts[i];
        DomVec2i b = poly->pts[(i + 1u) % poly->count];
        dom_dx9_draw_line(dev, (float)a.x, (float)a.y, (float)b.x, (float)b.y, (D3DCOLOR)poly->color);
    }
}

static void dom_render_dx9_submit(DomRenderer *r, const DomRenderCommandBuffer *cb)
{
    DomRenderDX9State *st;
    dom_u32 i;

    if (!r || !cb || !r->backend_state) {
        return;
    }

    st = (DomRenderDX9State *)r->backend_state;
    if (!st->device) {
        return;
    }

    IDirect3DDevice9_Clear(st->device, 0, NULL, D3DCLEAR_TARGET, (D3DCOLOR)r->state.clear_color, 1.0f, 0);

    if (FAILED(IDirect3DDevice9_BeginScene(st->device))) {
        return;
    }

    IDirect3DDevice9_SetFVF(st->device, DOM_DX9_FVF);

    for (i = 0; i < cb->count; ++i) {
        const DomRenderCmd *cmd = &cb->cmds[i];
        switch (cmd->kind) {
        case DOM_CMD_LINE:
            dom_dx9_draw_line(st->device,
                              (float)cmd->u.line.x0, (float)cmd->u.line.y0,
                              (float)cmd->u.line.x1, (float)cmd->u.line.y1,
                              (D3DCOLOR)cmd->u.line.color);
            break;
        case DOM_CMD_RECT:
            dom_dx9_draw_rect(st->device, &cmd->u.rect);
            break;
        case DOM_CMD_POLY:
            dom_dx9_draw_poly(st->device, &cmd->u.poly);
            break;
        default:
            /* Unsupported command types are ignored in the MVP */
            break;
        }
    }

    IDirect3DDevice9_EndScene(st->device);
}

static void dom_render_dx9_present(DomRenderer *r)
{
    DomRenderDX9State *st;
    if (!r || !r->backend_state) {
        return;
    }
    st = (DomRenderDX9State *)r->backend_state;
    if (!st->device) {
        return;
    }
    IDirect3DDevice9_Present(st->device, NULL, NULL, NULL, NULL);
}

static const DomRenderBackendAPI g_dom_render_dx9 = {
    dom_render_dx9_init,
    dom_render_dx9_shutdown,
    dom_render_dx9_resize,
    dom_render_dx9_submit,
    dom_render_dx9_present
};

const DomRenderBackendAPI *dom_render_backend_dx9(void)
{
    return &g_dom_render_dx9;
}
