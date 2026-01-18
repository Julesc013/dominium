/*
CIV5 WAR1 security force tests.
*/
#include "dominium/epistemic.h"
#include "dominium/rules/governance/enforcement_capacity.h"
#include "dominium/rules/governance/legitimacy_model.h"
#include "dominium/rules/infrastructure/store_model.h"
#include "dominium/rules/population/cohort_types.h"
#include "dominium/rules/war/demobilization_pipeline.h"
#include "dominium/rules/war/mobilization_pipeline.h"
#include "dominium/rules/war/morale_state.h"
#include "dominium/rules/war/readiness_state.h"
#include "dominium/rules/war/security_force.h"

#include <stdio.h>
#include <string.h>

#define EXPECT(cond, msg) do { \
    if (!(cond)) { \
        fprintf(stderr, "FAIL: %s\n", msg); \
        return 1; \
    } \
} while (0)

typedef struct war1_test_context {
    security_force force_storage[4];
    security_force_registry forces;

    military_cohort cohort_storage[4];
    military_cohort_registry military;

    population_cohort_state pop_storage[4];
    population_cohort_registry population;

    readiness_state readiness_storage[4];
    readiness_registry readiness;
    readiness_event readiness_events[8];
    dom_time_event readiness_due_events[16];
    dg_due_entry readiness_due_entries[8];
    readiness_due_user readiness_due_users[8];
    readiness_scheduler readiness_sched;

    morale_state morale_storage[4];
    morale_registry morale;
    morale_event morale_events[8];
    dom_time_event morale_due_events[16];
    dg_due_entry morale_due_entries[8];
    morale_due_user morale_due_users[8];
    morale_scheduler morale_sched;

    infra_store store_storage[4];
    infra_store_registry stores;

    legitimacy_state legitimacy_storage[2];
    legitimacy_registry legitimacy;

    enforcement_capacity enforcement_storage[2];
    enforcement_capacity_registry enforcement;
} war1_test_context;

static void war1_context_init(war1_test_context* t, dom_act_time_t start_tick)
{
    memset(t, 0, sizeof(*t));
    security_force_registry_init(&t->forces, t->force_storage, 4u, 1u);
    military_cohort_registry_init(&t->military, t->cohort_storage, 4u);
    population_cohort_registry_init(&t->population, t->pop_storage, 4u);
    readiness_registry_init(&t->readiness, t->readiness_storage, 4u);
    readiness_scheduler_init(&t->readiness_sched,
                             t->readiness_due_events,
                             16u,
                             t->readiness_due_entries,
                             t->readiness_due_users,
                             8u,
                             start_tick,
                             t->readiness_events,
                             8u,
                             &t->readiness,
                             &t->stores,
                             1u);
    morale_registry_init(&t->morale, t->morale_storage, 4u);
    morale_scheduler_init(&t->morale_sched,
                          t->morale_due_events,
                          16u,
                          t->morale_due_entries,
                          t->morale_due_users,
                          8u,
                          start_tick,
                          t->morale_events,
                          8u,
                          &t->morale,
                          &t->legitimacy,
                          1u);
    infra_store_registry_init(&t->stores, t->store_storage, 4u);
    legitimacy_registry_init(&t->legitimacy, t->legitimacy_storage, 2u);
    enforcement_capacity_registry_init(&t->enforcement, t->enforcement_storage, 2u);
}

static u64 war1_seed_population(war1_test_context* t, u32 count)
{
    population_cohort_key key;
    memset(&key, 0, sizeof(key));
    key.body_id = 1u;
    key.region_id = 2u;
    key.org_id = 3u;
    if (population_cohort_register(&t->population, &key, count, 0u) != 0) {
        return 0u;
    }
    return population_cohort_id_from_key(&key);
}

static int war1_seed_legitimacy(war1_test_context* t, u64 legit_id, u32 value)
{
    return legitimacy_register(&t->legitimacy, legit_id, value, LEGITIMACY_SCALE,
                               700u, 400u, 100u);
}

static int war1_seed_enforcement(war1_test_context* t, u64 cap_id, u32 enforcers)
{
    return enforcement_capacity_register(&t->enforcement, cap_id, enforcers,
                                         100u, 1u, 0u);
}

static int war1_seed_store(war1_test_context* t, u64 store_id)
{
    return infra_store_register(&t->stores, store_id);
}

static int test_mobilization_determinism(void)
{
    war1_test_context a;
    war1_test_context b;
    mobilization_context ctx_a;
    mobilization_context ctx_b;
    mobilization_request req;
    mobilization_result ra;
    mobilization_result rb;
    war_refusal_code refusal;
    u64 cohort_id;

    war1_context_init(&a, 0u);
    war1_context_init(&b, 0u);

    cohort_id = war1_seed_population(&a, 50u);
    EXPECT(cohort_id != 0u, "seed population a");
    EXPECT(war1_seed_population(&b, 50u) != 0u, "seed population b");
    EXPECT(war1_seed_store(&a, 100u) == 0, "register store a");
    EXPECT(war1_seed_store(&b, 100u) == 0, "register store b");
    EXPECT(infra_store_add(&a.stores, 100u, 10u, 5u) == 0, "seed equipment a");
    EXPECT(infra_store_add(&b.stores, 100u, 10u, 5u) == 0, "seed equipment b");
    EXPECT(infra_store_add(&a.stores, 100u, 20u, 5u) == 0, "seed supply a");
    EXPECT(infra_store_add(&b.stores, 100u, 20u, 5u) == 0, "seed supply b");
    EXPECT(war1_seed_legitimacy(&a, 9u, 900u) == 0, "register legitimacy a");
    EXPECT(war1_seed_legitimacy(&b, 9u, 900u) == 0, "register legitimacy b");
    EXPECT(war1_seed_enforcement(&a, 7u, 60u) == 0, "register enforcement a");
    EXPECT(war1_seed_enforcement(&b, 7u, 60u) == 0, "register enforcement b");

    memset(&req, 0, sizeof(req));
    req.force_id = 0u;
    req.owning_org_or_jurisdiction = 42u;
    req.domain_scope = WAR_DOMAIN_LOCAL;
    req.population_cohort_id = cohort_id;
    req.population_count = 20u;
    req.equipment_store_ref = 100u;
    req.equipment_asset_ids[0] = 10u;
    req.equipment_qtys[0] = 2u;
    req.equipment_count = 1u;
    req.logistics_dependency_refs[0] = 100u;
    req.logistics_dependency_count = 1u;
    req.readiness_start = 200u;
    req.readiness_target = 600u;
    req.readiness_degradation_rate = 50u;
    req.readiness_recovery_rate = 25u;
    req.readiness_ramp_act = 10u;
    req.morale_start = 500u;
    req.morale_legitimacy_delta = -50;
    req.legitimacy_id = 9u;
    req.legitimacy_min = 500u;
    req.enforcement_capacity_id = 7u;
    req.provenance_ref = 77u;
    req.now_act = 0u;
    req.supply_check_act = 5u;
    req.supply_asset_id = 20u;
    req.supply_qty = 1u;

    ctx_a.forces = &a.forces;
    ctx_a.military_cohorts = &a.military;
    ctx_a.population = &a.population;
    ctx_a.readiness = &a.readiness;
    ctx_a.readiness_sched = &a.readiness_sched;
    ctx_a.morale = &a.morale;
    ctx_a.morale_sched = &a.morale_sched;
    ctx_a.stores = &a.stores;
    ctx_a.legitimacy = &a.legitimacy;
    ctx_a.enforcement = &a.enforcement;

    ctx_b.forces = &b.forces;
    ctx_b.military_cohorts = &b.military;
    ctx_b.population = &b.population;
    ctx_b.readiness = &b.readiness;
    ctx_b.readiness_sched = &b.readiness_sched;
    ctx_b.morale = &b.morale;
    ctx_b.morale_sched = &b.morale_sched;
    ctx_b.stores = &b.stores;
    ctx_b.legitimacy = &b.legitimacy;
    ctx_b.enforcement = &b.enforcement;

    EXPECT(war_mobilization_apply(&req, &ctx_a, &refusal, &ra) == 0,
           "mobilization a");
    EXPECT(war_mobilization_apply(&req, &ctx_b, &refusal, &rb) == 0,
           "mobilization b");

    EXPECT(ra.force_id == rb.force_id, "force id mismatch");
    EXPECT(ra.readiness_id == rb.readiness_id, "readiness id mismatch");
    EXPECT(ra.morale_id == rb.morale_id, "morale id mismatch");
    EXPECT(a.forces.forces[0].equipment_count == b.forces.forces[0].equipment_count,
           "equipment count mismatch");
    EXPECT(a.readiness.states[0].readiness_level == b.readiness.states[0].readiness_level,
           "readiness level mismatch");
    EXPECT(a.morale.states[0].morale_level == b.morale.states[0].morale_level,
           "morale level mismatch");
    EXPECT(a.forces.forces[0].next_due_tick == b.forces.forces[0].next_due_tick,
           "next due mismatch");
    return 0;
}

static int test_no_fabrication(void)
{
    war1_test_context t;
    mobilization_context ctx;
    mobilization_request req;
    war_refusal_code refusal;
    u64 cohort_id;

    war1_context_init(&t, 0u);
    cohort_id = war1_seed_population(&t, 5u);
    EXPECT(cohort_id != 0u, "seed population");
    EXPECT(war1_seed_store(&t, 100u) == 0, "register store");
    EXPECT(war1_seed_legitimacy(&t, 9u, 900u) == 0, "register legitimacy");
    EXPECT(war1_seed_enforcement(&t, 7u, 60u) == 0, "register enforcement");

    memset(&req, 0, sizeof(req));
    req.population_cohort_id = cohort_id;
    req.population_count = 10u;
    req.equipment_store_ref = 100u;
    req.equipment_asset_ids[0] = 10u;
    req.equipment_qtys[0] = 1u;
    req.equipment_count = 1u;
    req.logistics_dependency_refs[0] = 100u;
    req.logistics_dependency_count = 1u;
    req.readiness_start = 100u;
    req.readiness_target = 200u;
    req.readiness_ramp_act = 5u;
    req.morale_start = 300u;
    req.legitimacy_id = 9u;
    req.legitimacy_min = 500u;
    req.enforcement_capacity_id = 7u;
    req.supply_asset_id = 20u;
    req.supply_qty = 1u;
    req.supply_check_act = 5u;

    ctx.forces = &t.forces;
    ctx.military_cohorts = &t.military;
    ctx.population = &t.population;
    ctx.readiness = &t.readiness;
    ctx.readiness_sched = &t.readiness_sched;
    ctx.morale = &t.morale;
    ctx.morale_sched = &t.morale_sched;
    ctx.stores = &t.stores;
    ctx.legitimacy = &t.legitimacy;
    ctx.enforcement = &t.enforcement;

    EXPECT(war_mobilization_apply(&req, &ctx, &refusal, 0) != 0,
           "mobilization should fail missing population");
    EXPECT(refusal == WAR_REFUSAL_INSUFFICIENT_POPULATION, "wrong refusal for population");

    req.population_count = 5u;
    EXPECT(war_mobilization_apply(&req, &ctx, &refusal, 0) != 0,
           "mobilization should fail missing equipment");
    EXPECT(refusal == WAR_REFUSAL_INSUFFICIENT_EQUIPMENT, "wrong refusal for equipment");
    return 0;
}

static int test_readiness_batch_vs_step(void)
{
    war1_test_context step;
    war1_test_context batch;
    u64 readiness_id = 42u;
    u32 readiness_step;
    u32 readiness_batch;

    war1_context_init(&step, 0u);
    war1_context_init(&batch, 0u);
    EXPECT(war1_seed_store(&step, 200u) == 0, "register store step");
    EXPECT(war1_seed_store(&batch, 200u) == 0, "register store batch");

    EXPECT(readiness_register(&step.readiness, readiness_id, 500u, 50u, 25u) == 0,
           "register readiness step");
    EXPECT(readiness_register(&batch.readiness, readiness_id, 500u, 50u, 25u) == 0,
           "register readiness batch");

    EXPECT(readiness_schedule_supply_check(&step.readiness_sched, readiness_id, 5u,
                                           200u, 99u, 1u, -50) == 0,
           "schedule supply check step");
    EXPECT(readiness_schedule_supply_check(&step.readiness_sched, readiness_id, 10u,
                                           200u, 99u, 1u, -50) == 0,
           "schedule supply check step 2");
    EXPECT(readiness_schedule_supply_check(&batch.readiness_sched, readiness_id, 5u,
                                           200u, 99u, 1u, -50) == 0,
           "schedule supply check batch");
    EXPECT(readiness_schedule_supply_check(&batch.readiness_sched, readiness_id, 10u,
                                           200u, 99u, 1u, -50) == 0,
           "schedule supply check batch 2");

    EXPECT(readiness_scheduler_advance(&step.readiness_sched, 5u) == 0, "step advance 5");
    EXPECT(readiness_scheduler_advance(&step.readiness_sched, 10u) == 0, "step advance 10");
    EXPECT(readiness_scheduler_advance(&batch.readiness_sched, 10u) == 0, "batch advance 10");

    readiness_step = step.readiness.states[0].readiness_level;
    readiness_batch = batch.readiness.states[0].readiness_level;
    EXPECT(readiness_step == readiness_batch, "batch vs step mismatch");
    return 0;
}

static int test_demobilization_conservation(void)
{
    war1_test_context t;
    mobilization_context mctx;
    demobilization_context dctx;
    mobilization_request req;
    mobilization_result res;
    demobilization_request dreq;
    war_refusal_code refusal;
    u64 cohort_id;
    u32 count_after = 0u;
    u32 equip_after = 0u;

    war1_context_init(&t, 0u);
    cohort_id = war1_seed_population(&t, 30u);
    EXPECT(cohort_id != 0u, "seed population");
    EXPECT(war1_seed_store(&t, 300u) == 0, "register store");
    EXPECT(infra_store_add(&t.stores, 300u, 10u, 4u) == 0, "seed equipment");
    EXPECT(infra_store_add(&t.stores, 300u, 20u, 4u) == 0, "seed supply");
    EXPECT(war1_seed_legitimacy(&t, 9u, 900u) == 0, "register legitimacy");
    EXPECT(war1_seed_enforcement(&t, 7u, 60u) == 0, "register enforcement");

    memset(&req, 0, sizeof(req));
    req.population_cohort_id = cohort_id;
    req.population_count = 10u;
    req.equipment_store_ref = 300u;
    req.equipment_asset_ids[0] = 10u;
    req.equipment_qtys[0] = 2u;
    req.equipment_count = 1u;
    req.logistics_dependency_refs[0] = 300u;
    req.logistics_dependency_count = 1u;
    req.readiness_start = 100u;
    req.readiness_target = 200u;
    req.readiness_ramp_act = 5u;
    req.morale_start = 300u;
    req.legitimacy_id = 9u;
    req.legitimacy_min = 500u;
    req.enforcement_capacity_id = 7u;
    req.supply_asset_id = 20u;
    req.supply_qty = 1u;
    req.supply_check_act = 5u;

    mctx.forces = &t.forces;
    mctx.military_cohorts = &t.military;
    mctx.population = &t.population;
    mctx.readiness = &t.readiness;
    mctx.readiness_sched = &t.readiness_sched;
    mctx.morale = &t.morale;
    mctx.morale_sched = &t.morale_sched;
    mctx.stores = &t.stores;
    mctx.legitimacy = &t.legitimacy;
    mctx.enforcement = &t.enforcement;

    EXPECT(war_mobilization_apply(&req, &mctx, &refusal, &res) == 0,
           "mobilization");

    memset(&dreq, 0, sizeof(dreq));
    dreq.force_id = res.force_id;
    dreq.equipment_store_ref = 300u;
    dreq.population_cohort_id = cohort_id;
    dreq.now_act = 20u;
    dctx.forces = &t.forces;
    dctx.military_cohorts = &t.military;
    dctx.population = &t.population;
    dctx.readiness = &t.readiness;
    dctx.morale = &t.morale;
    dctx.stores = &t.stores;

    EXPECT(war_demobilization_apply(&dreq, &dctx, &refusal) == 0,
           "demobilization");

    EXPECT(population_cohort_adjust_count(&t.population, cohort_id, 0, &count_after) == 0,
           "get population count");
    EXPECT(count_after == 30u, "population not restored");
    EXPECT(infra_store_get_qty(&t.stores, 300u, 10u, &equip_after) == 0,
           "get equipment qty");
    EXPECT(equip_after == 4u, "equipment not restored");
    return 0;
}

static int test_epistemic_visibility(void)
{
    dom_epistemic_view unknown;
    dom_epistemic_view known;
    security_force_estimate est;

    memset(&unknown, 0, sizeof(unknown));
    unknown.state = DOM_EPI_UNKNOWN;
    unknown.uncertainty_q16 = 0xFFFFu;
    unknown.is_uncertain = 1;

    memset(&known, 0, sizeof(known));
    known.state = DOM_EPI_KNOWN;
    known.uncertainty_q16 = 0u;
    known.is_uncertain = 0;

    EXPECT(security_force_estimate_from_view(&unknown, 123u, 735u, 812u, &est) == 0,
           "estimate unknown");
    EXPECT(est.is_exact == 0, "unknown should be estimate");
    EXPECT(est.estimated_count != 123u, "unknown count should be bucketed");

    EXPECT(security_force_estimate_from_view(&known, 123u, 735u, 812u, &est) == 0,
           "estimate known");
    EXPECT(est.is_exact == 1, "known should be exact");
    EXPECT(est.estimated_count == 123u, "known count mismatch");
    EXPECT(est.estimated_readiness == 735u, "known readiness mismatch");
    EXPECT(est.estimated_morale == 812u, "known morale mismatch");
    return 0;
}

int main(void)
{
    if (test_mobilization_determinism() != 0) return 1;
    if (test_no_fabrication() != 0) return 1;
    if (test_readiness_batch_vs_step() != 0) return 1;
    if (test_demobilization_conservation() != 0) return 1;
    if (test_epistemic_visibility() != 0) return 1;
    return 0;
}
