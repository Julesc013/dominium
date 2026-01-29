/*
FILE: source/domino/render/stub/d_gfx_stub.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / render/stub/d_gfx_stub
RESPONSIBILITY: Implements soft-backed renderer stubs for GPU/back-compat backends.
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: Deterministic: stubs delegate to software backend.
VERSIONING / ABI / DATA FORMAT NOTES: Internal only.
EXTENSION POINTS: Replace stub backends with real GPU backends behind same contract.
*/
#include "render/stub/d_gfx_stub.h"
#include "soft/d_gfx_soft.h"

static const d_gfx_backend_soft* d_gfx_stub_soft_backend(void)
{
    return d_gfx_soft_register_backend();
}

static int d_gfx_stub_init(void)
{
    const d_gfx_backend_soft* soft = d_gfx_stub_soft_backend();
    if (!soft || !soft->init) {
        return -1;
    }
    return soft->init();
}

static void d_gfx_stub_shutdown(void)
{
    const d_gfx_backend_soft* soft = d_gfx_stub_soft_backend();
    if (soft && soft->shutdown) {
        soft->shutdown();
    }
}

static void d_gfx_stub_submit(const d_gfx_cmd_buffer* buf)
{
    const d_gfx_backend_soft* soft = d_gfx_stub_soft_backend();
    if (soft && soft->submit_cmd_buffer) {
        soft->submit_cmd_buffer(buf);
    }
}

static void d_gfx_stub_present(void)
{
    const d_gfx_backend_soft* soft = d_gfx_stub_soft_backend();
    if (soft && soft->present) {
        soft->present();
    }
}

#define DEFINE_STUB_BACKEND(name)               \
    static d_gfx_backend_soft g_stub_##name = { \
        d_gfx_stub_init,                        \
        d_gfx_stub_shutdown,                    \
        d_gfx_stub_submit,                      \
        d_gfx_stub_present                      \
    };

DEFINE_STUB_BACKEND(dx7)
DEFINE_STUB_BACKEND(dx9)
DEFINE_STUB_BACKEND(dx11)
DEFINE_STUB_BACKEND(gl2)
DEFINE_STUB_BACKEND(vk1)
DEFINE_STUB_BACKEND(metal)
DEFINE_STUB_BACKEND(vesa)
DEFINE_STUB_BACKEND(vga)

#undef DEFINE_STUB_BACKEND

const d_gfx_backend_soft* d_gfx_stub_register_dx7(void)   { return &g_stub_dx7; }
const d_gfx_backend_soft* d_gfx_stub_register_dx9(void)   { return &g_stub_dx9; }
const d_gfx_backend_soft* d_gfx_stub_register_dx11(void)  { return &g_stub_dx11; }
const d_gfx_backend_soft* d_gfx_stub_register_gl2(void)   { return &g_stub_gl2; }
const d_gfx_backend_soft* d_gfx_stub_register_vk1(void)   { return &g_stub_vk1; }
const d_gfx_backend_soft* d_gfx_stub_register_metal(void) { return &g_stub_metal; }
const d_gfx_backend_soft* d_gfx_stub_register_vesa(void)  { return &g_stub_vesa; }
const d_gfx_backend_soft* d_gfx_stub_register_vga(void)   { return &g_stub_vga; }

int d_gfx_stub_uses_soft(const d_gfx_backend_soft* backend)
{
    if (!backend) {
        return 0;
    }
    if (backend == d_gfx_soft_register_backend()) {
        return 1;
    }
    return backend == &g_stub_dx7 ||
           backend == &g_stub_dx9 ||
           backend == &g_stub_dx11 ||
           backend == &g_stub_gl2 ||
           backend == &g_stub_vk1 ||
           backend == &g_stub_metal ||
           backend == &g_stub_vesa ||
           backend == &g_stub_vga;
}
