#include "metal_gfx.h"

/* Objective-C++ implementations live in metal_backend.mm */
bool      metal_backend_init(const dgfx_desc* desc);
void      metal_backend_shutdown(void);
dgfx_caps metal_backend_get_caps(void);
void      metal_backend_resize(int width, int height);
void      metal_backend_begin_frame(void);
void      metal_backend_execute(const dgfx_cmd_buffer* cmd);
void      metal_backend_end_frame(void);

metal_state_t g_metal;

static bool      metal_init(const dgfx_desc* desc)         { return metal_backend_init(desc); }
static void      metal_shutdown(void)                      { metal_backend_shutdown(); }
static dgfx_caps metal_get_caps(void)                      { return metal_backend_get_caps(); }
static void      metal_resize(int width, int height)       { metal_backend_resize(width, height); }
static void      metal_begin_frame(void)                   { metal_backend_begin_frame(); }
static void      metal_execute(const dgfx_cmd_buffer* cmd) { metal_backend_execute(cmd); }
static void      metal_end_frame(void)                     { metal_backend_end_frame(); }

static const dgfx_backend_vtable g_metal_vtable = {
    metal_init,
    metal_shutdown,
    metal_get_caps,
    metal_resize,
    metal_begin_frame,
    metal_execute,
    metal_end_frame
};

const dgfx_backend_vtable* dgfx_metal_get_vtable(void)
{
    return &g_metal_vtable;
}
