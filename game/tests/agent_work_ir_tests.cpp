/*
Agent Work IR migration tests (ADOPT6).
*/
#include "dominium/rules/agents/agent_system.h"
#include "dominium/rules/agents/agent_planning_tasks.h"
#include "dominium/rules/agents/agent_doctrine_tasks.h"
#include "dominium/rules/agents/agent_aggregation_tasks.h"
#include "dominium/execution/work_graph_builder.h"
#include "dominium/execution/access_set_builder.h"
#include "domino/execution/task_graph.h"

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

static void init_inputs(dom_agent_inputs* inputs,
                        dom_agent_schedule_item* schedule,
                        u32 schedule_count,
                        const agent_goal_registry* goals,
                        dom_agent_belief* beliefs,
                        u32 belief_count,
                        dom_agent_capability* capabilities,
                        u32 capability_count,
                        dom_agent_doctrine_entry* doctrines,
                        u32 doctrine_count,
                        dom_agent_population_item* population,
                        u32 population_count,
                        const dom_agent_aggregation_policy* policy)
{
    if (!inputs) {
        return;
    }
    inputs->schedule = schedule;
    inputs->schedule_count = schedule_count;
    inputs->schedule_set_id = 8701u;

    inputs->goals = goals;
    inputs->goal_set_id = 8700u;

    inputs->beliefs = beliefs;
    inputs->belief_count = belief_count;
    inputs->belief_set_id = 8702u;

    inputs->capabilities = capabilities;
    inputs->capability_count = capability_count;
    inputs->capability_set_id = 8703u;

    inputs->authority = 0;
    inputs->authority_set_id = 0u;
    inputs->constraints = 0;
    inputs->constraint_set_id = 0u;
    inputs->contracts = 0;
    inputs->contract_set_id = 0u;
    inputs->delegations = 0;
    inputs->delegation_set_id = 0u;

    inputs->doctrines = doctrines;
    inputs->doctrine_count = doctrine_count;
    inputs->doctrine_set_id = 8704u;

    inputs->population = population;
    inputs->population_count = population_count;
    inputs->population_set_id = 8705u;

    inputs->aggregation_policy = policy;
}

static int init_buffers(dom_agent_buffers* buffers,
                        dom_agent_goal_buffer* goals,
                        dom_agent_goal_choice* goal_storage,
                        u32 goal_capacity,
                        dom_agent_plan_buffer* plans,
                        dom_agent_plan* plan_storage,
                        u32 plan_capacity,
                        dom_agent_command_buffer* commands,
                        dom_agent_command* command_storage,
                        u32 command_capacity,
                        dom_agent_role_buffer* roles,
                        dom_agent_role_state* role_storage,
                        u32 role_capacity,
                        dom_agent_cohort_buffer* cohorts,
                        dom_agent_cohort_item* cohort_storage,
                        u32 cohort_capacity,
                        dom_agent_audit_log* audit,
                        dom_agent_audit_entry* audit_storage,
                        u32 audit_capacity)
{
    if (!buffers || !goals || !plans || !commands || !roles || !cohorts || !audit) {
        return -1;
    }
    dom_agent_goal_buffer_init(goals, goal_storage, goal_capacity);
    dom_agent_plan_buffer_init(plans, plan_storage, plan_capacity, 1u);
    dom_agent_command_buffer_init(commands, command_storage, command_capacity, 1u);
    dom_agent_role_buffer_init(roles, role_storage, role_capacity);
    dom_agent_cohort_buffer_init(cohorts, cohort_storage, cohort_capacity);
    dom_agent_audit_init(audit, audit_storage, audit_capacity, 1u);

    buffers->goals = goals;
    buffers->plans = plans;
    buffers->commands = commands;
    buffers->roles = roles;
    buffers->cohorts = cohorts;
    buffers->audit_log = audit;
    buffers->goal_set_id = 8801u;
    buffers->plan_set_id = 8802u;
    buffers->command_set_id = 8803u;
    buffers->role_set_id = 8804u;
    buffers->cohort_set_id = 8805u;
    buffers->audit_set_id = 8806u;
    return 0;
}

static int emit_graph(AgentSystem* system,
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

static int execute_agent_graph(const dom_task_graph* graph,
                               const dom_agent_inputs* inputs,
                               dom_agent_buffers* buffers)
{
    u32 i;
    if (!graph || !inputs || !buffers) {
        return -1;
    }
    for (i = 0u; i < graph->task_count; ++i) {
        const dom_task_node* node = &graph->tasks[i];
        const dom_agent_task_params* params = (const dom_agent_task_params*)node->policy_params;
        if (!params || params->count == 0u) {
            continue;
        }
        switch (params->op) {
            case DOM_AGENT_TASK_EVALUATE_GOALS:
                dom_agent_evaluate_goals_slice(inputs->schedule,
                                               inputs->schedule_count,
                                               params->start_index,
                                               params->count,
                                               (agent_goal_registry*)inputs->goals,
                                               inputs->beliefs,
                                               inputs->belief_count,
                                               inputs->capabilities,
                                               inputs->capability_count,
                                               buffers->goals,
                                               buffers->audit_log);
                break;
            case DOM_AGENT_TASK_PLAN_ACTIONS:
                dom_agent_plan_actions_slice(buffers->goals,
                                             params->start_index,
                                             params->count,
                                             (agent_goal_registry*)inputs->goals,
                                             inputs->beliefs,
                                             inputs->belief_count,
                                             inputs->capabilities,
                                             inputs->capability_count,
                                             inputs->schedule,
                                             inputs->schedule_count,
                                             buffers->plans,
                                             buffers->audit_log);
                break;
            case DOM_AGENT_TASK_VALIDATE_PLAN:
                dom_agent_validate_plan_slice(buffers->plans,
                                              params->start_index,
                                              params->count,
                                              inputs->capabilities,
                                              inputs->capability_count,
                                              inputs->authority,
                                              inputs->constraints,
                                              inputs->contracts,
                                              inputs->delegations,
                                              (agent_goal_registry*)inputs->goals,
                                              buffers->audit_log);
                break;
            case DOM_AGENT_TASK_EMIT_COMMANDS:
                dom_agent_emit_commands_slice(buffers->plans,
                                              params->start_index,
                                              params->count,
                                              buffers->commands,
                                              buffers->audit_log);
                break;
            case DOM_AGENT_TASK_APPLY_DOCTRINE:
                dom_agent_apply_doctrine_slice(inputs->doctrines,
                                               inputs->doctrine_count,
                                               params->start_index,
                                               params->count,
                                               buffers->roles,
                                               buffers->audit_log);
                break;
            case DOM_AGENT_TASK_UPDATE_ROLES:
                dom_agent_update_roles_slice(buffers->roles,
                                             params->start_index,
                                             params->count,
                                             buffers->audit_log);
                break;
            case DOM_AGENT_TASK_AGGREGATE_COHORTS:
                dom_agent_aggregate_cohorts_slice(inputs->population,
                                                  inputs->population_count,
                                                  params->start_index,
                                                  params->count,
                                                  buffers->cohorts,
                                                  buffers->audit_log);
                break;
            case DOM_AGENT_TASK_REFINE_INDIVIDUALS:
                dom_agent_refine_individuals_slice(inputs->population,
                                                   inputs->population_count,
                                                   params->start_index,
                                                   params->count,
                                                   inputs->aggregation_policy,
                                                   buffers->audit_log);
                break;
            case DOM_AGENT_TASK_COLLAPSE_INDIVIDUALS:
                dom_agent_collapse_individuals_slice(inputs->population,
                                                     inputs->population_count,
                                                     params->start_index,
                                                     params->count,
                                                     inputs->aggregation_policy,
                                                     buffers->audit_log);
                break;
            default:
                return -2;
        }
    }
    return 0;
}

static u64 hash_commands(const dom_agent_command_buffer* commands)
{
    u32 i;
    u64 h = fnv1a_init();
    if (!commands || !commands->entries) {
        return h;
    }
    h = fnv1a_u32(h, commands->count);
    for (i = 0u; i < commands->count; ++i) {
        const dom_agent_command* cmd = &commands->entries[i];
        h = fnv1a_u64(h, cmd->command_id);
        h = fnv1a_u64(h, cmd->agent_id);
        h = fnv1a_u64(h, cmd->process_id);
        h = fnv1a_u32(h, cmd->process_kind);
        h = fnv1a_u64(h, cmd->goal_id);
        h = fnv1a_u64(h, cmd->target_id);
    }
    return h;
}

static u64 hash_cohorts(const dom_agent_cohort_buffer* cohorts)
{
    u32 i;
    u64 h = fnv1a_init();
    if (!cohorts || !cohorts->entries) {
        return h;
    }
    h = fnv1a_u32(h, cohorts->count);
    for (i = 0u; i < cohorts->count; ++i) {
        const dom_agent_cohort_item* item = &cohorts->entries[i];
        h = fnv1a_u64(h, item->cohort_id);
        h = fnv1a_u32(h, item->member_count);
    }
    return h;
}

static int test_deterministic_planning(void)
{
    dom_agent_schedule_item schedule_a[2];
    dom_agent_schedule_item schedule_b[2];
    dom_agent_belief beliefs_a[3];
    dom_agent_belief beliefs_b[3];
    dom_agent_capability caps_a[2];
    dom_agent_capability caps_b[2];
    agent_goal goals_storage[4];
    agent_goal_registry goals;
    dom_agent_inputs inputs_a;
    dom_agent_inputs inputs_b;
    dom_agent_buffers buffers_a;
    dom_agent_buffers buffers_b;
    dom_agent_goal_buffer goals_a;
    dom_agent_goal_buffer goals_b;
    dom_agent_goal_choice goal_storage_a[4];
    dom_agent_goal_choice goal_storage_b[4];
    dom_agent_plan_buffer plans_a;
    dom_agent_plan_buffer plans_b;
    dom_agent_plan plan_storage_a[4];
    dom_agent_plan plan_storage_b[4];
    dom_agent_command_buffer commands_a;
    dom_agent_command_buffer commands_b;
    dom_agent_command command_storage_a[4];
    dom_agent_command command_storage_b[4];
    dom_agent_role_buffer roles_a;
    dom_agent_role_buffer roles_b;
    dom_agent_role_state role_storage_a[4];
    dom_agent_role_state role_storage_b[4];
    dom_agent_cohort_buffer cohorts_a;
    dom_agent_cohort_buffer cohorts_b;
    dom_agent_cohort_item cohort_storage_a[4];
    dom_agent_cohort_item cohort_storage_b[4];
    dom_agent_audit_log audit_a;
    dom_agent_audit_log audit_b;
    dom_agent_audit_entry audit_storage_a[16];
    dom_agent_audit_entry audit_storage_b[16];
    dom_task_node tasks[32];
    dom_dependency_edge deps[16];
    dom_phase_barrier barriers[8];
    dom_cost_model costs[32];
    dom_access_set access_sets[32];
    dom_access_range reads[64];
    dom_access_range writes[64];
    dom_access_range reduces[8];
    dom_work_graph_builder graph_builder;
    dom_access_set_builder access_builder;
    dom_task_graph graph;
    AgentSystem system_a;
    AgentSystem system_b;
    u64 hash_a;
    u64 hash_b;

    memset(schedule_a, 0, sizeof(schedule_a));
    schedule_a[0].agent_id = 101u;
    schedule_a[1].agent_id = 102u;
    memcpy(schedule_b, schedule_a, sizeof(schedule_a));

    memset(beliefs_a, 0, sizeof(beliefs_a));
    beliefs_a[0].agent_id = 101u;
    beliefs_a[0].knowledge_mask = 0u;
    beliefs_a[1].agent_id = 102u;
    beliefs_a[1].knowledge_mask = 0u;
    memcpy(beliefs_b, beliefs_a, sizeof(beliefs_a));

    caps_a[0].agent_id = 101u;
    caps_a[0].capability_mask = 0u;
    caps_a[0].authority_mask = 0u;
    caps_a[1].agent_id = 102u;
    caps_a[1].capability_mask = 0u;
    caps_a[1].authority_mask = 0u;
    memcpy(caps_b, caps_a, sizeof(caps_a));

    agent_goal_registry_init(&goals, goals_storage, 4u, 1u);
    {
        agent_goal_desc desc;
        u64 goal_id = 0u;
        memset(&desc, 0, sizeof(desc));
        desc.agent_id = 101u;
        desc.type = AGENT_GOAL_RESEARCH;
        desc.base_priority = 10u;
        agent_goal_register(&goals, &desc, &goal_id);
        memset(&desc, 0, sizeof(desc));
        desc.agent_id = 102u;
        desc.type = AGENT_GOAL_RESEARCH;
        desc.base_priority = 12u;
        agent_goal_register(&goals, &desc, &goal_id);
    }

    init_inputs(&inputs_a, schedule_a, 2u,
                &goals,
                beliefs_a, 2u,
                caps_a, 2u,
                0, 0u,
                0, 0u,
                0);
    init_inputs(&inputs_b, schedule_b, 2u,
                &goals,
                beliefs_b, 2u,
                caps_b, 2u,
                0, 0u,
                0, 0u,
                0);

    EXPECT(init_buffers(&buffers_a,
                        &goals_a, goal_storage_a, 4u,
                        &plans_a, plan_storage_a, 4u,
                        &commands_a, command_storage_a, 4u,
                        &roles_a, role_storage_a, 4u,
                        &cohorts_a, cohort_storage_a, 4u,
                        &audit_a, audit_storage_a, 16u) == 0, "buffers a");
    EXPECT(init_buffers(&buffers_b,
                        &goals_b, goal_storage_b, 4u,
                        &plans_b, plan_storage_b, 4u,
                        &commands_b, command_storage_b, 4u,
                        &roles_b, role_storage_b, 4u,
                        &cohorts_b, cohort_storage_b, 4u,
                        &audit_b, audit_storage_b, 16u) == 0, "buffers b");

    system_a.init(&inputs_a, &buffers_a);
    system_b.init(&inputs_b, &buffers_b);

    dom_work_graph_builder_init(&graph_builder, tasks, 32u, deps, 16u, barriers, 8u, costs, 32u);
    dom_access_set_builder_init(&access_builder, access_sets, 32u,
                                reads, 64u, writes, 64u, reduces, 8u);

    EXPECT(emit_graph(&system_a, &graph_builder, &access_builder, &graph) == 0, "emit a");
    EXPECT(execute_agent_graph(&graph, &inputs_a, &buffers_a) == 0, "exec a");
    hash_a = hash_commands(buffers_a.commands);

    EXPECT(emit_graph(&system_b, &graph_builder, &access_builder, &graph) == 0, "emit b");
    EXPECT(execute_agent_graph(&graph, &inputs_b, &buffers_b) == 0, "exec b");
    hash_b = hash_commands(buffers_b.commands);

    EXPECT(hash_a == hash_b, "planning determinism mismatch");
    return 0;
}

static int test_batch_vs_step_equivalence(void)
{
    dom_agent_schedule_item schedule[4];
    dom_agent_belief beliefs[4];
    dom_agent_capability caps[4];
    agent_goal goals_storage[8];
    agent_goal_registry goals;
    dom_agent_inputs inputs;
    dom_agent_buffers buffers_batch;
    dom_agent_buffers buffers_step;
    dom_agent_goal_buffer goals_batch;
    dom_agent_goal_buffer goals_step;
    dom_agent_goal_choice goal_storage_batch[8];
    dom_agent_goal_choice goal_storage_step[8];
    dom_agent_plan_buffer plans_batch;
    dom_agent_plan_buffer plans_step;
    dom_agent_plan plan_storage_batch[8];
    dom_agent_plan plan_storage_step[8];
    dom_agent_command_buffer commands_batch;
    dom_agent_command_buffer commands_step;
    dom_agent_command command_storage_batch[8];
    dom_agent_command command_storage_step[8];
    dom_agent_role_buffer roles_batch;
    dom_agent_role_buffer roles_step;
    dom_agent_role_state role_storage_batch[4];
    dom_agent_role_state role_storage_step[4];
    dom_agent_cohort_buffer cohorts_batch;
    dom_agent_cohort_buffer cohorts_step;
    dom_agent_cohort_item cohort_storage_batch[4];
    dom_agent_cohort_item cohort_storage_step[4];
    dom_agent_audit_log audit_batch;
    dom_agent_audit_log audit_step;
    dom_agent_audit_entry audit_storage_batch[32];
    dom_agent_audit_entry audit_storage_step[32];
    dom_task_node tasks[64];
    dom_dependency_edge deps[32];
    dom_phase_barrier barriers[16];
    dom_cost_model costs[64];
    dom_access_set access_sets[64];
    dom_access_range reads[128];
    dom_access_range writes[128];
    dom_access_range reduces[16];
    dom_work_graph_builder graph_builder;
    dom_access_set_builder access_builder;
    dom_task_graph graph;
    AgentSystem system_batch;
    AgentSystem system_step;
    u64 hash_batch;
    u64 hash_step;
    u32 processed = 0u;
    u32 iterations = 0u;
    u32 i;

    memset(schedule, 0, sizeof(schedule));
    for (i = 0u; i < 4u; ++i) {
        schedule[i].agent_id = 200u + i;
    }
    for (i = 0u; i < 4u; ++i) {
        beliefs[i].agent_id = schedule[i].agent_id;
        beliefs[i].knowledge_mask = 0u;
        caps[i].agent_id = schedule[i].agent_id;
        caps[i].capability_mask = 0u;
        caps[i].authority_mask = 0u;
    }

    agent_goal_registry_init(&goals, goals_storage, 8u, 1u);
    for (i = 0u; i < 4u; ++i) {
        agent_goal_desc desc;
        memset(&desc, 0, sizeof(desc));
        desc.agent_id = schedule[i].agent_id;
        desc.type = AGENT_GOAL_RESEARCH;
        desc.base_priority = 10u + i;
        agent_goal_register(&goals, &desc, 0);
    }

    init_inputs(&inputs, schedule, 4u,
                &goals,
                beliefs, 4u,
                caps, 4u,
                0, 0u,
                0, 0u,
                0);

    EXPECT(init_buffers(&buffers_batch,
                        &goals_batch, goal_storage_batch, 8u,
                        &plans_batch, plan_storage_batch, 8u,
                        &commands_batch, command_storage_batch, 8u,
                        &roles_batch, role_storage_batch, 4u,
                        &cohorts_batch, cohort_storage_batch, 4u,
                        &audit_batch, audit_storage_batch, 32u) == 0, "buffers batch");
    EXPECT(init_buffers(&buffers_step,
                        &goals_step, goal_storage_step, 8u,
                        &plans_step, plan_storage_step, 8u,
                        &commands_step, command_storage_step, 8u,
                        &roles_step, role_storage_step, 4u,
                        &cohorts_step, cohort_storage_step, 4u,
                        &audit_step, audit_storage_step, 32u) == 0, "buffers step");

    system_batch.init(&inputs, &buffers_batch);
    system_step.init(&inputs, &buffers_step);
    system_batch.set_budget_hint(16u);
    system_step.set_budget_hint(1u);

    dom_work_graph_builder_init(&graph_builder, tasks, 64u, deps, 32u, barriers, 16u, costs, 64u);
    dom_access_set_builder_init(&access_builder, access_sets, 64u,
                                reads, 128u, writes, 128u, reduces, 16u);

    EXPECT(emit_graph(&system_batch, &graph_builder, &access_builder, &graph) == 0, "emit batch");
    EXPECT(execute_agent_graph(&graph, &inputs, &buffers_batch) == 0, "exec batch");
    hash_batch = hash_commands(buffers_batch.commands);

    while (iterations < 16u && processed < inputs.schedule_count) {
        EXPECT(emit_graph(&system_step, &graph_builder, &access_builder, &graph) == 0, "emit step");
        EXPECT(execute_agent_graph(&graph, &inputs, &buffers_step) == 0, "exec step");
        for (i = 0u; i < graph.task_count; ++i) {
            const dom_task_node* node = &graph.tasks[i];
            const dom_agent_task_params* params = (const dom_agent_task_params*)node->policy_params;
            if (params && params->op == DOM_AGENT_TASK_EVALUATE_GOALS) {
                processed += params->count;
            }
        }
        iterations += 1u;
    }
    EXPECT(processed == inputs.schedule_count, "step processing incomplete");
    hash_step = hash_commands(buffers_step.commands);
    EXPECT(hash_batch == hash_step, "batch vs step mismatch");
    return 0;
}

static int test_law_gating(void)
{
    dom_agent_schedule_item schedule[1];
    dom_agent_belief beliefs[1];
    agent_goal goals_storage[2];
    agent_goal_registry goals;
    dom_agent_inputs inputs;
    dom_agent_buffers buffers;
    dom_agent_goal_buffer goal_buffer;
    dom_agent_goal_choice goal_storage[2];
    dom_agent_plan_buffer plans;
    dom_agent_plan plan_storage[2];
    dom_agent_command_buffer commands;
    dom_agent_command command_storage[2];
    dom_agent_role_buffer roles;
    dom_agent_role_state role_storage[2];
    dom_agent_cohort_buffer cohorts;
    dom_agent_cohort_item cohort_storage[2];
    dom_agent_audit_log audit;
    dom_agent_audit_entry audit_storage[8];
    dom_task_node tasks[16];
    dom_dependency_edge deps[8];
    dom_phase_barrier barriers[4];
    dom_cost_model costs[16];
    dom_access_set access_sets[16];
    dom_access_range reads[32];
    dom_access_range writes[32];
    dom_access_range reduces[8];
    dom_work_graph_builder graph_builder;
    dom_access_set_builder access_builder;
    dom_task_graph graph;
    AgentSystem system;

    memset(schedule, 0, sizeof(schedule));
    schedule[0].agent_id = 300u;
    beliefs[0].agent_id = 300u;
    beliefs[0].knowledge_mask = 0u;

    agent_goal_registry_init(&goals, goals_storage, 2u, 1u);
    {
        agent_goal_desc desc;
        memset(&desc, 0, sizeof(desc));
        desc.agent_id = 300u;
        desc.type = AGENT_GOAL_RESEARCH;
        desc.base_priority = 5u;
        agent_goal_register(&goals, &desc, 0);
    }

    init_inputs(&inputs, schedule, 1u,
                &goals,
                beliefs, 1u,
                0, 0u,
                0, 0u,
                0, 0u,
                0);

    EXPECT(init_buffers(&buffers,
                        &goal_buffer, goal_storage, 2u,
                        &plans, plan_storage, 2u,
                        &commands, command_storage, 2u,
                        &roles, role_storage, 2u,
                        &cohorts, cohort_storage, 2u,
                        &audit, audit_storage, 8u) == 0, "buffers");

    system.init(&inputs, &buffers);
    system.set_allowed_ops_mask(0u);

    dom_work_graph_builder_init(&graph_builder, tasks, 16u, deps, 8u, barriers, 4u, costs, 16u);
    dom_access_set_builder_init(&access_builder, access_sets, 16u,
                                reads, 32u, writes, 32u, reduces, 8u);

    EXPECT(emit_graph(&system, &graph_builder, &access_builder, &graph) == 0, "emit gated");
    EXPECT(graph.task_count == 0u, "gated agent should emit no tasks");
    return 0;
}

static int test_aggregation_determinism(void)
{
    dom_agent_population_item population_a[4];
    dom_agent_population_item population_b[4];
    dom_agent_inputs inputs_a;
    dom_agent_inputs inputs_b;
    dom_agent_aggregation_policy policy;
    dom_agent_buffers buffers_a;
    dom_agent_buffers buffers_b;
    dom_agent_goal_buffer goals_a;
    dom_agent_goal_buffer goals_b;
    dom_agent_goal_choice goal_storage_a[4];
    dom_agent_goal_choice goal_storage_b[4];
    dom_agent_plan_buffer plans_a;
    dom_agent_plan_buffer plans_b;
    dom_agent_plan plan_storage_a[4];
    dom_agent_plan plan_storage_b[4];
    dom_agent_command_buffer commands_a;
    dom_agent_command_buffer commands_b;
    dom_agent_command command_storage_a[4];
    dom_agent_command command_storage_b[4];
    dom_agent_role_buffer roles_a;
    dom_agent_role_buffer roles_b;
    dom_agent_role_state role_storage_a[4];
    dom_agent_role_state role_storage_b[4];
    dom_agent_cohort_buffer cohorts_a;
    dom_agent_cohort_buffer cohorts_b;
    dom_agent_cohort_item cohort_storage_a[4];
    dom_agent_cohort_item cohort_storage_b[4];
    dom_agent_audit_log audit_a;
    dom_agent_audit_log audit_b;
    dom_agent_audit_entry audit_storage_a[16];
    dom_agent_audit_entry audit_storage_b[16];
    dom_task_node tasks[32];
    dom_dependency_edge deps[16];
    dom_phase_barrier barriers[8];
    dom_cost_model costs[32];
    dom_access_set access_sets[32];
    dom_access_range reads[64];
    dom_access_range writes[64];
    dom_access_range reduces[8];
    dom_work_graph_builder graph_builder;
    dom_access_set_builder access_builder;
    dom_task_graph graph;
    AgentSystem system_a;
    AgentSystem system_b;
    u64 hash_a;
    u64 hash_b;

    memset(population_a, 0, sizeof(population_a));
    population_a[0].agent_id = 401u;
    population_a[0].cohort_id = 8001u;
    population_a[0].interest_level = 5u;
    population_a[0].status = DOM_AGENT_POP_COHORT;
    population_a[1].agent_id = 402u;
    population_a[1].cohort_id = 8001u;
    population_a[1].interest_level = 12u;
    population_a[1].status = DOM_AGENT_POP_COHORT;
    population_a[2].agent_id = 403u;
    population_a[2].cohort_id = 8002u;
    population_a[2].interest_level = 20u;
    population_a[2].status = DOM_AGENT_POP_INDIVIDUAL;
    population_a[3].agent_id = 404u;
    population_a[3].cohort_id = 0u;
    population_a[3].interest_level = 1u;
    population_a[3].status = DOM_AGENT_POP_COHORT;
    memcpy(population_b, population_a, sizeof(population_a));

    policy.refine_threshold = 10u;
    policy.collapse_threshold = 3u;
    policy.cohort_limit = 8u;

    init_inputs(&inputs_a, 0, 0u,
                0,
                0, 0u,
                0, 0u,
                0, 0u,
                population_a, 4u,
                &policy);
    init_inputs(&inputs_b, 0, 0u,
                0,
                0, 0u,
                0, 0u,
                0, 0u,
                population_b, 4u,
                &policy);

    EXPECT(init_buffers(&buffers_a,
                        &goals_a, goal_storage_a, 4u,
                        &plans_a, plan_storage_a, 4u,
                        &commands_a, command_storage_a, 4u,
                        &roles_a, role_storage_a, 4u,
                        &cohorts_a, cohort_storage_a, 4u,
                        &audit_a, audit_storage_a, 16u) == 0, "buffers a");
    EXPECT(init_buffers(&buffers_b,
                        &goals_b, goal_storage_b, 4u,
                        &plans_b, plan_storage_b, 4u,
                        &commands_b, command_storage_b, 4u,
                        &roles_b, role_storage_b, 4u,
                        &cohorts_b, cohort_storage_b, 4u,
                        &audit_b, audit_storage_b, 16u) == 0, "buffers b");

    system_a.init(&inputs_a, &buffers_a);
    system_b.init(&inputs_b, &buffers_b);
    system_a.set_budget_hint(8u);
    system_b.set_budget_hint(8u);

    dom_work_graph_builder_init(&graph_builder, tasks, 32u, deps, 16u, barriers, 8u, costs, 32u);
    dom_access_set_builder_init(&access_builder, access_sets, 32u,
                                reads, 64u, writes, 64u, reduces, 8u);

    EXPECT(emit_graph(&system_a, &graph_builder, &access_builder, &graph) == 0, "emit a");
    EXPECT(execute_agent_graph(&graph, &inputs_a, &buffers_a) == 0, "exec a");
    hash_a = hash_cohorts(buffers_a.cohorts);

    EXPECT(emit_graph(&system_b, &graph_builder, &access_builder, &graph) == 0, "emit b");
    EXPECT(execute_agent_graph(&graph, &inputs_b, &buffers_b) == 0, "exec b");
    hash_b = hash_cohorts(buffers_b.cohorts);

    EXPECT(hash_a == hash_b, "aggregation determinism mismatch");
    return 0;
}

static int test_disable_agents(void)
{
    dom_agent_schedule_item schedule[1];
    dom_agent_belief beliefs[1];
    dom_agent_capability caps[1];
    agent_goal goals_storage[2];
    agent_goal_registry goals;
    dom_agent_inputs inputs;
    dom_agent_buffers buffers;
    dom_agent_goal_buffer goal_buffer;
    dom_agent_goal_choice goal_storage[2];
    dom_agent_plan_buffer plans;
    dom_agent_plan plan_storage[2];
    dom_agent_command_buffer commands;
    dom_agent_command command_storage[2];
    dom_agent_role_buffer roles;
    dom_agent_role_state role_storage[2];
    dom_agent_cohort_buffer cohorts;
    dom_agent_cohort_item cohort_storage[2];
    dom_agent_audit_log audit;
    dom_agent_audit_entry audit_storage[8];
    dom_task_node tasks[16];
    dom_dependency_edge deps[8];
    dom_phase_barrier barriers[4];
    dom_cost_model costs[16];
    dom_access_set access_sets[16];
    dom_access_range reads[32];
    dom_access_range writes[32];
    dom_access_range reduces[8];
    dom_work_graph_builder graph_builder;
    dom_access_set_builder access_builder;
    dom_task_graph graph;
    AgentSystem system;

    memset(schedule, 0, sizeof(schedule));
    schedule[0].agent_id = 501u;
    beliefs[0].agent_id = 501u;
    beliefs[0].knowledge_mask = 0u;
    caps[0].agent_id = 501u;
    caps[0].capability_mask = 0u;
    caps[0].authority_mask = 0u;

    agent_goal_registry_init(&goals, goals_storage, 2u, 1u);
    {
        agent_goal_desc desc;
        memset(&desc, 0, sizeof(desc));
        desc.agent_id = 501u;
        desc.type = AGENT_GOAL_RESEARCH;
        desc.base_priority = 2u;
        agent_goal_register(&goals, &desc, 0);
    }

    init_inputs(&inputs, schedule, 1u,
                &goals,
                beliefs, 1u,
                caps, 1u,
                0, 0u,
                0, 0u,
                0);

    EXPECT(init_buffers(&buffers,
                        &goal_buffer, goal_storage, 2u,
                        &plans, plan_storage, 2u,
                        &commands, command_storage, 2u,
                        &roles, role_storage, 2u,
                        &cohorts, cohort_storage, 2u,
                        &audit, audit_storage, 8u) == 0, "buffers");

    system.init(&inputs, &buffers);
    system.set_allowed_ops_mask(0u);

    dom_work_graph_builder_init(&graph_builder, tasks, 16u, deps, 8u, barriers, 4u, costs, 16u);
    dom_access_set_builder_init(&access_builder, access_sets, 16u,
                                reads, 32u, writes, 32u, reduces, 8u);

    EXPECT(emit_graph(&system, &graph_builder, &access_builder, &graph) == 0, "emit");
    EXPECT(graph.task_count == 0u, "disabled agent should emit no tasks");
    return 0;
}

int main(void)
{
    if (test_deterministic_planning() != 0) return 1;
    if (test_batch_vs_step_equivalence() != 0) return 1;
    if (test_law_gating() != 0) return 1;
    if (test_aggregation_determinism() != 0) return 1;
    if (test_disable_agents() != 0) return 1;
    return 0;
}
