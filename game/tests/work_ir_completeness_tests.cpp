/*
Work IR completeness tests (EXEC-AUDIT0).
*/
#include "dominium/execution/system_registry.h"
#include "dominium/execution/work_graph_builder.h"
#include "dominium/execution/access_set_builder.h"
#include "dominium/rules/war/war_system.h"

#include <stdio.h>
#include <string.h>

#define EXPECT(cond, msg) do { \
    if (!(cond)) { \
        fprintf(stderr, "FAIL: %s\n", msg); \
        return 1; \
    } \
} while (0)

static void init_war_inputs(dom_war_inputs* inputs,
                            dom_war_engagement_item* engagements,
                            dom_war_occupation_item* occupations,
                            dom_war_resistance_item* resistances,
                            dom_war_disruption_item* disruptions,
                            dom_war_route_control_item* routes,
                            dom_war_blockade_item* blockades,
                            dom_war_interdiction_item* interdictions)
{
    if (!inputs) {
        return;
    }
    inputs->engagements = engagements;
    inputs->engagement_count = 1u;
    inputs->engagement_set_id = 9001u;
    inputs->occupations = occupations;
    inputs->occupation_count = 1u;
    inputs->occupation_set_id = 9002u;
    inputs->resistances = resistances;
    inputs->resistance_count = 1u;
    inputs->resistance_set_id = 9003u;
    inputs->disruptions = disruptions;
    inputs->disruption_count = 1u;
    inputs->disruption_set_id = 9004u;
    inputs->routes = routes;
    inputs->route_count = 1u;
    inputs->route_set_id = 9005u;
    inputs->blockades = blockades;
    inputs->blockade_count = 1u;
    inputs->blockade_set_id = 9006u;
    inputs->interdictions = interdictions;
    inputs->interdiction_count = 1u;
    inputs->interdiction_set_id = 9007u;
}

static int init_war_buffers(dom_war_buffers* buffers,
                            dom_war_outcome_list* outcomes,
                            dom_war_engagement_outcome* outcome_storage,
                            dom_war_casualty_log* casualties,
                            dom_war_casualty_entry* casualty_storage,
                            dom_war_equipment_log* equipment,
                            dom_war_equipment_loss_entry* equipment_storage,
                            dom_war_morale_state* morale,
                            dom_war_force_state* morale_storage,
                            dom_war_audit_log* audit,
                            dom_war_audit_entry* audit_storage)
{
    if (!buffers || !outcomes || !casualties || !equipment || !morale || !audit) {
        return -1;
    }
    dom_war_outcome_list_init(outcomes, outcome_storage, 4u, 1u);
    dom_war_casualty_log_init(casualties, casualty_storage, 4u);
    dom_war_equipment_log_init(equipment, equipment_storage, 4u);
    dom_war_morale_state_init(morale, morale_storage, 4u);
    dom_war_audit_init(audit, audit_storage, 8u, 1u);

    buffers->outcomes = outcomes;
    buffers->casualties = casualties;
    buffers->equipment_losses = equipment;
    buffers->morale = morale;
    buffers->audit_log = audit;
    buffers->outcome_set_id = 9101u;
    buffers->casualty_set_id = 9102u;
    buffers->equipment_set_id = 9103u;
    buffers->morale_set_id = 9104u;
    buffers->audit_set_id = 9105u;
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

static int test_work_ir_completeness(void)
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
    dom_task_node tasks[64];
    dom_dependency_edge deps[64];
    dom_phase_barrier barriers[8];
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

    memset(engagements, 0, sizeof(engagements));
    memset(occupations, 0, sizeof(occupations));
    memset(resistances, 0, sizeof(resistances));
    memset(disruptions, 0, sizeof(disruptions));
    memset(routes, 0, sizeof(routes));
    memset(blockades, 0, sizeof(blockades));
    memset(interdictions, 0, sizeof(interdictions));

    init_war_inputs(&inputs, engagements, occupations, resistances, disruptions,
                    routes, blockades, interdictions);
    EXPECT(init_war_buffers(&buffers, &outcomes, outcome_storage,
                            &casualties, casualty_storage,
                            &equipment, equipment_storage,
                            &morale, morale_storage,
                            &audit, audit_storage) == 0, "buffers");
    system.init(&inputs, &buffers);

    dom_work_graph_builder_init(&graph_builder, tasks, 64u, deps, 64u, barriers, 8u, costs, 64u);
    dom_access_set_builder_init(&access_builder, access_sets, 64u, reads, 128u, writes, 128u, reduces, 16u);
    dom_work_graph_builder_set_ids(&graph_builder, 400u, 1u);
    dom_work_graph_builder_reset(&graph_builder);
    dom_access_set_builder_reset(&access_builder);

    EXPECT(system.emit_tasks(0, 10, &graph_builder, &access_builder) == 0, "emit");
    dom_work_graph_builder_finalize(&graph_builder, &graph);
    EXPECT(graph.task_count > 0u, "expected tasks");

    for (i = 0u; i < graph.task_count; ++i) {
        const dom_task_node* node = &graph.tasks[i];
        const dom_access_set* set = find_access_set(access_sets, access_builder.set_count, node->access_set_id);
        EXPECT(node->access_set_id != 0u, "missing access_set_id");
        EXPECT(node->cost_model_id != 0u, "missing cost_model_id");
        EXPECT(node->determinism_class <= DOM_DET_DERIVED, "missing determinism_class");
        EXPECT(node->commit_key.phase_id == node->phase_id, "commit_key phase mismatch");
        EXPECT(node->commit_key.task_id == node->task_id, "commit_key task mismatch");
        if (node->category == DOM_TASK_AUTHORITATIVE) {
            EXPECT(node->law_targets != 0, "missing law_targets");
            EXPECT(node->law_target_count > 0u, "empty law_targets");
        }
        EXPECT(set != 0, "missing access set");
        if (set) {
            EXPECT(set->read_count + set->write_count + set->reduce_count > 0u, "empty access set");
        }
    }
    return 0;
}

static int test_disabled_system_emits_no_tasks(void)
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
    dom_system_registry registry;
    dom_system_entry entries[1];
    WarSystem system;

    memset(engagements, 0, sizeof(engagements));
    memset(occupations, 0, sizeof(occupations));
    memset(resistances, 0, sizeof(resistances));
    memset(disruptions, 0, sizeof(disruptions));
    memset(routes, 0, sizeof(routes));
    memset(blockades, 0, sizeof(blockades));
    memset(interdictions, 0, sizeof(interdictions));

    init_war_inputs(&inputs, engagements, occupations, resistances, disruptions,
                    routes, blockades, interdictions);
    EXPECT(init_war_buffers(&buffers, &outcomes, outcome_storage,
                            &casualties, casualty_storage,
                            &equipment, equipment_storage,
                            &morale, morale_storage,
                            &audit, audit_storage) == 0, "buffers");
    system.init(&inputs, &buffers);

    dom_system_registry_init(&registry, entries, 1u);
    EXPECT(dom_system_registry_register(&registry, &system) == 0, "register");
    EXPECT(dom_system_registry_set_enabled(&registry, system.system_id(), 0) == 0, "disable");

    dom_work_graph_builder_init(&graph_builder, tasks, 16u, deps, 8u, barriers, 4u, costs, 16u);
    dom_access_set_builder_init(&access_builder, access_sets, 16u, reads, 32u, writes, 32u, reduces, 8u);
    dom_work_graph_builder_reset(&graph_builder);
    dom_access_set_builder_reset(&access_builder);

    EXPECT(dom_system_registry_emit(&registry, 0, 10, &graph_builder, &access_builder) == 0, "emit");
    dom_work_graph_builder_finalize(&graph_builder, &graph);
    EXPECT(graph.task_count == 0u, "disabled system should emit no tasks");
    return 0;
}

int main(void)
{
    if (test_work_ir_completeness() != 0) return 1;
    if (test_disabled_system_emits_no_tasks() != 0) return 1;
    return 0;
}
