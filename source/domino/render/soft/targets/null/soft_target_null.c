#include "../../soft_internal.h"

static int null_init(domino_sys_context* sys, int width, int height, domino_pixfmt fmt, void** out_state)
{
    (void)sys; (void)width; (void)height; (void)fmt; (void)out_state;
    return 0;
}

static void null_shutdown(void* state)
{
    (void)state;
}

static int null_present(void* state, const void* pixels, int width, int height, int stride_bytes)
{
    (void)state; (void)pixels; (void)width; (void)height; (void)stride_bytes;
    return 0;
}

static const domino_soft_target_ops g_null_target = {
    "null",
    null_init,
    null_shutdown,
    null_present
};

const domino_soft_target_ops* domino_soft_target_null(void)
{
    return &g_null_target;
}
