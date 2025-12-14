/* World frame graph (C89).
 *
 * This module provides deterministic coordinate frames and bounded traversal
 * used by anchors and simulation transforms.
 *
 * Invariants:
 * - Fixed-point only (see core/dg_pose.h).
 * - Frame IDs are stable numeric identifiers (total order).
 * - Traversal is bounded and non-recursive (fixed maximum depth).
 *
 * See docs/SPEC_DOMAINS_FRAMES_PROP.md and docs/SPEC_POSE_AND_ANCHORS.md
 */
#ifndef D_WORLD_FRAME_H
#define D_WORLD_FRAME_H

#include "domino/core/types.h"
#include "sim/pkt/dg_pkt_common.h"

#include "core/dg_pose.h"

#ifdef __cplusplus
extern "C" {
#endif

/* Stable frame identifier used by packets and authoritative state. */
typedef u64 dg_frame_id;

/* Reserved world/root frame id. */
#define DG_FRAME_ID_WORLD ((dg_frame_id)0u)

/* Fixed bound for parent traversal (no unbounded recursion). */
#define D_WORLD_FRAME_MAX_DEPTH 16u

typedef struct d_world_frame_node {
    dg_frame_id id;
    dg_frame_id parent_id; /* DG_FRAME_ID_WORLD for root-attached frames */

    /* Transform from this frame to its parent frame (local -> parent). */
    dg_pose     to_parent;
} d_world_frame_node;

/* Simple caller-owned frame graph container.
 * Storage is provided by the caller for deterministic lifetime/control.
 */
typedef struct d_world_frame {
    d_world_frame_node *nodes;
    u32                 count;
    u32                 capacity;
} d_world_frame;

void d_world_frame_init(d_world_frame *g, d_world_frame_node *storage, u32 capacity);
void d_world_frame_clear(d_world_frame *g);

int d_world_frame_add(d_world_frame *g, const d_world_frame_node *node);
int d_world_frame_find(const d_world_frame *g, dg_frame_id id, d_world_frame_node *out_node);

/* Evaluate a frame's transform to world for the given tick.
 * For now frames are static; tick is reserved for future deterministic motion.
 */
int d_world_frame_eval_to_world(
    const d_world_frame *g,
    dg_frame_id          id,
    dg_tick              tick,
    dg_round_mode        round_mode,
    dg_pose             *out_pose
);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* D_WORLD_FRAME_H */
