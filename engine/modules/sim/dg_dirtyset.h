/*
FILE: source/domino/sim/dg_dirtyset.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / sim/dg_dirtyset
RESPONSIBILITY: Defines internal contract for `dg_dirtyset`; shared within its subsystem; does NOT define a public API (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (internal header).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DG_DIRTYSET_H
#define DG_DIRTYSET_H

/* Deterministic dirty set tracking (C89).
 *
 * Dirty sets store stable numeric IDs in canonical ascending order, independent
 * of insertion order. They are used to drive incremental rebuild scheduling.
 */

#include "domino/core/types.h"

#include "core/graph/dg_graph_node.h"
#include "core/graph/part/dg_graph_part.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct dg_dirtyset {
    dg_node_id *nodes; /* sorted ascending */
    u32         node_count;
    u32         node_capacity;

    dg_edge_id *edges; /* sorted ascending */
    u32         edge_count;
    u32         edge_capacity;

    dg_part_id *parts; /* sorted ascending */
    u32         part_count;
    u32         part_capacity;
} dg_dirtyset;

void dg_dirtyset_init(dg_dirtyset *d);
void dg_dirtyset_free(dg_dirtyset *d);
void dg_dirtyset_clear(dg_dirtyset *d);

int dg_dirtyset_reserve(dg_dirtyset *d, u32 node_capacity, u32 edge_capacity, u32 part_capacity);

int dg_dirtyset_add_node(dg_dirtyset *d, dg_node_id node_id);
int dg_dirtyset_add_edge(dg_dirtyset *d, dg_edge_id edge_id);
int dg_dirtyset_add_part(dg_dirtyset *d, dg_part_id part_id);

int dg_dirtyset_remove_node(dg_dirtyset *d, dg_node_id node_id);
int dg_dirtyset_remove_edge(dg_dirtyset *d, dg_edge_id edge_id);
int dg_dirtyset_remove_part(dg_dirtyset *d, dg_part_id part_id);

/* Merge (union) src into dst, preserving canonical order. */
int dg_dirtyset_merge(dg_dirtyset *dst, const dg_dirtyset *src);

u32 dg_dirtyset_node_count(const dg_dirtyset *d);
u32 dg_dirtyset_edge_count(const dg_dirtyset *d);
u32 dg_dirtyset_part_count(const dg_dirtyset *d);

dg_node_id dg_dirtyset_node_at(const dg_dirtyset *d, u32 index);
dg_edge_id dg_dirtyset_edge_at(const dg_dirtyset *d, u32 index);
dg_part_id dg_dirtyset_part_at(const dg_dirtyset *d, u32 index);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DG_DIRTYSET_H */

