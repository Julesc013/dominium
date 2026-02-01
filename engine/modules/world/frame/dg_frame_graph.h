/*
FILE: source/domino/world/frame/dg_frame_graph.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / world/frame/dg_frame_graph
RESPONSIBILITY: Defines internal contract for `dg_frame_graph`; shared within its subsystem; does NOT define a public API (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/specs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (internal header).
EXTENSION POINTS: Extend via public headers and relevant `docs/specs/SPEC_*.md` without cross-layer coupling.
*/
/* Deterministic frame graph container (C89).
 *
 * Storage is provided by the caller for deterministic lifetime/control.
 * Nodes may include simple time-varying parameters (deterministic functions of tick).
 */
#ifndef DG_FRAME_GRAPH_H
#define DG_FRAME_GRAPH_H

#include "domino/core/types.h"

#include "core/dg_pose.h"
#include "world/frame/dg_frame.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct dg_frame_node {
    dg_frame_id id;
    dg_frame_id parent_id; /* DG_FRAME_ID_WORLD for root-attached frames */

    /* Base transform from this frame to its parent frame (local -> parent). */
    dg_pose to_parent_base;

    /* Optional linear time variation (all zero => static). */
    dg_vec3_q vel_pos_per_tick;    /* position delta per tick (Q48.16) */
    dg_q      vel_incline_per_tick;
    dg_q      vel_roll_per_tick;
} dg_frame_node;

typedef struct dg_frame_graph {
    dg_frame_node *nodes;
    u32            count;
    u32            capacity;
} dg_frame_graph;

void dg_frame_graph_init(dg_frame_graph *g, dg_frame_node *storage, u32 capacity);
void dg_frame_graph_clear(dg_frame_graph *g);

int dg_frame_graph_add(dg_frame_graph *g, const dg_frame_node *node);
int dg_frame_graph_find(const dg_frame_graph *g, dg_frame_id id, dg_frame_node *out_node);

u32 dg_frame_graph_count(const dg_frame_graph *g);
const dg_frame_node *dg_frame_graph_at(const dg_frame_graph *g, u32 index);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DG_FRAME_GRAPH_H */

