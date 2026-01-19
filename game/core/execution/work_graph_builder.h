/*
FILE: game/core/execution/work_graph_builder.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium core / execution
RESPONSIBILITY: Deterministic Work IR graph builder (game-side).
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C89/C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
DETERMINISM: Stable ordering; explicit IDs only.
*/
#ifndef DOMINIUM_CORE_EXECUTION_WORK_GRAPH_BUILDER_H
#define DOMINIUM_CORE_EXECUTION_WORK_GRAPH_BUILDER_H

#include "domino/core/types.h"
#include "domino/execution/task_graph.h"
#include "domino/execution/cost_model.h"

#ifdef __cplusplus
extern "C" {
#endif

enum {
    DOM_WORK_ID_TASK = 1,
    DOM_WORK_ID_ACCESS = 2,
    DOM_WORK_ID_COST = 3
};

typedef struct dom_work_graph_builder {
    dom_task_node*       tasks;
    u32                  task_count;
    u32                  task_capacity;
    dom_dependency_edge* dependencies;
    u32                  dependency_count;
    u32                  dependency_capacity;
    dom_phase_barrier*   phase_barriers;
    u32                  phase_barrier_count;
    u32                  phase_barrier_capacity;
    dom_cost_model*      cost_models;
    u32                  cost_model_count;
    u32                  cost_model_capacity;
    u64                  graph_id;
    u64                  epoch_id;
} dom_work_graph_builder;

void dom_work_graph_builder_init(dom_work_graph_builder* builder,
                                 dom_task_node* task_storage,
                                 u32 task_capacity,
                                 dom_dependency_edge* dependency_storage,
                                 u32 dependency_capacity,
                                 dom_phase_barrier* phase_barrier_storage,
                                 u32 phase_barrier_capacity,
                                 dom_cost_model* cost_model_storage,
                                 u32 cost_model_capacity);

void dom_work_graph_builder_reset(dom_work_graph_builder* builder);
void dom_work_graph_builder_set_ids(dom_work_graph_builder* builder, u64 graph_id, u64 epoch_id);

int dom_work_graph_builder_add_task(dom_work_graph_builder* builder, const dom_task_node* node);
int dom_work_graph_builder_add_dependency(dom_work_graph_builder* builder, const dom_dependency_edge* edge);
int dom_work_graph_builder_add_phase_barrier(dom_work_graph_builder* builder, const dom_phase_barrier* barrier);
int dom_work_graph_builder_add_cost_model(dom_work_graph_builder* builder, const dom_cost_model* model);

void dom_work_graph_builder_finalize(dom_work_graph_builder* builder, dom_task_graph* out_graph);

u64 dom_work_graph_builder_make_id(u64 system_id, u32 local_id, u32 kind);
dom_commit_key dom_work_graph_builder_make_commit_key(u32 phase_id, u64 task_id, u32 sub_index);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_CORE_EXECUTION_WORK_GRAPH_BUILDER_H */
