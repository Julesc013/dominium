/*
FILE: source/domino/decor/d_decor.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / decor/d_decor
RESPONSIBILITY: Defines internal contract for `d_decor`; shared within its subsystem; does NOT define a public API (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/specs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (internal header).
EXTENSION POINTS: Extend via public headers and relevant `docs/specs/SPEC_*.md` without cross-layer coupling.
*/
/* DECOR layer scaffolding (C89).
 * See docs/specs/SPEC_TRANS_STRUCT_DECOR.md
 */
#ifndef D_DECOR_H
#define D_DECOR_H

#include "domino/core/types.h"

#ifdef __cplusplus
extern "C" {
#endif

/* Opaque decor context / compiled output handle(s). */
typedef struct d_decor d_decor;

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* D_DECOR_H */

