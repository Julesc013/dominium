#include "d_gfx_gl2.h"

#include "../d_gfx_internal.h"

#ifndef WIN32_LEAN_AND_MEAN
#define WIN32_LEAN_AND_MEAN
#endif

#include <windows.h>
#include <GL/gl.h>

static int d_gfx_gl2_init(void)
{
    return d_gfx_get_native_window() ? 1 : 0;
}

static void d_gfx_gl2_shutdown(void)
{
}

static void d_gfx_gl2_submit(const d_gfx_cmd_buffer* buf)
{
    (void)buf;
}

static void d_gfx_gl2_present(void)
{
}

static d_gfx_backend_soft g_gl2_backend = {
    d_gfx_gl2_init,
    d_gfx_gl2_shutdown,
    d_gfx_gl2_submit,
    d_gfx_gl2_present
};

const d_gfx_backend_soft* d_gfx_gl2_register_backend(void)
{
    return &g_gl2_backend;
}

