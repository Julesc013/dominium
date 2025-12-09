#ifndef DOMINIUM_DX9_GFX_H
#define DOMINIUM_DX9_GFX_H

#ifndef WIN32_LEAN_AND_MEAN
#define WIN32_LEAN_AND_MEAN
#endif
#include <windows.h>
#include <d3d9.h>
#include <stdint.h>

#include "domino/gfx.h"
#include "domino/canvas.h"

typedef struct dx9_state_t {
    HWND                  hwnd;
    HINSTANCE             hinstance;

    IDirect3D9*           d3d;
    IDirect3DDevice9*     device;

    D3DPRESENT_PARAMETERS pp;

    int                   width;
    int                   height;
    int                   fullscreen;

    dgfx_caps             caps;

    int                   scene_active;
} dx9_state_t;

extern dx9_state_t g_dx9;

const dgfx_backend_vtable* dgfx_dx9_get_vtable(void);

#endif /* DOMINIUM_DX9_GFX_H */
