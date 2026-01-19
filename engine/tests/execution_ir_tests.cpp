/*
Execution IR runtime tests.
*/
#include <string.h>

#include "domino/execution/task_graph.h"
#include "domino/execution/access_set.h"
#include "domino/execution/execution_context.h"
#include "domino/execution/scheduler_iface.h"

#define TEST_CHECK(cond) do { if (!(cond)) return 1; } while (0)

static dom_task_node make_task(u64 task_id, u32 phase_id, u32 sub_index) {
    dom_task_node node;
    static const u32 law_targets[1] = { 1u };
    node.task_id = task_id;
    node.system_id = 1u;
    node.category = DOM_TASK_AUTHORITATIVE;
    node.determinism_class = DOM_DET_STRICT;
    node.fidelity_tier = DOM_FID_MICRO;
    node.next_due_tick = DOM_EXEC_TICK_INVALID;
    node.access_set_id = 1u;
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

static int test_deterministic_ordering(void) {
    dom_task_node tasks_a[3];
    dom_task_node tasks_b[3];

    tasks_a[0] = make_task(5u, 2u, 0u);
    tasks_a[1] = make_task(1u, 1u, 0u);
    tasks_a[2] = make_task(3u, 1u, 1u);

    tasks_b[0] = tasks_a[2];
    tasks_b[1] = tasks_a[0];
    tasks_b[2] = tasks_a[1];

    dom_stable_task_sort(tasks_a, 3u);
    dom_stable_task_sort(tasks_b, 3u);

    TEST_CHECK(dom_task_graph_is_sorted(tasks_a, 3u) == D_TRUE);
    TEST_CHECK(dom_task_graph_is_sorted(tasks_b, 3u) == D_TRUE);
    TEST_CHECK(dom_task_node_compare(&tasks_a[0], &tasks_b[0]) == 0);
    TEST_CHECK(dom_task_node_compare(&tasks_a[1], &tasks_b[1]) == 0);
    TEST_CHECK(dom_task_node_compare(&tasks_a[2], &tasks_b[2]) == 0);
    return 0;
}

static int test_access_conflicts(void) {
    dom_access_range read_ranges[1];
    dom_access_range write_ranges_a[1];
    dom_access_range write_ranges_b[1];
    dom_access_set set_a;
    dom_access_set set_b;

    read_ranges[0].kind = DOM_RANGE_INDEX_RANGE;
    read_ranges[0].component_id = 1u;
    read_ranges[0].field_id = 1u;
    read_ranges[0].start_id = 0u;
    read_ranges[0].end_id = 10u;
    read_ranges[0].set_id = 0u;

    write_ranges_a[0] = read_ranges[0];
    write_ranges_b[0] = read_ranges[0];
    write_ranges_b[0].start_id = 20u;
    write_ranges_b[0].end_id = 30u;

    set_a.access_id = 1u;
    set_a.read_ranges = read_ranges;
    set_a.read_count = 1u;
    set_a.write_ranges = write_ranges_a;
    set_a.write_count = 1u;
    set_a.reduce_ranges = 0;
    set_a.reduce_count = 0u;
    set_a.reduction_op = DOM_REDUCE_NONE;
    set_a.commutative = D_FALSE;

    set_b.access_id = 2u;
    set_b.read_ranges = 0;
    set_b.read_count = 0u;
    set_b.write_ranges = write_ranges_b;
    set_b.write_count = 1u;
    set_b.reduce_ranges = 0;
    set_b.reduce_count = 0u;
    set_b.reduction_op = DOM_REDUCE_NONE;
    set_b.commutative = D_FALSE;

    TEST_CHECK(dom_detect_access_conflicts(&set_a, &set_b) == D_FALSE);

    write_ranges_b[0].start_id = 5u;
    write_ranges_b[0].end_id = 8u;
    TEST_CHECK(dom_detect_access_conflicts(&set_a, &set_b) == D_TRUE);
    return 0;
}

static int test_reduction_rules(void) {
    dom_access_range reduce_ranges[1];
    dom_access_set set_ok;
    dom_access_set set_bad_op;
    dom_access_set set_bad_comm;

    reduce_ranges[0].kind = DOM_RANGE_INDEX_RANGE;
    reduce_ranges[0].component_id = 2u;
    reduce_ranges[0].field_id = 3u;
    reduce_ranges[0].start_id = 0u;
    reduce_ranges[0].end_id = 4u;
    reduce_ranges[0].set_id = 0u;

    set_ok.access_id = 10u;
    set_ok.read_ranges = 0;
    set_ok.read_count = 0u;
    set_ok.write_ranges = 0;
    set_ok.write_count = 0u;
    set_ok.reduce_ranges = reduce_ranges;
    set_ok.reduce_count = 1u;
    set_ok.reduction_op = DOM_REDUCE_INT_SUM;
    set_ok.commutative = D_TRUE;

    set_bad_op = set_ok;
    set_bad_op.reduction_op = DOM_REDUCE_NONE;

    set_bad_comm = set_ok;
    set_bad_comm.commutative = D_FALSE;

    TEST_CHECK(dom_verify_reduction_rules(&set_ok) == D_TRUE);
    TEST_CHECK(dom_verify_reduction_rules(&set_bad_op) == D_FALSE);
    TEST_CHECK(dom_verify_reduction_rules(&set_bad_comm) == D_FALSE);
    return 0;
}

typedef struct test_law_state {
    u32 calls;
} test_law_state;

static dom_law_decision test_law_eval(const dom_execution_context *ctx,
                                      const dom_task_node *node,
                                      void *user_data) {
    test_law_state *state = (test_law_state *)user_data;
    dom_law_decision decision;
    (void)ctx;
    (void)node;
    if (state) {
        state->calls += 1u;
    }
    decision.kind = DOM_LAW_ACCEPT;
    decision.refusal_code = 0u;
    decision.transformed_fidelity_tier = 0u;
    decision.transformed_next_due_tick = DOM_EXEC_TICK_INVALID;
    return decision;
}

class TestSink : public IScheduleSink {
public:
    TestSink() : count(0u) {}
    virtual void on_task(const dom_task_node &, const dom_law_decision &) {
        count += 1u;
    }
    u32 count;
};

class TestScheduler : public IScheduler {
public:
    virtual void schedule(const dom_task_graph &graph,
                          dom_execution_context &ctx,
                          IScheduleSink &sink) {
        u32 i;
        u32 j;
        u32 *indices = 0;
        if (graph.task_count == 0u || !graph.tasks) {
            return;
        }
        indices = new u32[graph.task_count];
        for (i = 0u; i < graph.task_count; ++i) {
            indices[i] = i;
        }
        for (i = 1u; i < graph.task_count; ++i) {
            u32 key = indices[i];
            j = i;
            while (j > 0u) {
                const dom_task_node *prev = &graph.tasks[indices[j - 1u]];
                const dom_task_node *cur = &graph.tasks[key];
                if (dom_task_node_compare(prev, cur) <= 0) {
                    break;
                }
                indices[j] = indices[j - 1u];
                --j;
            }
            indices[j] = key;
        }
        for (i = 0u; i < graph.task_count; ++i) {
            const dom_task_node *node = &graph.tasks[indices[i]];
            dom_law_decision decision = dom_execution_context_evaluate_law(&ctx, node);
            sink.on_task(*node, decision);
        }
        delete[] indices;
    }
};

static int test_law_hook_invocation(void) {
    dom_task_node tasks[2];
    dom_task_graph graph;
    dom_execution_context ctx;
    test_law_state state;
    TestScheduler sched;
    TestSink sink;

    tasks[0] = make_task(2u, 1u, 0u);
    tasks[1] = make_task(1u, 1u, 0u);

    graph.graph_id = 1u;
    graph.epoch_id = 1u;
    graph.tasks = tasks;
    graph.task_count = 2u;
    graph.dependency_edges = 0;
    graph.dependency_count = 0u;
    graph.phase_barriers = 0;
    graph.phase_barrier_count = 0u;

    state.calls = 0u;
    ctx.act_now = 0u;
    ctx.scope_chain = 0;
    ctx.capability_sets = 0;
    ctx.budget_snapshot = 0;
    ctx.determinism_mode = DOM_DET_MODE_STRICT;
    ctx.evaluate_law = test_law_eval;
    ctx.record_audit = 0;
    ctx.lookup_access_set = 0;
    ctx.user_data = &state;

    sched.schedule(graph, ctx, sink);
    TEST_CHECK(state.calls == graph.task_count);
    TEST_CHECK(sink.count == graph.task_count);
    return 0;
}

static int test_task_immutability(void) {
    dom_task_node tasks[2];
    dom_task_node baseline[2];
    dom_task_graph graph;
    dom_execution_context ctx;
    test_law_state state;
    TestScheduler sched;
    TestSink sink;

    tasks[0] = make_task(10u, 2u, 0u);
    tasks[1] = make_task(11u, 2u, 0u);
    memcpy(baseline, tasks, sizeof(tasks));

    graph.graph_id = 2u;
    graph.epoch_id = 1u;
    graph.tasks = tasks;
    graph.task_count = 2u;
    graph.dependency_edges = 0;
    graph.dependency_count = 0u;
    graph.phase_barriers = 0;
    graph.phase_barrier_count = 0u;

    state.calls = 0u;
    ctx.act_now = 0u;
    ctx.scope_chain = 0;
    ctx.capability_sets = 0;
    ctx.budget_snapshot = 0;
    ctx.determinism_mode = DOM_DET_MODE_STRICT;
    ctx.evaluate_law = test_law_eval;
    ctx.record_audit = 0;
    ctx.lookup_access_set = 0;
    ctx.user_data = &state;

    sched.schedule(graph, ctx, sink);
    TEST_CHECK(memcmp(tasks, baseline, sizeof(tasks)) == 0);
    return 0;
}

int main(void) {
    if (test_deterministic_ordering() != 0) return 1;
    if (test_access_conflicts() != 0) return 1;
    if (test_reduction_rules() != 0) return 1;
    if (test_law_hook_invocation() != 0) return 1;
    if (test_task_immutability() != 0) return 1;
    return 0;
}
