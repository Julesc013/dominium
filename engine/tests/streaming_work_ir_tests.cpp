/*
Streaming Work IR migration tests (ADOPT1).
*/
#include "dominium/rules/scale/world_streaming_system.h"
#include "dominium/interest_set.h"
#include "dominium/execution/system_registry.h"
#include "dominium/execution/work_graph_builder.h"
#include "dominium/execution/access_set_builder.h"
#include "domino/execution/execution_context.h"
#include "execution/scheduler/scheduler_single_thread.h"

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

static u32 fnv1a_32(const char* text)
{
    const unsigned char* bytes = (const unsigned char*)(text ? text : "");
    u32 h = 2166136261u;
    while (*bytes) {
        h ^= (u32)(*bytes++);
        h *= 16777619u;
    }
    return h;
}

static u64 hash_task_graph(const dom_task_graph* graph)
{
    u32 i;
    u64 h = fnv1a_init();
    if (!graph || !graph->tasks) {
        return h;
    }
    h = fnv1a_u64(h, graph->graph_id);
    h = fnv1a_u64(h, graph->epoch_id);
    h = fnv1a_u32(h, graph->task_count);
    for (i = 0u; i < graph->task_count; ++i) {
        const dom_task_node* t = &graph->tasks[i];
        h = fnv1a_u64(h, t->task_id);
        h = fnv1a_u64(h, t->system_id);
        h = fnv1a_u32(h, t->category);
        h = fnv1a_u32(h, t->determinism_class);
        h = fnv1a_u32(h, t->fidelity_tier);
        h = fnv1a_u64(h, t->next_due_tick);
        h = fnv1a_u64(h, t->access_set_id);
        h = fnv1a_u64(h, t->cost_model_id);
        h = fnv1a_u32(h, t->law_target_count);
        h = fnv1a_u32(h, t->phase_id);
        h = fnv1a_u32(h, t->commit_key.phase_id);
        h = fnv1a_u64(h, t->commit_key.task_id);
        h = fnv1a_u32(h, t->commit_key.sub_index);
        if (t->policy_params && t->policy_params_size == sizeof(dom_streaming_request)) {
            const dom_streaming_request* req = (const dom_streaming_request*)t->policy_params;
            h = fnv1a_u32(h, req->op);
            h = fnv1a_u64(h, req->chunk_id);
        }
    }
    return h;
}

static int build_interest_set(dom_interest_set* set)
{
    if (!set) {
        return -1;
    }
    dom_interest_set_init(set);
    if (dom_interest_set_reserve(set, 8u) != 0) {
        return -2;
    }
    if (dom_interest_set_add(set, DOM_INTEREST_TARGET_REGION, 10u,
                             DOM_INTEREST_REASON_PLAYER_FOCUS,
                             DOM_INTEREST_STRENGTH_HIGH,
                             DOM_INTEREST_PERSISTENT) != 0) {
        return -3;
    }
    if (dom_interest_set_add(set, DOM_INTEREST_TARGET_REGION, 20u,
                             DOM_INTEREST_REASON_PLAYER_FOCUS,
                             DOM_INTEREST_STRENGTH_MED,
                             DOM_INTEREST_PERSISTENT) != 0) {
        return -4;
    }
    if (dom_interest_set_add(set, DOM_INTEREST_TARGET_REGION, 30u,
                             DOM_INTEREST_REASON_COMMAND_INTENT,
                             DOM_INTEREST_STRENGTH_HIGH,
                             DOM_INTEREST_PERSISTENT) != 0) {
        return -5;
    }
    dom_interest_set_finalize(set);
    return 0;
}

static void init_cache(dom_streaming_cache* cache, u64* storage, u32 count)
{
    if (!cache) {
        return;
    }
    cache->loaded_chunk_ids = storage;
    cache->loaded_count = count;
    cache->loaded_capacity = count;
}

static int emit_with_registry(dom_system_registry* registry,
                              WorldStreamingSystem* system,
                              dom_work_graph_builder* graph_builder,
                              dom_access_set_builder* access_builder,
                              dom_task_graph* out_graph)
{
    if (!registry || !system || !graph_builder || !access_builder || !out_graph) {
        return -1;
    }
    dom_work_graph_builder_reset(graph_builder);
    dom_access_set_builder_reset(access_builder);
    dom_work_graph_builder_set_ids(graph_builder, 900u, 1u);
    if (dom_system_registry_emit(registry, 0, 10, graph_builder, access_builder) != 0) {
        return -2;
    }
    dom_work_graph_builder_finalize(graph_builder, out_graph);
    return 0;
}

static int test_deterministic_emission(void)
{
    dom_interest_set interest;
    dom_streaming_cache cache;
    u64 cache_ids[2] = { 20u, 40u };
    dom_streaming_request ir_storage[16];
    dom_streaming_request legacy_storage[16];
    WorldStreamingSystem system;
    dom_system_registry registry;
    dom_system_entry entries[1];
    dom_task_node tasks[16];
    dom_dependency_edge deps[1];
    dom_phase_barrier barriers[1];
    dom_cost_model costs[16];
    dom_access_set access_sets[16];
    dom_access_range reads[32];
    dom_access_range writes[16];
    dom_access_range reduces[4];
    dom_task_graph graph_a;
    dom_task_graph graph_b;
    dom_work_graph_builder graph_builder;
    dom_access_set_builder access_builder;
    u64 hash_a;
    u64 hash_b;

    EXPECT(build_interest_set(&interest) == 0, "interest set");
    init_cache(&cache, cache_ids, 2u);

    system.init(&interest, &cache, 77u, ir_storage, 16u, legacy_storage, 16u);

    dom_system_registry_init(&registry, entries, 1u);
    EXPECT(dom_system_registry_register_streaming(&registry, &system) == 0, "register streaming");
    EXPECT(dom_system_registry_set_fidelity(&registry, system.system_id(), DOM_FIDELITY_MICRO) == 0, "set fidelity");
    EXPECT(dom_system_registry_set_budget_hint(&registry, system.system_id(), 8u) == 0, "set budget");

    dom_work_graph_builder_init(&graph_builder, tasks, 16u, deps, 1u, barriers, 1u, costs, 16u);
    dom_access_set_builder_init(&access_builder, access_sets, 16u, reads, 32u, writes, 16u, reduces, 4u);

    EXPECT(emit_with_registry(&registry, &system, &graph_builder, &access_builder, &graph_a) == 0, "emit A");
    hash_a = hash_task_graph(&graph_a);
    EXPECT(emit_with_registry(&registry, &system, &graph_builder, &access_builder, &graph_b) == 0, "emit B");
    hash_b = hash_task_graph(&graph_b);

    EXPECT(hash_a == hash_b, "deterministic hash mismatch");
    EXPECT(system.mismatch_count() == 0u, "dual-path mismatch");

    dom_interest_set_free(&interest);
    return 0;
}

static int test_budget_enforcement(void)
{
    dom_interest_set interest;
    dom_streaming_cache cache;
    u64 cache_ids[1] = { 999u };
    dom_streaming_request ir_storage[16];
    dom_streaming_request legacy_storage[16];
    WorldStreamingSystem system;
    dom_system_registry registry;
    dom_system_entry entries[1];
    dom_task_node tasks[16];
    dom_dependency_edge deps[1];
    dom_phase_barrier barriers[1];
    dom_cost_model costs[16];
    dom_access_set access_sets[16];
    dom_access_range reads[32];
    dom_access_range writes[16];
    dom_access_range reduces[4];
    dom_task_graph graph;
    dom_work_graph_builder graph_builder;
    dom_access_set_builder access_builder;

    EXPECT(build_interest_set(&interest) == 0, "interest set");
    init_cache(&cache, cache_ids, 1u);
    system.init(&interest, &cache, 88u, ir_storage, 16u, legacy_storage, 16u);

    dom_system_registry_init(&registry, entries, 1u);
    EXPECT(dom_system_registry_register_streaming(&registry, &system) == 0, "register streaming");
    EXPECT(dom_system_registry_set_fidelity(&registry, system.system_id(), DOM_FIDELITY_FOCUS) == 0, "set fidelity");
    EXPECT(dom_system_registry_set_budget_hint(&registry, system.system_id(), 1u) == 0, "set budget");

    dom_work_graph_builder_init(&graph_builder, tasks, 16u, deps, 1u, barriers, 1u, costs, 16u);
    dom_access_set_builder_init(&access_builder, access_sets, 16u, reads, 32u, writes, 16u, reduces, 4u);

    EXPECT(emit_with_registry(&registry, &system, &graph_builder, &access_builder, &graph) == 0, "emit budget");
    EXPECT(graph.task_count <= 1u, "budget exceeded");

    dom_interest_set_free(&interest);
    return 0;
}

static int test_degradation(void)
{
    dom_interest_set interest;
    dom_streaming_cache cache;
    u64 cache_ids[1] = { 20u };
    dom_streaming_request ir_storage[16];
    dom_streaming_request legacy_storage[16];
    WorldStreamingSystem system;
    dom_system_registry registry;
    dom_system_entry entries[1];
    dom_task_node tasks[16];
    dom_dependency_edge deps[1];
    dom_phase_barrier barriers[1];
    dom_cost_model costs[16];
    dom_access_set access_sets[16];
    dom_access_range reads[32];
    dom_access_range writes[16];
    dom_access_range reduces[4];
    dom_task_graph graph;
    dom_work_graph_builder graph_builder;
    dom_access_set_builder access_builder;
    u32 macro_count;
    u32 latent_count;

    EXPECT(build_interest_set(&interest) == 0, "interest set");
    init_cache(&cache, cache_ids, 1u);
    system.init(&interest, &cache, 99u, ir_storage, 16u, legacy_storage, 16u);

    dom_system_registry_init(&registry, entries, 1u);
    EXPECT(dom_system_registry_register_streaming(&registry, &system) == 0, "register streaming");
    EXPECT(dom_system_registry_set_budget_hint(&registry, system.system_id(), 8u) == 0, "set budget");

    dom_work_graph_builder_init(&graph_builder, tasks, 16u, deps, 1u, barriers, 1u, costs, 16u);
    dom_access_set_builder_init(&access_builder, access_sets, 16u, reads, 32u, writes, 16u, reduces, 4u);

    EXPECT(dom_system_registry_set_fidelity(&registry, system.system_id(), DOM_FIDELITY_MACRO) == 0, "set macro");
    EXPECT(emit_with_registry(&registry, &system, &graph_builder, &access_builder, &graph) == 0, "emit macro");
    macro_count = graph.task_count;

    EXPECT(dom_system_registry_set_fidelity(&registry, system.system_id(), DOM_FIDELITY_LATENT) == 0, "set latent");
    EXPECT(emit_with_registry(&registry, &system, &graph_builder, &access_builder, &graph) == 0, "emit latent");
    latent_count = graph.task_count;

    EXPECT(latent_count == 0u, "latent should emit no tasks");
    EXPECT(macro_count >= latent_count, "macro count");

    dom_interest_set_free(&interest);
    return 0;
}

typedef struct streaming_test_ctx {
    const dom_access_set* sets;
    u32 count;
    u32 refuse_target;
} streaming_test_ctx;

static const dom_access_set* lookup_access_set(const dom_execution_context* ctx,
                                               u64 access_set_id,
                                               void* user_data)
{
    streaming_test_ctx* state = (streaming_test_ctx*)user_data;
    u32 i;
    (void)ctx;
    if (!state || !state->sets) {
        return 0;
    }
    for (i = 0u; i < state->count; ++i) {
        if (state->sets[i].access_id == access_set_id) {
            return &state->sets[i];
        }
    }
    return 0;
}

static dom_law_decision refuse_streaming(const dom_execution_context* ctx,
                                         const dom_task_node* node,
                                         void* user_data)
{
    streaming_test_ctx* state = (streaming_test_ctx*)user_data;
    dom_law_decision decision;
    u32 i;
    (void)ctx;
    decision.kind = DOM_LAW_ACCEPT;
    decision.refusal_code = 0u;
    decision.transformed_fidelity_tier = 0u;
    decision.transformed_next_due_tick = DOM_EXEC_TICK_INVALID;
    if (node && node->law_targets && state) {
        for (i = 0u; i < node->law_target_count; ++i) {
            if (node->law_targets[i] == state->refuse_target) {
                decision.kind = DOM_LAW_REFUSE;
                decision.refusal_code = 900u;
                break;
            }
        }
    }
    return decision;
}

class TestSink : public IScheduleSink {
public:
    TestSink() : executed(0u) {}
    virtual void on_task(const dom_task_node&, const dom_law_decision&) {
        executed += 1u;
    }
    u32 executed;
};

static int test_law_refusal(void)
{
    dom_interest_set interest;
    dom_streaming_cache cache;
    u64 cache_ids[1] = { 20u };
    dom_streaming_request ir_storage[16];
    dom_streaming_request legacy_storage[16];
    WorldStreamingSystem system;
    dom_task_node tasks[16];
    dom_dependency_edge deps[1];
    dom_phase_barrier barriers[1];
    dom_cost_model costs[16];
    dom_access_set access_sets[16];
    dom_access_range reads[32];
    dom_access_range writes[16];
    dom_access_range reduces[4];
    dom_task_graph graph;
    dom_work_graph_builder graph_builder;
    dom_access_set_builder access_builder;
    dom_execution_context ctx;
    streaming_test_ctx test_ctx;
    dom_scheduler_single_thread scheduler;
    TestSink sink;

    EXPECT(build_interest_set(&interest) == 0, "interest set");
    init_cache(&cache, cache_ids, 1u);
    system.init(&interest, &cache, 123u, ir_storage, 16u, legacy_storage, 16u);
    system.degrade(DOM_FIDELITY_MICRO, 0u);

    dom_work_graph_builder_init(&graph_builder, tasks, 16u, deps, 1u, barriers, 1u, costs, 16u);
    dom_access_set_builder_init(&access_builder, access_sets, 16u, reads, 32u, writes, 16u, reduces, 4u);

    dom_work_graph_builder_reset(&graph_builder);
    dom_access_set_builder_reset(&access_builder);
    dom_work_graph_builder_set_ids(&graph_builder, 777u, 1u);
    EXPECT(system.emit_tasks(0, 10, &graph_builder, &access_builder) == 0, "emit tasks");
    dom_work_graph_builder_finalize(&graph_builder, &graph);

    test_ctx.sets = access_sets;
    test_ctx.count = access_builder.set_count;
    test_ctx.refuse_target = fnv1a_32("WORLD.DATA_ACCESS");

    memset(&ctx, 0, sizeof(ctx));
    ctx.act_now = 0u;
    ctx.determinism_mode = DOM_DET_MODE_TEST;
    ctx.evaluate_law = refuse_streaming;
    ctx.lookup_access_set = lookup_access_set;
    ctx.user_data = &test_ctx;

    scheduler.schedule(graph, ctx, sink);
    EXPECT(sink.executed == 0u, "law refusal expected");

    dom_interest_set_free(&interest);
    return 0;
}

int main(void)
{
    if (test_deterministic_emission() != 0) return 1;
    if (test_budget_enforcement() != 0) return 1;
    if (test_degradation() != 0) return 1;
    if (test_law_refusal() != 0) return 1;
    return 0;
}
