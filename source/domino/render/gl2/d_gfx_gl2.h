/*
FILE: source/domino/render/gl2/d_gfx_gl2.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / render/gl2/d_gfx_gl2
RESPONSIBILITY: Defines internal contract for `d_gfx_gl2`; shared within its subsystem; does NOT define a public API (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (internal header).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef D_GFX_GL2_H
#define D_GFX_GL2_H

#include "../soft/d_gfx_soft.h"

#ifdef __cplusplus
extern "C" {
#endif

const d_gfx_backend_soft* d_gfx_gl2_register_backend(void);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* D_GFX_GL2_H */

