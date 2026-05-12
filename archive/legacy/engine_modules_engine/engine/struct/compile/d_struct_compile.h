/*
FILE: source/domino/struct/compile/d_struct_compile.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / struct/compile/d_struct_compile
RESPONSIBILITY: Defines internal contract for `d_struct_compile`; shared within its subsystem; does NOT define a public API (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (internal header).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
/* STRUCT compile scaffolding (C89).
 * See docs/SPEC_TRANS_STRUCT_DECOR.md
 */
#ifndef D_STRUCT_COMPILE_H
#define D_STRUCT_COMPILE_H

#include "domino/core/types.h"

#ifdef __cplusplus
extern "C" {
#endif

/* Opaque compiled structure artifact(s). */
typedef struct d_struct_compiled d_struct_compiled;

/* Anchors are authoritative: compiled artifacts are derived caches only.
 * STRUCT compiled artifacts (packed rooms, surface caches, collision proxies)
 * MUST be rebuildable from authoritative anchors + parameters at any time.
 *
 * This interface is intentionally a stub in this prompt.
 */
struct dg_anchor;
int d_struct_compile_rebuild_from_anchors(
    d_struct_compiled     *out_compiled,
    const struct dg_anchor *anchors,
    u32                    anchor_count
);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* D_STRUCT_COMPILE_H */
