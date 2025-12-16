/*
FILE: source/domino/render/dx11/d_gfx_dx11.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / render/dx11/d_gfx_dx11
RESPONSIBILITY: Implements `d_gfx_dx11`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include "d_gfx_dx11.h"

#include "../d_gfx_internal.h"

#ifndef WIN32_LEAN_AND_MEAN
#define WIN32_LEAN_AND_MEAN
#endif

#include <windows.h>
#include <d3d11.h>
#include <dxgi.h>
#include <d3dcompiler.h>

static int d_gfx_dx11_init(void)
{
    return d_gfx_get_native_window() ? 1 : 0;
}

static void d_gfx_dx11_shutdown(void)
{
}

static void d_gfx_dx11_submit(const d_gfx_cmd_buffer* buf)
{
    (void)buf;
}

static void d_gfx_dx11_present(void)
{
}

static d_gfx_backend_soft g_dx11_backend = {
    d_gfx_dx11_init,
    d_gfx_dx11_shutdown,
    d_gfx_dx11_submit,
    d_gfx_dx11_present
};

const d_gfx_backend_soft* d_gfx_dx11_register_backend(void)
{
    return &g_dx11_backend;
}

