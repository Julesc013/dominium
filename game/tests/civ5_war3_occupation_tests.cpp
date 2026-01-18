/*
CIV5 WAR3 occupation and resistance tests.
*/
#include "dominium/rules/governance/enforcement_capacity.h"
#include "dominium/rules/governance/legitimacy_model.h"
#include "dominium/rules/infrastructure/store_model.h"
#include "dominium/rules/logistics/transport_capacity.h"
#include "dominium/rules/survival/cohort_model.h"
#include "dominium/rules/survival/needs_model.h"
#include "dominium/rules/war/disruption_effects.h"
#include "dominium/rules/war/occupation_state.h"
#include "dominium/rules/war/pacification_policies.h"
#include "dominium/rules/war/resistance_scheduler.h"
#include "dominium/rules/war/resistance_state.h"
#include "dominium/rules/war/territory_control.h"

#include <stdio.h>
#include <string.h>

#define EXPECT(cond, msg) do { \
    if (!(cond)) { \
        fprintf(stderr, "FAIL: %s\n", msg); \
        return 1; \
    } \
} while (0)

typedef struct war3_test_context {
    territory_control territory_storage[8];
    territory_control_registry territories;

    occupation_state occupation_storage[8];
    occupation_registry occupations;

    resistance_state resistance_storage[8];
    resistance_registry resistances;

    disruption_event disruption_storage[8];
    disruption_event_list disruptions;

    pacification_policy policy_storage[4];
    pacification_policy_registry policies;

    pacification_policy_event policy_event_storage[8];
    pacification_policy_event_list policy_events;

    legitimacy_state legitimacy_storage[4];
    legitimacy_registry legitimacy;

    enforcement_capacity enforcement_storage[4];
    enforcement_capacity_registry enforcement;

    infra_store store_storage[4];
    infra_store_registry stores;

    transport_capacity transport_storage[4];
    transport_capacity_registry transport;

    survival_cohort survival_storage[4];
    survival_cohort_registry cohorts;

    survival_needs_entry needs_storage[4];
    survival_needs_registry needs;

    survival_needs_params needs_params;

    dom_time_event due_events[32];
    dg_due_entry due_entries[32];
    resistance_due_user due_users[32];
    resistance_scheduler scheduler;
} war3_test_context;

static void war3_context_init(war3_test_context* t)
{
    memset(t, 0, sizeof(*t));
    territory_control_registry_init(&t->territories, t->territory_storage, 8u);
    occupation_registry_init(&t->occupations, t->occupation_storage, 8u, 1u);
    resistance_registry_init(&t->resistances, t->resistance_storage, 8u, 1u);
    disruption_event_list_init(&t->disruptions, t->disruption_storage, 8u, 1u);
    pacification_policy_registry_init(&t->policies, t->policy_storage, 4u, 1u);
    pacification_policy_event_list_init(&t->policy_events, t->policy_event_storage, 8u, 1u);
    legitimacy_registry_init(&t->legitimacy, t->legitimacy_storage, 4u);
    enforcement_capacity_registry_init(&t->enforcement, t->enforcement_storage, 4u);
    infra_store_registry_init(&t->stores, t->store_storage, 4u);
    transport_capacity_registry_init(&t->transport, t->transport_storage, 4u);
    survival_cohort_registry_init(&t->cohorts, t->survival_storage, 4u);
    survival_needs_registry_init(&t->needs, t->needs_storage, 4u);
    survival_needs_params_default(&t->needs_params);

    (void)resistance_scheduler_init(&t->scheduler,
                                    t->due_events,
                                    32u,
                                    t->due_entries,
                                    t->due_users,
                                    32u,
                                    0u,
                                    &t->occupations,
                                    &t->resistances,
                                    &t->territories,
                                    &t->disruptions,
                                    &t->policies,
                                    &t->policy_events,
                                    &t->legitimacy,
                                    &t->enforcement,
                                    &t->stores,
                                    &t->transport,
                                    &t->cohorts,
                                    &t->needs,
                                    &t->needs_params);
}

static int war3_seed_territory(war3_test_context* t, u64 territory_id, u64 controller_id, u32 strength)
{
    return territory_control_register(&t->territories, territory_id, controller_id, strength);
}

static int war3_seed_enforcement(war3_test_context* t, u64 cap_id, u32 enforcers)
{
    return enforcement_capacity_register(&t->enforcement, cap_id, enforcers, 100u, 1u, 0u);
}

static int war3_seed_legitimacy(war3_test_context* t, u64 legit_id, u32 value)
{
    return legitimacy_register(&t->legitimacy, legit_id, value, LEGITIMACY_SCALE,
                               700u, 400u, 100u);
}

static int war3_seed_store(war3_test_context* t, u64 store_id, u64 asset_id, u32 qty)
{
    if (infra_store_register(&t->stores, store_id) != 0) {
        return -1;
    }
    if (qty > 0u) {
        if (infra_store_add(&t->stores, store_id, asset_id, qty) != 0) {
            return -2;
        }
    }
    return 0;
}

static int war3_seed_transport(war3_test_context* t, u64 cap_id, u32 qty)
{
    return transport_capacity_register(&t->transport, cap_id, qty);
}

static int war3_seed_cohort(war3_test_context* t, u64 cohort_id, u32 count)
{
    return survival_cohort_register(&t->cohorts, cohort_id, count, 1u);
}

static int war3_seed_needs(war3_test_context* t,
                           u64 cohort_id,
                           u32 food,
                           u32 water,
                           u32 shelter,
                           u32 hunger,
                           u32 thirst)
{
    survival_needs_state state;
    memset(&state, 0, sizeof(state));
    state.food_store = food;
    state.water_store = water;
    state.shelter_level = shelter;
    state.hunger_level = hunger;
    state.thirst_level = thirst;
    return survival_needs_register(&t->needs, cohort_id, &state);
}

static int war3_register_occupation(war3_test_context* t,
                                    u64 occupation_id,
                                    u64 territory_id,
                                    u64 occupier_id,
                                    u64 enforcement_id,
                                    u64 legitimacy_id,
                                    u64 store_ref,
                                    u64 supply_asset_id,
                                    u32 supply_qty,
                                    dom_act_time_t next_due,
                                    u32 interval)
{
    occupation_state occ;
    memset(&occ, 0, sizeof(occ));
    occ.occupation_id = occupation_id;
    occ.territory_id = territory_id;
    occ.occupier_org_id = occupier_id;
    occ.enforcement_capacity_id = enforcement_id;
    occ.enforcement_min = 1u;
    occ.legitimacy_id = legitimacy_id;
    occ.legitimacy_min = 500u;
    occ.legitimacy_decay = -10;
    occ.supply_refs[0] = store_ref;
    occ.supply_ref_count = 1u;
    occ.supply_asset_id = supply_asset_id;
    occ.supply_qty = supply_qty;
    occ.control_gain = 10u;
    occ.control_loss = 20u;
    occ.start_act = 0u;
    occ.next_due_tick = next_due;
    occ.maintenance_interval = interval;
    occ.status = OCCUPATION_STATUS_ACTIVE;
    return occupation_register(&t->occupations, &occ, 0);
}

static int test_deterministic_occupation_failure_no_supply(void)
{
    war3_test_context a;
    war3_test_context b;
    occupation_state* oa;
    occupation_state* ob;

    war3_context_init(&a);
    war3_context_init(&b);
    EXPECT(war3_seed_territory(&a, 1u, 7u, 500u) == 0, "territory a");
    EXPECT(war3_seed_territory(&b, 1u, 7u, 500u) == 0, "territory b");
    EXPECT(war3_seed_enforcement(&a, 2u, 10u) == 0, "enforcement a");
    EXPECT(war3_seed_enforcement(&b, 2u, 10u) == 0, "enforcement b");
    EXPECT(war3_seed_legitimacy(&a, 3u, 800u) == 0, "legitimacy a");
    EXPECT(war3_seed_legitimacy(&b, 3u, 800u) == 0, "legitimacy b");
    EXPECT(war3_seed_store(&a, 100u, 99u, 0u) == 0, "store a");
    EXPECT(war3_seed_store(&b, 100u, 99u, 0u) == 0, "store b");

    EXPECT(war3_register_occupation(&a, 1u, 1u, 7u, 2u, 3u, 100u, 99u, 1u, 5u, 5u) == 0, "occ a");
    EXPECT(war3_register_occupation(&b, 1u, 1u, 7u, 2u, 3u, 100u, 99u, 1u, 5u, 5u) == 0, "occ b");

    oa = occupation_find(&a.occupations, 1u);
    ob = occupation_find(&b.occupations, 1u);
    EXPECT(oa != 0 && ob != 0, "find occupations");
    EXPECT(resistance_scheduler_register_occupation(&a.scheduler, oa) == 0, "sched occ a");
    EXPECT(resistance_scheduler_register_occupation(&b.scheduler, ob) == 0, "sched occ b");
    EXPECT(resistance_scheduler_advance(&a.scheduler, 5u) == 0, "advance a");
    EXPECT(resistance_scheduler_advance(&b.scheduler, 5u) == 0, "advance b");

    EXPECT(oa->status == OCCUPATION_STATUS_FAILED, "occ a should fail");
    EXPECT(ob->status == OCCUPATION_STATUS_FAILED, "occ b should fail");
    EXPECT(a.territories.controls[0].control_strength == b.territories.controls[0].control_strength,
           "control strength mismatch");
    return 0;
}

static int test_resistance_activation_legitimacy(void)
{
    war3_test_context t;
    resistance_state res;
    resistance_state* stored;

    war3_context_init(&t);
    EXPECT(war3_seed_territory(&t, 2u, 9u, 500u) == 0, "territory");
    EXPECT(war3_seed_legitimacy(&t, 5u, 100u) == 0, "legitimacy");
    EXPECT(war3_seed_cohort(&t, 42u, 10u) == 0, "cohort");
    EXPECT(war3_seed_needs(&t, 42u, 50u, 50u, 2u, 0u, 0u) == 0, "needs");

    memset(&res, 0, sizeof(res));
    res.resistance_id = 1u;
    res.territory_id = 2u;
    res.legitimacy_id = 5u;
    res.population_cohort_id = 42u;
    res.legitimacy_min = 900u;
    res.pressure_gain_base = 150u;
    res.activation_threshold = 200u;
    res.suppression_threshold = 100u;
    res.update_interval = 5u;
    res.next_due_tick = 5u;
    res.status = RESISTANCE_STATUS_LATENT;

    EXPECT(resistance_register(&t.resistances, &res, 0) == 0, "register resistance");
    stored = resistance_find(&t.resistances, 1u);
    EXPECT(stored != 0, "find resistance");
    EXPECT(resistance_scheduler_register_resistance(&t.scheduler, stored) == 0, "sched resistance");
    EXPECT(resistance_scheduler_advance(&t.scheduler, 5u) == 0, "advance");
    EXPECT(stored->status == RESISTANCE_STATUS_ACTIVE, "resistance not active");
    EXPECT(stored->resistance_pressure >= stored->activation_threshold, "pressure below threshold");
    return 0;
}

static int test_disruption_determinism(void)
{
    war3_test_context a;
    war3_test_context b;
    disruption_event ev_a;
    disruption_event ev_b;
    disruption_effects_context ctx_a;
    disruption_effects_context ctx_b;
    transport_capacity* cap_a;
    transport_capacity* cap_b;
    u32 qty_a = 0u;
    u32 qty_b = 0u;

    war3_context_init(&a);
    war3_context_init(&b);
    EXPECT(war3_seed_transport(&a, 10u, 20u) == 0, "transport a");
    EXPECT(war3_seed_transport(&b, 10u, 20u) == 0, "transport b");
    EXPECT(war3_seed_store(&a, 200u, 55u, 5u) == 0, "store a");
    EXPECT(war3_seed_store(&b, 200u, 55u, 5u) == 0, "store b");
    EXPECT(war3_seed_legitimacy(&a, 6u, 800u) == 0, "legitimacy a");
    EXPECT(war3_seed_legitimacy(&b, 6u, 800u) == 0, "legitimacy b");

    memset(&ev_a, 0, sizeof(ev_a));
    memset(&ev_b, 0, sizeof(ev_b));
    ev_a.disruption_id = 1u;
    ev_a.transport_capacity_id = 10u;
    ev_a.capacity_delta = 3u;
    ev_a.supply_store_ref = 200u;
    ev_a.supply_asset_id = 55u;
    ev_a.supply_qty = 2u;
    ev_a.legitimacy_id = 6u;
    ev_a.legitimacy_delta = -10;
    ev_a.status = DISRUPTION_STATUS_SCHEDULED;
    ev_b = ev_a;

    memset(&ctx_a, 0, sizeof(ctx_a));
    memset(&ctx_b, 0, sizeof(ctx_b));
    ctx_a.stores = &a.stores;
    ctx_a.transport = &a.transport;
    ctx_a.legitimacy = &a.legitimacy;
    ctx_b.stores = &b.stores;
    ctx_b.transport = &b.transport;
    ctx_b.legitimacy = &b.legitimacy;

    EXPECT(disruption_apply(&ev_a, &ctx_a) == 0, "apply a");
    EXPECT(disruption_apply(&ev_b, &ctx_b) == 0, "apply b");

    cap_a = transport_capacity_find(&a.transport, 10u);
    cap_b = transport_capacity_find(&b.transport, 10u);
    EXPECT(cap_a != 0 && cap_b != 0, "find transport");
    EXPECT(cap_a->available_qty == cap_b->available_qty, "capacity mismatch");
    EXPECT(infra_store_get_qty(&a.stores, 200u, 55u, &qty_a) == 0, "qty a");
    EXPECT(infra_store_get_qty(&b.stores, 200u, 55u, &qty_b) == 0, "qty b");
    EXPECT(qty_a == qty_b, "store qty mismatch");
    EXPECT(a.legitimacy.states[0].value == b.legitimacy.states[0].value, "legitimacy mismatch");
    return 0;
}

static int test_batch_vs_step_equivalence(void)
{
    war3_test_context step;
    war3_test_context batch;
    occupation_state* occ_step;
    occupation_state* occ_batch;
    u32 strength_step;
    u32 strength_batch;

    war3_context_init(&step);
    war3_context_init(&batch);
    EXPECT(war3_seed_territory(&step, 3u, 7u, 400u) == 0, "territory step");
    EXPECT(war3_seed_territory(&batch, 3u, 7u, 400u) == 0, "territory batch");
    EXPECT(war3_seed_enforcement(&step, 2u, 10u) == 0, "enforcement step");
    EXPECT(war3_seed_enforcement(&batch, 2u, 10u) == 0, "enforcement batch");
    EXPECT(war3_seed_legitimacy(&step, 3u, 900u) == 0, "legitimacy step");
    EXPECT(war3_seed_legitimacy(&batch, 3u, 900u) == 0, "legitimacy batch");
    EXPECT(war3_seed_store(&step, 100u, 99u, 10u) == 0, "store step");
    EXPECT(war3_seed_store(&batch, 100u, 99u, 10u) == 0, "store batch");

    EXPECT(war3_register_occupation(&step, 1u, 3u, 7u, 2u, 3u, 100u, 99u, 1u, 5u, 5u) == 0, "occ step");
    EXPECT(war3_register_occupation(&batch, 1u, 3u, 7u, 2u, 3u, 100u, 99u, 1u, 5u, 5u) == 0, "occ batch");

    occ_step = occupation_find(&step.occupations, 1u);
    occ_batch = occupation_find(&batch.occupations, 1u);
    EXPECT(occ_step != 0 && occ_batch != 0, "find occupations");
    EXPECT(resistance_scheduler_register_occupation(&step.scheduler, occ_step) == 0, "sched step");
    EXPECT(resistance_scheduler_register_occupation(&batch.scheduler, occ_batch) == 0, "sched batch");

    EXPECT(resistance_scheduler_advance(&step.scheduler, 5u) == 0, "step 5");
    EXPECT(resistance_scheduler_advance(&step.scheduler, 10u) == 0, "step 10");
    EXPECT(resistance_scheduler_advance(&step.scheduler, 15u) == 0, "step 15");
    EXPECT(resistance_scheduler_advance(&step.scheduler, 20u) == 0, "step 20");

    EXPECT(resistance_scheduler_advance(&batch.scheduler, 20u) == 0, "batch 20");

    strength_step = step.territories.controls[0].control_strength;
    strength_batch = batch.territories.controls[0].control_strength;
    EXPECT(strength_step == strength_batch, "batch vs step control mismatch");
    return 0;
}

static int test_no_global_iteration(void)
{
    war3_test_context t;
    occupation_state* occ_a;
    occupation_state* occ_b;
    occupation_state* occ_c;
    u32 before_a;
    u32 after_a;
    u32 before_b;
    u32 after_b;
    u32 before_c;
    u32 after_c;

    war3_context_init(&t);
    EXPECT(war3_seed_territory(&t, 10u, 7u, 300u) == 0, "territory a");
    EXPECT(war3_seed_territory(&t, 11u, 7u, 300u) == 0, "territory b");
    EXPECT(war3_seed_territory(&t, 12u, 7u, 300u) == 0, "territory c");
    EXPECT(war3_seed_enforcement(&t, 2u, 10u) == 0, "enforcement");
    EXPECT(war3_seed_legitimacy(&t, 3u, 900u) == 0, "legitimacy");
    EXPECT(war3_seed_store(&t, 100u, 99u, 5u) == 0, "store");

    EXPECT(war3_register_occupation(&t, 1u, 10u, 7u, 2u, 3u, 100u, 99u, 1u, 5u, 5u) == 0, "occ a");
    EXPECT(war3_register_occupation(&t, 2u, 11u, 7u, 2u, 3u, 100u, 99u, 1u, 50u, 5u) == 0, "occ b");
    EXPECT(war3_register_occupation(&t, 3u, 12u, 7u, 2u, 3u, 100u, 99u, 1u, 50u, 5u) == 0, "occ c");

    occ_a = occupation_find(&t.occupations, 1u);
    occ_b = occupation_find(&t.occupations, 2u);
    occ_c = occupation_find(&t.occupations, 3u);
    EXPECT(occ_a && occ_b && occ_c, "find occupations");
    EXPECT(resistance_scheduler_register_occupation(&t.scheduler, occ_a) == 0, "sched a");
    EXPECT(resistance_scheduler_register_occupation(&t.scheduler, occ_b) == 0, "sched b");
    EXPECT(resistance_scheduler_register_occupation(&t.scheduler, occ_c) == 0, "sched c");

    before_a = t.territories.controls[0].control_strength;
    before_b = t.territories.controls[1].control_strength;
    before_c = t.territories.controls[2].control_strength;

    EXPECT(resistance_scheduler_advance(&t.scheduler, 5u) == 0, "advance");
    EXPECT(t.scheduler.processed_last == 1u, "processed count");

    after_a = t.territories.controls[0].control_strength;
    after_b = t.territories.controls[1].control_strength;
    after_c = t.territories.controls[2].control_strength;

    EXPECT(after_a != before_a, "due occupation did not change");
    EXPECT(after_b == before_b, "non-due occupation changed");
    EXPECT(after_c == before_c, "non-due occupation changed");
    return 0;
}

int main(void)
{
    if (test_deterministic_occupation_failure_no_supply() != 0) return 1;
    if (test_resistance_activation_legitimacy() != 0) return 1;
    if (test_disruption_determinism() != 0) return 1;
    if (test_batch_vs_step_equivalence() != 0) return 1;
    if (test_no_global_iteration() != 0) return 1;
    return 0;
}
