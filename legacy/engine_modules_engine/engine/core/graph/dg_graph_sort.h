/*
FILE: source/domino/core/graph/dg_graph_sort.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / core/graph/dg_graph_sort
RESPONSIBILITY: Defines internal contract for `dg_graph_sort`; shared within its subsystem; does NOT define a public API (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (internal header).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DG_GRAPH_SORT_H
#define DG_GRAPH_SORT_H

/* Deterministic sorting helpers used by graph infrastructure (C89). */

#include "domino/core/types.h"
#include "core/graph/dg_graph_node.h"

#ifdef __cplusplus
extern "C" {
#endif

void dg_graph_sort_u32(u32 *v, u32 n);
void dg_graph_sort_u64(u64 *v, u32 n);

void dg_graph_sort_node_ids(dg_node_id *v, u32 n);
void dg_graph_sort_edge_ids(dg_edge_id *v, u32 n);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DG_GRAPH_SORT_H */

