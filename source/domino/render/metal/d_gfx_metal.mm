#include "d_gfx_metal.h"

#import <Metal/Metal.h>

static int d_gfx_metal_init(void)
{
    id<MTLDevice> device;
    device = MTLCreateSystemDefaultDevice();
    return device ? 1 : 0;
}

static void d_gfx_metal_shutdown(void)
{
}

static void d_gfx_metal_submit(const d_gfx_cmd_buffer* buf)
{
    (void)buf;
}

static void d_gfx_metal_present(void)
{
}

static d_gfx_backend_soft g_metal_backend = {
    d_gfx_metal_init,
    d_gfx_metal_shutdown,
    d_gfx_metal_submit,
    d_gfx_metal_present
};

const d_gfx_backend_soft* d_gfx_metal_register_backend(void)
{
    return &g_metal_backend;
}

