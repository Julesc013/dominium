/*
FILE: source/domino/render/metal/metal_gfx.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / render/metal/metal_gfx
RESPONSIBILITY: Implements `metal_gfx`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
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
