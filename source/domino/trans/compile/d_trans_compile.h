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
