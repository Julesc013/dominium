/*
FILE: source/domino/decor/compile/d_decor_compile.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / decor/compile/d_decor_compile
RESPONSIBILITY: Implements `d_decor_compile`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
/* DECOR compile scaffolding (C89).
 * See docs/SPEC_TRANS_STRUCT_DECOR.md
 */
#ifndef D_DECOR_COMPILE_H
#define D_DECOR_COMPILE_H

#include "domino/core/types.h"

#ifdef __cplusplus
extern "C" {
#endif

/* Opaque compiled decor artifact(s). */
typedef struct d_decor_compiled d_decor_compiled;

/* Anchors are authoritative: compiled artifacts are derived caches only.
 * DECOR compiled artifacts (scatter results, instance lists, baked meshes)
 * MUST be rebuildable from authoritative anchors + parameters at any time.
 *
 * This interface is intentionally a stub in this prompt.
 */
struct dg_anchor;
int d_decor_compile_rebuild_from_anchors(
    d_decor_compiled      *out_compiled,
    const struct dg_anchor *anchors,
    u32                    anchor_count
);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* D_DECOR_COMPILE_H */
