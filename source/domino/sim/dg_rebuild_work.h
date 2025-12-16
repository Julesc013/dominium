/*
FILE: source/domino/sim/dg_rebuild_work.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / sim/dg_rebuild_work
RESPONSIBILITY: Defines internal contract for `dg_rebuild_work`; shared within its subsystem; does NOT define a public API (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (internal header).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DG_REBUILD_WORK_H
#define DG_REBUILD_WORK_H

/* Rebuild work item encoding (C89).
 *
 * Rebuild work items are scheduled into the deterministic scheduler queues as
 * dg_work_item records. Work identity is encoded in the dg_order_key fields:
 * - key.type_id      : graph_type_id
 * - key.entity_id    : graph_instance_id
 * - key.chunk_id     : partition/chunk id (0 allowed)
 * - key.component_id : packed (work_kind, item_id)
 *
 * No pointer identity, hash iteration order, or discovery order is permitted.
 */

#include "domino/core/types.h"

#include "core/graph/dg_graph_registry.h"
#include "core/graph/part/dg_graph_part.h"

#include "sim/sched/dg_work_item.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef enum dg_rebuild_work_kind {
    DG_REBUILD_WORK_INVALID   = 0,
    DG_REBUILD_WORK_PARTITION = 1,
    DG_REBUILD_WORK_NODE      = 2,
    DG_REBUILD_WORK_EDGE      = 3
} dg_rebuild_work_kind;

typedef struct dg_rebuild_work {
    dg_graph_type_id     graph_type_id;
    dg_graph_instance_id graph_instance_id;
    dg_part_id           part_id; /* chunk-aligned partition id; 0 allowed */
    dg_rebuild_work_kind kind;
    u64                  item_id; /* node_id/edge_id/etc. 0 allowed by kind */
} dg_rebuild_work;

/* Pack work kind + item_id into a u64 suitable for dg_order_key.component_id.
 * item_id is limited to 56 bits.
 */
u64 dg_rebuild_pack_component(dg_rebuild_work_kind kind, u64 item_id);
dg_rebuild_work_kind dg_rebuild_unpack_kind(u64 component_id);
u64 dg_rebuild_unpack_item_id(u64 component_id);

/* Decode a scheduler work item into a rebuild work description.
 * Returns 0 on success, <0 on error.
 */
int dg_rebuild_work_from_item(const dg_work_item *it, dg_rebuild_work *out);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DG_REBUILD_WORK_H */
