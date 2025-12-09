#ifndef DOMINIUM_DX7_GFX_H
#define DOMINIUM_DX7_GFX_H

#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <ddraw.h>
#include <d3d.h>
#include <stdint.h>

#include "domino/gfx.h"
#include "domino/canvas.h"

typedef struct dx7_state_t {
    HWND                 hwnd;
    HINSTANCE            hinstance;

    LPDIRECTDRAW7        dd;
    LPDIRECTDRAWSURFACE7 primary;
    LPDIRECTDRAWSURFACE7 backbuffer;
    LPDIRECTDRAWCLIPPER  clipper;

    LPDIRECT3D7          d3d;
    LPDIRECT3DDEVICE7    d3d_device;
    LPDIRECT3DVIEWPORT3  viewport;

    int                  width;
    int                  height;
    int                  fullscreen;

    dgfx_caps            caps;
} dx7_state_t;

extern dx7_state_t g_dx7;

const dgfx_backend_vtable* dgfx_dx7_get_vtable(void);

#endif /* DOMINIUM_DX7_GFX_H */
