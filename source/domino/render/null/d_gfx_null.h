/*
FILE: source/domino/render/null/d_gfx_null.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / render/null/d_gfx_null
RESPONSIBILITY: Implements `d_gfx_null`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef D_GFX_NULL_H
#define D_GFX_NULL_H

#include "render/soft/d_gfx_soft.h"

#ifdef __cplusplus
extern "C" {
#endif

const d_gfx_backend_soft *d_gfx_null_register_backend(void);

#ifdef __cplusplus
}
#endif

#endif /* D_GFX_NULL_H */

