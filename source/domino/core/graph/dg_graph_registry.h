#ifndef DG_GRAPH_REGISTRY_H
#define DG_GRAPH_REGISTRY_H

/* Graph registry + typed graphs (deterministic; C89).
 *
 * The registry supports multiple graph instances keyed by:
 *   (graph_type_id, graph_instance_id)
 *
 * Registry iteration order is canonical:
 * - types: ascending graph_type_id
 * - instances: ascending (graph_type_id, graph_instance_id)
 *
 * Graph ordering policy is fixed (authoritative): node_id then edge_id.
 */

#include "domino/core/types.h"
#include "sim/pkt/dg_pkt_common.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef dg_type_id dg_graph_type_id;
typedef u64        dg_graph_instance_id;

typedef struct dg_graph dg_graph;
typedef struct dg_rebuild_work dg_rebuild_work;

typedef struct dg_graph_rebuild_vtbl {
    /* Optional cost estimate (work units) used for budgeting. */
    u32 (*estimate_cost_units)(void *instance_user, const dg_rebuild_work *work);

    /* Execute one rebuild work item. Return 0 on success. */
    int (*execute)(void *instance_user, const dg_rebuild_work *work);
} dg_graph_rebuild_vtbl;

typedef struct dg_graph_registry_type {
    dg_graph_type_id  graph_type_id;
    dg_schema_id      node_schema_id;
    dg_schema_id      edge_schema_id;

    d_bool             has_rebuild_vtbl;
    dg_graph_rebuild_vtbl rebuild_vtbl;

    u32 insert_index; /* stable tie-break/debug */
} dg_graph_registry_type;

typedef struct dg_graph_registry_instance {
    dg_graph_type_id     graph_type_id;
    dg_graph_instance_id graph_instance_id;

    dg_graph *graph;    /* borrowed */
    void     *user_ctx; /* borrowed */

    u32 insert_index; /* stable tie-break/debug */
} dg_graph_registry_instance;

typedef struct dg_graph_registry {
    dg_graph_registry_type *types; /* sorted by graph_type_id */
    u32                     type_count;
    u32                     type_capacity;
    u32                     next_type_insert_index;

    dg_graph_registry_instance *instances; /* sorted by (graph_type_id, graph_instance_id) */
    u32                         instance_count;
    u32                         instance_capacity;
    u32                         next_instance_insert_index;
} dg_graph_registry;

void dg_graph_registry_init(dg_graph_registry *r);
void dg_graph_registry_free(dg_graph_registry *r);

int dg_graph_registry_reserve(dg_graph_registry *r, u32 type_capacity, u32 instance_capacity);

int dg_graph_registry_add_type(
    dg_graph_registry          *r,
    dg_graph_type_id            graph_type_id,
    dg_schema_id                node_schema_id,
    dg_schema_id                edge_schema_id,
    const dg_graph_rebuild_vtbl *rebuild_vtbl /* optional */
);

int dg_graph_registry_add_instance(
    dg_graph_registry     *r,
    dg_graph_type_id       graph_type_id,
    dg_graph_instance_id   graph_instance_id,
    dg_graph             *graph,
    void                 *user_ctx
);

u32 dg_graph_registry_type_count(const dg_graph_registry *r);
u32 dg_graph_registry_instance_count(const dg_graph_registry *r);

const dg_graph_registry_type *dg_graph_registry_type_at(const dg_graph_registry *r, u32 index);
const dg_graph_registry_instance *dg_graph_registry_instance_at(const dg_graph_registry *r, u32 index);

const dg_graph_registry_type *dg_graph_registry_find_type(const dg_graph_registry *r, dg_graph_type_id graph_type_id);
const dg_graph_registry_instance *dg_graph_registry_find_instance(
    const dg_graph_registry *r,
    dg_graph_type_id         graph_type_id,
    dg_graph_instance_id     graph_instance_id
);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DG_GRAPH_REGISTRY_H */

