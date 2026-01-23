/*
FILE: game/core/execution/work_graph_builder.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium core / execution
RESPONSIBILITY: Deterministic Work IR graph builder implementation.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
DETERMINISM: Stable ordering and stable ID derivation.
*/
#include "work_graph_builder.h"

static u64 dom_work_hash_init(void)
{
    return 1469598103934665603ULL;
}

static u64 dom_work_hash_update_u32(u64 hash, u32 v)
{
    u32 i;
    for (i = 0u; i < 4u; ++i) {
        hash ^= (u64)((v >> (i * 8u)) & 0xFFu);
        hash *= 1099511628211ULL;
    }
    return hash;
}

static u64 dom_work_hash_update_u64(u64 hash, u64 v)
{
    u32 i;
    for (i = 0u; i < 8u; ++i) {
        hash ^= (u64)((v >> (i * 8u)) & 0xFFu);
        hash *= 1099511628211ULL;
    }
    return hash;
}

void dom_work_graph_builder_init(dom_work_graph_builder* builder,
                                 dom_task_node* task_storage,
                                 u32 task_capacity,
                                 dom_dependency_edge* dependency_storage,
                                 u32 dependency_capacity,
                                 dom_phase_barrier* phase_barrier_storage,
                                 u32 phase_barrier_capacity,
                                 dom_cost_model* cost_model_storage,
                                 u32 cost_model_capacity)
{
    if (!builder) {
        return;
    }
    builder->tasks = task_storage;
    builder->task_count = 0u;
    builder->task_capacity = task_capacity;
    builder->dependencies = dependency_storage;
    builder->dependency_count = 0u;
    builder->dependency_capacity = dependency_capacity;
    builder->phase_barriers = phase_barrier_storage;
    builder->phase_barrier_count = 0u;
    builder->phase_barrier_capacity = phase_barrier_capacity;
    builder->cost_models = cost_model_storage;
    builder->cost_model_count = 0u;
    builder->cost_model_capacity = cost_model_capacity;
    builder->graph_id = 0u;
    builder->epoch_id = 0u;
}

void dom_work_graph_builder_reset(dom_work_graph_builder* builder)
{
    if (!builder) {
        return;
    }
    builder->task_count = 0u;
    builder->dependency_count = 0u;
    builder->phase_barrier_count = 0u;
    builder->cost_model_count = 0u;
}

void dom_work_graph_builder_set_ids(dom_work_graph_builder* builder, u64 graph_id, u64 epoch_id)
{
    if (!builder) {
        return;
    }
    builder->graph_id = graph_id;
    builder->epoch_id = epoch_id;
}

int dom_work_graph_builder_add_task(dom_work_graph_builder* builder, const dom_task_node* node)
{
    if (!builder || !builder->tasks || !node) {
        return -1;
    }
    if (builder->task_count >= builder->task_capacity) {
        return -2;
    }
    builder->tasks[builder->task_count++] = *node;
    return 0;
}

int dom_work_graph_builder_add_dependency(dom_work_graph_builder* builder, const dom_dependency_edge* edge)
{
    if (!builder || !edge) {
        return -1;
    }
    if (!builder->dependencies || builder->dependency_capacity == 0u) {
        return -2;
    }
    if (builder->dependency_count >= builder->dependency_capacity) {
        return -3;
    }
    builder->dependencies[builder->dependency_count++] = *edge;
    return 0;
}

int dom_work_graph_builder_add_phase_barrier(dom_work_graph_builder* builder, const dom_phase_barrier* barrier)
{
    if (!builder || !barrier) {
        return -1;
    }
    if (!builder->phase_barriers || builder->phase_barrier_capacity == 0u) {
        return -2;
    }
    if (builder->phase_barrier_count >= builder->phase_barrier_capacity) {
        return -3;
    }
    builder->phase_barriers[builder->phase_barrier_count++] = *barrier;
    return 0;
}

int dom_work_graph_builder_add_cost_model(dom_work_graph_builder* builder, const dom_cost_model* model)
{
    if (!builder || !model) {
        return -1;
    }
    if (!builder->cost_models || builder->cost_model_capacity == 0u) {
        return -2;
    }
    if (builder->cost_model_count >= builder->cost_model_capacity) {
        return -3;
    }
    builder->cost_models[builder->cost_model_count++] = *model;
    return 0;
}

void dom_work_graph_builder_finalize(dom_work_graph_builder* builder, dom_task_graph* out_graph)
{
    if (!builder || !out_graph) {
        return;
    }
    if (builder->tasks && builder->task_count > 1u) {
        dom_stable_task_sort(builder->tasks, builder->task_count);
    }
    out_graph->graph_id = builder->graph_id;
    out_graph->epoch_id = builder->epoch_id;
    out_graph->tasks = builder->tasks;
    out_graph->task_count = builder->task_count;
    out_graph->dependency_edges = builder->dependencies;
    out_graph->dependency_count = builder->dependency_count;
    out_graph->phase_barriers = builder->phase_barriers;
    out_graph->phase_barrier_count = builder->phase_barrier_count;
}

u64 dom_work_graph_builder_make_id(u64 system_id, u32 local_id, u32 kind)
{
    u64 hash = dom_work_hash_init();
    hash = dom_work_hash_update_u64(hash, system_id);
    hash = dom_work_hash_update_u32(hash, kind);
    hash = dom_work_hash_update_u32(hash, local_id);
    return hash;
}

dom_commit_key dom_work_graph_builder_make_commit_key(u32 phase_id, u64 task_id, u32 sub_index)
{
    dom_commit_key key;
    key.phase_id = phase_id;
    key.task_id = task_id;
    key.sub_index = sub_index;
    return key;
}
