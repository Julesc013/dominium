/*
Execution scheduler equivalence tests (EXEC2 vs EXEC3 shim).
*/
#include "execution/scheduler/scheduler_single_thread.h"
#include "execution/scheduler/scheduler_parallel.h"
#include "domino/execution/access_set.h"

#define TEST_CHECK(cond) do { if (!(cond)) return 1; } while (0)

static u64 fnv1a_init(void) {
    return 1469598103934665603ULL;
}

static u64 fnv1a_u32(u64 hash, u32 v) {
    u32 i;
    for (i = 0u; i < 4u; ++i) {
        hash ^= (u64)((v >> (i * 8u)) & 0xFFu);
        hash *= 1099511628211ULL;
    }
    return hash;
}

static u64 fnv1a_u64(u64 hash, u64 v) {
    u32 i;
    for (i = 0u; i < 8u; ++i) {
        hash ^= (u64)((v >> (i * 8u)) & 0xFFu);
        hash *= 1099511628211ULL;
    }
    return hash;
}

typedef struct audit_log {
    dom_audit_event events[64];
    u32 count;
} audit_log;

typedef struct law_state {
    u32 transform_used;
} law_state;

typedef struct test_ctx {
    const dom_access_set *sets;
    u32 set_count;
    law_state *law;
    audit_log *audit;
} test_ctx;

static const dom_access_set *lookup_access_set(const dom_execution_context *ctx,
                                               u64 access_set_id,
                                               void *user_data) {
    test_ctx *tctx = (test_ctx *)user_data;
    u32 i;
    (void)ctx;
    if (!tctx || !tctx->sets) {
        return 0;
    }
    for (i = 0u; i < tctx->set_count; ++i) {
        if (tctx->sets[i].access_id == access_set_id) {
            return &tctx->sets[i];
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
    if (!tctx || !node || !tctx->law) {
        return decision;
    }
    if (node->task_id == 11u) {
        decision.kind = DOM_LAW_REFUSE;
        decision.refusal_code = 42u;
        return decision;
    }
    if (node->task_id == 12u && tctx->law->transform_used == 0u) {
        tctx->law->transform_used += 1u;
        decision.kind = DOM_LAW_TRANSFORM;
        decision.transformed_fidelity_tier = DOM_FID_MACRO;
    }
    return decision;
}

static void record_audit(const dom_execution_context *ctx,
                         const dom_audit_event *event,
                         void *user_data) {
    test_ctx *tctx = (test_ctx *)user_data;
    (void)ctx;
    if (!tctx || !tctx->audit || !event) {
        return;
    }
    if (tctx->audit->count >= 64u) {
        return;
    }
    tctx->audit->events[tctx->audit->count] = *event;
    tctx->audit->count += 1u;
}

class TestSink : public IScheduleSink {
public:
    TestSink() : count(0u) {}
    virtual void on_task(const dom_task_node &node, const dom_law_decision &) {
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
                               u64 access_set_id,
                               u32 category,
                               u32 det_class) {
    static const u32 law_targets[1] = { 1u };
    dom_task_node node;
    node.task_id = task_id;
    node.system_id = 1u;
    node.category = category;
    node.determinism_class = det_class;
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

static u64 hash_sink(const TestSink &sink) {
    u64 h = fnv1a_init();
    u32 i;
    h = fnv1a_u32(h, sink.count);
    for (i = 0u; i < sink.count && i < 16u; ++i) {
        h = fnv1a_u64(h, sink.task_ids[i]);
        h = fnv1a_u32(h, sink.fidelities[i]);
    }
    return h;
}

static u64 hash_audit(const audit_log &log) {
    u64 h = fnv1a_init();
    u32 i;
    h = fnv1a_u32(h, log.count);
    for (i = 0u; i < log.count && i < 64u; ++i) {
        const dom_audit_event *event = &log.events[i];
        h = fnv1a_u32(h, event->event_id);
        h = fnv1a_u64(h, event->task_id);
        h = fnv1a_u32(h, event->decision_kind);
        h = fnv1a_u32(h, event->refusal_code);
    }
    return h;
}

static void init_ctx(dom_execution_context *ctx, test_ctx *tctx) {
    ctx->act_now = 0u;
    ctx->scope_chain = 0;
    ctx->capability_sets = 0;
    ctx->budget_snapshot = 0;
    ctx->determinism_mode = DOM_DET_MODE_STRICT;
    ctx->evaluate_law = test_law_eval;
    ctx->record_audit = record_audit;
    ctx->lookup_access_set = lookup_access_set;
    ctx->user_data = tctx;
}

static int test_scheduler_equivalence(void) {
    dom_task_node tasks[5];
    dom_task_graph graph;
    dom_access_range ranges[4];
    dom_access_set sets[4];
    dom_execution_context ctx_ref;
    dom_execution_context ctx_par;
    dom_scheduler_single_thread sched_ref;
    dom_scheduler_parallel sched_par;
    TestSink sink_ref;
    TestSink sink_par;
    audit_log audit_ref;
    audit_log audit_par;
    law_state law_ref;
    law_state law_par;
    test_ctx tctx_ref;
    test_ctx tctx_par;
    u64 hash_ref;
    u64 hash_par;

    tasks[0] = make_task(10u, 1u, 0u, 1u, DOM_TASK_AUTHORITATIVE, DOM_DET_STRICT);
    tasks[1] = make_task(11u, 1u, 0u, 2u, DOM_TASK_AUTHORITATIVE, DOM_DET_ORDERED);
    tasks[2] = make_task(12u, 1u, 0u, 3u, DOM_TASK_AUTHORITATIVE, DOM_DET_COMMUTATIVE);
    tasks[3] = make_task(13u, 1u, 0u, 2u, DOM_TASK_AUTHORITATIVE, DOM_DET_STRICT);
    tasks[4] = make_task(20u, 2u, 0u, 4u, DOM_TASK_DERIVED, DOM_DET_DERIVED);

    dom_stable_task_sort(tasks, 5u);

    graph.graph_id = 99u;
    graph.epoch_id = 1u;
    graph.tasks = tasks;
    graph.task_count = 5u;
    graph.dependency_edges = 0;
    graph.dependency_count = 0u;
    graph.phase_barriers = 0;
    graph.phase_barrier_count = 0u;

    ranges[0].kind = DOM_RANGE_INDEX_RANGE;
    ranges[0].component_id = 1u;
    ranges[0].field_id = 1u;
    ranges[0].start_id = 0u;
    ranges[0].end_id = 10u;
    ranges[0].set_id = 0u;

    ranges[1] = ranges[0];
    ranges[1].start_id = 5u;
    ranges[1].end_id = 8u;

    ranges[2].kind = DOM_RANGE_INDEX_RANGE;
    ranges[2].component_id = 2u;
    ranges[2].field_id = 1u;
    ranges[2].start_id = 0u;
    ranges[2].end_id = 4u;
    ranges[2].set_id = 0u;

    ranges[3].kind = DOM_RANGE_INDEX_RANGE;
    ranges[3].component_id = 3u;
    ranges[3].field_id = 1u;
    ranges[3].start_id = 0u;
    ranges[3].end_id = 4u;
    ranges[3].set_id = 0u;

    sets[0].access_id = 1u;
    sets[0].read_ranges = 0;
    sets[0].read_count = 0u;
    sets[0].write_ranges = &ranges[0];
    sets[0].write_count = 1u;
    sets[0].reduce_ranges = 0;
    sets[0].reduce_count = 0u;
    sets[0].reduction_op = DOM_REDUCE_NONE;
    sets[0].commutative = D_FALSE;

    sets[1] = sets[0];
    sets[1].access_id = 2u;
    sets[1].write_ranges = &ranges[1];

    sets[2].access_id = 3u;
    sets[2].read_ranges = 0;
    sets[2].read_count = 0u;
    sets[2].write_ranges = 0;
    sets[2].write_count = 0u;
    sets[2].reduce_ranges = &ranges[2];
    sets[2].reduce_count = 1u;
    sets[2].reduction_op = DOM_REDUCE_INT_SUM;
    sets[2].commutative = D_TRUE;

    sets[3].access_id = 4u;
    sets[3].read_ranges = &ranges[3];
    sets[3].read_count = 1u;
    sets[3].write_ranges = 0;
    sets[3].write_count = 0u;
    sets[3].reduce_ranges = 0;
    sets[3].reduce_count = 0u;
    sets[3].reduction_op = DOM_REDUCE_NONE;
    sets[3].commutative = D_FALSE;

    audit_ref.count = 0u;
    law_ref.transform_used = 0u;
    tctx_ref.sets = sets;
    tctx_ref.set_count = 4u;
    tctx_ref.law = &law_ref;
    tctx_ref.audit = &audit_ref;
    init_ctx(&ctx_ref, &tctx_ref);

    audit_par.count = 0u;
    law_par.transform_used = 0u;
    tctx_par.sets = sets;
    tctx_par.set_count = 4u;
    tctx_par.law = &law_par;
    tctx_par.audit = &audit_par;
    init_ctx(&ctx_par, &tctx_par);

    sched_ref.schedule(graph, ctx_ref, sink_ref);
    sched_par.schedule(graph, ctx_par, sink_par);

    hash_ref = fnv1a_u64(hash_sink(sink_ref), hash_audit(audit_ref));
    hash_par = fnv1a_u64(hash_sink(sink_par), hash_audit(audit_par));

    TEST_CHECK(hash_ref == hash_par);
    TEST_CHECK(sink_ref.count == sink_par.count);
    return 0;
}

int main(void) {
    if (test_scheduler_equivalence() != 0) return 1;
    return 0;
}
