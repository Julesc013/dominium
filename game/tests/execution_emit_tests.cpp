/*
EXEC4 Work IR emission tests.
*/
#include "game/core/execution/system_registry.h"
#include "game/core/execution/work_graph_builder.h"
#include "game/core/execution/access_set_builder.h"
#include "domino/execution/task_node.h"

#include <stdio.h>

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

static u32 task_fidelity(dom_fidelity_tier tier)
{
    switch (tier) {
        case DOM_FIDELITY_LATENT: return DOM_FID_LATENT;
        case DOM_FIDELITY_MACRO: return DOM_FID_MACRO;
        case DOM_FIDELITY_MESO: return DOM_FID_MESO;
        case DOM_FIDELITY_MICRO: return DOM_FID_MICRO;
        case DOM_FIDELITY_FOCUS: return DOM_FID_FOCUS;
        default: return DOM_FID_LATENT;
    }
}

static u64 hash_task_graph(const dom_task_graph* graph)
{
    u32 i;
    u32 j;
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
        for (j = 0u; j < t->law_target_count; ++j) {
            h = fnv1a_u32(h, t->law_targets[j]);
        }
        h = fnv1a_u32(h, t->phase_id);
        h = fnv1a_u32(h, t->commit_key.phase_id);
        h = fnv1a_u64(h, t->commit_key.task_id);
        h = fnv1a_u32(h, t->commit_key.sub_index);
    }
    return h;
}

class TestSystem : public ISimSystem {
public:
    TestSystem(u64 id, d_bool sim_affecting)
        : system_id_(id),
          sim_affecting_(sim_affecting),
          tier_(DOM_FIDELITY_MACRO),
          next_due_(0),
          emit_latent_(0u),
          emit_macro_(1u),
          emit_micro_(2u),
          law_target_count_(0u)
    {
        law_targets_[0] = fnv1a_32("EXEC.AUTH_TASK");
        if (sim_affecting_) {
            law_target_count_ = 1u;
        }
    }

    void set_emit_counts(u32 latent_count, u32 macro_count, u32 micro_count)
    {
        emit_latent_ = latent_count;
        emit_macro_ = macro_count;
        emit_micro_ = micro_count;
    }

    void set_next_due(dom_act_time_t tick)
    {
        next_due_ = tick;
    }

    u64 system_id() const { return system_id_; }
    d_bool is_sim_affecting() const { return sim_affecting_; }

    const u32* law_targets(u32* out_count) const
    {
        if (out_count) {
            *out_count = law_target_count_;
        }
        return law_target_count_ ? law_targets_ : (const u32*)0;
    }

    dom_act_time_t get_next_due_tick() const
    {
        return next_due_;
    }

    int emit_tasks(dom_act_time_t act_now,
                   dom_act_time_t act_target,
                   dom_work_graph_builder* graph_builder,
                   dom_access_set_builder* access_builder)
    {
        u32 i;
        u32 count = emit_count_for_tier(tier_);
        u32 component_base = (u32)(system_id_ & 0xFFFFu);
        (void)act_now;
        (void)act_target;

        for (i = 0u; i < count; ++i) {
            u32 local_id = i + 1u;
            u64 task_id = dom_work_graph_builder_make_id(system_id_, local_id, DOM_WORK_ID_TASK);
            u64 access_id = dom_work_graph_builder_make_id(system_id_, local_id, DOM_WORK_ID_ACCESS);
            u64 cost_id = dom_work_graph_builder_make_id(system_id_, local_id, DOM_WORK_ID_COST);
            dom_task_node node;
            dom_access_set* set;
            dom_access_range range;
            dom_cost_model cost;

            node.task_id = task_id;
            node.system_id = system_id_;
            node.category = sim_affecting_ ? DOM_TASK_AUTHORITATIVE : DOM_TASK_DERIVED;
            node.determinism_class = sim_affecting_ ? DOM_DET_STRICT : DOM_DET_DERIVED;
            node.fidelity_tier = task_fidelity(tier_);
            node.next_due_tick = DOM_EXEC_TICK_INVALID;
            node.access_set_id = access_id;
            node.cost_model_id = cost_id;
            node.law_targets = law_target_count_ ? law_targets_ : (const u32*)0;
            node.law_target_count = law_target_count_;
            node.phase_id = 0u;
            node.commit_key = dom_work_graph_builder_make_commit_key(0u, task_id, 0u);
            node.law_scope_ref = 0u;
            node.actor_ref = 0u;
            node.capability_set_ref = 0u;
            node.policy_params = (const void*)0;
            node.policy_params_size = 0u;

            cost.cost_id = cost_id;
            cost.cpu_upper_bound = 1u + i;
            cost.memory_upper_bound = 1u;
            cost.bandwidth_upper_bound = 1u;
            cost.latency_class = DOM_LATENCY_LOW;
            cost.degradation_priority = 0;

            if (dom_work_graph_builder_add_cost_model(graph_builder, &cost) != 0) {
                return -1;
            }
            set = dom_access_set_builder_begin(access_builder, access_id, DOM_REDUCE_NONE, 0);
            if (!set) {
                return -2;
            }
            range.kind = DOM_RANGE_COMPONENT_SET;
            range.component_id = component_base + local_id;
            range.field_id = 0u;
            range.start_id = 0u;
            range.end_id = 0u;
            range.set_id = 0u;
            if (dom_access_set_builder_add_read(access_builder, &range) != 0) {
                return -3;
            }
            if (dom_access_set_builder_add_write(access_builder, &range) != 0) {
                return -4;
            }
            if (dom_access_set_builder_finalize(access_builder) != 0) {
                return -5;
            }
            if (dom_work_graph_builder_add_task(graph_builder, &node) != 0) {
                return -6;
            }
        }
        return 0;
    }

    void degrade(dom_fidelity_tier tier, u32 reason)
    {
        (void)reason;
        tier_ = tier;
    }

private:
    u32 emit_count_for_tier(dom_fidelity_tier tier) const
    {
        switch (tier) {
            case DOM_FIDELITY_LATENT: return emit_latent_;
            case DOM_FIDELITY_MACRO: return emit_macro_;
            case DOM_FIDELITY_MESO: return emit_micro_;
            case DOM_FIDELITY_MICRO: return emit_micro_;
            case DOM_FIDELITY_FOCUS: return emit_micro_;
            default: return emit_latent_;
        }
    }

    u64 system_id_;
    d_bool sim_affecting_;
    dom_fidelity_tier tier_;
    dom_act_time_t next_due_;
    u32 emit_latent_;
    u32 emit_macro_;
    u32 emit_micro_;
    u32 law_targets_[1];
    u32 law_target_count_;
};

static int test_registry_order(void)
{
    dom_system_registry registry;
    dom_system_entry entries[3];
    TestSystem sys_a(30u, 1);
    TestSystem sys_b(10u, 1);
    TestSystem sys_c(20u, 1);

    dom_system_registry_init(&registry, entries, 3u);
    EXPECT(dom_system_registry_register(&registry, &sys_a) == 0, "register a");
    EXPECT(dom_system_registry_register(&registry, &sys_b) == 0, "register b");
    EXPECT(dom_system_registry_register(&registry, &sys_c) == 0, "register c");
    EXPECT(dom_system_registry_count(&registry) == 3u, "registry count");
    EXPECT(dom_system_registry_system_id_at(&registry, 0u) == 10u, "order 0");
    EXPECT(dom_system_registry_system_id_at(&registry, 1u) == 20u, "order 1");
    EXPECT(dom_system_registry_system_id_at(&registry, 2u) == 30u, "order 2");
    return 0;
}

static int test_deterministic_emission(void)
{
    dom_system_registry registry;
    dom_system_entry entries[1];
    TestSystem sys(42u, 1);
    dom_task_node tasks[8];
    dom_dependency_edge deps[1];
    dom_phase_barrier barriers[1];
    dom_cost_model costs[8];
    dom_access_set access_sets[8];
    dom_access_range reads[16];
    dom_access_range writes[16];
    dom_access_range reduces[4];
    dom_task_graph graph_a;
    dom_task_graph graph_b;
    dom_work_graph_builder graph_builder;
    dom_access_set_builder access_builder;
    u64 hash_a;
    u64 hash_b;

    sys.set_emit_counts(1u, 2u, 3u);

    dom_system_registry_init(&registry, entries, 1u);
    EXPECT(dom_system_registry_register(&registry, &sys) == 0, "register sys");

    dom_work_graph_builder_init(&graph_builder, tasks, 8u, deps, 1u, barriers, 1u, costs, 8u);
    dom_access_set_builder_init(&access_builder, access_sets, 8u, reads, 16u, writes, 16u, reduces, 4u);

    dom_work_graph_builder_set_ids(&graph_builder, 100u, 1u);
    dom_access_set_builder_reset(&access_builder);
    dom_work_graph_builder_reset(&graph_builder);
    EXPECT(dom_system_registry_emit(&registry, 0, 10, &graph_builder, &access_builder) == 0, "emit A");
    dom_work_graph_builder_finalize(&graph_builder, &graph_a);
    hash_a = hash_task_graph(&graph_a);

    dom_access_set_builder_reset(&access_builder);
    dom_work_graph_builder_reset(&graph_builder);
    EXPECT(dom_system_registry_emit(&registry, 0, 10, &graph_builder, &access_builder) == 0, "emit B");
    dom_work_graph_builder_finalize(&graph_builder, &graph_b);
    hash_b = hash_task_graph(&graph_b);

    EXPECT(hash_a == hash_b, "deterministic hash mismatch");
    return 0;
}

static const dom_access_set* find_access_set(const dom_access_set* sets, u32 count, u64 access_id)
{
    u32 i;
    for (i = 0u; i < count; ++i) {
        if (sets[i].access_id == access_id) {
            return &sets[i];
        }
    }
    return (const dom_access_set*)0;
}

static int test_access_sets_and_law_targets(void)
{
    dom_system_registry registry;
    dom_system_entry entries[1];
    TestSystem sys(77u, 1);
    dom_task_node tasks[8];
    dom_dependency_edge deps[1];
    dom_phase_barrier barriers[1];
    dom_cost_model costs[8];
    dom_access_set access_sets[8];
    dom_access_range reads[16];
    dom_access_range writes[16];
    dom_access_range reduces[4];
    dom_work_graph_builder graph_builder;
    dom_access_set_builder access_builder;
    dom_task_graph graph;
    u32 i;

    sys.set_emit_counts(0u, 2u, 3u);
    dom_system_registry_init(&registry, entries, 1u);
    EXPECT(dom_system_registry_register(&registry, &sys) == 0, "register sys");

    dom_work_graph_builder_init(&graph_builder, tasks, 8u, deps, 1u, barriers, 1u, costs, 8u);
    dom_access_set_builder_init(&access_builder, access_sets, 8u, reads, 16u, writes, 16u, reduces, 4u);
    dom_work_graph_builder_reset(&graph_builder);
    dom_access_set_builder_reset(&access_builder);
    EXPECT(dom_system_registry_emit(&registry, 0, 10, &graph_builder, &access_builder) == 0, "emit tasks");
    dom_work_graph_builder_finalize(&graph_builder, &graph);

    for (i = 0u; i < graph.task_count; ++i) {
        const dom_task_node* node = &graph.tasks[i];
        const dom_access_set* set = find_access_set(access_sets, access_builder.set_count, node->access_set_id);
        EXPECT(set != 0, "missing access set");
        EXPECT(set->read_count > 0u || set->write_count > 0u, "empty access set");
        if (node->category == DOM_TASK_AUTHORITATIVE) {
            EXPECT(node->law_targets != 0, "missing law targets");
            EXPECT(node->law_target_count > 0u, "empty law targets");
        }
    }
    return 0;
}

static int test_disable_and_degrade(void)
{
    dom_system_registry registry;
    dom_system_entry entries[1];
    TestSystem sys(123u, 1);
    dom_task_node tasks[8];
    dom_dependency_edge deps[1];
    dom_phase_barrier barriers[1];
    dom_cost_model costs[8];
    dom_access_set access_sets[8];
    dom_access_range reads[16];
    dom_access_range writes[16];
    dom_access_range reduces[4];
    dom_work_graph_builder graph_builder;
    dom_access_set_builder access_builder;
    dom_task_graph graph;

    sys.set_emit_counts(0u, 2u, 3u);
    dom_system_registry_init(&registry, entries, 1u);
    EXPECT(dom_system_registry_register(&registry, &sys) == 0, "register sys");

    dom_work_graph_builder_init(&graph_builder, tasks, 8u, deps, 1u, barriers, 1u, costs, 8u);
    dom_access_set_builder_init(&access_builder, access_sets, 8u, reads, 16u, writes, 16u, reduces, 4u);

    EXPECT(dom_system_registry_set_fidelity(&registry, 123u, DOM_FIDELITY_MACRO) == 0, "set macro");
    dom_work_graph_builder_reset(&graph_builder);
    dom_access_set_builder_reset(&access_builder);
    EXPECT(dom_system_registry_emit(&registry, 0, 10, &graph_builder, &access_builder) == 0, "emit macro");
    dom_work_graph_builder_finalize(&graph_builder, &graph);
    EXPECT(graph.task_count == 2u, "macro count");

    EXPECT(dom_system_registry_set_fidelity(&registry, 123u, DOM_FIDELITY_LATENT) == 0, "set latent");
    dom_work_graph_builder_reset(&graph_builder);
    dom_access_set_builder_reset(&access_builder);
    EXPECT(dom_system_registry_emit(&registry, 0, 10, &graph_builder, &access_builder) == 0, "emit latent");
    dom_work_graph_builder_finalize(&graph_builder, &graph);
    EXPECT(graph.task_count == 0u, "latent count");

    EXPECT(dom_system_registry_set_enabled(&registry, 123u, 0) == 0, "disable system");
    dom_work_graph_builder_reset(&graph_builder);
    dom_access_set_builder_reset(&access_builder);
    EXPECT(dom_system_registry_emit(&registry, 0, 10, &graph_builder, &access_builder) == 0, "emit disabled");
    dom_work_graph_builder_finalize(&graph_builder, &graph);
    EXPECT(graph.task_count == 0u, "disabled count");
    return 0;
}

int main(void)
{
    if (test_registry_order() != 0) {
        return 1;
    }
    if (test_deterministic_emission() != 0) {
        return 1;
    }
    if (test_access_sets_and_law_targets() != 0) {
        return 1;
    }
    if (test_disable_and_degrade() != 0) {
        return 1;
    }
    return 0;
}
