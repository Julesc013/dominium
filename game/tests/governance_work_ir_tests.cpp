/*
Governance Work IR migration tests (ADOPT4).
*/
#include "dominium/rules/governance/governance_system.h"
#include "dominium/rules/governance/legitimacy_tasks.h"
#include "dominium/execution/work_graph_builder.h"
#include "dominium/execution/access_set_builder.h"
#include "domino/execution/task_graph.h"

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

static u64 hash_legitimacy(const legitimacy_registry* reg)
{
    u32 i;
    u64 h = fnv1a_init();
    if (!reg || !reg->states) {
        return h;
    }
    h = fnv1a_u32(h, reg->count);
    for (i = 0u; i < reg->count; ++i) {
        h = fnv1a_u64(h, reg->states[i].legitimacy_id);
        h = fnv1a_u32(h, reg->states[i].value);
        h = fnv1a_u32(h, reg->states[i].max_value);
    }
    return h;
}

static u64 hash_laws(const dom_governance_law_registry* reg)
{
    u32 i;
    u64 h = fnv1a_init();
    if (!reg || !reg->states) {
        return h;
    }
    h = fnv1a_u32(h, reg->count);
    for (i = 0u; i < reg->count; ++i) {
        h = fnv1a_u64(h, reg->states[i].law_id);
        h = fnv1a_u32(h, reg->states[i].state);
    }
    return h;
}

static int emit_graph(GovernanceSystem* system,
                      dom_work_graph_builder* graph_builder,
                      dom_access_set_builder* access_builder,
                      dom_task_graph* out_graph)
{
    if (!system || !graph_builder || !access_builder || !out_graph) {
        return -1;
    }
    dom_work_graph_builder_reset(graph_builder);
    dom_access_set_builder_reset(access_builder);
    dom_work_graph_builder_set_ids(graph_builder, 701u, 1u);
    if (system->emit_tasks(0, 10, graph_builder, access_builder) != 0) {
        return -2;
    }
    dom_work_graph_builder_finalize(graph_builder, out_graph);
    return 0;
}

static int execute_governance_graph(const dom_task_graph* graph,
                                    const dom_governance_inputs* inputs,
                                    dom_governance_buffers* buffers,
                                    dom_act_time_t now_tick)
{
    u32 i;
    if (!graph || !inputs || !buffers) {
        return -1;
    }
    for (i = 0u; i < graph->task_count; ++i) {
        const dom_task_node* node = &graph->tasks[i];
        const dom_governance_task_params* params = (const dom_governance_task_params*)node->policy_params;
        if (!params || params->count == 0u) {
            continue;
        }
        switch (params->op) {
            case DOM_GOV_TASK_POLICY_APPLY:
                dom_governance_policy_apply_slice(inputs->policies,
                                                  inputs->jurisdictions,
                                                  inputs->legitimacies,
                                                  inputs->enforcement,
                                                  params->start_index,
                                                  params->count,
                                                  now_tick,
                                                  buffers->audit_log);
                break;
            case DOM_GOV_TASK_LEGITIMACY_UPDATE:
                dom_governance_legitimacy_apply_slice(inputs->legitimacies,
                                                      inputs->legitimacy_events,
                                                      inputs->legitimacy_event_count,
                                                      params->start_index,
                                                      params->count,
                                                      now_tick,
                                                      buffers->audit_log);
                break;
            case DOM_GOV_TASK_AUTHORITY_ENFORCEMENT:
                dom_governance_authority_enforce_slice(inputs->authority_actions,
                                                       inputs->authority_action_count,
                                                       params->start_index,
                                                       params->count,
                                                       now_tick,
                                                       buffers->audit_log);
                break;
            case DOM_GOV_TASK_LAW_LIFECYCLE:
                dom_governance_law_lifecycle_slice(inputs->law_registry,
                                                   inputs->lifecycle_events,
                                                   inputs->lifecycle_event_count,
                                                   params->start_index,
                                                   params->count,
                                                   now_tick,
                                                   buffers->audit_log);
                break;
            default:
                return -2;
        }
    }
    return 0;
}

static void init_governance_inputs(dom_governance_inputs* inputs,
                                   policy_registry* policies,
                                   jurisdiction_registry* jurisdictions,
                                   legitimacy_registry* legitimacies,
                                   enforcement_capacity_registry* enforcement,
                                   dom_governance_law_registry* law_registry,
                                   const dom_governance_legitimacy_event* legit_events,
                                   u32 legit_count,
                                   const dom_governance_authority_action* authority_actions,
                                   u32 authority_count,
                                   const dom_governance_law_lifecycle_event* lifecycle_events,
                                   u32 lifecycle_count)
{
    if (!inputs) {
        return;
    }
    inputs->policies = policies;
    inputs->jurisdictions = jurisdictions;
    inputs->legitimacies = legitimacies;
    inputs->enforcement = enforcement;
    inputs->law_registry = law_registry;
    inputs->legitimacy_events = legit_events;
    inputs->legitimacy_event_count = legit_count;
    inputs->legitimacy_event_set_id = 7101u;
    inputs->authority_actions = authority_actions;
    inputs->authority_action_count = authority_count;
    inputs->authority_action_set_id = 7102u;
    inputs->lifecycle_events = lifecycle_events;
    inputs->lifecycle_event_count = lifecycle_count;
    inputs->lifecycle_event_set_id = 7103u;
}

static int init_governance_buffers(dom_governance_buffers* buffers,
                                   dom_governance_audit_log* audit,
                                   dom_governance_audit_entry* audit_entries,
                                   u32 audit_capacity)
{
    if (!buffers || !audit) {
        return -1;
    }
    dom_governance_audit_init(audit, audit_entries, audit_capacity, 1u);
    buffers->audit_log = audit;
    buffers->policy_set_id = 7201u;
    buffers->legitimacy_set_id = 7202u;
    buffers->enforcement_set_id = 7203u;
    buffers->law_state_set_id = 7204u;
    buffers->audit_set_id = 7205u;
    return 0;
}

static int setup_registries(policy_registry* policies,
                            policy_record* policy_storage,
                            u32 policy_capacity,
                            jurisdiction_registry* jurisdictions,
                            jurisdiction_record* jurisdiction_storage,
                            u32 jurisdiction_capacity,
                            legitimacy_registry* legitimacies,
                            legitimacy_state* legitimacy_storage,
                            u32 legitimacy_capacity,
                            enforcement_capacity_registry* enforcement,
                            enforcement_capacity* enforcement_storage,
                            u32 enforcement_capacity_max)
{
    policy_record policy;
    legitimacy_state* legitimacy;
    policy_registry_init(policies, policy_storage, policy_capacity);
    jurisdiction_registry_init(jurisdictions, jurisdiction_storage, jurisdiction_capacity);
    legitimacy_registry_init(legitimacies, legitimacy_storage, legitimacy_capacity);
    enforcement_capacity_registry_init(enforcement, enforcement_storage, enforcement_capacity_max);

    if (jurisdiction_register(jurisdictions, 100u, 0u, 0u, 0u) != 0) {
        return -1;
    }
    if (legitimacy_register(legitimacies, 200u, 500u, 1000u, 700u, 300u, 100u) != 0) {
        return -2;
    }
    if (enforcement_capacity_register(enforcement, 300u, 5u, 100u, 1u, 0u) != 0) {
        return -3;
    }
    if (jurisdiction_set_refs(jurisdictions, 100u, 200u, 300u) != 0) {
        return -4;
    }
    legitimacy = legitimacy_find(legitimacies, 200u);
    if (!legitimacy) {
        return -5;
    }

    policy.policy_id = 400u;
    policy.jurisdiction_id = 100u;
    policy.type = POLICY_TAXATION;
    policy.schedule.start_act = 0u;
    policy.schedule.interval_act = 5u;
    policy.legitimacy_min = 200u;
    policy.capacity_min = 1u;
    policy.next_due_tick = 0u;
    if (policy_register(policies, &policy) != 0) {
        return -6;
    }
    return 0;
}

static int test_deterministic_governance(void)
{
    policy_registry policies_a;
    policy_registry policies_b;
    jurisdiction_registry jurisdictions_a;
    jurisdiction_registry jurisdictions_b;
    legitimacy_registry legitimacies_a;
    legitimacy_registry legitimacies_b;
    enforcement_capacity_registry enforcement_a;
    enforcement_capacity_registry enforcement_b;
    dom_governance_law_registry law_a;
    dom_governance_law_registry law_b;
    dom_governance_law_state law_states_a[4];
    dom_governance_law_state law_states_b[4];
    dom_governance_legitimacy_event legit_events[2] = {
        { 1u, 200u, -50, 0u },
        { 2u, 200u, 25, 0u }
    };
    dom_governance_authority_action authority_actions[1] = {
        { 10u, 100u, 1u, 0u }
    };
    dom_governance_law_lifecycle_event lifecycle_events[1] = {
        { 900u, 2u, 0u }
    };
    dom_governance_inputs inputs_a;
    dom_governance_inputs inputs_b;
    dom_governance_buffers buffers_a;
    dom_governance_buffers buffers_b;
    dom_governance_audit_log audit_a;
    dom_governance_audit_log audit_b;
    dom_governance_audit_entry audit_entries_a[16];
    dom_governance_audit_entry audit_entries_b[16];
    dom_task_node tasks[16];
    dom_dependency_edge deps[16];
    dom_phase_barrier barriers[4];
    dom_cost_model costs[16];
    dom_access_set access_sets[16];
    dom_access_range reads[32];
    dom_access_range writes[32];
    dom_access_range reduces[8];
    dom_work_graph_builder graph_builder;
    dom_access_set_builder access_builder;
    dom_task_graph graph;
    GovernanceSystem system_a;
    GovernanceSystem system_b;
    u64 hash_a;
    u64 hash_b;

    policy_record policy_storage_a[4];
    policy_record policy_storage_b[4];
    jurisdiction_record jurisdiction_storage_a[2];
    jurisdiction_record jurisdiction_storage_b[2];
    legitimacy_state legitimacy_storage_a[2];
    legitimacy_state legitimacy_storage_b[2];
    enforcement_capacity enforcement_storage_a[2];
    enforcement_capacity enforcement_storage_b[2];
    EXPECT(setup_registries(&policies_a, policy_storage_a, 4u,
                            &jurisdictions_a, jurisdiction_storage_a, 2u,
                            &legitimacies_a, legitimacy_storage_a, 2u,
                            &enforcement_a, enforcement_storage_a, 2u) == 0, "setup A");
    EXPECT(setup_registries(&policies_b, policy_storage_b, 4u,
                            &jurisdictions_b, jurisdiction_storage_b, 2u,
                            &legitimacies_b, legitimacy_storage_b, 2u,
                            &enforcement_b, enforcement_storage_b, 2u) == 0, "setup B");
    dom_governance_law_registry_init(&law_a, law_states_a, 4u);
    dom_governance_law_registry_init(&law_b, law_states_b, 4u);

    init_governance_inputs(&inputs_a, &policies_a, &jurisdictions_a, &legitimacies_a, &enforcement_a,
                           &law_a, legit_events, 2u, authority_actions, 1u, lifecycle_events, 1u);
    init_governance_inputs(&inputs_b, &policies_b, &jurisdictions_b, &legitimacies_b, &enforcement_b,
                           &law_b, legit_events, 2u, authority_actions, 1u, lifecycle_events, 1u);

    EXPECT(init_governance_buffers(&buffers_a, &audit_a, audit_entries_a, 16u) == 0, "buffers A");
    EXPECT(init_governance_buffers(&buffers_b, &audit_b, audit_entries_b, 16u) == 0, "buffers B");

    system_a.init(&inputs_a, &buffers_a);
    system_b.init(&inputs_b, &buffers_b);

    dom_work_graph_builder_init(&graph_builder, tasks, 16u, deps, 16u, barriers, 4u, costs, 16u);
    dom_access_set_builder_init(&access_builder, access_sets, 16u, reads, 32u, writes, 32u, reduces, 8u);

    EXPECT(emit_graph(&system_a, &graph_builder, &access_builder, &graph) == 0, "emit A");
    EXPECT(execute_governance_graph(&graph, &inputs_a, &buffers_a, 0u) == 0, "exec A");
    hash_a = hash_legitimacy(&legitimacies_a) ^ hash_laws(&law_a);

    EXPECT(emit_graph(&system_b, &graph_builder, &access_builder, &graph) == 0, "emit B");
    EXPECT(execute_governance_graph(&graph, &inputs_b, &buffers_b, 0u) == 0, "exec B");
    hash_b = hash_legitimacy(&legitimacies_b) ^ hash_laws(&law_b);

    EXPECT(hash_a == hash_b, "governance determinism mismatch");
    return 0;
}

static int test_budget_compliance(void)
{
    policy_registry policies;
    jurisdiction_registry jurisdictions;
    legitimacy_registry legitimacies;
    enforcement_capacity_registry enforcement;
    dom_governance_law_registry law_reg;
    dom_governance_law_state law_states[2];
    dom_governance_legitimacy_event legit_events[2] = {
        { 1u, 200u, -10, 0u },
        { 2u, 200u, -10, 0u }
    };
    dom_governance_inputs inputs;
    dom_governance_buffers buffers;
    dom_governance_audit_log audit;
    dom_governance_audit_entry audit_entries[8];
    dom_task_node tasks[16];
    dom_dependency_edge deps[16];
    dom_phase_barrier barriers[4];
    dom_cost_model costs[16];
    dom_access_set access_sets[16];
    dom_access_range reads[32];
    dom_access_range writes[32];
    dom_access_range reduces[8];
    dom_work_graph_builder graph_builder;
    dom_access_set_builder access_builder;
    dom_task_graph graph;
    GovernanceSystem system;
    u32 total = 0u;
    u32 i;

    policy_record policy_storage[4];
    jurisdiction_record jurisdiction_storage[2];
    legitimacy_state legitimacy_storage[2];
    enforcement_capacity enforcement_storage[2];
    EXPECT(setup_registries(&policies, policy_storage, 4u,
                            &jurisdictions, jurisdiction_storage, 2u,
                            &legitimacies, legitimacy_storage, 2u,
                            &enforcement, enforcement_storage, 2u) == 0, "setup");
    dom_governance_law_registry_init(&law_reg, law_states, 2u);
    init_governance_inputs(&inputs, &policies, &jurisdictions, &legitimacies, &enforcement,
                           &law_reg, legit_events, 2u, 0, 0u, 0, 0u);
    EXPECT(init_governance_buffers(&buffers, &audit, audit_entries, 8u) == 0, "buffers");

    system.init(&inputs, &buffers);
    system.set_budget_hint(1u);

    dom_work_graph_builder_init(&graph_builder, tasks, 16u, deps, 16u, barriers, 4u, costs, 16u);
    dom_access_set_builder_init(&access_builder, access_sets, 16u, reads, 32u, writes, 32u, reduces, 8u);

    EXPECT(emit_graph(&system, &graph_builder, &access_builder, &graph) == 0, "emit budget");
    for (i = 0u; i < graph.task_count; ++i) {
        const dom_governance_task_params* params = (const dom_governance_task_params*)graph.tasks[i].policy_params;
        if (params) {
            total += params->count;
        }
    }
    EXPECT(total <= 1u, "budget exceeded");
    return 0;
}

static int test_law_gating(void)
{
    policy_registry policies;
    jurisdiction_registry jurisdictions;
    legitimacy_registry legitimacies;
    enforcement_capacity_registry enforcement;
    dom_governance_law_registry law_reg;
    dom_governance_law_state law_states[2];
    dom_governance_inputs inputs;
    dom_governance_buffers buffers;
    dom_governance_audit_log audit;
    dom_governance_audit_entry audit_entries[8];
    dom_task_node tasks[8];
    dom_dependency_edge deps[8];
    dom_phase_barrier barriers[2];
    dom_cost_model costs[8];
    dom_access_set access_sets[8];
    dom_access_range reads[16];
    dom_access_range writes[16];
    dom_access_range reduces[4];
    dom_work_graph_builder graph_builder;
    dom_access_set_builder access_builder;
    dom_task_graph graph;
    GovernanceSystem system;

    policy_record policy_storage2[4];
    jurisdiction_record jurisdiction_storage2[2];
    legitimacy_state legitimacy_storage2[2];
    enforcement_capacity enforcement_storage2[2];
    EXPECT(setup_registries(&policies, policy_storage2, 4u,
                            &jurisdictions, jurisdiction_storage2, 2u,
                            &legitimacies, legitimacy_storage2, 2u,
                            &enforcement, enforcement_storage2, 2u) == 0, "setup");
    dom_governance_law_registry_init(&law_reg, law_states, 2u);
    init_governance_inputs(&inputs, &policies, &jurisdictions, &legitimacies, &enforcement,
                           &law_reg, 0, 0u, 0, 0u, 0, 0u);
    EXPECT(init_governance_buffers(&buffers, &audit, audit_entries, 8u) == 0, "buffers");

    system.init(&inputs, &buffers);
    system.set_allowed_ops_mask(0u);

    dom_work_graph_builder_init(&graph_builder, tasks, 8u, deps, 8u, barriers, 2u, costs, 8u);
    dom_access_set_builder_init(&access_builder, access_sets, 8u, reads, 16u, writes, 16u, reduces, 4u);

    EXPECT(emit_graph(&system, &graph_builder, &access_builder, &graph) == 0, "emit gated");
    EXPECT(graph.task_count == 0u, "gated governance should emit no tasks");
    return 0;
}

static int test_batch_vs_step_equivalence(void)
{
    policy_registry policies_batch;
    policy_registry policies_step;
    jurisdiction_registry jurisdictions_batch;
    jurisdiction_registry jurisdictions_step;
    legitimacy_registry legitimacies_batch;
    legitimacy_registry legitimacies_step;
    enforcement_capacity_registry enforcement_batch;
    enforcement_capacity_registry enforcement_step;
    dom_governance_law_registry law_batch;
    dom_governance_law_registry law_step;
    dom_governance_law_state law_states_batch[4];
    dom_governance_law_state law_states_step[4];
    dom_governance_legitimacy_event legit_events[2] = {
        { 1u, 200u, -50, 0u },
        { 2u, 200u, 10, 0u }
    };
    dom_governance_inputs inputs_batch;
    dom_governance_inputs inputs_step;
    dom_governance_buffers buffers_batch;
    dom_governance_buffers buffers_step;
    dom_governance_audit_log audit_batch;
    dom_governance_audit_log audit_step;
    dom_governance_audit_entry audit_entries_batch[16];
    dom_governance_audit_entry audit_entries_step[16];
    dom_task_node tasks[16];
    dom_dependency_edge deps[16];
    dom_phase_barrier barriers[4];
    dom_cost_model costs[16];
    dom_access_set access_sets[16];
    dom_access_range reads[32];
    dom_access_range writes[32];
    dom_access_range reduces[8];
    dom_work_graph_builder graph_builder;
    dom_access_set_builder access_builder;
    dom_task_graph graph;
    GovernanceSystem system_batch;
    GovernanceSystem system_step;
    u64 hash_batch;
    u64 hash_step;
    u32 iterations = 0u;

    policy_record policy_storage_batch[4];
    policy_record policy_storage_step[4];
    jurisdiction_record jurisdiction_storage_batch[2];
    jurisdiction_record jurisdiction_storage_step[2];
    legitimacy_state legitimacy_storage_batch[2];
    legitimacy_state legitimacy_storage_step[2];
    enforcement_capacity enforcement_storage_batch[2];
    enforcement_capacity enforcement_storage_step[2];
    EXPECT(setup_registries(&policies_batch, policy_storage_batch, 4u,
                            &jurisdictions_batch, jurisdiction_storage_batch, 2u,
                            &legitimacies_batch, legitimacy_storage_batch, 2u,
                            &enforcement_batch, enforcement_storage_batch, 2u) == 0, "setup batch");
    EXPECT(setup_registries(&policies_step, policy_storage_step, 4u,
                            &jurisdictions_step, jurisdiction_storage_step, 2u,
                            &legitimacies_step, legitimacy_storage_step, 2u,
                            &enforcement_step, enforcement_storage_step, 2u) == 0, "setup step");
    dom_governance_law_registry_init(&law_batch, law_states_batch, 4u);
    dom_governance_law_registry_init(&law_step, law_states_step, 4u);

    init_governance_inputs(&inputs_batch, &policies_batch, &jurisdictions_batch, &legitimacies_batch, &enforcement_batch,
                           &law_batch, legit_events, 2u, 0, 0u, 0, 0u);
    init_governance_inputs(&inputs_step, &policies_step, &jurisdictions_step, &legitimacies_step, &enforcement_step,
                           &law_step, legit_events, 2u, 0, 0u, 0, 0u);

    EXPECT(init_governance_buffers(&buffers_batch, &audit_batch, audit_entries_batch, 16u) == 0, "buffers batch");
    EXPECT(init_governance_buffers(&buffers_step, &audit_step, audit_entries_step, 16u) == 0, "buffers step");

    system_batch.init(&inputs_batch, &buffers_batch);
    system_step.init(&inputs_step, &buffers_step);
    system_batch.set_budget_hint(16u);
    system_step.set_budget_hint(1u);

    dom_work_graph_builder_init(&graph_builder, tasks, 16u, deps, 16u, barriers, 4u, costs, 16u);
    dom_access_set_builder_init(&access_builder, access_sets, 16u, reads, 32u, writes, 32u, reduces, 8u);

    EXPECT(emit_graph(&system_batch, &graph_builder, &access_builder, &graph) == 0, "emit batch");
    EXPECT(execute_governance_graph(&graph, &inputs_batch, &buffers_batch, 0u) == 0, "exec batch");
    hash_batch = hash_legitimacy(&legitimacies_batch) ^ hash_laws(&law_batch);

    while (iterations < 16u) {
        EXPECT(emit_graph(&system_step, &graph_builder, &access_builder, &graph) == 0, "emit step");
        if (graph.task_count == 0u) {
            break;
        }
        EXPECT(execute_governance_graph(&graph, &inputs_step, &buffers_step, 0u) == 0, "exec step");
        iterations += 1u;
    }
    hash_step = hash_legitimacy(&legitimacies_step) ^ hash_laws(&law_step);
    EXPECT(hash_batch == hash_step, "batch vs step mismatch");
    return 0;
}

static int test_auditability(void)
{
    policy_registry policies;
    jurisdiction_registry jurisdictions;
    legitimacy_registry legitimacies;
    enforcement_capacity_registry enforcement;
    dom_governance_law_registry law_reg;
    dom_governance_law_state law_states[2];
    dom_governance_legitimacy_event legit_events[1] = { { 1u, 200u, -10, 0u } };
    dom_governance_authority_action authority_actions[1] = { { 20u, 100u, 1u, 0u } };
    dom_governance_law_lifecycle_event lifecycle_events[1] = { { 900u, 3u, 0u } };
    dom_governance_inputs inputs;
    dom_governance_buffers buffers;
    dom_governance_audit_log audit;
    dom_governance_audit_entry audit_entries[16];
    dom_task_node tasks[16];
    dom_dependency_edge deps[16];
    dom_phase_barrier barriers[4];
    dom_cost_model costs[16];
    dom_access_set access_sets[16];
    dom_access_range reads[32];
    dom_access_range writes[32];
    dom_access_range reduces[8];
    dom_work_graph_builder graph_builder;
    dom_access_set_builder access_builder;
    dom_task_graph graph;
    GovernanceSystem system;

    policy_record policy_storage3[4];
    jurisdiction_record jurisdiction_storage3[2];
    legitimacy_state legitimacy_storage3[2];
    enforcement_capacity enforcement_storage3[2];
    EXPECT(setup_registries(&policies, policy_storage3, 4u,
                            &jurisdictions, jurisdiction_storage3, 2u,
                            &legitimacies, legitimacy_storage3, 2u,
                            &enforcement, enforcement_storage3, 2u) == 0, "setup");
    dom_governance_law_registry_init(&law_reg, law_states, 2u);
    init_governance_inputs(&inputs, &policies, &jurisdictions, &legitimacies, &enforcement,
                           &law_reg, legit_events, 1u, authority_actions, 1u, lifecycle_events, 1u);
    EXPECT(init_governance_buffers(&buffers, &audit, audit_entries, 16u) == 0, "buffers");

    system.init(&inputs, &buffers);

    dom_work_graph_builder_init(&graph_builder, tasks, 16u, deps, 16u, barriers, 4u, costs, 16u);
    dom_access_set_builder_init(&access_builder, access_sets, 16u, reads, 32u, writes, 32u, reduces, 8u);

    EXPECT(emit_graph(&system, &graph_builder, &access_builder, &graph) == 0, "emit audit");
    EXPECT(execute_governance_graph(&graph, &inputs, &buffers, 0u) == 0, "exec audit");
    EXPECT(audit.count >= 3u, "audit count too low");
    return 0;
}

int main(void)
{
    if (test_deterministic_governance() != 0) return 1;
    if (test_budget_compliance() != 0) return 1;
    if (test_law_gating() != 0) return 1;
    if (test_batch_vs_step_equivalence() != 0) return 1;
    if (test_auditability() != 0) return 1;
    return 0;
}
