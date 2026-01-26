/*
FILE: include/render/null/d_gfx_null.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino API / render/null/d_gfx_null
RESPONSIBILITY: Defines the public contract for `d_gfx_null`; does NOT provide implementation.
ALLOWED DEPENDENCIES: `include/domino/**` plus C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `source/**` private headers; keep contracts freestanding and layer-respecting.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: Public header; see `docs/SPEC_ABI_TEMPLATES.md` where ABI stability matters.
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef D_GFX_NULL_H
#define D_GFX_NULL_H

#include "domino/gfx.h"

struct d_gfx_backend_soft_s;
typedef struct d_gfx_backend_soft_s d_gfx_backend_soft;

#ifdef __cplusplus
extern "C" {
#endif

const d_gfx_backend_soft *d_gfx_null_register_backend(void);
void d_gfx_null_set_delay_ms(u32 submit_ms, u32 present_ms);

#ifdef __cplusplus
}
#endif

#endif /* D_GFX_NULL_H */
