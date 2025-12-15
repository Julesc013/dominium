#include "d_gfx_null.h"

static int d_gfx_null_init(void)
{
    return 0;
}

static void d_gfx_null_shutdown(void)
{
}

static void d_gfx_null_submit(const d_gfx_cmd_buffer* buf)
{
    (void)buf;
}

static void d_gfx_null_present(void)
{
}

static d_gfx_backend_soft g_null_backend = {
    d_gfx_null_init,
    d_gfx_null_shutdown,
    d_gfx_null_submit,
    d_gfx_null_present
};

const d_gfx_backend_soft* d_gfx_null_register_backend(void)
{
    return &g_null_backend;
}

