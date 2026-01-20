/*
Interest Work IR migration tests (ADOPT3).
*/
#include "dominium/rules/scale/interest_system.h"
#include "dominium/execution/system_registry.h"
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

static u64 hash_interest_set(const dom_interest_set* set)
{
    u32 i;
    u64 h = fnv1a_init();
    if (!set || !set->entries) {
        return h;
    }
    h = fnv1a_u32(h, set->count);
    for (i = 0u; i < set->count; ++i) {
        const dom_interest_entry* entry = &set->entries[i];
        h = fnv1a_u64(h, entry->target_id);
        h = fnv1a_u32(h, entry->target_kind);
        h = fnv1a_u32(h, entry->reason);
        h = fnv1a_u32(h, entry->strength);
        h = fnv1a_u64(h, entry->expiry_tick);
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
        if (t->policy_params && t->policy_params_size == sizeof(dom_interest_task_params)) {
            const dom_interest_task_params* params = (const dom_interest_task_params*)t->policy_params;
            h = fnv1a_u32(h, params->op);
            h = fnv1a_u32(h, params->source_kind);
            h = fnv1a_u32(h, params->start_index);
            h = fnv1a_u32(h, params->count);
            h = fnv1a_u32(h, params->reason);
            h = fnv1a_u32(h, params->refine_tier);
            h = fnv1a_u32(h, params->collapse_tier);
        }
    }
    return h;
}

static void init_inputs(dom_interest_inputs* inputs,
                        u64 base_set_id,
                        u64* ids_player,
                        u32 count_player,
                        u64* ids_command,
                        u32 count_command,
                        u64* ids_logistics,
                        u32 count_logistics,
                        u64* ids_sensor,
                        u32 count_sensor,
                        u64* ids_hazard,
                        u32 count_hazard,
                        u64* ids_gov,
                        u32 count_gov,
                        u32 strength)
{
    u32 i;
    if (!inputs) {
        return;
    }
    for (i = 0u; i < DOM_INTEREST_SOURCE_COUNT; ++i) {
        inputs->sources[i].list.ids = 0;
        inputs->sources[i].list.count = 0u;
        inputs->sources[i].list.target_kind = DOM_INTEREST_TARGET_SYSTEM;
        inputs->sources[i].list.strength = strength;
        inputs->sources[i].list.ttl_ticks = 5;
        inputs->sources[i].set_id = base_set_id + i;
    }
    inputs->sources[DOM_INTEREST_SOURCE_PLAYER_FOCUS].list.ids = ids_player;
    inputs->sources[DOM_INTEREST_SOURCE_PLAYER_FOCUS].list.count = count_player;
    inputs->sources[DOM_INTEREST_SOURCE_COMMAND_INTENT].list.ids = ids_command;
    inputs->sources[DOM_INTEREST_SOURCE_COMMAND_INTENT].list.count = count_command;
    inputs->sources[DOM_INTEREST_SOURCE_LOGISTICS].list.ids = ids_logistics;
    inputs->sources[DOM_INTEREST_SOURCE_LOGISTICS].list.count = count_logistics;
    inputs->sources[DOM_INTEREST_SOURCE_SENSOR_COMMS].list.ids = ids_sensor;
    inputs->sources[DOM_INTEREST_SOURCE_SENSOR_COMMS].list.count = count_sensor;
    inputs->sources[DOM_INTEREST_SOURCE_HAZARD_CONFLICT].list.ids = ids_hazard;
    inputs->sources[DOM_INTEREST_SOURCE_HAZARD_CONFLICT].list.count = count_hazard;
    inputs->sources[DOM_INTEREST_SOURCE_GOVERNANCE_SCOPE].list.ids = ids_gov;
    inputs->sources[DOM_INTEREST_SOURCE_GOVERNANCE_SCOPE].list.count = count_gov;

    inputs->policy.enter_warm = 50u;
    inputs->policy.exit_warm = 40u;
    inputs->policy.enter_hot = 80u;
    inputs->policy.exit_hot = 60u;
    inputs->policy.min_dwell_ticks = 2;
    inputs->refine_tier = DOM_FIDELITY_MICRO;
    inputs->collapse_tier = DOM_FIDELITY_MACRO;
    inputs->request_reason = 900u;
}

static int init_buffers(dom_interest_buffers* buffers,
                        dom_interest_set* scratch_set,
                        dom_interest_set* merged_set,
                        dom_interest_state* states,
                        u32 state_count,
                        dom_interest_transition* transitions,
                        u32 transition_capacity,
                        dom_fidelity_request* requests,
                        u32 request_capacity,
                        u64 scratch_set_id,
                        u64 merged_set_id)
{
    if (!buffers || !scratch_set || !merged_set) {
        return -1;
    }
    dom_interest_set_init(scratch_set);
    dom_interest_set_init(merged_set);
    if (dom_interest_set_reserve(scratch_set, 64u) != 0) {
        return -2;
    }
    if (dom_interest_set_reserve(merged_set, 64u) != 0) {
        return -3;
    }
    buffers->scratch_set = scratch_set;
    buffers->merged_set = merged_set;
    buffers->relevance_states = states;
    buffers->relevance_count = state_count;
    buffers->transitions = transitions;
    buffers->transition_capacity = transition_capacity;
    buffers->requests = requests;
    buffers->request_capacity = request_capacity;
    buffers->scratch_set_id = scratch_set_id;
    buffers->merged_set_id = merged_set_id;
    buffers->state_set_id = 4001u;
    buffers->transition_set_id = 4002u;
    buffers->request_set_id = 4003u;
    return 0;
}

static int execute_interest_graph(const dom_task_graph* graph,
                                  const dom_interest_inputs* inputs,
                                  dom_interest_runtime_state* runtime,
                                  dom_act_time_t now_tick)
{
    u32 i;
    if (!graph || !inputs || !runtime) {
        return -1;
    }
    for (i = 0u; i < graph->task_count; ++i) {
        const dom_task_node* node = &graph->tasks[i];
        const dom_interest_task_params* params = (const dom_interest_task_params*)node->policy_params;
        if (!params || params->op == 0u) {
            continue;
        }
        switch (params->op) {
            case DOM_INTEREST_TASK_COLLECT_SOURCES: {
                dom_interest_source_kind kind = (dom_interest_source_kind)params->source_kind;
                if (kind >= DOM_INTEREST_SOURCE_COUNT) {
                    return -2;
                }
                const dom_interest_source_list* list = &inputs->sources[kind].list;
                if (dom_interest_collect_slice(runtime, list,
                                               (dom_interest_reason)params->reason,
                                               params->start_index,
                                               params->count,
                                               now_tick) != 0) {
                    return -2;
                }
                break;
            }
            case DOM_INTEREST_TASK_MERGE:
                if (dom_interest_merge_sets(runtime) < 0) {
                    return -3;
                }
                break;
            case DOM_INTEREST_TASK_APPLY_HYSTERESIS:
                dom_interest_apply_hysteresis(runtime, &inputs->policy, now_tick);
                break;
            case DOM_INTEREST_TASK_BUILD_REQUESTS:
                dom_interest_build_fidelity_requests(runtime,
                                                     inputs->refine_tier,
                                                     inputs->collapse_tier,
                                                     params->reason);
                break;
            default:
                return -4;
        }
    }
    return 0;
}

static int emit_graph(InterestSystem* system,
                      dom_work_graph_builder* graph_builder,
                      dom_access_set_builder* access_builder,
                      dom_task_graph* out_graph)
{
    if (!system || !graph_builder || !access_builder || !out_graph) {
        return -1;
    }
    dom_work_graph_builder_reset(graph_builder);
    dom_access_set_builder_reset(access_builder);
    dom_work_graph_builder_set_ids(graph_builder, 111u, 1u);
    if (system->emit_tasks(0, 10, graph_builder, access_builder) != 0) {
        return -2;
    }
    dom_work_graph_builder_finalize(graph_builder, out_graph);
    return 0;
}

static int test_deterministic_emission(void)
{
    InterestSystem system;
    dom_system_registry registry;
    dom_system_entry entries[1];
    dom_task_node tasks[32];
    dom_dependency_edge deps[16];
    dom_phase_barrier barriers[4];
    dom_cost_model costs[32];
    dom_access_set access_sets[32];
    dom_access_range reads[64];
    dom_access_range writes[64];
    dom_access_range reduces[8];
    dom_work_graph_builder graph_builder;
    dom_access_set_builder access_builder;
    dom_task_graph graph_a;
    dom_task_graph graph_b;
    dom_interest_inputs inputs;
    dom_interest_buffers buffers;
    dom_interest_set scratch_set;
    dom_interest_set merged_set;
    dom_interest_state states[8];
    dom_interest_transition transitions[16];
    dom_fidelity_request requests[16];
    u64 ids_player[2] = { 1u, 2u };
    u64 ids_command[1] = { 3u };
    u64 ids_logistics[2] = { 4u, 5u };
    u64 ids_sensor[1] = { 6u };
    u64 ids_hazard[1] = { 7u };
    u64 ids_gov[1] = { 8u };
    u64 hash_a;
    u64 hash_b;

    init_inputs(&inputs, 2000u,
                ids_player, 2u,
                ids_command, 1u,
                ids_logistics, 2u,
                ids_sensor, 1u,
                ids_hazard, 1u,
                ids_gov, 1u,
                DOM_INTEREST_STRENGTH_HIGH);
    EXPECT(init_buffers(&buffers, &scratch_set, &merged_set,
                        states, 8u, transitions, 16u,
                        requests, 16u, 3001u, 3002u) == 0, "buffers");
    system.init(&inputs, &buffers);

    dom_system_registry_init(&registry, entries, 1u);
    EXPECT(dom_system_registry_register_interest(&registry, &system) == 0, "register interest");

    dom_work_graph_builder_init(&graph_builder, tasks, 32u, deps, 16u, barriers, 4u, costs, 32u);
    dom_access_set_builder_init(&access_builder, access_sets, 32u,
                                reads, 64u, writes, 64u, reduces, 8u);

    EXPECT(emit_graph(&system, &graph_builder, &access_builder, &graph_a) == 0, "emit A");
    hash_a = hash_task_graph(&graph_a);
    EXPECT(emit_graph(&system, &graph_builder, &access_builder, &graph_b) == 0, "emit B");
    hash_b = hash_task_graph(&graph_b);

    EXPECT(hash_a == hash_b, "graph determinism mismatch");

    dom_interest_set_free(&scratch_set);
    dom_interest_set_free(&merged_set);
    return 0;
}

static int test_budget_amortization(void)
{
    InterestSystem system;
    dom_task_node tasks[32];
    dom_dependency_edge deps[16];
    dom_phase_barrier barriers[4];
    dom_cost_model costs[32];
    dom_access_set access_sets[32];
    dom_access_range reads[64];
    dom_access_range writes[64];
    dom_access_range reduces[8];
    dom_work_graph_builder graph_builder;
    dom_access_set_builder access_builder;
    dom_task_graph graph;
    dom_interest_inputs inputs;
    dom_interest_buffers buffers;
    dom_interest_set scratch_set;
    dom_interest_set merged_set;
    dom_interest_state states[8];
    dom_interest_transition transitions[16];
    dom_fidelity_request requests[16];
    u64 ids_player[3] = { 1u, 2u, 3u };
    u64 ids_command[2] = { 4u, 5u };
    u64 ids_logistics[2] = { 6u, 7u };
    u32 total_collected = 0u;
    u32 i;

    init_inputs(&inputs, 2100u,
                ids_player, 3u,
                ids_command, 2u,
                ids_logistics, 2u,
                0, 0u,
                0, 0u,
                0, 0u,
                DOM_INTEREST_STRENGTH_MED);
    EXPECT(init_buffers(&buffers, &scratch_set, &merged_set,
                        states, 8u, transitions, 16u,
                        requests, 16u, 3101u, 3102u) == 0, "buffers");
    system.init(&inputs, &buffers);
    system.set_budget_hint(1u);

    dom_work_graph_builder_init(&graph_builder, tasks, 32u, deps, 16u, barriers, 4u, costs, 32u);
    dom_access_set_builder_init(&access_builder, access_sets, 32u,
                                reads, 64u, writes, 64u, reduces, 8u);

    EXPECT(emit_graph(&system, &graph_builder, &access_builder, &graph) == 0, "emit");
    for (i = 0u; i < graph.task_count; ++i) {
        const dom_task_node* node = &graph.tasks[i];
        const dom_interest_task_params* params = (const dom_interest_task_params*)node->policy_params;
        if (params && params->op == DOM_INTEREST_TASK_COLLECT_SOURCES) {
            total_collected += params->count;
        }
    }
    EXPECT(total_collected <= 1u, "budget exceeded");
    EXPECT(system.runtime_state()->source_cursor[DOM_INTEREST_SOURCE_PLAYER_FOCUS] == 1u,
           "cursor did not advance");

    dom_interest_set_free(&scratch_set);
    dom_interest_set_free(&merged_set);
    return 0;
}

static int test_hysteresis_stability(void)
{
    InterestSystem system;
    dom_task_node tasks[32];
    dom_dependency_edge deps[16];
    dom_phase_barrier barriers[4];
    dom_cost_model costs[32];
    dom_access_set access_sets[32];
    dom_access_range reads[64];
    dom_access_range writes[64];
    dom_access_range reduces[8];
    dom_work_graph_builder graph_builder;
    dom_access_set_builder access_builder;
    dom_task_graph graph;
    dom_interest_inputs inputs;
    dom_interest_buffers buffers;
    dom_interest_set scratch_set;
    dom_interest_set merged_set;
    dom_interest_state states[1];
    dom_interest_transition transitions[8];
    dom_fidelity_request requests[8];
    u64 ids_player[1] = { 9u };

    init_inputs(&inputs, 2200u,
                ids_player, 1u,
                0, 0u,
                0, 0u,
                0, 0u,
                0, 0u,
                0, 0u,
                90u);
    inputs.policy.min_dwell_ticks = 5;
    EXPECT(init_buffers(&buffers, &scratch_set, &merged_set,
                        states, 1u, transitions, 8u,
                        requests, 8u, 3201u, 3202u) == 0, "buffers");
    states[0].target_id = 9u;
    states[0].target_kind = DOM_INTEREST_TARGET_SYSTEM;
    states[0].state = DOM_REL_LATENT;
    states[0].last_change_tick = 0;

    system.init(&inputs, &buffers);

    dom_work_graph_builder_init(&graph_builder, tasks, 32u, deps, 16u, barriers, 4u, costs, 32u);
    dom_access_set_builder_init(&access_builder, access_sets, 32u,
                                reads, 64u, writes, 64u, reduces, 8u);

    dom_interest_runtime_reset(system.runtime_state());
    EXPECT(emit_graph(&system, &graph_builder, &access_builder, &graph) == 0, "emit hot");
    EXPECT(execute_interest_graph(&graph, &inputs, system.runtime_state(), 10u) == 0, "exec hot");
    EXPECT(states[0].state == DOM_REL_HOT, "expected HOT after entry");

    inputs.sources[DOM_INTEREST_SOURCE_PLAYER_FOCUS].list.strength = 30u;
    dom_interest_runtime_reset(system.runtime_state());
    EXPECT(emit_graph(&system, &graph_builder, &access_builder, &graph) == 0, "emit cool");
    EXPECT(execute_interest_graph(&graph, &inputs, system.runtime_state(), 12u) == 0, "exec cool");
    EXPECT(states[0].state == DOM_REL_HOT, "dwell should prevent collapse");

    dom_interest_set_free(&scratch_set);
    dom_interest_set_free(&merged_set);
    return 0;
}

static int test_law_gating(void)
{
    InterestSystem system;
    dom_task_node tasks[32];
    dom_dependency_edge deps[16];
    dom_phase_barrier barriers[4];
    dom_cost_model costs[32];
    dom_access_set access_sets[32];
    dom_access_range reads[64];
    dom_access_range writes[64];
    dom_access_range reduces[8];
    dom_work_graph_builder graph_builder;
    dom_access_set_builder access_builder;
    dom_task_graph graph;
    dom_interest_inputs inputs;
    dom_interest_buffers buffers;
    dom_interest_set scratch_set;
    dom_interest_set merged_set;
    dom_interest_state states[2];
    dom_interest_transition transitions[8];
    dom_fidelity_request requests[8];
    u64 ids_player[1] = { 1u };
    u64 ids_sensor[1] = { 2u };
    u32 i;
    u32 sensor_found = 0u;

    init_inputs(&inputs, 2300u,
                ids_player, 1u,
                0, 0u,
                0, 0u,
                ids_sensor, 1u,
                0, 0u,
                0, 0u,
                DOM_INTEREST_STRENGTH_HIGH);
    EXPECT(init_buffers(&buffers, &scratch_set, &merged_set,
                        states, 2u, transitions, 8u,
                        requests, 8u, 3301u, 3302u) == 0, "buffers");
    system.init(&inputs, &buffers);
    system.set_allowed_sources_mask(1u << DOM_INTEREST_SOURCE_PLAYER_FOCUS);

    dom_work_graph_builder_init(&graph_builder, tasks, 32u, deps, 16u, barriers, 4u, costs, 32u);
    dom_access_set_builder_init(&access_builder, access_sets, 32u,
                                reads, 64u, writes, 64u, reduces, 8u);

    EXPECT(emit_graph(&system, &graph_builder, &access_builder, &graph) == 0, "emit gated");
    for (i = 0u; i < graph.task_count; ++i) {
        const dom_task_node* node = &graph.tasks[i];
        const dom_interest_task_params* params = (const dom_interest_task_params*)node->policy_params;
        if (params && params->op == DOM_INTEREST_TASK_COLLECT_SOURCES &&
            params->source_kind == DOM_INTEREST_SOURCE_SENSOR_COMMS) {
            sensor_found = 1u;
        }
    }
    EXPECT(sensor_found == 0u, "sensor source should be gated");

    dom_interest_set_free(&scratch_set);
    dom_interest_set_free(&merged_set);
    return 0;
}

static int test_batch_vs_step_equivalence(void)
{
    InterestSystem system_batch;
    InterestSystem system_step;
    dom_task_node tasks[32];
    dom_dependency_edge deps[16];
    dom_phase_barrier barriers[4];
    dom_cost_model costs[32];
    dom_access_set access_sets[32];
    dom_access_range reads[64];
    dom_access_range writes[64];
    dom_access_range reduces[8];
    dom_work_graph_builder graph_builder;
    dom_access_set_builder access_builder;
    dom_task_graph graph;
    dom_interest_inputs inputs;
    dom_interest_buffers buffers_batch;
    dom_interest_buffers buffers_step;
    dom_interest_set scratch_batch;
    dom_interest_set merged_batch;
    dom_interest_set scratch_step;
    dom_interest_set merged_step;
    dom_interest_state states_batch[4];
    dom_interest_state states_step[4];
    dom_interest_transition transitions_batch[16];
    dom_interest_transition transitions_step[16];
    dom_fidelity_request requests_batch[16];
    dom_fidelity_request requests_step[16];
    u64 ids_player[2] = { 11u, 12u };
    u64 ids_command[2] = { 13u, 14u };
    u64 ids_logistics[2] = { 15u, 16u };
    u64 hash_batch;
    u64 hash_step;
    u32 iterations = 0u;
    u32 i;
    d_bool merged = D_FALSE;

    init_inputs(&inputs, 2400u,
                ids_player, 2u,
                ids_command, 2u,
                ids_logistics, 2u,
                0, 0u,
                0, 0u,
                0, 0u,
                DOM_INTEREST_STRENGTH_MED);

    EXPECT(init_buffers(&buffers_batch, &scratch_batch, &merged_batch,
                        states_batch, 4u, transitions_batch, 16u,
                        requests_batch, 16u, 3401u, 3402u) == 0, "buffers batch");
    EXPECT(init_buffers(&buffers_step, &scratch_step, &merged_step,
                        states_step, 4u, transitions_step, 16u,
                        requests_step, 16u, 3501u, 3502u) == 0, "buffers step");

    for (i = 0u; i < 4u; ++i) {
        states_batch[i].target_id = 11u + i;
        states_batch[i].target_kind = DOM_INTEREST_TARGET_SYSTEM;
        states_batch[i].state = DOM_REL_LATENT;
        states_batch[i].last_change_tick = 0;
        states_step[i] = states_batch[i];
    }

    system_batch.init(&inputs, &buffers_batch);
    system_step.init(&inputs, &buffers_step);
    system_batch.set_budget_hint(16u);
    system_step.set_budget_hint(1u);

    dom_work_graph_builder_init(&graph_builder, tasks, 32u, deps, 16u, barriers, 4u, costs, 32u);
    dom_access_set_builder_init(&access_builder, access_sets, 32u,
                                reads, 64u, writes, 64u, reduces, 8u);

    dom_interest_runtime_reset(system_batch.runtime_state());
    EXPECT(emit_graph(&system_batch, &graph_builder, &access_builder, &graph) == 0, "emit batch");
    EXPECT(execute_interest_graph(&graph, &inputs, system_batch.runtime_state(), 20u) == 0, "exec batch");
    hash_batch = hash_interest_set(buffers_batch.merged_set);

    dom_interest_runtime_reset(system_step.runtime_state());
    while (iterations < 16u && merged == D_FALSE) {
        EXPECT(emit_graph(&system_step, &graph_builder, &access_builder, &graph) == 0, "emit step");
        EXPECT(execute_interest_graph(&graph, &inputs, system_step.runtime_state(), 20u + iterations) == 0, "exec step");
        if (graph.task_count > 0u) {
            for (i = 0u; i < graph.task_count; ++i) {
                const dom_task_node* node = &graph.tasks[i];
                const dom_interest_task_params* params = (const dom_interest_task_params*)node->policy_params;
                if (params && params->op == DOM_INTEREST_TASK_MERGE) {
                    merged = D_TRUE;
                    break;
                }
            }
        }
        iterations += 1u;
    }
    EXPECT(merged == D_TRUE, "merge task never emitted");
    hash_step = hash_interest_set(buffers_step.merged_set);
    EXPECT(hash_batch == hash_step, "batch vs step mismatch");

    dom_interest_set_free(&scratch_batch);
    dom_interest_set_free(&merged_batch);
    dom_interest_set_free(&scratch_step);
    dom_interest_set_free(&merged_step);
    return 0;
}

int main(void)
{
    if (test_deterministic_emission() != 0) return 1;
    if (test_budget_amortization() != 0) return 1;
    if (test_hysteresis_stability() != 0) return 1;
    if (test_law_gating() != 0) return 1;
    if (test_batch_vs_step_equivalence() != 0) return 1;
    return 0;
}
