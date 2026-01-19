/*
Law integration scheduler tests (EXEC2).
*/
#include "execution/scheduler/scheduler_single_thread.h"

#define TEST_CHECK(cond) do { if (!(cond)) return 1; } while (0)

typedef struct law_access_registry {
    dom_access_set set;
} law_access_registry;

typedef struct law_state {
    d_bool meta_deny;
    d_bool cap_deny;
    d_bool allow;
    u32 calls;
    u32 refusal_code;
} law_state;

typedef struct law_ctx {
    law_access_registry access;
    law_state law;
    dom_audit_event last_event;
    d_bool has_event;
} law_ctx;

static const dom_access_set *lookup_access_set(const dom_execution_context *ctx,
                                               u64 access_set_id,
                                               void *user_data) {
    law_ctx *lctx = (law_ctx *)user_data;
    (void)ctx;
    if (!lctx) {
        return 0;
    }
    if (lctx->access.set.access_id == access_set_id) {
        return &lctx->access.set;
    }
    return 0;
}

static dom_law_decision law_eval(const dom_execution_context *ctx,
                                 const dom_task_node *node,
                                 void *user_data) {
    law_ctx *lctx = (law_ctx *)user_data;
    dom_law_decision decision;
    (void)ctx;
    (void)node;
    decision.kind = DOM_LAW_ACCEPT;
    decision.refusal_code = 0u;
    decision.transformed_fidelity_tier = 0u;
    decision.transformed_next_due_tick = DOM_EXEC_TICK_INVALID;
    if (!lctx) {
        return decision;
    }
    lctx->law.calls += 1u;
    if (lctx->law.meta_deny == D_TRUE) {
        decision.kind = DOM_LAW_REFUSE;
        decision.refusal_code = 900u;
        return decision;
    }
    if (lctx->law.cap_deny == D_TRUE) {
        decision.kind = DOM_LAW_REFUSE;
        decision.refusal_code = 901u;
        return decision;
    }
    if (lctx->law.allow == D_TRUE) {
        return decision;
    }
    return decision;
}

static void record_audit(const dom_execution_context *ctx,
                         const dom_audit_event *event,
                         void *user_data) {
    law_ctx *lctx = (law_ctx *)user_data;
    (void)ctx;
    if (!lctx || !event) {
        return;
    }
    lctx->last_event = *event;
    lctx->has_event = D_TRUE;
}

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
    node.cost_model_id = 1u;
    node.law_targets = law_targets;
    node.law_target_count = 1u;
    node.phase_id = 1u;
    node.commit_key.phase_id = 1u;
    node.commit_key.task_id = task_id;
    node.commit_key.sub_index = 0u;
    node.law_scope_ref = 1u;
    node.actor_ref = 0u;
    node.capability_set_ref = 0u;
    node.policy_params = 0;
    node.policy_params_size = 0u;
    return node;
}

static int test_capability_deny_overrides_allow(void) {
    dom_task_node tasks[1];
    dom_task_graph graph;
    dom_execution_context ctx;
    dom_scheduler_single_thread sched;
    class Sink : public IScheduleSink {
    public:
        Sink() : count(0u) {}
        virtual void on_task(const dom_task_node &, const dom_law_decision &) {
            count += 1u;
        }
        u32 count;
    } sink;
    law_ctx lctx;

    tasks[0] = make_task(1u, 1u);
    graph.graph_id = 10u;
    graph.epoch_id = 1u;
    graph.tasks = tasks;
    graph.task_count = 1u;
    graph.dependency_edges = 0;
    graph.dependency_count = 0u;
    graph.phase_barriers = 0;
    graph.phase_barrier_count = 0u;

    lctx.access.set.access_id = 1u;
    lctx.access.set.read_ranges = 0;
    lctx.access.set.read_count = 0u;
    lctx.access.set.write_ranges = 0;
    lctx.access.set.write_count = 0u;
    lctx.access.set.reduce_ranges = 0;
    lctx.access.set.reduce_count = 0u;
    lctx.access.set.reduction_op = DOM_REDUCE_NONE;
    lctx.access.set.commutative = D_FALSE;
    lctx.law.meta_deny = D_FALSE;
    lctx.law.cap_deny = D_TRUE;
    lctx.law.allow = D_TRUE;
    lctx.law.calls = 0u;
    lctx.law.refusal_code = 0u;
    lctx.has_event = D_FALSE;

    ctx.act_now = 0u;
    ctx.scope_chain = 0;
    ctx.capability_sets = 0;
    ctx.budget_snapshot = 0;
    ctx.determinism_mode = DOM_DET_MODE_STRICT;
    ctx.evaluate_law = law_eval;
    ctx.record_audit = record_audit;
    ctx.lookup_access_set = lookup_access_set;
    ctx.user_data = &lctx;

    sched.schedule(graph, ctx, sink);
    TEST_CHECK(sink.count == 0u);
    TEST_CHECK(lctx.has_event == D_TRUE);
    TEST_CHECK(lctx.last_event.refusal_code == 901u);
    return 0;
}

static int test_meta_overrides_capability(void) {
    dom_task_node tasks[1];
    dom_task_graph graph;
    dom_execution_context ctx;
    dom_scheduler_single_thread sched;
    class Sink : public IScheduleSink {
    public:
        Sink() : count(0u) {}
        virtual void on_task(const dom_task_node &, const dom_law_decision &) {
            count += 1u;
        }
        u32 count;
    } sink;
    law_ctx lctx;

    tasks[0] = make_task(1u, 1u);
    graph.graph_id = 11u;
    graph.epoch_id = 1u;
    graph.tasks = tasks;
    graph.task_count = 1u;
    graph.dependency_edges = 0;
    graph.dependency_count = 0u;
    graph.phase_barriers = 0;
    graph.phase_barrier_count = 0u;

    lctx.access.set.access_id = 1u;
    lctx.access.set.read_ranges = 0;
    lctx.access.set.read_count = 0u;
    lctx.access.set.write_ranges = 0;
    lctx.access.set.write_count = 0u;
    lctx.access.set.reduce_ranges = 0;
    lctx.access.set.reduce_count = 0u;
    lctx.access.set.reduction_op = DOM_REDUCE_NONE;
    lctx.access.set.commutative = D_FALSE;
    lctx.law.meta_deny = D_TRUE;
    lctx.law.cap_deny = D_TRUE;
    lctx.law.allow = D_TRUE;
    lctx.law.calls = 0u;
    lctx.law.refusal_code = 0u;
    lctx.has_event = D_FALSE;

    ctx.act_now = 0u;
    ctx.scope_chain = 0;
    ctx.capability_sets = 0;
    ctx.budget_snapshot = 0;
    ctx.determinism_mode = DOM_DET_MODE_STRICT;
    ctx.evaluate_law = law_eval;
    ctx.record_audit = record_audit;
    ctx.lookup_access_set = lookup_access_set;
    ctx.user_data = &lctx;

    sched.schedule(graph, ctx, sink);
    TEST_CHECK(sink.count == 0u);
    TEST_CHECK(lctx.has_event == D_TRUE);
    TEST_CHECK(lctx.last_event.refusal_code == 900u);
    return 0;
}

int main(void) {
    if (test_capability_deny_overrides_allow() != 0) return 1;
    if (test_meta_overrides_capability() != 0) return 1;
    return 0;
}
