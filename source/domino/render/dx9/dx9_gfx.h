/*
FILE: source/domino/render/dx9/dx9_gfx.h
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
