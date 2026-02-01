/*
FILE: source/domino/core/dg_pose.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / core/dg_pose
RESPONSIBILITY: Defines internal contract for `dg_pose`; shared within its subsystem; does NOT define a public API (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/specs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (internal header).
EXTENSION POINTS: Extend via public headers and relevant `docs/specs/SPEC_*.md` without cross-layer coupling.
*/
/* Canonical fixed-point pose model (C89).
 *
 * This module defines the engine's canonical pose representation used by
 * anchors, frame transforms, and deterministic simulation contracts.
 *
 * Hard rules:
 * - Fixed-point only (no float/double in core deterministic logic).
 * - All ops are deterministic and MUST specify an explicit rounding mode.
 * - No world grid assumptions; poses are arbitrary in continuous space.
 *
 * Q formats used here:
 * - dg_q is Q48.16 (signed).
 *   - Position units are "meters" in Q48.16.
 *   - Angle units are "turns" in Q48.16 where 1.0 turn == 2*pi radians.
 */
#ifndef DG_POSE_H
#define DG_POSE_H

#include "domino/core/types.h"
#include "domino/core/fixed.h"

#ifdef __cplusplus
extern "C" {
#endif

/* Canonical scalar fixed-point type for pose math: Q48.16. */
typedef q48_16 dg_q;

/* Explicit rounding mode for downscales (e.g., fixed-point multiplies). */
typedef enum dg_round_mode {
    DG_ROUND_FLOOR = 0, /* toward -infinity */
    DG_ROUND_NEAR  = 1  /* nearest; halves away from zero */
} dg_round_mode;

typedef struct dg_vec3_q {
    dg_q x;
    dg_q y;
    dg_q z;
} dg_vec3_q;

/* Canonical rotation representation: unit quaternion in Q48.16.
 * This avoids runtime trig for compose/invert/transform.
 *
 * Convention: (x,y,z,w) where w is the scalar component.
 */
typedef struct dg_rot_q {
    dg_q x;
    dg_q y;
    dg_q z;
    dg_q w;
} dg_rot_q;

typedef struct dg_pose {
    dg_vec3_q pos;     /* fixed-point world or frame-local position */
    dg_rot_q  rot;     /* orientation quaternion (unit length expected) */
    dg_q      incline; /* slope relative to host (turns, Q48.16) */
    dg_q      roll;    /* roll about forward axis (turns, Q48.16) */
} dg_pose;

/* Identity helpers. */
dg_vec3_q dg_vec3_zero(void);
dg_rot_q  dg_rot_identity(void);
dg_pose   dg_pose_identity(void);

/* Compose two poses: out = a ∘ b (apply b in a's local frame). */
dg_pose dg_pose_compose(const dg_pose *a, const dg_pose *b, dg_round_mode round_mode);

/* Invert a pose (best-effort; assumes rot is unit quaternion). */
dg_pose dg_pose_invert(const dg_pose *p, dg_round_mode round_mode);

/* Transform helpers. */
dg_vec3_q dg_pose_transform_point(const dg_pose *p, dg_vec3_q local_point, dg_round_mode round_mode);
dg_vec3_q dg_pose_transform_dir(const dg_pose *p, dg_vec3_q local_dir, dg_round_mode round_mode);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DG_POSE_H */

