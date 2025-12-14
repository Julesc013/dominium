/* Deterministic local frame construction for TRANS (C89).
 *
 * Frame construction rules:
 * - forward axis = normalized tangent
 * - base up reference = world up (0,0,1) unless parallel to forward
 * - right = normalize(cross(up_ref, forward))
 * - up    = normalize(cross(forward, right))
 * - apply roll about forward axis (turns, Q48.16) via deterministic sin/cos
 *
 * No tolerance/epsilon comparisons are used; only exact checks.
 */
#ifndef DG_TRANS_FRAME_H
#define DG_TRANS_FRAME_H

#include "domino/core/types.h"

#include "core/dg_pose.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct dg_trans_frame {
    dg_vec3_q origin;  /* world/local position at station */
    dg_vec3_q forward; /* unit length, Q48.16 */
    dg_vec3_q right;   /* unit length, Q48.16 */
    dg_vec3_q up;      /* unit length, Q48.16 */
} dg_trans_frame;

/* Compute deterministic sin/cos for an angle in turns (Q48.16).
 * Outputs are Q48.16 in [-1,1].
 */
int dg_trans_sincos_turns(dg_q turns, dg_q *out_cos, dg_q *out_sin);

/* Build a right-handed frame from a forward direction and roll (turns).
 * forward_dir does not need to be normalized.
 */
int dg_trans_frame_build(dg_vec3_q origin, dg_vec3_q forward_dir, dg_q roll_turns, dg_trans_frame *out_frame);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DG_TRANS_FRAME_H */

