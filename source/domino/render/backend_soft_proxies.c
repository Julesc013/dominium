#include "domino/gfx.h"
#include "soft_gfx.h"

/* Thin wrappers that currently route unimplemented backends to the reference
 * software renderer. This preserves IR semantics for all opcodes while the
 * hardware-specific paths are brought up later. */

const dgfx_backend_vtable *dgfx_gl1_get_vtable(void)      { return dgfx_soft_get_vtable(); }
const dgfx_backend_vtable *dgfx_x11_get_vtable(void)      { return dgfx_soft_get_vtable(); }
const dgfx_backend_vtable *dgfx_cocoa_get_vtable(void)    { return dgfx_soft_get_vtable(); }
const dgfx_backend_vtable *dgfx_sdl1_get_vtable(void)     { return dgfx_soft_get_vtable(); }
const dgfx_backend_vtable *dgfx_sdl2_get_vtable(void)     { return dgfx_soft_get_vtable(); }
const dgfx_backend_vtable *dgfx_wayland_get_vtable(void)  { return dgfx_soft_get_vtable(); }
const dgfx_backend_vtable *dgfx_null_get_vtable(void)     { return dgfx_soft_get_vtable(); }
