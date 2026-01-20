/*
War Work IR migration tests (ADOPT5).
*/
#include "dominium/rules/war/war_system.h"
#include "dominium/rules/war/war_tasks_engagement.h"
#include "dominium/rules/war/war_tasks_occupation.h"
#include "dominium/rules/war/war_tasks_interdiction.h"
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

static void init_war_inputs(dom_war_inputs* inputs,
                            dom_war_engagement_item* engagements,
                            u32 engagement_count,
                            dom_war_occupation_item* occupations,
                            u32 occupation_count,
                            dom_war_resistance_item* resistances,
                            u32 resistance_count,
                            dom_war_disruption_item* disruptions,
                            u32 disruption_count,
                            dom_war_route_control_item* routes,
                            u32 route_count,
                            dom_war_blockade_item* blockades,
                            u32 blockade_count,
                            dom_war_interdiction_item* interdictions,
                            u32 interdiction_count)
{
    if (!inputs) {
        return;
    }
    inputs->engagements = engagements;
    inputs->engagement_count = engagement_count;
    inputs->engagement_set_id = 8101u;
    inputs->occupations = occupations;
    inputs->occupation_count = occupation_count;
    inputs->occupation_set_id = 8102u;
    inputs->resistances = resistances;
    inputs->resistance_count = resistance_count;
    inputs->resistance_set_id = 8103u;
    inputs->disruptions = disruptions;
    inputs->disruption_count = disruption_count;
    inputs->disruption_set_id = 8104u;
    inputs->routes = routes;
    inputs->route_count = route_count;
    inputs->route_set_id = 8105u;
    inputs->blockades = blockades;
    inputs->blockade_count = blockade_count;
    inputs->blockade_set_id = 8106u;
    inputs->interdictions = interdictions;
    inputs->interdiction_count = interdiction_count;
    inputs->interdiction_set_id = 8107u;
}

static int init_war_buffers(dom_war_buffers* buffers,
                            dom_war_outcome_list* outcomes,
                            dom_war_engagement_outcome* outcome_storage,
                            u32 outcome_capacity,
                            dom_war_casualty_log* casualties,
                            dom_war_casualty_entry* casualty_storage,
                            u32 casualty_capacity,
                            dom_war_equipment_log* equipment,
                            dom_war_equipment_loss_entry* equipment_storage,
                            u32 equipment_capacity,
                            dom_war_morale_state* morale,
                            dom_war_force_state* morale_storage,
                            u32 morale_capacity,
                            dom_war_audit_log* audit,
                            dom_war_audit_entry* audit_storage,
                            u32 audit_capacity)
{
    if (!buffers || !outcomes || !casualties || !equipment || !morale || !audit) {
        return -1;
    }
    dom_war_outcome_list_init(outcomes, outcome_storage, outcome_capacity, 1u);
    dom_war_casualty_log_init(casualties, casualty_storage, casualty_capacity);
    dom_war_equipment_log_init(equipment, equipment_storage, equipment_capacity);
    dom_war_morale_state_init(morale, morale_storage, morale_capacity);
    dom_war_audit_init(audit, audit_storage, audit_capacity, 1u);

    buffers->outcomes = outcomes;
    buffers->casualties = casualties;
    buffers->equipment_losses = equipment;
    buffers->morale = morale;
    buffers->audit_log = audit;
    buffers->outcome_set_id = 8201u;
    buffers->casualty_set_id = 8202u;
    buffers->equipment_set_id = 8203u;
    buffers->morale_set_id = 8204u;
    buffers->audit_set_id = 8205u;
    return 0;
}

static int emit_graph(WarSystem* system,
                      dom_work_graph_builder* graph_builder,
                      dom_access_set_builder* access_builder,
                      dom_task_graph* out_graph)
{
    if (!system || !graph_builder || !access_builder || !out_graph) {
        return -1;
    }
    dom_work_graph_builder_reset(graph_builder);
    dom_access_set_builder_reset(access_builder);
    dom_work_graph_builder_set_ids(graph_builder, 901u, 1u);
    if (system->emit_tasks(0, 10, graph_builder, access_builder) != 0) {
        return -2;
    }
    dom_work_graph_builder_finalize(graph_builder, out_graph);
    return 0;
}

static int execute_war_graph(const dom_task_graph* graph,
                             const dom_war_inputs* inputs,
                             dom_war_buffers* buffers,
                             dom_act_time_t now_tick)
{
    u32 i;
    if (!graph || !inputs || !buffers) {
        return -1;
    }
    for (i = 0u; i < graph->task_count; ++i) {
        const dom_task_node* node = &graph->tasks[i];
        const dom_war_task_params* params = (const dom_war_task_params*)node->policy_params;
        if (!params || params->count == 0u) {
            continue;
        }
        switch (params->op) {
            case DOM_WAR_TASK_ENGAGEMENT_ADMIT:
                dom_war_engagement_admit_slice(inputs->engagements,
                                               inputs->engagement_count,
                                               params->start_index,
                                               params->count,
                                               buffers->audit_log);
                break;
            case DOM_WAR_TASK_ENGAGEMENT_RESOLVE:
                dom_war_engagement_resolve_slice(inputs->engagements,
                                                 inputs->engagement_count,
                                                 params->start_index,
                                                 params->count,
                                                 buffers->outcomes,
                                                 buffers->audit_log);
                break;
            case DOM_WAR_TASK_APPLY_CASUALTIES:
                dom_war_apply_casualties_slice(buffers->outcomes,
                                               params->start_index,
                                               params->count,
                                               buffers->casualties,
                                               buffers->audit_log);
                break;
            case DOM_WAR_TASK_APPLY_EQUIPMENT_LOSSES:
                dom_war_apply_equipment_losses_slice(buffers->outcomes,
                                                     params->start_index,
                                                     params->count,
                                                     buffers->equipment_losses,
                                                     buffers->audit_log);
                break;
            case DOM_WAR_TASK_UPDATE_MORALE_READINESS:
                dom_war_update_morale_readiness_slice(buffers->outcomes,
                                                      params->start_index,
                                                      params->count,
                                                      buffers->morale,
                                                      buffers->audit_log);
                break;
            case DOM_WAR_TASK_OCCUPATION_MAINTAIN:
                dom_war_occupation_maintain_slice(inputs->occupations,
                                                  inputs->occupation_count,
                                                  params->start_index,
                                                  params->count,
                                                  buffers->audit_log,
                                                  now_tick);
                break;
            case DOM_WAR_TASK_RESISTANCE_UPDATE:
                dom_war_resistance_update_slice(inputs->resistances,
                                                inputs->resistance_count,
                                                params->start_index,
                                                params->count,
                                                buffers->audit_log,
                                                now_tick);
                break;
            case DOM_WAR_TASK_DISRUPTION_APPLY:
                dom_war_disruption_apply_slice(inputs->disruptions,
                                               inputs->disruption_count,
                                               params->start_index,
                                               params->count,
                                               buffers->audit_log,
                                               now_tick);
                break;
            case DOM_WAR_TASK_ROUTE_CONTROL_UPDATE:
                dom_war_route_control_update_slice(inputs->routes,
                                                   inputs->route_count,
                                                   params->start_index,
                                                   params->count,
                                                   buffers->audit_log,
                                                   now_tick);
                break;
            case DOM_WAR_TASK_BLOCKADE_APPLY:
                dom_war_blockade_apply_slice(inputs->blockades,
                                             inputs->blockade_count,
                                             params->start_index,
                                             params->count,
                                             buffers->audit_log,
                                             now_tick);
                break;
            case DOM_WAR_TASK_INTERDICTION_SCHEDULE:
                dom_war_interdiction_schedule_slice(inputs->interdictions,
                                                    inputs->interdiction_count,
                                                    params->start_index,
                                                    params->count,
                                                    buffers->audit_log,
                                                    now_tick);
                break;
            case DOM_WAR_TASK_INTERDICTION_RESOLVE:
                dom_war_interdiction_resolve_slice(inputs->interdictions,
                                                   inputs->interdiction_count,
                                                   params->start_index,
                                                   params->count,
                                                   buffers->audit_log,
                                                   now_tick);
                break;
            default:
                return -2;
        }
    }
    return 0;
}

static u64 hash_outcomes(const dom_war_outcome_list* list)
{
    u32 i;
    u64 h = fnv1a_init();
    if (!list || !list->outcomes) {
        return h;
    }
    h = fnv1a_u32(h, list->count);
    for (i = 0u; i < list->count; ++i) {
        const dom_war_engagement_outcome* o = &list->outcomes[i];
        h = fnv1a_u64(h, o->engagement_id);
        h = fnv1a_u64(h, o->winner_force_id);
        h = fnv1a_u64(h, o->loser_force_id);
        h = fnv1a_u32(h, o->casualty_count);
        h = fnv1a_u32(h, o->equipment_loss_count);
        h = fnv1a_u32(h, (u32)o->morale_delta);
        h = fnv1a_u32(h, (u32)o->readiness_delta);
    }
    return h;
}

static u64 hash_casualties(const dom_war_casualty_log* log)
{
    u32 i;
    u64 h = fnv1a_init();
    if (!log || !log->entries) {
        return h;
    }
    h = fnv1a_u32(h, log->count);
    for (i = 0u; i < log->count; ++i) {
        const dom_war_casualty_entry* e = &log->entries[i];
        h = fnv1a_u64(h, e->engagement_id);
        h = fnv1a_u32(h, e->casualty_count);
    }
    return h;
}

static u64 hash_morale(const dom_war_morale_state* state)
{
    u32 i;
    u64 h = fnv1a_init();
    if (!state || !state->entries) {
        return h;
    }
    h = fnv1a_u32(h, state->count);
    for (i = 0u; i < state->count; ++i) {
        const dom_war_force_state* entry = &state->entries[i];
        h = fnv1a_u64(h, entry->force_id);
        h = fnv1a_u32(h, (u32)entry->morale);
        h = fnv1a_u32(h, (u32)entry->readiness);
    }
    return h;
}

static u64 hash_graph(const dom_task_graph* graph)
{
    u32 i;
    u64 h = fnv1a_init();
    if (!graph) {
        return h;
    }
    h = fnv1a_u32(h, graph->task_count);
    for (i = 0u; i < graph->task_count; ++i) {
        const dom_task_node* node = &graph->tasks[i];
        h = fnv1a_u64(h, node->task_id);
        h = fnv1a_u64(h, node->access_set_id);
        h = fnv1a_u32(h, node->phase_id);
        h = fnv1a_u32(h, node->determinism_class);
    }
    return h;
}

static void seed_inputs(dom_war_engagement_item* engagements,
                        dom_war_occupation_item* occupations,
                        dom_war_resistance_item* resistances,
                        dom_war_disruption_item* disruptions,
                        dom_war_route_control_item* routes,
                        dom_war_blockade_item* blockades,
                        dom_war_interdiction_item* interdictions)
{
    memset(engagements, 0, sizeof(dom_war_engagement_item) * 3u);
    engagements[0].engagement_id = 1u;
    engagements[0].attacker_force_id = 100u;
    engagements[0].defender_force_id = 200u;
    engagements[0].supply_qty = 5u;
    engagements[0].status = DOM_WAR_ENGAGEMENT_PENDING;
    engagements[1].engagement_id = 2u;
    engagements[1].attacker_force_id = 101u;
    engagements[1].defender_force_id = 201u;
    engagements[1].supply_qty = 3u;
    engagements[1].status = DOM_WAR_ENGAGEMENT_PENDING;
    engagements[2].engagement_id = 3u;
    engagements[2].attacker_force_id = 0u;
    engagements[2].defender_force_id = 202u;
    engagements[2].supply_qty = 0u;
    engagements[2].status = DOM_WAR_ENGAGEMENT_PENDING;

    memset(occupations, 0, sizeof(dom_war_occupation_item) * 2u);
    occupations[0].occupation_id = 10u;
    occupations[0].territory_id = 900u;
    occupations[0].control_level = 100u;
    occupations[0].control_delta = 5;
    occupations[0].supply_qty = 4u;
    occupations[0].status = DOM_WAR_OCCUPATION_ACTIVE;
    occupations[1].occupation_id = 11u;
    occupations[1].territory_id = 901u;
    occupations[1].control_level = 20u;
    occupations[1].control_delta = -10;
    occupations[1].supply_qty = 0u;
    occupations[1].status = DOM_WAR_OCCUPATION_ACTIVE;

    memset(resistances, 0, sizeof(dom_war_resistance_item) * 2u);
    resistances[0].resistance_id = 20u;
    resistances[0].territory_id = 900u;
    resistances[0].pressure = 200u;
    resistances[0].pressure_delta = 50;
    resistances[0].status = DOM_WAR_RESISTANCE_LATENT;
    resistances[1].resistance_id = 21u;
    resistances[1].territory_id = 901u;
    resistances[1].pressure = 0u;
    resistances[1].pressure_delta = 0;
    resistances[1].status = DOM_WAR_RESISTANCE_LATENT;

    memset(disruptions, 0, sizeof(dom_war_disruption_item) * 1u);
    disruptions[0].disruption_id = 30u;
    disruptions[0].territory_id = 900u;
    disruptions[0].severity = 5u;
    disruptions[0].severity_delta = 2;
    disruptions[0].status = DOM_WAR_DISRUPTION_PENDING;

    memset(routes, 0, sizeof(dom_war_route_control_item) * 1u);
    routes[0].route_id = 40u;
    routes[0].control_level = 10u;
    routes[0].control_delta = 3;

    memset(blockades, 0, sizeof(dom_war_blockade_item) * 1u);
    blockades[0].blockade_id = 50u;
    blockades[0].route_id = 40u;
    blockades[0].flow_limit = 100u;
    blockades[0].flow_delta = -25;

    memset(interdictions, 0, sizeof(dom_war_interdiction_item) * 2u);
    interdictions[0].interdiction_id = 60u;
    interdictions[0].route_id = 40u;
    interdictions[0].attacker_force_id = 100u;
    interdictions[0].defender_force_id = 200u;
    interdictions[0].status = DOM_WAR_INTERDICTION_PENDING;
    interdictions[1].interdiction_id = 61u;
    interdictions[1].route_id = 41u;
    interdictions[1].attacker_force_id = 0u;
    interdictions[1].defender_force_id = 200u;
    interdictions[1].status = DOM_WAR_INTERDICTION_PENDING;
}

static int test_deterministic_emission(void)
{
    dom_war_engagement_item engagements_a[3];
    dom_war_engagement_item engagements_b[3];
    dom_war_occupation_item occupations_a[2];
    dom_war_occupation_item occupations_b[2];
    dom_war_resistance_item resistances_a[2];
    dom_war_resistance_item resistances_b[2];
    dom_war_disruption_item disruptions_a[1];
    dom_war_disruption_item disruptions_b[1];
    dom_war_route_control_item routes_a[1];
    dom_war_route_control_item routes_b[1];
    dom_war_blockade_item blockades_a[1];
    dom_war_blockade_item blockades_b[1];
    dom_war_interdiction_item interdictions_a[2];
    dom_war_interdiction_item interdictions_b[2];
    dom_war_inputs inputs_a;
    dom_war_inputs inputs_b;
    dom_war_buffers buffers_a;
    dom_war_buffers buffers_b;
    dom_war_outcome_list outcomes_a;
    dom_war_outcome_list outcomes_b;
    dom_war_engagement_outcome outcome_storage_a[8];
    dom_war_engagement_outcome outcome_storage_b[8];
    dom_war_casualty_log casualties_a;
    dom_war_casualty_log casualties_b;
    dom_war_casualty_entry casualty_storage_a[8];
    dom_war_casualty_entry casualty_storage_b[8];
    dom_war_equipment_log equipment_a;
    dom_war_equipment_log equipment_b;
    dom_war_equipment_loss_entry equipment_storage_a[8];
    dom_war_equipment_loss_entry equipment_storage_b[8];
    dom_war_morale_state morale_a;
    dom_war_morale_state morale_b;
    dom_war_force_state morale_storage_a[8];
    dom_war_force_state morale_storage_b[8];
    dom_war_audit_log audit_a;
    dom_war_audit_log audit_b;
    dom_war_audit_entry audit_storage_a[16];
    dom_war_audit_entry audit_storage_b[16];
    dom_task_node tasks[64];
    dom_dependency_edge deps[64];
    dom_phase_barrier barriers[16];
    dom_cost_model costs[64];
    dom_access_set access_sets[64];
    dom_access_range reads[128];
    dom_access_range writes[128];
    dom_access_range reduces[16];
    dom_work_graph_builder graph_builder;
    dom_access_set_builder access_builder;
    dom_task_graph graph_a;
    dom_task_graph graph_b;
    WarSystem system_a;
    WarSystem system_b;
    u64 hash_a;
    u64 hash_b;

    seed_inputs(engagements_a, occupations_a, resistances_a, disruptions_a, routes_a, blockades_a, interdictions_a);
    seed_inputs(engagements_b, occupations_b, resistances_b, disruptions_b, routes_b, blockades_b, interdictions_b);
    init_war_inputs(&inputs_a, engagements_a, 3u, occupations_a, 2u, resistances_a, 2u,
                    disruptions_a, 1u, routes_a, 1u, blockades_a, 1u, interdictions_a, 2u);
    init_war_inputs(&inputs_b, engagements_b, 3u, occupations_b, 2u, resistances_b, 2u,
                    disruptions_b, 1u, routes_b, 1u, blockades_b, 1u, interdictions_b, 2u);
    EXPECT(init_war_buffers(&buffers_a, &outcomes_a, outcome_storage_a, 8u,
                            &casualties_a, casualty_storage_a, 8u,
                            &equipment_a, equipment_storage_a, 8u,
                            &morale_a, morale_storage_a, 8u,
                            &audit_a, audit_storage_a, 16u) == 0, "buffers a");
    EXPECT(init_war_buffers(&buffers_b, &outcomes_b, outcome_storage_b, 8u,
                            &casualties_b, casualty_storage_b, 8u,
                            &equipment_b, equipment_storage_b, 8u,
                            &morale_b, morale_storage_b, 8u,
                            &audit_b, audit_storage_b, 16u) == 0, "buffers b");

    system_a.init(&inputs_a, &buffers_a);
    system_b.init(&inputs_b, &buffers_b);

    dom_work_graph_builder_init(&graph_builder, tasks, 64u, deps, 64u, barriers, 16u, costs, 64u);
    dom_access_set_builder_init(&access_builder, access_sets, 64u, reads, 128u, writes, 128u, reduces, 16u);

    EXPECT(emit_graph(&system_a, &graph_builder, &access_builder, &graph_a) == 0, "emit a");
    EXPECT(emit_graph(&system_b, &graph_builder, &access_builder, &graph_b) == 0, "emit b");

    hash_a = hash_graph(&graph_a);
    hash_b = hash_graph(&graph_b);
    EXPECT(hash_a == hash_b, "war emission determinism mismatch");
    return 0;
}

static int test_batch_vs_step_equivalence(void)
{
    dom_war_engagement_item engagements_batch[3];
    dom_war_engagement_item engagements_step[3];
    dom_war_occupation_item occupations_batch[2];
    dom_war_occupation_item occupations_step[2];
    dom_war_resistance_item resistances_batch[2];
    dom_war_resistance_item resistances_step[2];
    dom_war_disruption_item disruptions_batch[1];
    dom_war_disruption_item disruptions_step[1];
    dom_war_route_control_item routes_batch[1];
    dom_war_route_control_item routes_step[1];
    dom_war_blockade_item blockades_batch[1];
    dom_war_blockade_item blockades_step[1];
    dom_war_interdiction_item interdictions_batch[2];
    dom_war_interdiction_item interdictions_step[2];
    dom_war_inputs inputs_batch;
    dom_war_inputs inputs_step;
    dom_war_buffers buffers_batch;
    dom_war_buffers buffers_step;
    dom_war_outcome_list outcomes_batch;
    dom_war_outcome_list outcomes_step;
    dom_war_engagement_outcome outcome_storage_batch[8];
    dom_war_engagement_outcome outcome_storage_step[8];
    dom_war_casualty_log casualties_batch;
    dom_war_casualty_log casualties_step;
    dom_war_casualty_entry casualty_storage_batch[8];
    dom_war_casualty_entry casualty_storage_step[8];
    dom_war_equipment_log equipment_batch;
    dom_war_equipment_log equipment_step;
    dom_war_equipment_loss_entry equipment_storage_batch[8];
    dom_war_equipment_loss_entry equipment_storage_step[8];
    dom_war_morale_state morale_batch;
    dom_war_morale_state morale_step;
    dom_war_force_state morale_storage_batch[8];
    dom_war_force_state morale_storage_step[8];
    dom_war_audit_log audit_batch;
    dom_war_audit_log audit_step;
    dom_war_audit_entry audit_storage_batch[32];
    dom_war_audit_entry audit_storage_step[32];
    dom_task_node tasks[64];
    dom_dependency_edge deps[64];
    dom_phase_barrier barriers[16];
    dom_cost_model costs[64];
    dom_access_set access_sets[64];
    dom_access_range reads[128];
    dom_access_range writes[128];
    dom_access_range reduces[16];
    dom_work_graph_builder graph_builder;
    dom_access_set_builder access_builder;
    dom_task_graph graph;
    WarSystem system_batch;
    WarSystem system_step;
    u64 hash_batch;
    u64 hash_step;
    u32 iterations = 0u;

    seed_inputs(engagements_batch, occupations_batch, resistances_batch, disruptions_batch,
                routes_batch, blockades_batch, interdictions_batch);
    seed_inputs(engagements_step, occupations_step, resistances_step, disruptions_step,
                routes_step, blockades_step, interdictions_step);

    init_war_inputs(&inputs_batch, engagements_batch, 3u, occupations_batch, 2u, resistances_batch, 2u,
                    disruptions_batch, 1u, routes_batch, 1u, blockades_batch, 1u, interdictions_batch, 2u);
    init_war_inputs(&inputs_step, engagements_step, 3u, occupations_step, 2u, resistances_step, 2u,
                    disruptions_step, 1u, routes_step, 1u, blockades_step, 1u, interdictions_step, 2u);
    EXPECT(init_war_buffers(&buffers_batch, &outcomes_batch, outcome_storage_batch, 8u,
                            &casualties_batch, casualty_storage_batch, 8u,
                            &equipment_batch, equipment_storage_batch, 8u,
                            &morale_batch, morale_storage_batch, 8u,
                            &audit_batch, audit_storage_batch, 32u) == 0, "buffers batch");
    EXPECT(init_war_buffers(&buffers_step, &outcomes_step, outcome_storage_step, 8u,
                            &casualties_step, casualty_storage_step, 8u,
                            &equipment_step, equipment_storage_step, 8u,
                            &morale_step, morale_storage_step, 8u,
                            &audit_step, audit_storage_step, 32u) == 0, "buffers step");

    system_batch.init(&inputs_batch, &buffers_batch);
    system_step.init(&inputs_step, &buffers_step);
    system_batch.set_budget_hint(16u);
    system_step.set_budget_hint(1u);

    dom_work_graph_builder_init(&graph_builder, tasks, 64u, deps, 64u, barriers, 16u, costs, 64u);
    dom_access_set_builder_init(&access_builder, access_sets, 64u, reads, 128u, writes, 128u, reduces, 16u);

    EXPECT(emit_graph(&system_batch, &graph_builder, &access_builder, &graph) == 0, "emit batch");
    EXPECT(execute_war_graph(&graph, &inputs_batch, &buffers_batch, 0u) == 0, "exec batch");
    hash_batch = hash_outcomes(buffers_batch.outcomes) ^
                 hash_casualties(buffers_batch.casualties) ^
                 hash_morale(buffers_batch.morale);

    while (iterations < 32u) {
        EXPECT(emit_graph(&system_step, &graph_builder, &access_builder, &graph) == 0, "emit step");
        if (graph.task_count == 0u) {
            break;
        }
        EXPECT(execute_war_graph(&graph, &inputs_step, &buffers_step, 0u) == 0, "exec step");
        iterations += 1u;
    }
    hash_step = hash_outcomes(buffers_step.outcomes) ^
                hash_casualties(buffers_step.casualties) ^
                hash_morale(buffers_step.morale);
    EXPECT(hash_batch == hash_step, "batch vs step mismatch");
    return 0;
}

static int test_law_gating(void)
{
    dom_war_engagement_item engagements[1];
    dom_war_occupation_item occupations[1];
    dom_war_resistance_item resistances[1];
    dom_war_disruption_item disruptions[1];
    dom_war_route_control_item routes[1];
    dom_war_blockade_item blockades[1];
    dom_war_interdiction_item interdictions[1];
    dom_war_inputs inputs;
    dom_war_buffers buffers;
    dom_war_outcome_list outcomes;
    dom_war_engagement_outcome outcome_storage[4];
    dom_war_casualty_log casualties;
    dom_war_casualty_entry casualty_storage[4];
    dom_war_equipment_log equipment;
    dom_war_equipment_loss_entry equipment_storage[4];
    dom_war_morale_state morale;
    dom_war_force_state morale_storage[4];
    dom_war_audit_log audit;
    dom_war_audit_entry audit_storage[8];
    dom_task_node tasks[16];
    dom_dependency_edge deps[16];
    dom_phase_barrier barriers[8];
    dom_cost_model costs[16];
    dom_access_set access_sets[16];
    dom_access_range reads[32];
    dom_access_range writes[32];
    dom_access_range reduces[8];
    dom_work_graph_builder graph_builder;
    dom_access_set_builder access_builder;
    dom_task_graph graph;
    WarSystem system;

    seed_inputs(engagements, occupations, resistances, disruptions, routes, blockades, interdictions);
    init_war_inputs(&inputs, engagements, 1u, occupations, 1u, resistances, 1u,
                    disruptions, 1u, routes, 1u, blockades, 1u, interdictions, 1u);
    EXPECT(init_war_buffers(&buffers, &outcomes, outcome_storage, 4u,
                            &casualties, casualty_storage, 4u,
                            &equipment, equipment_storage, 4u,
                            &morale, morale_storage, 4u,
                            &audit, audit_storage, 8u) == 0, "buffers");
    system.init(&inputs, &buffers);
    system.set_allowed_ops_mask(0u);

    dom_work_graph_builder_init(&graph_builder, tasks, 16u, deps, 16u, barriers, 8u, costs, 16u);
    dom_access_set_builder_init(&access_builder, access_sets, 16u, reads, 32u, writes, 32u, reduces, 8u);

    EXPECT(emit_graph(&system, &graph_builder, &access_builder, &graph) == 0, "emit gated");
    EXPECT(graph.task_count == 0u, "gated war should emit no tasks");
    return 0;
}

static int test_budget_bounded_emission(void)
{
    dom_war_engagement_item engagements[3];
    dom_war_occupation_item occupations[2];
    dom_war_resistance_item resistances[2];
    dom_war_disruption_item disruptions[1];
    dom_war_route_control_item routes[1];
    dom_war_blockade_item blockades[1];
    dom_war_interdiction_item interdictions[2];
    dom_war_inputs inputs;
    dom_war_buffers buffers;
    dom_war_outcome_list outcomes;
    dom_war_engagement_outcome outcome_storage[8];
    dom_war_casualty_log casualties;
    dom_war_casualty_entry casualty_storage[8];
    dom_war_equipment_log equipment;
    dom_war_equipment_loss_entry equipment_storage[8];
    dom_war_morale_state morale;
    dom_war_force_state morale_storage[8];
    dom_war_audit_log audit;
    dom_war_audit_entry audit_storage[16];
    dom_task_node tasks[64];
    dom_dependency_edge deps[64];
    dom_phase_barrier barriers[16];
    dom_cost_model costs[64];
    dom_access_set access_sets[64];
    dom_access_range reads[128];
    dom_access_range writes[128];
    dom_access_range reduces[16];
    dom_work_graph_builder graph_builder;
    dom_access_set_builder access_builder;
    dom_task_graph graph;
    WarSystem system;
    u32 i;
    u32 max_slice = 0u;

    seed_inputs(engagements, occupations, resistances, disruptions, routes, blockades, interdictions);
    init_war_inputs(&inputs, engagements, 3u, occupations, 2u, resistances, 2u,
                    disruptions, 1u, routes, 1u, blockades, 1u, interdictions, 2u);
    EXPECT(init_war_buffers(&buffers, &outcomes, outcome_storage, 8u,
                            &casualties, casualty_storage, 8u,
                            &equipment, equipment_storage, 8u,
                            &morale, morale_storage, 8u,
                            &audit, audit_storage, 16u) == 0, "buffers");
    system.init(&inputs, &buffers);
    system.set_budget_hint(1u);

    dom_work_graph_builder_init(&graph_builder, tasks, 64u, deps, 64u, barriers, 16u, costs, 64u);
    dom_access_set_builder_init(&access_builder, access_sets, 64u, reads, 128u, writes, 128u, reduces, 16u);

    EXPECT(emit_graph(&system, &graph_builder, &access_builder, &graph) == 0, "emit budget");
    for (i = 0u; i < graph.task_count; ++i) {
        const dom_war_task_params* params = (const dom_war_task_params*)graph.tasks[i].policy_params;
        if (params && params->count > max_slice) {
            max_slice = params->count;
        }
    }
    EXPECT(max_slice <= 1u, "budget slice exceeded");
    return 0;
}

static int test_casualty_tasks_only(void)
{
    dom_war_engagement_item engagements[2];
    dom_war_occupation_item occupations[1];
    dom_war_resistance_item resistances[1];
    dom_war_disruption_item disruptions[1];
    dom_war_route_control_item routes[1];
    dom_war_blockade_item blockades[1];
    dom_war_interdiction_item interdictions[1];
    dom_war_inputs inputs;
    dom_war_buffers buffers;
    dom_war_outcome_list outcomes;
    dom_war_engagement_outcome outcome_storage[4];
    dom_war_casualty_log casualties;
    dom_war_casualty_entry casualty_storage[4];
    dom_war_equipment_log equipment;
    dom_war_equipment_loss_entry equipment_storage[4];
    dom_war_morale_state morale;
    dom_war_force_state morale_storage[4];
    dom_war_audit_log audit;
    dom_war_audit_entry audit_storage[8];
    dom_task_node tasks[32];
    dom_dependency_edge deps[32];
    dom_phase_barrier barriers[8];
    dom_cost_model costs[32];
    dom_access_set access_sets[32];
    dom_access_range reads[64];
    dom_access_range writes[64];
    dom_access_range reduces[8];
    dom_work_graph_builder graph_builder;
    dom_access_set_builder access_builder;
    dom_task_graph graph;
    WarSystem system;
    u32 mask = 0u;

    seed_inputs(engagements, occupations, resistances, disruptions, routes, blockades, interdictions);
    init_war_inputs(&inputs, engagements, 2u, occupations, 1u, resistances, 1u,
                    disruptions, 1u, routes, 1u, blockades, 1u, interdictions, 1u);
    EXPECT(init_war_buffers(&buffers, &outcomes, outcome_storage, 4u,
                            &casualties, casualty_storage, 4u,
                            &equipment, equipment_storage, 4u,
                            &morale, morale_storage, 4u,
                            &audit, audit_storage, 8u) == 0, "buffers");
    system.init(&inputs, &buffers);

    mask |= (1u << DOM_WAR_TASK_ENGAGEMENT_ADMIT);
    mask |= (1u << DOM_WAR_TASK_ENGAGEMENT_RESOLVE);
    system.set_allowed_ops_mask(mask);

    dom_work_graph_builder_init(&graph_builder, tasks, 32u, deps, 32u, barriers, 8u, costs, 32u);
    dom_access_set_builder_init(&access_builder, access_sets, 32u, reads, 64u, writes, 64u, reduces, 8u);

    EXPECT(emit_graph(&system, &graph_builder, &access_builder, &graph) == 0, "emit limited");
    EXPECT(execute_war_graph(&graph, &inputs, &buffers, 0u) == 0, "exec limited");
    EXPECT(buffers.casualties->count == 0u, "casualties should be empty without task");
    return 0;
}

int main(void)
{
    if (test_deterministic_emission() != 0) return 1;
    if (test_batch_vs_step_equivalence() != 0) return 1;
    if (test_law_gating() != 0) return 1;
    if (test_budget_bounded_emission() != 0) return 1;
    if (test_casualty_tasks_only() != 0) return 1;
    return 0;
}
