/*
FILE: source/domino/trans/compile/d_trans_compile.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / trans/compile/d_trans_compile
RESPONSIBILITY: Defines internal contract for `d_trans_compile`; shared within its subsystem; does NOT define a public API (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (internal header).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
/* TRANS compile scaffolding (C89).
 * See docs/SPEC_TRANS_STRUCT_DECOR.md
 */
#ifndef D_TRANS_COMPILE_H
#define D_TRANS_COMPILE_H

#include "domino/core/types.h"

#ifdef __cplusplus
extern "C" {
#endif

/* Opaque compiled TRANS artifact(s). */
typedef struct d_trans_compiled d_trans_compiled;

/* Anchors are authoritative: compiled artifacts are derived caches only.
 * TRANS compiled artifacts (microsegments, surfaces, etc.) MUST be rebuildable
 * from authoritative anchors + parameters at any time; LOD transitions MUST
 * NOT rewrite anchors.
 *
 * This interface is intentionally a stub in this prompt.
 */
struct dg_anchor;
int d_trans_compile_rebuild_from_anchors(
    d_trans_compiled      *out_compiled,
    const struct dg_anchor *anchors,
    u32                    anchor_count
);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* D_TRANS_COMPILE_H */
