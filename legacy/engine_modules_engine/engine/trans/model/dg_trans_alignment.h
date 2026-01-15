/*
FILE: source/domino/trans/model/dg_trans_alignment.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / trans/model/dg_trans_alignment
RESPONSIBILITY: Defines internal contract for `dg_trans_alignment`; shared within its subsystem; does NOT define a public API (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (internal header).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
/* TRANS corridor alignment authoring model (C89).
 *
 * An alignment is a parametric curve (spine) that supports:
 * - deterministic evaluation in fixed-point
 * - separate z-offset and roll profiles (piecewise-linear over station)
 *
 * Current representation: 3D polyline control points (ordered by point_index).
 * Interface is kept abstract for later spline extension.
 */
#ifndef DG_TRANS_ALIGNMENT_H
#define DG_TRANS_ALIGNMENT_H

#include "domino/core/types.h"

#include "core/dg_pose.h"
#include "trans/model/dg_trans_ids.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct dg_trans_alignment_point {
    u32       point_index; /* stable ordering key (monotonic by convention) */
    dg_vec3_q pos;         /* fixed-point world/local coordinates (Q48.16 meters) */
} dg_trans_alignment_point;

typedef struct dg_trans_profile_knot {
    dg_q s; /* station */
    dg_q v; /* value */
} dg_trans_profile_knot;

typedef struct dg_trans_alignment {
    dg_trans_alignment_id         id;
    dg_trans_section_archetype_id section_id;

    /* Polyline control points (canonical sorted by point_index). */
    dg_trans_alignment_point *points;
    u32                       point_count;
    u32                       point_capacity;

    /* Z-offset profile: meters to add to evaluated position.z. */
    dg_trans_profile_knot *z_profile;
    u32                   z_count;
    u32                   z_capacity;

    /* Roll profile: turns about forward axis. */
    dg_trans_profile_knot *roll_profile;
    u32                   roll_count;
    u32                   roll_capacity;
} dg_trans_alignment;

void dg_trans_alignment_init(dg_trans_alignment *a);
void dg_trans_alignment_free(dg_trans_alignment *a);

int dg_trans_alignment_reserve_points(dg_trans_alignment *a, u32 capacity);
int dg_trans_alignment_set_point(dg_trans_alignment *a, u32 point_index, dg_vec3_q pos);

int dg_trans_alignment_reserve_z_profile(dg_trans_alignment *a, u32 capacity);
int dg_trans_alignment_set_z_knot(dg_trans_alignment *a, dg_q s, dg_q z_offset);

int dg_trans_alignment_reserve_roll_profile(dg_trans_alignment *a, u32 capacity);
int dg_trans_alignment_set_roll_knot(dg_trans_alignment *a, dg_q s, dg_q roll_turns);

/* Deterministic evaluation (station is clamped to [0, length]). */
int dg_trans_alignment_length_q(const dg_trans_alignment *a, dg_q *out_len);
int dg_trans_alignment_eval_pos(const dg_trans_alignment *a, dg_q s, dg_vec3_q *out_pos);
int dg_trans_alignment_eval_tangent(const dg_trans_alignment *a, dg_q s, dg_vec3_q *out_tangent_unit);
int dg_trans_alignment_eval_roll(const dg_trans_alignment *a, dg_q s, dg_q *out_roll_turns);
int dg_trans_alignment_eval_up(const dg_trans_alignment *a, dg_q s, dg_vec3_q *out_up_unit);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DG_TRANS_ALIGNMENT_H */
