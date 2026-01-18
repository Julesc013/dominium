/*
CIV1 city/infrastructure/logistics tests.
*/
#include "dominium/rules/city/city_model.h"
#include "dominium/rules/infrastructure/building_machine.h"
#include "dominium/rules/infrastructure/machine_scheduler.h"
#include "dominium/rules/infrastructure/production_chain.h"
#include "dominium/rules/infrastructure/store_model.h"
#include "dominium/rules/logistics/logistics_flow.h"
#include "dominium/rules/logistics/transport_capacity.h"

#include <stdio.h>
#include <string.h>

#define EXPECT(cond, msg) do { \
    if (!(cond)) { \
        fprintf(stderr, "FAIL: %s\n", msg); \
        return 1; \
    } \
} while (0)

typedef struct civ1_test_context {
    infra_store store_storage[16];
    infra_store_registry stores;
    production_recipe recipe_storage[8];
    production_recipe_registry recipes;
    building_machine machine_storage[8];
    building_machine_registry machines;
    dom_time_event machine_events[32];
    dg_due_entry machine_entries[8];
    machine_due_user machine_users[8];
    machine_scheduler machine_sched;

    transport_capacity capacity_storage[8];
    transport_capacity_registry capacities;
    logistics_flow flow_storage[8];
    logistics_flow_registry flows;
    dom_time_event flow_events[32];
    dg_due_entry flow_entries[8];
    logistics_flow_due_user flow_users[8];
    logistics_flow_scheduler flow_sched;

    city_record city_storage[4];
    city_registry cities;
} civ1_test_context;

static void civ1_context_init(civ1_test_context* t, dom_act_time_t start_tick)
{
    machine_scheduler_params mparams;
    memset(t, 0, sizeof(*t));
    infra_store_registry_init(&t->stores, t->store_storage, 16u);
    production_recipe_registry_init(&t->recipes, t->recipe_storage, 8u);
    building_machine_registry_init(&t->machines, t->machine_storage, 8u);
    machine_scheduler_params_default(&mparams);
    (void)machine_scheduler_init(&t->machine_sched,
                                 t->machine_events,
                                 32u,
                                 t->machine_entries,
                                 t->machine_users,
                                 8u,
                                 start_tick,
                                 &t->machines,
                                 &t->recipes,
                                 &t->stores,
                                 &mparams);

    transport_capacity_registry_init(&t->capacities, t->capacity_storage, 8u);
    logistics_flow_registry_init(&t->flows, t->flow_storage, 8u, 1u);
    (void)logistics_flow_scheduler_init(&t->flow_sched,
                                        t->flow_events,
                                        32u,
                                        t->flow_entries,
                                        t->flow_users,
                                        8u,
                                        start_tick,
                                        &t->flows,
                                        &t->stores,
                                        &t->capacities);

    city_registry_init(&t->cities, t->city_storage, 4u);
}

static void civ1_seed_recipe(production_recipe_registry* reg, u64 recipe_id)
{
    production_recipe recipe;
    memset(&recipe, 0, sizeof(recipe));
    recipe.recipe_id = recipe_id;
    recipe.input_count = 1u;
    recipe.inputs[0].asset_id = 1u;
    recipe.inputs[0].qty = 2u;
    recipe.output_count = 1u;
    recipe.outputs[0].asset_id = 2u;
    recipe.outputs[0].qty = 1u;
    recipe.duration_act = 5u;
    (void)production_recipe_register(reg, &recipe);
}

static int test_deterministic_production(void)
{
    civ1_test_context a;
    civ1_test_context b;
    building_machine* ma;
    building_machine* mb;

    civ1_context_init(&a, 0);
    civ1_context_init(&b, 0);
    civ1_seed_recipe(&a.recipes, 101u);
    civ1_seed_recipe(&b.recipes, 101u);

    EXPECT(infra_store_register(&a.stores, 100u) == 0, "register store a input");
    EXPECT(infra_store_register(&a.stores, 200u) == 0, "register store a output");
    EXPECT(infra_store_add(&a.stores, 100u, 1u, 4u) == 0, "seed inputs a");

    EXPECT(infra_store_register(&b.stores, 100u) == 0, "register store b input");
    EXPECT(infra_store_register(&b.stores, 200u) == 0, "register store b output");
    EXPECT(infra_store_add(&b.stores, 100u, 1u, 4u) == 0, "seed inputs b");

    EXPECT(building_machine_register(&a.machines, 500u, 7u, 1u) == 0, "register machine a");
    EXPECT(building_machine_register(&b.machines, 500u, 7u, 1u) == 0, "register machine b");
    ma = building_machine_find(&a.machines, 500u);
    mb = building_machine_find(&b.machines, 500u);
    EXPECT(building_machine_set_recipe(&a.machines, 500u, 101u) == 0, "set recipe a");
    EXPECT(building_machine_set_recipe(&b.machines, 500u, 101u) == 0, "set recipe b");
    EXPECT(building_machine_add_input_store(&a.machines, 500u, 100u) == 0, "add input a");
    EXPECT(building_machine_add_output_store(&a.machines, 500u, 200u) == 0, "add output a");
    EXPECT(building_machine_add_input_store(&b.machines, 500u, 100u) == 0, "add input b");
    EXPECT(building_machine_add_output_store(&b.machines, 500u, 200u) == 0, "add output b");
    ma->next_due_tick = 5u;
    mb->next_due_tick = 5u;
    EXPECT(machine_scheduler_register(&a.machine_sched, ma) == 0, "register sched a");
    EXPECT(machine_scheduler_register(&b.machine_sched, mb) == 0, "register sched b");

    EXPECT(machine_scheduler_advance(&a.machine_sched, 10, 0) == 0, "advance a");
    EXPECT(machine_scheduler_advance(&b.machine_sched, 10, 0) == 0, "advance b");

    {
        u32 qa = 0u;
        u32 qb = 0u;
        (void)infra_store_get_qty(&a.stores, 200u, 2u, &qa);
        (void)infra_store_get_qty(&b.stores, 200u, 2u, &qb);
        EXPECT(qa == qb, "output mismatch");
        EXPECT(ma->next_due_tick == mb->next_due_tick, "next due mismatch");
    }
    return 0;
}

static int test_batch_vs_step_equivalence(void)
{
    civ1_test_context step;
    civ1_test_context batch;
    building_machine* ms;
    building_machine* mb;
    dom_act_time_t tick;
    u32 qs = 0u;
    u32 qb = 0u;

    civ1_context_init(&step, 0);
    civ1_context_init(&batch, 0);
    civ1_seed_recipe(&step.recipes, 201u);
    civ1_seed_recipe(&batch.recipes, 201u);

    EXPECT(infra_store_register(&step.stores, 300u) == 0, "register store step input");
    EXPECT(infra_store_register(&step.stores, 400u) == 0, "register store step output");
    EXPECT(infra_store_add(&step.stores, 300u, 1u, 20u) == 0, "seed inputs step");

    EXPECT(infra_store_register(&batch.stores, 300u) == 0, "register store batch input");
    EXPECT(infra_store_register(&batch.stores, 400u) == 0, "register store batch output");
    EXPECT(infra_store_add(&batch.stores, 300u, 1u, 20u) == 0, "seed inputs batch");

    EXPECT(building_machine_register(&step.machines, 600u, 7u, 1u) == 0, "register machine step");
    EXPECT(building_machine_register(&batch.machines, 600u, 7u, 1u) == 0, "register machine batch");
    ms = building_machine_find(&step.machines, 600u);
    mb = building_machine_find(&batch.machines, 600u);
    EXPECT(building_machine_set_recipe(&step.machines, 600u, 201u) == 0, "set recipe step");
    EXPECT(building_machine_set_recipe(&batch.machines, 600u, 201u) == 0, "set recipe batch");
    EXPECT(building_machine_add_input_store(&step.machines, 600u, 300u) == 0, "add input step");
    EXPECT(building_machine_add_output_store(&step.machines, 600u, 400u) == 0, "add output step");
    EXPECT(building_machine_add_input_store(&batch.machines, 600u, 300u) == 0, "add input batch");
    EXPECT(building_machine_add_output_store(&batch.machines, 600u, 400u) == 0, "add output batch");
    ms->next_due_tick = 5u;
    mb->next_due_tick = 5u;
    EXPECT(machine_scheduler_register(&step.machine_sched, ms) == 0, "register sched step");
    EXPECT(machine_scheduler_register(&batch.machine_sched, mb) == 0, "register sched batch");

    for (tick = 5u; tick <= 30u; tick += 5u) {
        EXPECT(machine_scheduler_advance(&step.machine_sched, tick, 0) == 0, "step advance");
    }
    EXPECT(machine_scheduler_advance(&batch.machine_sched, 30u, 0) == 0, "batch advance");

    (void)infra_store_get_qty(&step.stores, 400u, 2u, &qs);
    (void)infra_store_get_qty(&batch.stores, 400u, 2u, &qb);
    EXPECT(qs == qb, "batch vs step output mismatch");
    return 0;
}

static int test_logistics_arrival_determinism(void)
{
    civ1_test_context t;
    logistics_flow_input input;
    civ1_refusal_code refusal;
    u32 qty_out = 0u;
    transport_capacity* cap;

    civ1_context_init(&t, 0);
    EXPECT(infra_store_register(&t.stores, 900u) == 0, "register src store");
    EXPECT(infra_store_register(&t.stores, 901u) == 0, "register dst store");
    EXPECT(infra_store_add(&t.stores, 900u, 5u, 10u) == 0, "seed src assets");
    EXPECT(transport_capacity_register(&t.capacities, 77u, 10u) == 0, "register capacity");

    memset(&input, 0, sizeof(input));
    input.src_store_ref = 900u;
    input.dst_store_ref = 901u;
    input.asset_id = 5u;
    input.qty = 4u;
    input.departure_act = 0u;
    input.arrival_act = 10u;
    input.capacity_ref = 77u;
    EXPECT(logistics_flow_schedule(&t.flows, &input, &t.stores, &t.capacities, &refusal) == 0,
           "schedule flow");
    EXPECT(logistics_flow_scheduler_register(&t.flow_sched, &t.flows.flows[0]) == 0, "register flow");
    EXPECT(logistics_flow_scheduler_advance(&t.flow_sched, 10u) == 0, "advance flow");
    (void)infra_store_get_qty(&t.stores, 901u, 5u, &qty_out);
    EXPECT(qty_out == 4u, "arrival qty mismatch");
    cap = transport_capacity_find(&t.capacities, 77u);
    EXPECT(cap && cap->available_qty == cap->max_qty, "capacity not released");
    return 0;
}

static int test_macro_micro_totals_preserved(void)
{
    civ1_test_context t;
    city_macro_summary summary;
    u32 before = 0u;
    u32 after = 0u;
    building_machine* machine;
    civ1_refusal_code refusal;

    civ1_context_init(&t, 0);
    EXPECT(city_register(&t.cities, 1u, 100u, 0u) == 0, "register city");
    EXPECT(building_machine_register(&t.machines, 700u, 9u, 1u) == 0, "register machine");
    machine = building_machine_find(&t.machines, 700u);
    EXPECT(infra_store_register(&t.stores, 1000u) == 0, "register output store");
    EXPECT(building_machine_add_output_store(&t.machines, 700u, 1000u) == 0, "add output store");
    EXPECT(infra_store_add(&t.stores, 1000u, 42u, 7u) == 0, "seed outputs");
    EXPECT(city_add_building(&t.cities, 1u, 700u, &refusal) == 0, "add building");

    EXPECT(city_collect_macro_summary(city_find(&t.cities, 1u),
                                      &t.machines, &t.stores, &summary) == 0, "collect summary");
    if (summary.total_count > 0u) {
        before = summary.totals[0].qty;
    }
    EXPECT(city_apply_macro_summary(city_find(&t.cities, 1u),
                                    &t.machines, &t.stores, &summary) == 0, "apply summary");
    EXPECT(city_collect_macro_summary(city_find(&t.cities, 1u),
                                      &t.machines, &t.stores, &summary) == 0, "collect summary after");
    if (summary.total_count > 0u) {
        after = summary.totals[0].qty;
    }
    EXPECT(before == after, "macro/micro totals mismatch");
    return 0;
}

static int test_no_global_iteration(void)
{
    civ1_test_context t;
    u32 i;
    building_machine* machine;

    civ1_context_init(&t, 0);
    civ1_seed_recipe(&t.recipes, 301u);
    EXPECT(infra_store_register(&t.stores, 1100u) == 0, "register input store");
    EXPECT(infra_store_register(&t.stores, 1101u) == 0, "register output store");
    EXPECT(infra_store_add(&t.stores, 1100u, 1u, 100u) == 0, "seed inputs");

    for (i = 0u; i < 5u; ++i) {
        u64 id = 800u + i;
        EXPECT(building_machine_register(&t.machines, id, 9u, 1u) == 0, "register machine");
        EXPECT(building_machine_set_recipe(&t.machines, id, 301u) == 0, "set recipe");
        EXPECT(building_machine_add_input_store(&t.machines, id, 1100u) == 0, "add input store");
        EXPECT(building_machine_add_output_store(&t.machines, id, 1101u) == 0, "add output store");
        machine = building_machine_find(&t.machines, id);
        machine->next_due_tick = (i == 0u) ? 5u : 1000u;
        EXPECT(machine_scheduler_register(&t.machine_sched, machine) == 0, "register sched");
    }
    EXPECT(machine_scheduler_advance(&t.machine_sched, 5u, 0) == 0, "advance scheduler");
    EXPECT(t.machine_sched.processed_last == 1u, "processed unexpected machines");
    return 0;
}

int main(void)
{
    if (test_deterministic_production() != 0) return 1;
    if (test_batch_vs_step_equivalence() != 0) return 1;
    if (test_logistics_arrival_determinism() != 0) return 1;
    if (test_macro_micro_totals_preserved() != 0) return 1;
    if (test_no_global_iteration() != 0) return 1;
    return 0;
}
