/*
FILE: source/domino/core/graph/part/dg_graph_part.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / core/graph/part/dg_graph_part
RESPONSIBILITY: Implements `dg_graph_part`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DG_GRAPH_PART_H
#define DG_GRAPH_PART_H

/* Chunk-aligned graph partitioning (C89).
 *
 * Partitions are generic "chunks/domains/regions" keyed by a stable u64.
 * Nodes are assigned to partitions, and each partition maintains a canonical
 * ascending node_id list.
 */

#include "domino/core/types.h"
#include "core/graph/dg_graph_node.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef u64 dg_part_id;

#define DG_PART_ID_INVALID ((dg_part_id)0u)

typedef struct dg_graph_part_node_map {
    dg_node_id node_id;
    dg_part_id part_id;
} dg_graph_part_node_map;

typedef struct dg_graph_part_entry {
    dg_part_id  part_id;
    dg_node_id *node_ids; /* sorted ascending */
    u32         node_count;
    u32         node_capacity;
} dg_graph_part_entry;

typedef struct dg_graph_part {
    dg_graph_part_node_map *node_map; /* sorted by node_id */
    u32                     node_map_count;
    u32                     node_map_capacity;

    dg_graph_part_entry *parts; /* sorted by part_id */
    u32                 part_count;
    u32                 part_capacity;
} dg_graph_part;

void dg_graph_part_init(dg_graph_part *p);
void dg_graph_part_free(dg_graph_part *p);
void dg_graph_part_clear(dg_graph_part *p);

/* Ensure capacities are at least the requested values (preserves contents). */
int dg_graph_part_reserve(dg_graph_part *p, u32 node_map_capacity, u32 part_capacity);

/* Assign a node to a partition (or unassign if part_id == DG_PART_ID_INVALID).
 * Returns 0 on success.
 */
int dg_graph_part_set_node(dg_graph_part *p, dg_node_id node_id, dg_part_id part_id);

/* Query node->partition mapping (DG_PART_ID_INVALID if unassigned). */
dg_part_id dg_graph_part_get_node_partition(const dg_graph_part *p, dg_node_id node_id);

/* Partition iteration (canonical by part_id). */
u32 dg_graph_part_count(const dg_graph_part *p);
const dg_graph_part_entry *dg_graph_part_at(const dg_graph_part *p, u32 index);
const dg_graph_part_entry *dg_graph_part_find(const dg_graph_part *p, dg_part_id part_id);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DG_GRAPH_PART_H */

