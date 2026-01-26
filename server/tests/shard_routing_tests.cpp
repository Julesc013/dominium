/*
Shard routing tests (DIST1).
*/
#include "shard/shard_api.h"
#include "shard/task_splitter.h"
#include "shard/message_bus.h"
#include "shard/shard_executor.h"

#include "domino/execution/access_set.h"
#include "domino/execution/scheduler_iface.h"

#include <stdio.h>
#include <string.h>

#define EXPECT(cond, msg) do { \
    if (!(cond)) { \
        fprintf(stderr, "FAIL: %s\n", msg); \
        return 1; \
    } \
} while (0)

static u64 fnv1a_init(void)
{
    return 1469598103934665603ULL;
}

static u64 fnv1a_u64(u64 h, u64 v)
{
    u32 i;
    for (i = 0u; i < 8u; ++i) {
        h ^= (u64)((v >> (i * 8u)) & 0xFFu);
        h *= 1099511628211ULL;
    }
    return h;
}

static u64 fnv1a_u32(u64 h, u32 v)
{
    u32 i;
    for (i = 0u; i < 4u; ++i) {
        h ^= (u64)((v >> (i * 8u)) & 0xFFu);
        h *= 1099511628211ULL;
    }
    return h;
}

static u64 fnv1a_pair(u64 a, u64 b)
{
    u64 h = 1469598103934665603ULL;
    h ^= a;
    h *= 1099511628211ULL;
    h ^= b;
    h *= 1099511628211ULL;
    return h;
}

typedef struct access_set_table {
    dom_access_set* sets;
    u32 count;
} access_set_table;

static const dom_access_set* lookup_access_set(const dom_execution_context* ctx,
                                               u64 access_set_id,
                                               void* user_data)
{
    access_set_table* table = (access_set_table*)user_data;
    u32 i;
    (void)ctx;
    if (!table || !table->sets) {
        return 0;
    }
    for (i = 0u; i < table->count; ++i) {
        if (table->sets[i].access_id == access_set_id) {
            return &table->sets[i];
        }
    }
    return 0;
}

static dom_law_decision law_accept(const dom_execution_context* ctx,
                                   const dom_task_node* node,
                                   void* user_data)
{
    dom_law_decision decision;
    (void)ctx;
    (void)node;
    (void)user_data;
    decision.kind = DOM_LAW_ACCEPT;
    decision.refusal_code = 0u;
    decision.transformed_fidelity_tier = 0u;
    decision.transformed_next_due_tick = DOM_EXEC_TICK_INVALID;
    return decision;
}

class TestScheduler : public IScheduler {
public:
    virtual void schedule(const dom_task_graph &graph,
                          dom_execution_context &ctx,
                          IScheduleSink &sink)
    {
        u32 i;
        for (i = 0u; i < graph.task_count; ++i) {
            const dom_task_node& node = graph.tasks[i];
            dom_law_decision decision = dom_execution_context_evaluate_law(&ctx, &node);
            sink.on_task(node, decision);
        }
    }
};

static void seed_registry(dom_shard_registry* registry, dom_shard* storage, u32 capacity)
{
    dom_shard shard;
    dom_shard_registry_init(registry, storage, capacity);

    shard.shard_id = 1u;
    shard.scope.kind = DOM_SHARD_SCOPE_ENTITY_RANGE;
    shard.scope.start_id = 0u;
    shard.scope.end_id = 999u;
    shard.scope.domain_tag = 0u;
    shard.determinism_domain = 10u;
    dom_shard_registry_add(registry, &shard);

    shard.shard_id = 2u;
    shard.scope.kind = DOM_SHARD_SCOPE_ENTITY_RANGE;
    shard.scope.start_id = 1000u;
    shard.scope.end_id = 1999u;
    shard.scope.domain_tag = 0u;
    shard.determinism_domain = 10u;
    dom_shard_registry_add(registry, &shard);
}

static void seed_graph(dom_task_graph* graph,
                       dom_task_node* tasks,
                       dom_dependency_edge* edges,
                       u32* out_task_count,
                       u32* out_edge_count)
{
    memset(tasks, 0, sizeof(dom_task_node) * 3u);
    tasks[0].task_id = 1001u;
    tasks[0].system_id = 5001u;
    tasks[0].category = DOM_TASK_AUTHORITATIVE;
    tasks[0].determinism_class = DOM_DET_STRICT;
    tasks[0].access_set_id = 2001u;
    tasks[0].phase_id = 1u;
    tasks[0].commit_key.phase_id = 1u;
    tasks[0].commit_key.task_id = tasks[0].task_id;
    tasks[0].commit_key.sub_index = 0u;
    tasks[0].next_due_tick = 5u;

    tasks[1].task_id = 1002u;
    tasks[1].system_id = 5001u;
    tasks[1].category = DOM_TASK_AUTHORITATIVE;
    tasks[1].determinism_class = DOM_DET_STRICT;
    tasks[1].access_set_id = 2002u;
    tasks[1].phase_id = 2u;
    tasks[1].commit_key.phase_id = 2u;
    tasks[1].commit_key.task_id = tasks[1].task_id;
    tasks[1].commit_key.sub_index = 0u;
    tasks[1].next_due_tick = 7u;

    tasks[2].task_id = 1003u;
    tasks[2].system_id = 5002u;
    tasks[2].category = DOM_TASK_DERIVED;
    tasks[2].determinism_class = DOM_DET_DERIVED;
    tasks[2].access_set_id = 2003u;
    tasks[2].phase_id = 3u;
    tasks[2].commit_key.phase_id = 3u;
    tasks[2].commit_key.task_id = tasks[2].task_id;
    tasks[2].commit_key.sub_index = 0u;
    tasks[2].next_due_tick = DOM_EXEC_TICK_INVALID;

    edges[0].from_task_id = 1001u;
    edges[0].to_task_id = 1002u;
    edges[0].reason_id = 0u;
    edges[1].from_task_id = 1002u;
    edges[1].to_task_id = 1003u;
    edges[1].reason_id = 0u;

    graph->graph_id = 900u;
    graph->epoch_id = 1u;
    graph->tasks = tasks;
    graph->task_count = 3u;
    graph->dependency_edges = edges;
    graph->dependency_count = 2u;
    graph->phase_barriers = 0;
    graph->phase_barrier_count = 0u;

    if (out_task_count) {
        *out_task_count = 3u;
    }
    if (out_edge_count) {
        *out_edge_count = 2u;
    }
}

static void seed_access_sets(dom_access_set* sets,
                             dom_access_range* ranges)
{
    ranges[0].kind = DOM_RANGE_INDEX_RANGE;
    ranges[0].start_id = 100u;
    ranges[0].end_id = 100u;
    ranges[0].set_id = 0u;
    ranges[0].component_id = 0u;
    ranges[0].field_id = 0u;

    ranges[1].kind = DOM_RANGE_INDEX_RANGE;
    ranges[1].start_id = 1500u;
    ranges[1].end_id = 1500u;
    ranges[1].set_id = 0u;
    ranges[1].component_id = 0u;
    ranges[1].field_id = 0u;

    ranges[2].kind = DOM_RANGE_ENTITY_SET;
    ranges[2].start_id = 0u;
    ranges[2].end_id = 0u;
    ranges[2].set_id = 100u;
    ranges[2].component_id = 0u;
    ranges[2].field_id = 0u;

    sets[0].access_id = 2001u;
    sets[0].read_ranges = 0;
    sets[0].read_count = 0u;
    sets[0].write_ranges = &ranges[0];
    sets[0].write_count = 1u;
    sets[0].reduce_ranges = 0;
    sets[0].reduce_count = 0u;
    sets[0].reduction_op = DOM_REDUCE_NONE;
    sets[0].commutative = D_FALSE;

    sets[1].access_id = 2002u;
    sets[1].read_ranges = 0;
    sets[1].read_count = 0u;
    sets[1].write_ranges = &ranges[1];
    sets[1].write_count = 1u;
    sets[1].reduce_ranges = 0;
    sets[1].reduce_count = 0u;
    sets[1].reduction_op = DOM_REDUCE_NONE;
    sets[1].commutative = D_FALSE;

    sets[2].access_id = 2003u;
    sets[2].read_ranges = &ranges[2];
    sets[2].read_count = 1u;
    sets[2].write_ranges = 0;
    sets[2].write_count = 0u;
    sets[2].reduce_ranges = 0;
    sets[2].reduce_count = 0u;
    sets[2].reduction_op = DOM_REDUCE_NONE;
    sets[2].commutative = D_FALSE;
}

static u64 hash_shard_graph(const dom_shard_task_graph* graph)
{
    u32 i;
    u64 h = fnv1a_init();
    if (!graph) {
        return h;
    }
    h = fnv1a_u32(h, graph->task_count);
    h = fnv1a_u32(h, graph->edge_count);
    for (i = 0u; i < graph->task_count; ++i) {
        const dom_task_node* node = &graph->tasks[i];
        h = fnv1a_u64(h, node->task_id);
        h = fnv1a_u64(h, node->system_id);
        h = fnv1a_u32(h, node->category);
        h = fnv1a_u32(h, node->determinism_class);
        h = fnv1a_u64(h, node->access_set_id);
    }
    for (i = 0u; i < graph->edge_count; ++i) {
        const dom_dependency_edge* edge = &graph->edges[i];
        h = fnv1a_u64(h, edge->from_task_id);
        h = fnv1a_u64(h, edge->to_task_id);
        h = fnv1a_u32(h, edge->reason_id);
    }
    return h;
}

static u64 hash_messages(const dom_shard_message* messages, u32 count)
{
    u32 i;
    u64 h = fnv1a_init();
    if (!messages) {
        return h;
    }
    h = fnv1a_u32(h, count);
    for (i = 0u; i < count; ++i) {
        h = fnv1a_u64(h, messages[i].message_id);
        h = fnv1a_u64(h, messages[i].task_id);
        h = fnv1a_u32(h, messages[i].source_shard);
        h = fnv1a_u32(h, messages[i].target_shard);
        h = fnv1a_u64(h, messages[i].arrival_tick);
    }
    return h;
}

static u64 hash_log_entries(const dom_shard_log* log)
{
    u32 i;
    u64 h = fnv1a_init();
    if (!log) {
        return h;
    }
    h = fnv1a_u32(h, log->event_count);
    for (i = 0u; i < log->event_count; ++i) {
        const dom_shard_event_entry* entry = &log->events[i];
        h = fnv1a_u64(h, entry->task_id);
        h = fnv1a_u64(h, (u64)entry->tick);
    }
    return h;
}

static const dom_task_node* find_task(const dom_task_graph* graph, u64 task_id)
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

static u64 owner_id_from_range(const dom_access_range* range)
{
    if (!range) {
        return 0u;
    }
    if (range->kind == DOM_RANGE_INDEX_RANGE || range->kind == DOM_RANGE_SINGLE) {
        return range->start_id;
    }
    return range->set_id;
}

static u64 owner_id_from_access(const dom_execution_context* ctx,
                                const dom_task_node* node)
{
    const dom_access_set* set = dom_execution_context_lookup_access_set(ctx, node->access_set_id);
    const dom_access_range* range = 0;
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
    return owner_id_from_range(range);
}

static u64 hash_unsharded_partition(const dom_shard_log* log,
                                    const dom_task_graph* graph,
                                    const dom_execution_context* ctx,
                                    const dom_shard_registry* registry,
                                    dom_shard_id shard_id)
{
    u32 i;
    u32 count = 0u;
    u64 h = fnv1a_init();
    if (!log) {
        return h;
    }
    for (i = 0u; i < log->event_count; ++i) {
        const dom_shard_event_entry* entry = &log->events[i];
        const dom_task_node* node = find_task(graph, entry->task_id);
        dom_shard_id owner = dom_shard_find_owner(registry, owner_id_from_access(ctx, node));
        if (owner == shard_id) {
            count += 1u;
        }
    }
    h = fnv1a_u32(h, count);
    for (i = 0u; i < log->event_count; ++i) {
        const dom_shard_event_entry* entry = &log->events[i];
        const dom_task_node* node = find_task(graph, entry->task_id);
        dom_shard_id owner = dom_shard_find_owner(registry, owner_id_from_access(ctx, node));
        if (owner == shard_id) {
            h = fnv1a_u64(h, entry->task_id);
            h = fnv1a_u64(h, (u64)entry->tick);
        }
    }
    return h;
}

static int test_deterministic_partitioning(void)
{
    dom_task_node tasks[3];
    dom_dependency_edge edges[2];
    dom_task_graph graph;
    dom_access_set sets[3];
    dom_access_range ranges[3];
    access_set_table table;
    dom_execution_context ctx;
    dom_shard_registry registry;
    dom_shard shards[2];

    dom_shard_task_graph shard_graphs_a[2];
    dom_shard_task_graph shard_graphs_b[2];
    dom_task_node shard_tasks_a[2][4];
    dom_task_node shard_tasks_b[2][4];
    dom_dependency_edge shard_edges_a[2][4];
    dom_dependency_edge shard_edges_b[2][4];
    dom_shard_task_mapping map_a[4];
    dom_shard_task_mapping map_b[4];
    dom_shard_message messages_a[4];
    dom_shard_message messages_b[4];
    dom_shard_task_splitter splitter_a;
    dom_shard_task_splitter splitter_b;
    u64 hash_a;
    u64 hash_b;

    seed_registry(&registry, shards, 2u);
    seed_graph(&graph, tasks, edges, 0, 0);
    seed_access_sets(sets, ranges);

    table.sets = sets;
    table.count = 3u;
    ctx.act_now = 0u;
    ctx.scope_chain = 0;
    ctx.capability_sets = 0;
    ctx.budget_snapshot = 0;
    ctx.determinism_mode = DOM_DET_MODE_STRICT;
    ctx.evaluate_law = law_accept;
    ctx.record_audit = 0;
    ctx.lookup_access_set = lookup_access_set;
    ctx.user_data = &table;

    dom_shard_task_graph_init(&shard_graphs_a[0], 1u, shard_tasks_a[0], 4u, shard_edges_a[0], 4u);
    dom_shard_task_graph_init(&shard_graphs_a[1], 2u, shard_tasks_a[1], 4u, shard_edges_a[1], 4u);
    dom_shard_task_graph_init(&shard_graphs_b[0], 1u, shard_tasks_b[0], 4u, shard_edges_b[0], 4u);
    dom_shard_task_graph_init(&shard_graphs_b[1], 2u, shard_tasks_b[1], 4u, shard_edges_b[1], 4u);

    dom_shard_task_splitter_init(&splitter_a, shard_graphs_a, 2u, map_a, 4u, messages_a, 4u);
    dom_shard_task_splitter_init(&splitter_b, shard_graphs_b, 2u, map_b, 4u, messages_b, 4u);

    EXPECT(dom_shard_task_splitter_split(&splitter_a, &graph, &registry, &ctx, 1u) == 0, "split A");
    EXPECT(dom_shard_task_splitter_split(&splitter_b, &graph, &registry, &ctx, 1u) == 0, "split B");

    hash_a = hash_shard_graph(&shard_graphs_a[0]) ^ hash_shard_graph(&shard_graphs_a[1]) ^ hash_messages(messages_a, splitter_a.message_count);
    hash_b = hash_shard_graph(&shard_graphs_b[0]) ^ hash_shard_graph(&shard_graphs_b[1]) ^ hash_messages(messages_b, splitter_b.message_count);
    EXPECT(hash_a == hash_b, "partitioning determinism mismatch");
    return 0;
}

static int test_message_emission(void)
{
    dom_task_node tasks[3];
    dom_dependency_edge edges[2];
    dom_task_graph graph;
    dom_access_set sets[3];
    dom_access_range ranges[3];
    access_set_table table;
    dom_execution_context ctx;
    dom_shard_registry registry;
    dom_shard shards[2];
    dom_shard_task_graph shard_graphs[2];
    dom_task_node shard_tasks[2][4];
    dom_dependency_edge shard_edges[2][4];
    dom_shard_task_mapping map[4];
    dom_shard_message messages[4];
    dom_shard_task_splitter splitter;
    u64 expected_a;
    u64 expected_b;

    seed_registry(&registry, shards, 2u);
    seed_graph(&graph, tasks, edges, 0, 0);
    seed_access_sets(sets, ranges);

    table.sets = sets;
    table.count = 3u;
    ctx.act_now = 0u;
    ctx.scope_chain = 0;
    ctx.capability_sets = 0;
    ctx.budget_snapshot = 0;
    ctx.determinism_mode = DOM_DET_MODE_STRICT;
    ctx.evaluate_law = law_accept;
    ctx.record_audit = 0;
    ctx.lookup_access_set = lookup_access_set;
    ctx.user_data = &table;

    dom_shard_task_graph_init(&shard_graphs[0], 1u, shard_tasks[0], 4u, shard_edges[0], 4u);
    dom_shard_task_graph_init(&shard_graphs[1], 2u, shard_tasks[1], 4u, shard_edges[1], 4u);
    dom_shard_task_splitter_init(&splitter, shard_graphs, 2u, map, 4u, messages, 4u);

    EXPECT(dom_shard_task_splitter_split(&splitter, &graph, &registry, &ctx, 1u) == 0, "split");
    EXPECT(splitter.message_count == 2u, "expected two cross-shard messages");

    expected_a = fnv1a_pair(1001u, 1002u);
    expected_b = fnv1a_pair(1002u, 1003u);
    EXPECT(messages[0].message_id == expected_a || messages[1].message_id == expected_a,
           "missing message for A->B");
    EXPECT(messages[0].message_id == expected_b || messages[1].message_id == expected_b,
           "missing message for B->C");
    EXPECT(messages[0].arrival_tick <= messages[1].arrival_tick, "message order");
    return 0;
}

static int test_message_ordering(void)
{
    dom_shard_message_bus bus;
    dom_shard_message storage[3];
    dom_shard_message msg;
    dom_shard_message out;
    int res;

    dom_shard_message_bus_init(&bus, storage, 3u);

    msg.source_shard = 1u;
    msg.target_shard = 2u;
    msg.task_id = 1001u;
    msg.payload = 0;
    msg.payload_size = 0u;

    msg.arrival_tick = 10u;
    msg.message_id = 5u;
    dom_shard_message_bus_enqueue(&bus, &msg);

    msg.arrival_tick = 5u;
    msg.message_id = 7u;
    dom_shard_message_bus_enqueue(&bus, &msg);

    msg.arrival_tick = 5u;
    msg.message_id = 2u;
    dom_shard_message_bus_enqueue(&bus, &msg);

    res = dom_shard_message_bus_pop_ready(&bus, 10u, &out);
    EXPECT(res == 0, "pop ready 1");
    EXPECT(out.arrival_tick == 5u && out.message_id == 2u, "order 1");
    res = dom_shard_message_bus_pop_ready(&bus, 10u, &out);
    EXPECT(res == 0, "pop ready 2");
    EXPECT(out.arrival_tick == 5u && out.message_id == 7u, "order 2");
    res = dom_shard_message_bus_pop_ready(&bus, 10u, &out);
    EXPECT(res == 0, "pop ready 3");
    EXPECT(out.arrival_tick == 10u && out.message_id == 5u, "order 3");
    return 0;
}

static int test_illegal_placement_refused(void)
{
    dom_task_node tasks[3];
    dom_dependency_edge edges[2];
    dom_task_graph graph;
    dom_access_set sets[3];
    dom_access_range ranges[3];
    access_set_table table;
    dom_execution_context ctx;
    dom_shard_registry registry;
    dom_shard shards[2];
    dom_shard_message_bus bus;
    dom_shard_message bus_storage[4];
    dom_shard_log log;
    dom_shard_event_entry events[8];
    dom_shard_message messages[4];
    dom_shard_executor executor;
    u64 accepted[8];
    TestScheduler scheduler;

    seed_registry(&registry, shards, 2u);
    seed_graph(&graph, tasks, edges, 0, 0);
    seed_access_sets(sets, ranges);

    table.sets = sets;
    table.count = 3u;
    ctx.act_now = 0u;
    ctx.scope_chain = 0;
    ctx.capability_sets = 0;
    ctx.budget_snapshot = 0;
    ctx.determinism_mode = DOM_DET_MODE_STRICT;
    ctx.evaluate_law = law_accept;
    ctx.record_audit = 0;
    ctx.lookup_access_set = lookup_access_set;
    ctx.user_data = &table;

    dom_shard_message_bus_init(&bus, bus_storage, 4u);
    dom_shard_log_init(&log, events, 8u, messages, 4u);

    dom_shard_executor_init(&executor, 1u, &scheduler, &ctx, &bus, &log, accepted, 8u);
    EXPECT(dom_shard_executor_execute(&executor, &graph, &registry, 0, 0u) != 0,
           "illegal placement should be refused");
    return 0;
}

static int test_replay_equivalence(void)
{
    dom_task_node tasks[3];
    dom_dependency_edge edges[2];
    dom_task_graph graph;
    dom_access_set sets[3];
    dom_access_range ranges[3];
    access_set_table table;
    dom_execution_context ctx;
    dom_shard_registry registry;
    dom_shard shards[2];
    dom_shard_task_graph shard_graphs[2];
    dom_task_node shard_tasks[2][4];
    dom_dependency_edge shard_edges[2][4];
    dom_shard_task_mapping map[4];
    dom_shard_message messages[4];
    dom_shard_task_splitter splitter;
    dom_shard_message_bus bus;
    dom_shard_message bus_storage[8];
    dom_shard_log logs[2];
    dom_shard_event_entry events_a[8];
    dom_shard_event_entry events_b[8];
    dom_shard_message msg_log_storage_a[4];
    dom_shard_message msg_log_storage_b[4];
    dom_shard_executor exec_a;
    dom_shard_executor exec_b;
    u64 accepted_a[8];
    u64 accepted_b[8];
    TestScheduler scheduler;
    u64 shard_hash_a;
    u64 shard_hash_b;

    dom_shard_registry registry_single;
    dom_shard shard_single;
    dom_shard_task_graph single_graph;
    dom_task_node single_tasks[4];
    dom_dependency_edge single_edges[4];
    dom_shard_task_mapping single_map[4];
    dom_shard_message single_messages[4];
    dom_shard_message msg_log_storage_single[4];
    dom_shard_task_splitter splitter_single;
    dom_shard_log single_log;
    dom_shard_event_entry single_events[8];
    u64 accepted_single[8];
    dom_shard_executor exec_single;
    u64 unsharded_a;
    u64 unsharded_b;

    seed_registry(&registry, shards, 2u);
    seed_graph(&graph, tasks, edges, 0, 0);
    seed_access_sets(sets, ranges);

    table.sets = sets;
    table.count = 3u;
    ctx.act_now = 0u;
    ctx.scope_chain = 0;
    ctx.capability_sets = 0;
    ctx.budget_snapshot = 0;
    ctx.determinism_mode = DOM_DET_MODE_STRICT;
    ctx.evaluate_law = law_accept;
    ctx.record_audit = 0;
    ctx.lookup_access_set = lookup_access_set;
    ctx.user_data = &table;

    dom_shard_task_graph_init(&shard_graphs[0], 1u, shard_tasks[0], 4u, shard_edges[0], 4u);
    dom_shard_task_graph_init(&shard_graphs[1], 2u, shard_tasks[1], 4u, shard_edges[1], 4u);
    dom_shard_task_splitter_init(&splitter, shard_graphs, 2u, map, 4u, messages, 4u);
    EXPECT(dom_shard_task_splitter_split(&splitter, &graph, &registry, &ctx, 1u) == 0, "split");

    dom_shard_message_bus_init(&bus, bus_storage, 8u);
    dom_shard_log_init(&logs[0], events_a, 8u, msg_log_storage_a, 4u);
    dom_shard_log_init(&logs[1], events_b, 8u, msg_log_storage_b, 4u);

    dom_shard_executor_init(&exec_a, 1u, &scheduler, &ctx, &bus, &logs[0], accepted_a, 8u);
    dom_shard_executor_init(&exec_b, 2u, &scheduler, &ctx, &bus, &logs[1], accepted_b, 8u);
    EXPECT(dom_shard_executor_execute(&exec_a, &shard_graphs[0].graph, &registry,
                                      messages, splitter.message_count) == 0, "exec shard a");
    EXPECT(dom_shard_executor_execute(&exec_b, &shard_graphs[1].graph, &registry,
                                      messages, splitter.message_count) == 0, "exec shard b");

    shard_hash_a = hash_log_entries(&logs[0]);
    shard_hash_b = hash_log_entries(&logs[1]);

    dom_shard_registry_init(&registry_single, &shard_single, 1u);
    shard_single.shard_id = 1u;
    shard_single.scope.kind = DOM_SHARD_SCOPE_ENTITY_RANGE;
    shard_single.scope.start_id = 0u;
    shard_single.scope.end_id = 1999u;
    shard_single.scope.domain_tag = 0u;
    shard_single.determinism_domain = 10u;
    dom_shard_registry_add(&registry_single, &shard_single);

    dom_shard_task_graph_init(&single_graph, 1u, single_tasks, 4u, single_edges, 4u);
    dom_shard_task_splitter_init(&splitter_single, &single_graph, 1u,
                                 single_map, 4u, single_messages, 4u);
    EXPECT(dom_shard_task_splitter_split(&splitter_single, &graph, &registry_single, &ctx, 1u) == 0,
           "split single");

    dom_shard_log_init(&single_log, single_events, 8u, msg_log_storage_single, 4u);
    dom_shard_executor_init(&exec_single, 1u, &scheduler, &ctx, &bus, &single_log, accepted_single, 8u);
    EXPECT(dom_shard_executor_execute(&exec_single, &single_graph.graph, &registry_single,
                                      0, 0u) == 0, "exec single");

    unsharded_a = hash_unsharded_partition(&single_log, &graph, &ctx, &registry, 1u);
    unsharded_b = hash_unsharded_partition(&single_log, &graph, &ctx, &registry, 2u);

    EXPECT(shard_hash_a == unsharded_a, "shard A replay mismatch");
    EXPECT(shard_hash_b == unsharded_b, "shard B replay mismatch");
    return 0;
}

int main(void)
{
    if (test_deterministic_partitioning() != 0) return 1;
    if (test_message_emission() != 0) return 1;
    if (test_message_ordering() != 0) return 1;
    if (test_illegal_placement_refused() != 0) return 1;
    if (test_replay_equivalence() != 0) return 1;
    return 0;
}
