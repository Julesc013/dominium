/*
FILE: source/domino/render/d_gfx_internal.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / render/d_gfx_internal
RESPONSIBILITY: Implements `d_gfx_internal`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef D_GFX_INTERNAL_H
#define D_GFX_INTERNAL_H

#include "domino/core/types.h"

#ifdef __cplusplus
extern "C" {
#endif

void* d_gfx_get_native_window(void);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* D_GFX_INTERNAL_H */

