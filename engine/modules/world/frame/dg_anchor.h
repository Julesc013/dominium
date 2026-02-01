/*
FILE: source/domino/world/frame/dg_anchor.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / world/frame/dg_anchor
RESPONSIBILITY: Defines internal contract for `dg_anchor`; shared within its subsystem; does NOT define a public API (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/specs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (internal header).
EXTENSION POINTS: Extend via public headers and relevant `docs/specs/SPEC_*.md` without cross-layer coupling.
*/
/* Parametric anchors (C89).
 *
 * Anchors are authoritative placement references. They point to authoring
 * primitives (terrain patch space, TRANS alignments, structure surfaces, etc.)
 * rather than any baked/compiled world-space geometry.
 *
 * This module lives in world/frame because anchor evaluation is defined in
 * terms of the frame graph traversal order:
 *   anchor local -> host frame -> parent frames -> world frame
 *
 * Determinism rules:
 * - All anchor parameters MUST be quantized before becoming authoritative.
 * - dg_anchor_eval is deterministic and MUST NOT cache in this prompt.
 */
#ifndef DG_ANCHOR_H
#define DG_ANCHOR_H

#include "domino/core/types.h"

#include "core/dg_pose.h"
#include "sim/pkt/dg_pkt_common.h"
#include "world/frame/d_world_frame.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef enum dg_anchor_kind {
    DG_ANCHOR_NONE = 0,
    DG_ANCHOR_TERRAIN = 1,
    DG_ANCHOR_CORRIDOR_TRANS = 2,
    DG_ANCHOR_STRUCT_SURFACE = 3,
    DG_ANCHOR_ROOM_SURFACE = 4,
    DG_ANCHOR_SOCKET = 5
} dg_anchor_kind;

typedef struct dg_anchor_terrain {
    dg_q u; /* terrain patch space u */
    dg_q v; /* terrain patch space v */
    dg_q h; /* height offset in patch space */
} dg_anchor_terrain;

typedef struct dg_anchor_corridor_trans {
    u64  alignment_id;
    dg_q s;    /* longitudinal station */
    dg_q t;    /* lateral offset */
    dg_q h;    /* vertical offset */
    dg_q roll; /* roll about forward axis */
} dg_anchor_corridor_trans;

typedef struct dg_anchor_struct_surface {
    u64  structure_id;
    u64  surface_id;
    dg_q u;
    dg_q v;
    dg_q offset;
} dg_anchor_struct_surface;

typedef struct dg_anchor_room_surface {
    u64  room_id;
    u64  surface_id;
    dg_q u;
    dg_q v;
    dg_q offset;
} dg_anchor_room_surface;

typedef struct dg_anchor_socket {
    u64  socket_id;
    dg_q param;
} dg_anchor_socket;

typedef union dg_anchor_u {
    dg_anchor_terrain        terrain;
    dg_anchor_corridor_trans corridor;
    dg_anchor_struct_surface struct_surface;
    dg_anchor_room_surface   room_surface;
    dg_anchor_socket         socket;
} dg_anchor_u;

typedef struct dg_anchor {
    dg_anchor_kind kind;
    u32            _pad32;     /* reserved (must be zero) */
    dg_frame_id    host_frame; /* coordinate frame the anchor is defined in */
    dg_anchor_u    u;
} dg_anchor;

void dg_anchor_clear(dg_anchor *a);

/* Canonical total order comparator for anchors. */
int dg_anchor_cmp(const dg_anchor *a, const dg_anchor *b);

/* Evaluate an anchor into a world-space pose at a given tick.
 * No caching in this prompt.
 */
int dg_anchor_eval(
    const dg_anchor    *anchor,
    const d_world_frame *frames,
    dg_tick             tick,
    dg_round_mode       round_mode,
    dg_pose            *out_pose
);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DG_ANCHOR_H */

