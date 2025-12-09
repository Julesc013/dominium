#ifndef DOMINIUM_DX11_GFX_H
#define DOMINIUM_DX11_GFX_H

#include <windows.h>
#include <d3d11.h>
#include <dxgi.h>
#include <stdint.h>

#include "domino/gfx.h"
#include "domino/canvas.h"

/* DX11 renderer state */
typedef struct dx11_state_t {
    HWND                 hwnd;
    HINSTANCE            hinstance;

    IDXGISwapChain*      swap_chain;
    ID3D11Device*        device;
    ID3D11DeviceContext* context;

    ID3D11RenderTargetView* rtv;
    ID3D11Texture2D*        depth_tex;
    ID3D11DepthStencilView* dsv;

    int                  width;
    int                  height;
    int                  fullscreen;
    int                  vsync;

    dgfx_caps            caps;

    int                  frame_in_progress;

    ID3D11VertexShader*  vs_sprite;
    ID3D11PixelShader*   ps_sprite;
    ID3D11InputLayout*   il_sprite;
    ID3D11Buffer*        vb_sprite;

    ID3D11VertexShader*  vs_mesh;
    ID3D11PixelShader*   ps_mesh;
    ID3D11InputLayout*   il_mesh;
    ID3D11Buffer*        vb_mesh;
    ID3D11Buffer*        ib_mesh;
    ID3D11Buffer*        cb_camera;

    ID3D11BlendState*      blend_alpha;
    ID3D11RasterizerState* rs_solid;
    ID3D11DepthStencilState* ds_default;

} dx11_state_t;

extern dx11_state_t g_dx11;

const dgfx_backend_vtable* dgfx_dx11_get_vtable(void);

#endif /* DOMINIUM_DX11_GFX_H */
