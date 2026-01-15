/*
FILE: source/domino/render/dx9/d_gfx_dx9.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / render/dx9/d_gfx_dx9
RESPONSIBILITY: Defines internal contract for `d_gfx_dx9`; shared within its subsystem; does NOT define a public API (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (internal header).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef D_GFX_DX9_H
#define D_GFX_DX9_H

#include "../soft/d_gfx_soft.h"

#ifdef __cplusplus
extern "C" {
#endif

const d_gfx_backend_soft* d_gfx_dx9_register_backend(void);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* D_GFX_DX9_H */
