#include "domino/gfx.h"
#include "soft_gfx.h"

/* Thin wrappers that currently route unimplemented backends to the reference
 * software renderer. This preserves IR semantics for all opcodes while the
 * hardware-specific paths are brought up later. */

/* Windows and platform-specific backends */
#ifndef DOMINIUM_GFX_DX7
const dgfx_backend_vtable *dgfx_dx7_get_vtable(void)     { return dgfx_soft_get_vtable(); }
#endif
#ifndef DOMINIUM_GFX_DX9
const dgfx_backend_vtable *dgfx_dx9_get_vtable(void)     { return dgfx_soft_get_vtable(); }
#endif
#ifndef DOMINIUM_GFX_DX11
const dgfx_backend_vtable *dgfx_dx11_get_vtable(void)    { return dgfx_soft_get_vtable(); }
#endif
#ifndef DOMINIUM_GFX_GDI
const dgfx_backend_vtable *dgfx_gdi_get_vtable(void)     { return dgfx_soft_get_vtable(); }
#endif
#ifndef DGFX_HAS_VK1
const dgfx_backend_vtable *dgfx_vk1_get_vtable(void)     { return dgfx_soft_get_vtable(); }
#endif
#ifndef DOMINIUM_GFX_QUICKDRAW
const dgfx_backend_vtable *dgfx_quickdraw_get_vtable(void) { return dgfx_soft_get_vtable(); }
#endif
#ifndef DOMINIUM_GFX_QUARTZ
const dgfx_backend_vtable *dgfx_quartz_get_vtable(void)  { return dgfx_soft_get_vtable(); }
#endif
#ifndef DOMINIUM_GFX_METAL
const dgfx_backend_vtable *dgfx_metal_get_vtable(void)   { return dgfx_soft_get_vtable(); }
#endif

const dgfx_backend_vtable *dgfx_gl1_get_vtable(void)      { return dgfx_soft_get_vtable(); }
const dgfx_backend_vtable *dgfx_x11_get_vtable(void)      { return dgfx_soft_get_vtable(); }
const dgfx_backend_vtable *dgfx_cocoa_get_vtable(void)    { return dgfx_soft_get_vtable(); }
const dgfx_backend_vtable *dgfx_sdl1_get_vtable(void)     { return dgfx_soft_get_vtable(); }
const dgfx_backend_vtable *dgfx_sdl2_get_vtable(void)     { return dgfx_soft_get_vtable(); }
const dgfx_backend_vtable *dgfx_wayland_get_vtable(void)  { return dgfx_soft_get_vtable(); }
const dgfx_backend_vtable *dgfx_null_get_vtable(void)     { return dgfx_soft_get_vtable(); }
