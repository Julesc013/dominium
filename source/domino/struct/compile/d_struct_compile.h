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
