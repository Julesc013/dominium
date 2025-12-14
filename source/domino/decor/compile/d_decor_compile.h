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
