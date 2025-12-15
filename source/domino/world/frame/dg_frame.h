/* Generic frame identifiers (C89).
 *
 * Frames form a directed acyclic parent graph (forest) used for deterministic
 * coordinate transforms. No semantics are implied by "frame".
 */
#ifndef DG_FRAME_H
#define DG_FRAME_H

#include "domino/core/types.h"

#include "sim/pkt/dg_pkt_common.h"

#ifdef __cplusplus
extern "C" {
#endif

/* Stable frame identifier used by packets and authoritative state. */
typedef u64 dg_frame_id;

/* Reserved world/root frame id. */
#define DG_FRAME_ID_WORLD ((dg_frame_id)0u)

/* Fixed bound for parent traversal (no unbounded recursion). */
#define DG_FRAME_MAX_DEPTH 16u

d_bool dg_frame_id_is_world(dg_frame_id id);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DG_FRAME_H */

