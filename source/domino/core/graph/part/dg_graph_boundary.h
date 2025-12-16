/*
FILE: source/domino/core/graph/part/dg_graph_boundary.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / core/graph/part/dg_graph_boundary
RESPONSIBILITY: Implements `dg_graph_boundary`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DG_GRAPH_BOUNDARY_H
#define DG_GRAPH_BOUNDARY_H

/* Deterministic boundary stitching (C89).
 *
 * Boundary endpoints are grouped by a stable boundary_key. For each key, all
 * endpoints in distinct partitions are stitched by adding edges between their
 * node IDs in canonical order.
 */

#include "domino/core/types.h"

#include "core/graph/dg_graph.h"
#include "core/graph/part/dg_graph_part.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct dg_graph_boundary_endpoint {
    u64        boundary_key; /* stable, domain-provided key (no floats) */
    dg_part_id part_id;
    dg_node_id node_id;
} dg_graph_boundary_endpoint;

/* Stitch boundary edges deterministically.
 * Returns 0 on success, <0 on error.
 */
int dg_graph_boundary_stitch(dg_graph *g, const dg_graph_boundary_endpoint *eps, u32 ep_count);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DG_GRAPH_BOUNDARY_H */

