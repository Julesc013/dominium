/*
FILE: source/domino/core/graph/dg_graph_edge.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / core/graph/dg_graph_edge
RESPONSIBILITY: Defines internal contract for `dg_graph_edge`; shared within its subsystem; does NOT define a public API (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/specs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (internal header).
EXTENSION POINTS: Extend via public headers and relevant `docs/specs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DG_GRAPH_EDGE_H
#define DG_GRAPH_EDGE_H

/* Canonical deterministic graph edge identity (C89). */

#include "core/graph/dg_graph_node.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef u32 dg_edge_flags;

#define DG_EDGE_FLAG_NONE     0u
#define DG_EDGE_FLAG_DIRECTED 1u /* interpret (a -> b) */

typedef struct dg_graph_edge {
    dg_edge_id    id;
    dg_node_id    a;
    dg_node_id    b;
    dg_edge_flags flags;
} dg_graph_edge;

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DG_GRAPH_EDGE_H */

