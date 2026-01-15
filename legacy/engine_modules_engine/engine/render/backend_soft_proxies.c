/*
FILE: source/domino/render/backend_soft_proxies.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / render/backend_soft_proxies
RESPONSIBILITY: Implements `backend_soft_proxies`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
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
