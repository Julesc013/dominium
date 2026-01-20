/*
Execution contract enforcement tests (EXEC-AUDIT0).
*/
#include "execution/scheduler/scheduler_single_thread.h"
#include "domino/execution/access_set.h"

#include <stdio.h>
#include <string.h>

#define EXPECT(cond, msg) do { if (!(cond)) { \
    fprintf(stderr, "FAIL: %s\n", msg); \
    return 1; \
} } while (0)

static dom_task_node make_task(u64 task_id, u64 access_set_id) {
    static const u32 law_targets[1] = { 1u };
    dom_task_node node;
    node.task_id = task_id;
    node.system_id = 1u;
    node.category = DOM_TASK_AUTHORITATIVE;
    node.determinism_class = DOM_DET_STRICT;
    node.fidelity_tier = DOM_FID_MICRO;
    node.next_due_tick = DOM_EXEC_TICK_INVALID;
    node.access_set_id = access_set_id;
    node.cost_model_id = 9u;
    node.law_targets = law_targets;
    node.law_target_count = 1u;
    node.phase_id = 1u;
    node.commit_key.phase_id = node.phase_id;
    node.commit_key.task_id = node.task_id;
    node.commit_key.sub_index = 0u;
    node.law_scope_ref = 1u;
    node.actor_ref = 0u;
    node.capability_set_ref = 0u;
    node.policy_params = 0;
    node.policy_params_size = 0u;
    return node;
}

static d_bool task_complete(const dom_task_node *node) {
    if (!node) {
        return D_FALSE;
    }
    if (node->access_set_id == 0u || node->cost_model_id == 0u) {
        return D_FALSE;
    }
    if (node->determinism_class > DOM_DET_DERIVED) {
        return D_FALSE;
    }
    if (node->commit_key.phase_id != node->phase_id) {
        return D_FALSE;
    }
    if (node->commit_key.task_id != node->task_id) {
        return D_FALSE;
    }
    if (node->category == DOM_TASK_AUTHORITATIVE) {
        if (!node->law_targets || node->law_target_count == 0u) {
            return D_FALSE;
        }
    }
    return D_TRUE;
}

static int test_task_node_completeness(void) {
    dom_task_node node = make_task(1u, 1u);
    dom_task_node bad = node;

    EXPECT(task_complete(&node) == D_TRUE, "baseline task incomplete");

    bad.access_set_id = 0u;
    EXPECT(task_complete(&bad) == D_FALSE, "missing access_set_id");
    bad = node;

    bad.cost_model_id = 0u;
    EXPECT(task_complete(&bad) == D_FALSE, "missing cost_model_id");
    bad = node;

    bad.law_targets = 0;
    bad.law_target_count = 0u;
    EXPECT(task_complete(&bad) == D_FALSE, "missing law_targets");
    bad = node;

    bad.commit_key.phase_id = node.phase_id + 1u;
    EXPECT(task_complete(&bad) == D_FALSE, "commit_key mismatch");
    bad = node;

    bad.determinism_class = 99u;
    EXPECT(task_complete(&bad) == D_FALSE, "invalid determinism_class");
    return 0;
}

static int test_access_conflict_validation(void) {
    dom_access_range write_ranges[2];
    dom_access_set set_a;
    dom_access_set set_b;

    write_ranges[0].kind = DOM_RANGE_INDEX_RANGE;
    write_ranges[0].component_id = 1u;
    write_ranges[0].field_id = 1u;
    write_ranges[0].start_id = 0u;
    write_ranges[0].end_id = 10u;
    write_ranges[0].set_id = 0u;

    write_ranges[1] = write_ranges[0];
    write_ranges[1].start_id = 20u;
    write_ranges[1].end_id = 30u;

    set_a.access_id = 1u;
    set_a.read_ranges = 0;
    set_a.read_count = 0u;
    set_a.write_ranges = &write_ranges[0];
    set_a.write_count = 1u;
    set_a.reduce_ranges = 0;
    set_a.reduce_count = 0u;
    set_a.reduction_op = DOM_REDUCE_NONE;
    set_a.commutative = D_FALSE;

    set_b = set_a;
    set_b.access_id = 2u;
    set_b.write_ranges = &write_ranges[1];

    EXPECT(dom_detect_access_conflicts(&set_a, &set_b) == D_FALSE, "disjoint sets conflict");

    write_ranges[1].start_id = 5u;
    write_ranges[1].end_id = 6u;
    EXPECT(dom_detect_access_conflicts(&set_a, &set_b) == D_TRUE, "overlap not detected");
    return 0;
}

typedef struct test_law_state {
    u32 calls;
} test_law_state;

typedef struct test_ctx {
    const dom_access_set *sets;
    test_law_state *state;
} test_ctx;

static dom_law_decision test_law_eval(const dom_execution_context *ctx,
                                      const dom_task_node *node,
                                      void *user_data) {
    test_ctx *tctx = (test_ctx *)user_data;
    test_law_state *state = tctx ? tctx->state : 0;
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

static const dom_access_set *lookup_access_set(const dom_execution_context *ctx,
                                               u64 access_set_id,
                                               void *user_data) {
    test_ctx *tctx = (test_ctx *)user_data;
    const dom_access_set *sets = tctx ? tctx->sets : 0;
    (void)ctx;
    if (!sets) {
        return 0;
    }
    if (sets[0].access_id == access_set_id) {
        return &sets[0];
    }
    return 0;
}

class TestSink : public IScheduleSink {
public:
    TestSink() : count(0u) {}
    virtual void on_task(const dom_task_node &, const dom_law_decision &) {
        count += 1u;
    }
    u32 count;
};

static int test_law_admission_invocation(void) {
    dom_task_node tasks[2];
    dom_task_graph graph;
    dom_access_set access_sets[1];
    dom_execution_context ctx;
    test_law_state state;
    test_ctx tctx;
    dom_scheduler_single_thread scheduler;
    TestSink sink;

    tasks[0] = make_task(2u, 1u);
    tasks[1] = make_task(1u, 1u);

    dom_stable_task_sort(tasks, 2u);

    graph.graph_id = 1u;
    graph.epoch_id = 1u;
    graph.tasks = tasks;
    graph.task_count = 2u;
    graph.dependency_edges = 0;
    graph.dependency_count = 0u;
    graph.phase_barriers = 0;
    graph.phase_barrier_count = 0u;

    access_sets[0].access_id = 1u;
    access_sets[0].read_ranges = 0;
    access_sets[0].read_count = 0u;
    access_sets[0].write_ranges = 0;
    access_sets[0].write_count = 0u;
    access_sets[0].reduce_ranges = 0;
    access_sets[0].reduce_count = 0u;
    access_sets[0].reduction_op = DOM_REDUCE_NONE;
    access_sets[0].commutative = D_FALSE;

    state.calls = 0u;
    tctx.sets = access_sets;
    tctx.state = &state;
    ctx.act_now = 0u;
    ctx.scope_chain = 0;
    ctx.capability_sets = 0;
    ctx.budget_snapshot = 0;
    ctx.determinism_mode = DOM_DET_MODE_STRICT;
    ctx.evaluate_law = test_law_eval;
    ctx.record_audit = 0;
    ctx.lookup_access_set = lookup_access_set;
    ctx.user_data = &tctx;

    scheduler.schedule(graph, ctx, sink);
    EXPECT(state.calls == graph.task_count, "law admission calls mismatch");
    EXPECT(sink.count == graph.task_count, "sink count mismatch");
    return 0;
}

int main(void) {
    if (test_task_node_completeness() != 0) return 1;
    if (test_access_conflict_validation() != 0) return 1;
    if (test_law_admission_invocation() != 0) return 1;
    return 0;
}
