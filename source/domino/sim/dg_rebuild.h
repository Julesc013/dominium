#ifndef DG_REBUILD_H
#define DG_REBUILD_H

/* Generic incremental rebuild harness (C89).
 *
 * Responsibilities:
 * - Convert dirty sets into deterministic scheduler work items.
 * - Execute work items via a callback vtable under scheduler budgets.
 *
 * Non-responsibilities:
 * - No domain semantics, solvers, or IO.
 */

#include "domino/core/types.h"
#include "sim/pkt/dg_pkt_common.h"

#include "sim/sched/dg_sched.h"

#include "sim/dg_dirtyset.h"
#include "sim/dg_rebuild_work.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct dg_rebuild_target {
    dg_graph_type_id     graph_type_id;
    dg_graph_instance_id graph_instance_id;

    dg_domain_id domain_id; /* for scheduler budget scoping; 0 allowed */

    dg_graph_rebuild_vtbl rebuild_vtbl;
    void                *user_ctx;
} dg_rebuild_target;

typedef struct dg_rebuild_ctx {
    dg_tick tick;     /* last tick passed to begin_tick */
    u32     next_seq; /* monotonic per producer */
} dg_rebuild_ctx;

void dg_rebuild_init(dg_rebuild_ctx *r);
void dg_rebuild_begin_tick(dg_rebuild_ctx *r, dg_tick tick);

/* Convert dirty items into PH_TOPOLOGY scheduler work items (canonical).
 * Returns 0 on success.
 */
int dg_rebuild_enqueue_from_dirty(
    dg_sched          *sched,
    dg_rebuild_ctx    *r,
    const dg_dirtyset *dirty,
    const dg_rebuild_target *target
);

/* Scheduler work callback that dispatches rebuild work items to a single
 * dg_rebuild_target passed as user_ctx.
 */
void dg_rebuild_sched_work_handler(struct dg_sched *sched, const dg_work_item *item, void *user_ctx);

/* Convenience: schedule work for a registered graph instance. The graph type
 * provides the rebuild vtbl; the instance provides user_ctx.
 */
int dg_rebuild_enqueue_from_dirty_registry(
    dg_sched               *sched,
    dg_rebuild_ctx         *r,
    const dg_dirtyset      *dirty,
    const dg_graph_registry *registry,
    dg_graph_type_id        graph_type_id,
    dg_graph_instance_id    graph_instance_id,
    dg_domain_id            domain_id
);

/* Scheduler work callback that dispatches rebuild work via a dg_graph_registry
 * passed as user_ctx.
 */
void dg_rebuild_registry_sched_work_handler(struct dg_sched *sched, const dg_work_item *item, void *user_ctx);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DG_REBUILD_H */
