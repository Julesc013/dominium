/*
FILE: source/domino/render/stub/d_gfx_stub.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / render/stub/d_gfx_stub
RESPONSIBILITY: Declares soft-backed renderer stubs for GPU/back-compat backends.
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: Deterministic: stubs delegate to software backend.
VERSIONING / ABI / DATA FORMAT NOTES: Internal header only.
EXTENSION POINTS: Replace stub backends with real GPU backends behind same contract.
*/
#ifndef D_GFX_STUB_H
#define D_GFX_STUB_H

#include "soft/d_gfx_soft.h"

#ifdef __cplusplus
extern "C" {
#endif

/* Soft-backed stub registrations */
const d_gfx_backend_soft* d_gfx_stub_register_dx7(void);
const d_gfx_backend_soft* d_gfx_stub_register_dx9(void);
const d_gfx_backend_soft* d_gfx_stub_register_dx11(void);
const d_gfx_backend_soft* d_gfx_stub_register_gl2(void);
const d_gfx_backend_soft* d_gfx_stub_register_vk1(void);
const d_gfx_backend_soft* d_gfx_stub_register_metal(void);
const d_gfx_backend_soft* d_gfx_stub_register_vesa(void);
const d_gfx_backend_soft* d_gfx_stub_register_vga(void);

/* True if backend is soft-backed (soft or stub). */
int d_gfx_stub_uses_soft(const d_gfx_backend_soft* backend);

#ifdef __cplusplus
}
#endif

#endif /* D_GFX_STUB_H */
