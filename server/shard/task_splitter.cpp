/*
FILE: server/shard/task_splitter.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Server / shard
RESPONSIBILITY: Deterministic TaskGraph partitioning across shards.
*/
#include "task_splitter.h"

#include "domino/execution/access_set.h"

#include <string.h>

#ifdef __cplusplus
extern "C" {
#endif

static u64 dom_shard_fnv1a64_pair(u64 a, u64 b)
{
    u64 h = 1469598103934665603ULL;
    h ^= a;
    h *= 1099511628211ULL;
    h ^= b;
    h *= 1099511628211ULL;
    return h;
}

static u64 dom_shard_owner_id_from_range(const dom_access_range* range)
{
    if (!range) {
        return 0u;
    }
    switch (range->kind) {
        case DOM_RANGE_INDEX_RANGE:
        case DOM_RANGE_SINGLE:
            return range->start_id;
        case DOM_RANGE_COMPONENT_SET:
        case DOM_RANGE_ENTITY_SET:
        case DOM_RANGE_INTEREST_SET:
        default:
            return range->set_id;
    }
}

static u64 dom_shard_owner_id_from_access(const dom_execution_context* ctx,
                                          const dom_task_node* node)
{
    const dom_access_set* set;
    const dom_access_range* range = 0;
    if (!ctx || !node) {
        return 0u;
    }
    set = dom_execution_context_lookup_access_set(ctx, node->access_set_id);
    if (!set) {
        return 0u;
    }
    if (node->category == DOM_TASK_AUTHORITATIVE && set->write_count > 0u) {
        range = &set->write_ranges[0];
    } else if (set->read_count > 0u) {
        range = &set->read_ranges[0];
    } else if (set->reduce_count > 0u) {
        range = &set->reduce_ranges[0];
    }
    return dom_shard_owner_id_from_range(range);
}

void dom_shard_task_graph_init(dom_shard_task_graph* graph,
                               dom_shard_id shard_id,
                               dom_task_node* task_storage,
                               u32 task_capacity,
                               dom_dependency_edge* edge_storage,
                               u32 edge_capacity)
{
    if (!graph) {
        return;
    }
    graph->shard_id = shard_id;
    graph->tasks = task_storage;
    graph->task_capacity = task_capacity;
    graph->edges = edge_storage;
    graph->edge_capacity = edge_capacity;
    graph->task_count = 0u;
    graph->edge_count = 0u;
    graph->graph.graph_id = 0u;
    graph->graph.epoch_id = 0u;
    graph->graph.tasks = task_storage;
    graph->graph.task_count = 0u;
    graph->graph.dependency_edges = edge_storage;
    graph->graph.dependency_count = 0u;
    graph->graph.phase_barriers = 0;
    graph->graph.phase_barrier_count = 0u;
}

void dom_shard_task_splitter_init(dom_shard_task_splitter* splitter,
                                  dom_shard_task_graph* shard_graphs,
                                  u32 shard_graph_count,
                                  dom_shard_task_mapping* map_storage,
                                  u32 map_capacity,
                                  dom_shard_message* message_storage,
                                  u32 message_capacity)
{
    if (!splitter) {
        return;
    }
    splitter->shard_graphs = shard_graphs;
    splitter->shard_graph_count = shard_graph_count;
    splitter->task_map = map_storage;
    splitter->task_map_capacity = map_capacity;
    splitter->task_map_count = 0u;
    splitter->messages = message_storage;
    splitter->message_capacity = message_capacity;
    splitter->message_count = 0u;
}

void dom_shard_task_splitter_reset(dom_shard_task_splitter* splitter)
{
    u32 i;
    if (!splitter) {
        return;
    }
    splitter->task_map_count = 0u;
    splitter->message_count = 0u;
    for (i = 0u; i < splitter->shard_graph_count; ++i) {
        dom_shard_task_graph* graph = &splitter->shard_graphs[i];
        graph->task_count = 0u;
        graph->edge_count = 0u;
        graph->graph.task_count = 0u;
        graph->graph.dependency_count = 0u;
    }
}

static dom_shard_task_graph* dom_shard_graph_for(dom_shard_task_splitter* splitter,
                                                 dom_shard_id shard_id)
{
    u32 i;
    if (!splitter) {
        return 0;
    }
    for (i = 0u; i < splitter->shard_graph_count; ++i) {
        if (splitter->shard_graphs[i].shard_id == shard_id) {
            return &splitter->shard_graphs[i];
        }
    }
    return 0;
}

static int dom_shard_task_map_add(dom_shard_task_splitter* splitter,
                                  u64 task_id,
                                  dom_shard_id shard_id)
{
    if (!splitter || !splitter->task_map) {
        return -1;
    }
    if (splitter->task_map_count >= splitter->task_map_capacity) {
        return -2;
    }
    splitter->task_map[splitter->task_map_count].task_id = task_id;
    splitter->task_map[splitter->task_map_count].shard_id = shard_id;
    splitter->task_map_count += 1u;
    return 0;
}

static dom_shard_id dom_shard_task_map_find(const dom_shard_task_splitter* splitter,
                                            u64 task_id)
{
    u32 i;
    if (!splitter || !splitter->task_map) {
        return 0u;
    }
    for (i = 0u; i < splitter->task_map_count; ++i) {
        if (splitter->task_map[i].task_id == task_id) {
            return splitter->task_map[i].shard_id;
        }
    }
    return 0u;
}

static const dom_task_node* dom_shard_find_task(const dom_task_graph* graph, u64 task_id)
{
    u32 i;
    if (!graph || !graph->tasks) {
        return 0;
    }
    for (i = 0u; i < graph->task_count; ++i) {
        if (graph->tasks[i].task_id == task_id) {
            return &graph->tasks[i];
        }
    }
    return 0;
}

static dom_act_time_t dom_shard_message_arrival(const dom_task_node* from,
                                                const dom_task_node* to)
{
    dom_act_time_t tick = 0u;
    if (from && from->next_due_tick != DOM_EXEC_TICK_INVALID) {
        tick = from->next_due_tick;
    }
    if (to && to->next_due_tick != DOM_EXEC_TICK_INVALID) {
        if (to->next_due_tick > tick) {
            tick = to->next_due_tick;
        }
    }
    return tick;
}

static int dom_shard_message_before(const dom_shard_message* a,
                                    const dom_shard_message* b)
{
    if (a->arrival_tick < b->arrival_tick) {
        return 1;
    }
    if (a->arrival_tick > b->arrival_tick) {
        return 0;
    }
    return (a->message_id < b->message_id) ? 1 : 0;
}

static void dom_shard_message_sort(dom_shard_message* messages, u32 count)
{
    u32 i;
    if (!messages || count < 2u) {
        return;
    }
    for (i = 1u; i < count; ++i) {
        dom_shard_message key = messages[i];
        u32 j = i;
        while (j > 0u && dom_shard_message_before(&key, &messages[j - 1u])) {
            messages[j] = messages[j - 1u];
            j -= 1u;
        }
        messages[j] = key;
    }
}

int dom_shard_task_splitter_split(dom_shard_task_splitter* splitter,
                                  const dom_task_graph* graph,
                                  const dom_shard_registry* registry,
                                  const dom_execution_context* ctx,
                                  dom_shard_id fallback_shard)
{
    u32 i;
    if (!splitter || !graph || !registry) {
        return -1;
    }
    dom_shard_task_splitter_reset(splitter);

    for (i = 0u; i < splitter->shard_graph_count; ++i) {
        splitter->shard_graphs[i].graph.graph_id = graph->graph_id;
        splitter->shard_graphs[i].graph.epoch_id = graph->epoch_id;
    }

    for (i = 0u; i < graph->task_count; ++i) {
        const dom_task_node* node = &graph->tasks[i];
        dom_shard_task_key key;
        dom_shard_id shard_id;
        dom_shard_task_graph* shard_graph;
        u64 owner_id = dom_shard_owner_id_from_access(ctx, node);

        key.task_id = node->task_id;
        key.system_id = node->system_id;
        key.access_set_id = node->access_set_id;
        key.category = node->category;
        key.determinism_class = node->determinism_class;
        key.primary_owner_id = owner_id;

        shard_id = dom_shard_place_task(registry, &key, fallback_shard);
        shard_graph = dom_shard_graph_for(splitter, shard_id);
        if (!shard_graph) {
            return -2;
        }
        if (shard_graph->task_count >= shard_graph->task_capacity) {
            return -3;
        }
        shard_graph->tasks[shard_graph->task_count++] = *node;
        shard_graph->graph.task_count = shard_graph->task_count;
        if (dom_shard_task_map_add(splitter, node->task_id, shard_id) != 0) {
            return -4;
        }
    }

    for (i = 0u; i < graph->dependency_count; ++i) {
        const dom_dependency_edge* edge = &graph->dependency_edges[i];
        dom_shard_id from_shard = dom_shard_task_map_find(splitter, edge->from_task_id);
        dom_shard_id to_shard = dom_shard_task_map_find(splitter, edge->to_task_id);
        if (from_shard == 0u || to_shard == 0u) {
            return -5;
        }
        if (from_shard == to_shard) {
            dom_shard_task_graph* shard_graph = dom_shard_graph_for(splitter, from_shard);
            if (!shard_graph || shard_graph->edge_count >= shard_graph->edge_capacity) {
                return -6;
            }
            shard_graph->edges[shard_graph->edge_count++] = *edge;
            shard_graph->graph.dependency_count = shard_graph->edge_count;
        } else {
            dom_shard_message msg;
            const dom_task_node* from_node = dom_shard_find_task(graph, edge->from_task_id);
            const dom_task_node* to_node = dom_shard_find_task(graph, edge->to_task_id);
            if (splitter->message_count >= splitter->message_capacity) {
                return -7;
            }
            msg.source_shard = from_shard;
            msg.target_shard = to_shard;
            msg.task_id = edge->from_task_id;
            msg.message_id = dom_shard_fnv1a64_pair(edge->from_task_id, edge->to_task_id);
            msg.arrival_tick = dom_shard_message_arrival(from_node, to_node);
            msg.payload = 0;
            msg.payload_size = 0u;
            splitter->messages[splitter->message_count++] = msg;
        }
    }

    for (i = 0u; i < splitter->shard_graph_count; ++i) {
        dom_shard_task_graph* shard_graph = &splitter->shard_graphs[i];
        if (shard_graph->tasks && shard_graph->task_count > 1u) {
            dom_stable_task_sort(shard_graph->tasks, shard_graph->task_count);
        }
    }
    if (splitter->messages && splitter->message_count > 1u) {
        dom_shard_message_sort(splitter->messages, splitter->message_count);
    }
    return 0;
}

#ifdef __cplusplus
} /* extern "C" */
#endif
