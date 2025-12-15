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

