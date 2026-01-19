/*
Reference scheduler tests (EXEC2).
*/
#include <string.h>

#include "execution/scheduler/scheduler_single_thread.h"

#define TEST_CHECK(cond) do { if (!(cond)) return 1; } while (0)

typedef struct test_access_registry {
    dom_access_set *sets;
    u32 count;
} test_access_registry;

typedef struct test_law_state {
    u32 mode;
    u64 target_task;
    u32 calls;
    u32 refusal_code;
} test_law_state;

typedef struct audit_recorder {
    dom_audit_event events[64];
    u32 count;
} audit_recorder;

typedef struct test_ctx {
    test_access_registry access;
    test_law_state law;
    audit_recorder audit;
} test_ctx;

enum {
    LAW_MODE_ACCEPT = 0,
    LAW_MODE_REFUSE_TASK = 1,
    LAW_MODE_TRANSFORM_ONCE = 2
};

static const dom_access_set *lookup_access_set(const dom_execution_context *ctx,
                                               u64 access_set_id,
                                               void *user_data) {
    test_ctx *tctx = (test_ctx *)user_data;
    u32 i;
    (void)ctx;
    if (!tctx || !tctx->access.sets) {
        return 0;
    }
    for (i = 0u; i < tctx->access.count; ++i) {
        if (tctx->access.sets[i].access_id == access_set_id) {
            return &tctx->access.sets[i];
        }
    }
    return 0;
}

static dom_law_decision test_law_eval(const dom_execution_context *ctx,
                                      const dom_task_node *node,
                                      void *user_data) {
    test_ctx *tctx = (test_ctx *)user_data;
    dom_law_decision decision;
    (void)ctx;
    decision.kind = DOM_LAW_ACCEPT;
    decision.refusal_code = 0u;
    decision.transformed_fidelity_tier = 0u;
    decision.transformed_next_due_tick = DOM_EXEC_TICK_INVALID;
    if (!tctx || !node) {
        return decision;
    }
    tctx->law.calls += 1u;
    if (tctx->law.mode == LAW_MODE_REFUSE_TASK &&
        node->task_id == tctx->law.target_task) {
        decision.kind = DOM_LAW_REFUSE;
        decision.refusal_code = tctx->law.refusal_code;
        return decision;
    }
    if (tctx->law.mode == LAW_MODE_TRANSFORM_ONCE &&
        node->task_id == tctx->law.target_task &&
        tctx->law.calls == 1u) {
        decision.kind = DOM_LAW_TRANSFORM;
        decision.transformed_fidelity_tier = DOM_FID_MACRO;
        return decision;
    }
    return decision;
}

static void record_audit(const dom_execution_context *ctx,
                         const dom_audit_event *event,
                         void *user_data) {
    test_ctx *tctx = (test_ctx *)user_data;
    (void)ctx;
    if (!tctx || !event || tctx->audit.count >= 64u) {
        return;
    }
    tctx->audit.events[tctx->audit.count] = *event;
    tctx->audit.count += 1u;
}

class TestSink : public IScheduleSink {
public:
    TestSink() : count(0u) {}
    virtual void on_task(const dom_task_node &node,
                         const dom_law_decision &) {
        if (count < 16u) {
            task_ids[count] = node.task_id;
            fidelities[count] = node.fidelity_tier;
        }
        count += 1u;
    }
    u64 task_ids[16];
    u32 fidelities[16];
    u32 count;
};

static dom_task_node make_task(u64 task_id,
                               u32 phase_id,
                               u32 sub_index,
                               u64 access_set_id) {
    static const u32 law_targets[1] = { 1u };
    dom_task_node node;
    node.task_id = task_id;
    node.system_id = 1u;
    node.category = DOM_TASK_AUTHORITATIVE;
    node.determinism_class = DOM_DET_STRICT;
    node.fidelity_tier = DOM_FID_MICRO;
    node.next_due_tick = DOM_EXEC_TICK_INVALID;
    node.access_set_id = access_set_id;
    node.cost_model_id = 1u;
    node.law_targets = law_targets;
    node.law_target_count = 1u;
    node.phase_id = phase_id;
    node.commit_key.phase_id = phase_id;
    node.commit_key.task_id = task_id;
    node.commit_key.sub_index = sub_index;
    node.law_scope_ref = 1u;
    node.actor_ref = 0u;
    node.capability_set_ref = 0u;
    node.policy_params = 0;
    node.policy_params_size = 0u;
    return node;
}

static void init_ctx(dom_execution_context *ctx,
                     test_ctx *tctx,
                     audit_recorder *rec) {
    ctx->act_now = 0u;
    ctx->scope_chain = 0;
    ctx->capability_sets = 0;
    ctx->budget_snapshot = 0;
    ctx->determinism_mode = DOM_DET_MODE_STRICT;
    ctx->evaluate_law = test_law_eval;
    ctx->record_audit = record_audit;
    ctx->lookup_access_set = lookup_access_set;
    ctx->user_data = tctx;
    (void)rec;
}

static int test_stable_ordering(void) {
    dom_task_node tasks_a[3];
    dom_task_node tasks_b[3];
    dom_task_graph graph_a;
    dom_task_graph graph_b;
    dom_access_set sets[1];
    test_ctx tctx;
    audit_recorder *rec = 0;
    dom_execution_context ctx;
    dom_scheduler_single_thread sched;
    TestSink sink_a;
    TestSink sink_b;

    tasks_a[0] = make_task(1u, 1u, 0u, 1u);
    tasks_a[1] = make_task(2u, 1u, 0u, 1u);
    tasks_a[2] = make_task(3u, 1u, 0u, 1u);

    tasks_b[0] = tasks_a[0];
    tasks_b[1] = tasks_a[1];
    tasks_b[2] = tasks_a[2];

    sets[0].access_id = 1u;
    sets[0].read_ranges = 0;
    sets[0].read_count = 0u;
    sets[0].write_ranges = 0;
    sets[0].write_count = 0u;
    sets[0].reduce_ranges = 0;
    sets[0].reduce_count = 0u;
    sets[0].reduction_op = DOM_REDUCE_NONE;
    sets[0].commutative = D_FALSE;

    tctx.access.sets = sets;
    tctx.access.count = 1u;
    tctx.law.mode = LAW_MODE_ACCEPT;
    tctx.law.target_task = 0u;
    tctx.law.calls = 0u;
    tctx.law.refusal_code = 0u;
    tctx.audit.count = 0u;
    rec = &tctx.audit;
    init_ctx(&ctx, &tctx, rec);

    graph_a.graph_id = 1u;
    graph_a.epoch_id = 1u;
    graph_a.tasks = tasks_a;
    graph_a.task_count = 3u;
    graph_a.dependency_edges = 0;
    graph_a.dependency_count = 0u;
    graph_a.phase_barriers = 0;
    graph_a.phase_barrier_count = 0u;

    graph_b = graph_a;
    graph_b.tasks = tasks_b;

    sched.schedule(graph_a, ctx, sink_a);
    sched.schedule(graph_b, ctx, sink_b);

    TEST_CHECK(sink_a.count == sink_b.count);
    TEST_CHECK(sink_a.count == 3u);
    TEST_CHECK(sink_a.task_ids[0] == sink_b.task_ids[0]);
    TEST_CHECK(sink_a.task_ids[1] == sink_b.task_ids[1]);
    TEST_CHECK(sink_a.task_ids[2] == sink_b.task_ids[2]);
    return 0;
}

static int test_law_refusal(void) {
    dom_task_node tasks[2];
    dom_task_graph graph;
    dom_access_set sets[1];
    test_ctx tctx;
    audit_recorder *rec = 0;
    dom_execution_context ctx;
    dom_scheduler_single_thread sched;
    TestSink sink;
    u32 i;
    u32 refusals = 0u;

    tasks[0] = make_task(1u, 1u, 0u, 1u);
    tasks[1] = make_task(2u, 1u, 0u, 1u);

    sets[0].access_id = 1u;
    sets[0].read_ranges = 0;
    sets[0].read_count = 0u;
    sets[0].write_ranges = 0;
    sets[0].write_count = 0u;
    sets[0].reduce_ranges = 0;
    sets[0].reduce_count = 0u;
    sets[0].reduction_op = DOM_REDUCE_NONE;
    sets[0].commutative = D_FALSE;

    tctx.access.sets = sets;
    tctx.access.count = 1u;
    tctx.law.mode = LAW_MODE_REFUSE_TASK;
    tctx.law.target_task = 2u;
    tctx.law.calls = 0u;
    tctx.law.refusal_code = 77u;
    tctx.audit.count = 0u;
    rec = &tctx.audit;
    init_ctx(&ctx, &tctx, rec);

    graph.graph_id = 2u;
    graph.epoch_id = 1u;
    graph.tasks = tasks;
    graph.task_count = 2u;
    graph.dependency_edges = 0;
    graph.dependency_count = 0u;
    graph.phase_barriers = 0;
    graph.phase_barrier_count = 0u;

    sched.schedule(graph, ctx, sink);
    TEST_CHECK(sink.count == 1u);
    TEST_CHECK(sink.task_ids[0] == 1u);
    for (i = 0u; i < tctx.audit.count; ++i) {
        if (tctx.audit.events[i].event_id == DOM_EXEC_AUDIT_TASK_REFUSED &&
            tctx.audit.events[i].refusal_code == 77u) {
            refusals += 1u;
        }
    }
    TEST_CHECK(refusals == 1u);
    return 0;
}

static int test_transform(void) {
    dom_task_node tasks[1];
    dom_task_graph graph;
    dom_access_set sets[1];
    test_ctx tctx;
    audit_recorder *rec = 0;
    dom_execution_context ctx;
    dom_scheduler_single_thread sched;
    TestSink sink;

    tasks[0] = make_task(5u, 1u, 0u, 1u);

    sets[0].access_id = 1u;
    sets[0].read_ranges = 0;
    sets[0].read_count = 0u;
    sets[0].write_ranges = 0;
    sets[0].write_count = 0u;
    sets[0].reduce_ranges = 0;
    sets[0].reduce_count = 0u;
    sets[0].reduction_op = DOM_REDUCE_NONE;
    sets[0].commutative = D_FALSE;

    tctx.access.sets = sets;
    tctx.access.count = 1u;
    tctx.law.mode = LAW_MODE_TRANSFORM_ONCE;
    tctx.law.target_task = 5u;
    tctx.law.calls = 0u;
    tctx.law.refusal_code = 0u;
    tctx.audit.count = 0u;
    rec = &tctx.audit;
    init_ctx(&ctx, &tctx, rec);

    graph.graph_id = 3u;
    graph.epoch_id = 1u;
    graph.tasks = tasks;
    graph.task_count = 1u;
    graph.dependency_edges = 0;
    graph.dependency_count = 0u;
    graph.phase_barriers = 0;
    graph.phase_barrier_count = 0u;

    sched.schedule(graph, ctx, sink);
    TEST_CHECK(sink.count == 1u);
    TEST_CHECK(sink.fidelities[0] == DOM_FID_MACRO);
    TEST_CHECK(tctx.law.calls >= 2u);
    return 0;
}

static int test_access_conflict(void) {
    dom_task_node tasks[2];
    dom_task_graph graph;
    dom_access_range write_ranges[2];
    dom_access_set sets[2];
    test_ctx tctx;
    audit_recorder *rec = 0;
    dom_execution_context ctx;
    dom_scheduler_single_thread sched;
    TestSink sink;
    u32 i;
    u32 refusals = 0u;

    tasks[0] = make_task(1u, 1u, 0u, 1u);
    tasks[1] = make_task(2u, 1u, 0u, 2u);

    write_ranges[0].kind = DOM_RANGE_INDEX_RANGE;
    write_ranges[0].component_id = 1u;
    write_ranges[0].field_id = 1u;
    write_ranges[0].start_id = 0u;
    write_ranges[0].end_id = 10u;
    write_ranges[0].set_id = 0u;

    write_ranges[1] = write_ranges[0];
    write_ranges[1].start_id = 5u;
    write_ranges[1].end_id = 6u;

    sets[0].access_id = 1u;
    sets[0].read_ranges = 0;
    sets[0].read_count = 0u;
    sets[0].write_ranges = &write_ranges[0];
    sets[0].write_count = 1u;
    sets[0].reduce_ranges = 0;
    sets[0].reduce_count = 0u;
    sets[0].reduction_op = DOM_REDUCE_NONE;
    sets[0].commutative = D_FALSE;

    sets[1].access_id = 2u;
    sets[1].read_ranges = 0;
    sets[1].read_count = 0u;
    sets[1].write_ranges = &write_ranges[1];
    sets[1].write_count = 1u;
    sets[1].reduce_ranges = 0;
    sets[1].reduce_count = 0u;
    sets[1].reduction_op = DOM_REDUCE_NONE;
    sets[1].commutative = D_FALSE;

    tctx.access.sets = sets;
    tctx.access.count = 2u;
    tctx.law.mode = LAW_MODE_ACCEPT;
    tctx.law.target_task = 0u;
    tctx.law.calls = 0u;
    tctx.law.refusal_code = 0u;
    tctx.audit.count = 0u;
    rec = &tctx.audit;
    init_ctx(&ctx, &tctx, rec);

    graph.graph_id = 4u;
    graph.epoch_id = 1u;
    graph.tasks = tasks;
    graph.task_count = 2u;
    graph.dependency_edges = 0;
    graph.dependency_count = 0u;
    graph.phase_barriers = 0;
    graph.phase_barrier_count = 0u;

    sched.schedule(graph, ctx, sink);
    TEST_CHECK(sink.count == 1u);
    for (i = 0u; i < tctx.audit.count; ++i) {
        if (tctx.audit.events[i].event_id == DOM_EXEC_AUDIT_TASK_REFUSED &&
            tctx.audit.events[i].refusal_code == DOM_EXEC_REFUSE_CONFLICT) {
            refusals += 1u;
        }
    }
    TEST_CHECK(refusals == 1u);
    return 0;
}

static int test_commit_order(void) {
    dom_task_node tasks[2];
    dom_dependency_edge edges[1];
    dom_task_graph graph;
    dom_access_set sets[1];
    test_ctx tctx;
    audit_recorder *rec = 0;
    dom_execution_context ctx;
    dom_scheduler_single_thread sched;
    TestSink sink;
    u64 committed[2];
    u32 commit_count = 0u;
    u32 i;

    tasks[0] = make_task(1u, 1u, 0u, 1u);
    tasks[1] = make_task(2u, 1u, 0u, 1u);

    edges[0].from_task_id = 2u;
    edges[0].to_task_id = 1u;
    edges[0].reason_id = 0u;

    sets[0].access_id = 1u;
    sets[0].read_ranges = 0;
    sets[0].read_count = 0u;
    sets[0].write_ranges = 0;
    sets[0].write_count = 0u;
    sets[0].reduce_ranges = 0;
    sets[0].reduce_count = 0u;
    sets[0].reduction_op = DOM_REDUCE_NONE;
    sets[0].commutative = D_FALSE;

    tctx.access.sets = sets;
    tctx.access.count = 1u;
    tctx.law.mode = LAW_MODE_ACCEPT;
    tctx.law.target_task = 0u;
    tctx.law.calls = 0u;
    tctx.law.refusal_code = 0u;
    tctx.audit.count = 0u;
    rec = &tctx.audit;
    init_ctx(&ctx, &tctx, rec);

    graph.graph_id = 5u;
    graph.epoch_id = 1u;
    graph.tasks = tasks;
    graph.task_count = 2u;
    graph.dependency_edges = edges;
    graph.dependency_count = 1u;
    graph.phase_barriers = 0;
    graph.phase_barrier_count = 0u;

    sched.schedule(graph, ctx, sink);
    TEST_CHECK(sink.count == 2u);
    TEST_CHECK(sink.task_ids[0] == 2u);
    TEST_CHECK(sink.task_ids[1] == 1u);

    for (i = 0u; i < tctx.audit.count; ++i) {
        if (tctx.audit.events[i].event_id == DOM_EXEC_AUDIT_TASK_COMMITTED) {
            committed[commit_count] = tctx.audit.events[i].task_id;
            commit_count += 1u;
        }
    }
    TEST_CHECK(commit_count == 2u);
    TEST_CHECK(committed[0] == 1u);
    TEST_CHECK(committed[1] == 2u);
    return 0;
}

static int test_phase_barrier(void) {
    dom_task_node tasks[2];
    dom_task_graph graph;
    dom_access_set sets[1];
    test_ctx tctx;
    audit_recorder *rec = 0;
    dom_execution_context ctx;
    dom_scheduler_single_thread sched;
    TestSink sink;

    tasks[0] = make_task(1u, 1u, 0u, 1u);
    tasks[1] = make_task(2u, 2u, 0u, 1u);

    sets[0].access_id = 1u;
    sets[0].read_ranges = 0;
    sets[0].read_count = 0u;
    sets[0].write_ranges = 0;
    sets[0].write_count = 0u;
    sets[0].reduce_ranges = 0;
    sets[0].reduce_count = 0u;
    sets[0].reduction_op = DOM_REDUCE_NONE;
    sets[0].commutative = D_FALSE;

    tctx.access.sets = sets;
    tctx.access.count = 1u;
    tctx.law.mode = LAW_MODE_ACCEPT;
    tctx.law.target_task = 0u;
    tctx.law.calls = 0u;
    tctx.law.refusal_code = 0u;
    tctx.audit.count = 0u;
    rec = &tctx.audit;
    init_ctx(&ctx, &tctx, rec);

    graph.graph_id = 6u;
    graph.epoch_id = 1u;
    graph.tasks = tasks;
    graph.task_count = 2u;
    graph.dependency_edges = 0;
    graph.dependency_count = 0u;
    graph.phase_barriers = 0;
    graph.phase_barrier_count = 0u;

    sched.schedule(graph, ctx, sink);
    TEST_CHECK(sink.count == 2u);
    TEST_CHECK(sink.task_ids[0] == 1u);
    TEST_CHECK(sink.task_ids[1] == 2u);
    return 0;
}

int main(void) {
    if (test_stable_ordering() != 0) return 1;
    if (test_law_refusal() != 0) return 1;
    if (test_transform() != 0) return 1;
    if (test_access_conflict() != 0) return 1;
    if (test_commit_order() != 0) return 1;
    if (test_phase_barrier() != 0) return 1;
    return 0;
}
