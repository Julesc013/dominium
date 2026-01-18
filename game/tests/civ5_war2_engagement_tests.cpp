/*
CIV5 WAR2 engagement resolution tests.
*/
#include "dominium/epistemic.h"
#include "dominium/life/death_pipeline.h"
#include "dominium/rules/infrastructure/store_model.h"
#include "dominium/rules/war/casualty_generator.h"
#include "dominium/rules/war/engagement.h"
#include "dominium/rules/war/engagement_resolution.h"
#include "dominium/rules/war/engagement_scheduler.h"
#include "dominium/rules/war/military_cohort.h"
#include "dominium/rules/war/morale_state.h"
#include "dominium/rules/war/readiness_state.h"
#include "dominium/rules/war/security_force.h"

#include "domino/core/dom_ledger.h"

#include <stdio.h>
#include <string.h>

#define EXPECT(cond, msg) do { \
    if (!(cond)) { \
        fprintf(stderr, "FAIL: %s\n", msg); \
        return 1; \
    } \
} while (0)

typedef struct war2_life_context {
    dom_ledger ledger;
    life_body_record bodies_storage[64];
    life_person_record persons_storage[64];
    life_death_event death_storage[64];
    life_estate estate_storage[64];
    dom_account_id_t estate_account_storage[128];
    life_person_account_entry person_account_entries[64];
    dom_account_id_t person_account_storage[128];
    life_account_owner_entry owner_storage[128];
    life_inheritance_action action_storage[64];
    life_audit_entry audit_storage[128];
    dom_time_event due_event_storage[64];
    dg_due_entry due_entry_storage[32];
    life_inheritance_due_user due_user_storage[32];
    life_remains remains_storage[64];
    life_remains_aggregate remains_aggregate_storage[32];
    life_post_death_rights rights_storage[64];
    dom_time_event remains_due_event_storage[64];
    dg_due_entry remains_due_entry_storage[32];
    life_remains_decay_user remains_due_user_storage[32];

    life_body_registry bodies;
    life_person_registry persons;
    life_person_account_registry person_accounts;
    life_account_owner_registry owners;
    life_death_event_list deaths;
    life_estate_registry estates;
    life_inheritance_action_list actions;
    life_inheritance_scheduler scheduler;
    life_audit_log audit_log;
    life_remains_registry remains;
    life_remains_aggregate_registry remains_aggregates;
    life_post_death_rights_registry rights;
    life_remains_decay_scheduler remains_decay;
    life_death_context ctx;
} war2_life_context;

static void war2_life_context_init(war2_life_context* t,
                                   dom_act_time_t start_tick,
                                   dom_act_time_t claim_period)
{
    life_remains_decay_rules rules;
    memset(t, 0, sizeof(*t));
    (void)dom_ledger_init(&t->ledger);

    life_body_registry_init(&t->bodies, t->bodies_storage, 64u);
    life_person_registry_init(&t->persons, t->persons_storage, 64u);
    life_death_event_list_init(&t->deaths, t->death_storage, 64u, 1u);
    life_estate_registry_init(&t->estates, t->estate_storage, 64u,
                              t->estate_account_storage, 128u, 1u);
    life_person_account_registry_init(&t->person_accounts, t->person_account_entries, 64u,
                                      t->person_account_storage, 128u);
    life_account_owner_registry_init(&t->owners, t->owner_storage, 128u);
    life_inheritance_action_list_init(&t->actions, t->action_storage, 64u, 1u);
    life_audit_log_init(&t->audit_log, t->audit_storage, 128u, 1u);
    (void)life_inheritance_scheduler_init(&t->scheduler,
                                          t->due_event_storage,
                                          64u,
                                          t->due_entry_storage,
                                          t->due_user_storage,
                                          32u,
                                          start_tick,
                                          claim_period,
                                          &t->estates,
                                          &t->actions);
    life_remains_registry_init(&t->remains, t->remains_storage, 64u, 1u);
    life_remains_aggregate_registry_init(&t->remains_aggregates,
                                         t->remains_aggregate_storage,
                                         32u,
                                         1u);
    life_post_death_rights_registry_init(&t->rights, t->rights_storage, 64u, 1u);
    rules.fresh_to_decayed = 5;
    rules.decayed_to_skeletal = 5;
    rules.skeletal_to_unknown = 5;
    (void)life_remains_decay_scheduler_init(&t->remains_decay,
                                            t->remains_due_event_storage,
                                            64u,
                                            t->remains_due_entry_storage,
                                            t->remains_due_user_storage,
                                            32u,
                                            start_tick,
                                            &t->remains,
                                            &rules);

    t->ctx.bodies = &t->bodies;
    t->ctx.persons = &t->persons;
    t->ctx.person_accounts = &t->person_accounts;
    t->ctx.account_owners = &t->owners;
    t->ctx.death_events = &t->deaths;
    t->ctx.estates = &t->estates;
    t->ctx.scheduler = &t->scheduler;
    t->ctx.audit_log = &t->audit_log;
    t->ctx.ledger = &t->ledger;
    t->ctx.notice_cb = 0;
    t->ctx.notice_user = 0;
    t->ctx.remains = &t->remains;
    t->ctx.rights = &t->rights;
    t->ctx.remains_decay = &t->remains_decay;
    t->ctx.remains_aggregates = &t->remains_aggregates;
    t->ctx.observation_hooks = 0;
}

static int war2_seed_person(war2_life_context* t, u64 person_id, u64 body_id)
{
    dom_account_id_t account_id = (dom_account_id_t)person_id;
    if (life_person_register(&t->persons, person_id) != 0) {
        return -1;
    }
    if (life_body_register(&t->bodies, body_id, person_id, LIFE_BODY_ALIVE) != 0) {
        return -2;
    }
    if (dom_ledger_account_create(&t->ledger, account_id, 0u) != DOM_LEDGER_OK) {
        return -3;
    }
    if (life_person_account_register(&t->person_accounts, person_id, &account_id, 1u) != 0) {
        return -4;
    }
    return 0;
}

static u32 war2_seed_bodies(war2_life_context* t,
                            u64 person_start,
                            u64 body_start,
                            u32 count,
                            u64* out_body_ids)
{
    u32 i;
    if (!t || !out_body_ids) {
        return 0u;
    }
    for (i = 0u; i < count; ++i) {
        u64 person_id = person_start + i;
        u64 body_id = body_start + i;
        if (war2_seed_person(t, person_id, body_id) != 0) {
            return i;
        }
        out_body_ids[i] = body_id;
    }
    return count;
}

typedef struct war2_test_context {
    security_force forces_storage[4];
    security_force_registry forces;
    military_cohort military_storage[4];
    military_cohort_registry military;
    readiness_state readiness_storage[4];
    readiness_registry readiness;
    morale_state morale_storage[4];
    morale_registry morale;
    engagement engagements_storage[4];
    engagement_registry engagements;
    engagement_outcome outcomes_storage[4];
    engagement_outcome_list outcomes;
    dom_time_event due_events[16];
    dg_due_entry due_entries[8];
    engagement_due_user due_users[8];
    engagement_scheduler scheduler;

    infra_store store_storage[4];
    infra_store_registry stores;

    war2_life_context life;
    casualty_generator casualty_gen;
    engagement_casualty_source casualty_sources[4];
    engagement_resolution_context resolution;
} war2_test_context;

static void war2_context_init(war2_test_context* t)
{
    memset(t, 0, sizeof(*t));
    security_force_registry_init(&t->forces, t->forces_storage, 4u, 1u);
    military_cohort_registry_init(&t->military, t->military_storage, 4u);
    readiness_registry_init(&t->readiness, t->readiness_storage, 4u);
    morale_registry_init(&t->morale, t->morale_storage, 4u);
    engagement_registry_init(&t->engagements, t->engagements_storage, 4u, 1u);
    engagement_outcome_list_init(&t->outcomes, t->outcomes_storage, 4u, 1u);
    infra_store_registry_init(&t->stores, t->store_storage, 4u);
    war2_life_context_init(&t->life, 0u, 5u);
    t->casualty_gen.life = &t->life.ctx;

    t->resolution.forces = &t->forces;
    t->resolution.military = &t->military;
    t->resolution.readiness = &t->readiness;
    t->resolution.morale = &t->morale;
    t->resolution.legitimacy = 0;
    t->resolution.stores = &t->stores;
    t->resolution.casualty_gen = &t->casualty_gen;
    t->resolution.casualty_sources = t->casualty_sources;
    t->resolution.casualty_source_count = 0u;
    t->resolution.outcomes = &t->outcomes;
    memset(&t->resolution.casualty_config, 0, sizeof(t->resolution.casualty_config));
    t->resolution.casualty_config.cause_code = LIFE_DEATH_CAUSE_VIOLENCE;
    t->resolution.casualty_config.policy_id = 1u;
    t->resolution.casualty_config.collapse_remains = 1u;

    (void)engagement_scheduler_init(&t->scheduler,
                                    t->due_events,
                                    16u,
                                    t->due_entries,
                                    t->due_users,
                                    8u,
                                    0u,
                                    &t->engagements,
                                    &t->outcomes,
                                    &t->resolution);
}

static int war2_seed_force(war2_test_context* t,
                           u64 force_id,
                           u64 cohort_id,
                           u32 cohort_count,
                           u64 equipment_id,
                           u32 equipment_qty,
                           u64 supply_store_ref)
{
    if (security_force_register(&t->forces, force_id, 1u, WAR_DOMAIN_LOCAL,
                                cohort_id, force_id) != 0) {
        return -1;
    }
    if (military_cohort_register(&t->military, cohort_id, force_id,
                                 cohort_count, MILITARY_ROLE_INFANTRY,
                                 cohort_id) != 0) {
        return -2;
    }
    if (readiness_register(&t->readiness, force_id, 700u, 50u, 25u) != 0) {
        return -3;
    }
    if (morale_register(&t->morale, force_id, 800u, 0) != 0) {
        return -4;
    }
    if (security_force_add_equipment(&t->forces, force_id, equipment_id, equipment_qty) != 0) {
        return -5;
    }
    if (security_force_add_logistics_dependency(&t->forces, force_id, supply_store_ref) != 0) {
        return -6;
    }
    if (security_force_set_states(&t->forces, force_id, force_id, force_id) != 0) {
        return -7;
    }
    return 0;
}

static int war2_seed_supply_store(war2_test_context* t, u64 store_id, u64 asset_id, u32 qty)
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

static int war2_register_engagement(war2_test_context* t,
                                    u64 engagement_id,
                                    u64 attacker_force_id,
                                    u64 defender_force_id,
                                    u64 supply_asset_id,
                                    u32 supply_qty)
{
    engagement input;
    memset(&input, 0, sizeof(input));
    input.engagement_id = engagement_id;
    input.domain_scope = WAR_DOMAIN_LOCAL;
    input.participant_count = 2u;
    input.participants[0].force_id = attacker_force_id;
    input.participants[0].role = ENGAGEMENT_ROLE_ATTACKER;
    input.participants[0].supply_store_ref = 100u;
    input.participants[1].force_id = defender_force_id;
    input.participants[1].role = ENGAGEMENT_ROLE_DEFENDER;
    input.participants[1].supply_store_ref = 200u;
    input.start_act = 0u;
    input.resolution_act = 10u;
    input.objective = ENGAGEMENT_OBJECTIVE_ATTACK;
    input.supply_asset_id = supply_asset_id;
    input.supply_qty = supply_qty;
    input.provenance_ref = engagement_id;
    return engagement_register(&t->engagements, &input, 0);
}

static void war2_set_casualty_source(war2_test_context* t,
                                     u32 slot,
                                     u64 force_id,
                                     const u64* body_ids,
                                     u32 count)
{
    t->casualty_sources[slot].force_id = force_id;
    t->casualty_sources[slot].source.body_ids = body_ids;
    t->casualty_sources[slot].source.count = count;
    t->casualty_sources[slot].source.cursor = 0u;
    if (slot + 1u > t->resolution.casualty_source_count) {
        t->resolution.casualty_source_count = slot + 1u;
    }
}

static int test_deterministic_resolution(void)
{
    war2_test_context a;
    war2_test_context b;
    u64 bodies_a[20];
    u64 bodies_b[20];
    const engagement_outcome* oa;
    const engagement_outcome* ob;

    war2_context_init(&a);
    war2_context_init(&b);
    EXPECT(war2_seed_supply_store(&a, 100u, 99u, 10u) == 0, "store a atk");
    EXPECT(war2_seed_supply_store(&a, 200u, 99u, 10u) == 0, "store a def");
    EXPECT(war2_seed_supply_store(&b, 100u, 99u, 10u) == 0, "store b atk");
    EXPECT(war2_seed_supply_store(&b, 200u, 99u, 10u) == 0, "store b def");

    EXPECT(war2_seed_force(&a, 1u, 11u, 10u, 500u, 4u, 100u) == 0, "force a atk");
    EXPECT(war2_seed_force(&a, 2u, 12u, 10u, 501u, 4u, 200u) == 0, "force a def");
    EXPECT(war2_seed_force(&b, 1u, 11u, 10u, 500u, 4u, 100u) == 0, "force b atk");
    EXPECT(war2_seed_force(&b, 2u, 12u, 10u, 501u, 4u, 200u) == 0, "force b def");

    EXPECT(war2_seed_bodies(&a.life, 100u, 1000u, 10u, bodies_a) == 10u, "bodies a atk");
    EXPECT(war2_seed_bodies(&a.life, 200u, 2000u, 10u, bodies_a + 10u) == 10u, "bodies a def");
    EXPECT(war2_seed_bodies(&b.life, 100u, 1000u, 10u, bodies_b) == 10u, "bodies b atk");
    EXPECT(war2_seed_bodies(&b.life, 200u, 2000u, 10u, bodies_b + 10u) == 10u, "bodies b def");

    war2_set_casualty_source(&a, 0u, 1u, bodies_a, 10u);
    war2_set_casualty_source(&a, 1u, 2u, bodies_a + 10u, 10u);
    war2_set_casualty_source(&b, 0u, 1u, bodies_b, 10u);
    war2_set_casualty_source(&b, 1u, 2u, bodies_b + 10u, 10u);

    EXPECT(war2_register_engagement(&a, 1u, 1u, 2u, 99u, 1u) == 0, "engage a");
    EXPECT(war2_register_engagement(&b, 1u, 1u, 2u, 99u, 1u) == 0, "engage b");

    EXPECT(engagement_scheduler_register(&a.scheduler, &a.engagements.engagements[0]) == 0, "sched a");
    EXPECT(engagement_scheduler_register(&b.scheduler, &b.engagements.engagements[0]) == 0, "sched b");
    EXPECT(engagement_scheduler_advance(&a.scheduler, 10u) == 0, "advance a");
    EXPECT(engagement_scheduler_advance(&b.scheduler, 10u) == 0, "advance b");

    EXPECT(a.outcomes.count == 1u, "outcome count a");
    EXPECT(b.outcomes.count == 1u, "outcome count b");
    oa = &a.outcomes.outcomes[0];
    ob = &b.outcomes.outcomes[0];
    EXPECT(oa->casualty_count == ob->casualty_count, "casualty count mismatch");
    EXPECT(oa->equipment_loss_count == ob->equipment_loss_count, "equipment loss mismatch");
    EXPECT(oa->morale_delta == ob->morale_delta, "morale delta mismatch");
    EXPECT(oa->legitimacy_delta == ob->legitimacy_delta, "legitimacy delta mismatch");
    EXPECT(a.life.deaths.count == b.life.deaths.count, "death events mismatch");
    return 0;
}

static int test_batch_vs_step_equivalence(void)
{
    war2_test_context step;
    war2_test_context batch;
    u64 bodies_step[8];
    u64 bodies_batch[8];

    war2_context_init(&step);
    war2_context_init(&batch);
    EXPECT(war2_seed_supply_store(&step, 100u, 99u, 10u) == 0, "store step atk");
    EXPECT(war2_seed_supply_store(&step, 200u, 99u, 10u) == 0, "store step def");
    EXPECT(war2_seed_supply_store(&batch, 100u, 99u, 10u) == 0, "store batch atk");
    EXPECT(war2_seed_supply_store(&batch, 200u, 99u, 10u) == 0, "store batch def");

    EXPECT(war2_seed_force(&step, 1u, 11u, 8u, 500u, 3u, 100u) == 0, "force step atk");
    EXPECT(war2_seed_force(&step, 2u, 12u, 8u, 501u, 3u, 200u) == 0, "force step def");
    EXPECT(war2_seed_force(&batch, 1u, 11u, 8u, 500u, 3u, 100u) == 0, "force batch atk");
    EXPECT(war2_seed_force(&batch, 2u, 12u, 8u, 501u, 3u, 200u) == 0, "force batch def");

    EXPECT(war2_seed_bodies(&step.life, 100u, 1000u, 4u, bodies_step) == 4u, "bodies step atk");
    EXPECT(war2_seed_bodies(&step.life, 200u, 2000u, 4u, bodies_step + 4u) == 4u, "bodies step def");
    EXPECT(war2_seed_bodies(&batch.life, 100u, 1000u, 4u, bodies_batch) == 4u, "bodies batch atk");
    EXPECT(war2_seed_bodies(&batch.life, 200u, 2000u, 4u, bodies_batch + 4u) == 4u, "bodies batch def");

    war2_set_casualty_source(&step, 0u, 1u, bodies_step, 4u);
    war2_set_casualty_source(&step, 1u, 2u, bodies_step + 4u, 4u);
    war2_set_casualty_source(&batch, 0u, 1u, bodies_batch, 4u);
    war2_set_casualty_source(&batch, 1u, 2u, bodies_batch + 4u, 4u);

    EXPECT(war2_register_engagement(&step, 2u, 1u, 2u, 99u, 1u) == 0, "engage step");
    EXPECT(war2_register_engagement(&batch, 2u, 1u, 2u, 99u, 1u) == 0, "engage batch");

    EXPECT(engagement_scheduler_register(&step.scheduler, &step.engagements.engagements[0]) == 0, "sched step");
    EXPECT(engagement_scheduler_register(&batch.scheduler, &batch.engagements.engagements[0]) == 0, "sched batch");

    EXPECT(engagement_scheduler_advance(&step.scheduler, 5u) == 0, "advance step 5");
    EXPECT(engagement_scheduler_advance(&step.scheduler, 10u) == 0, "advance step 10");
    EXPECT(engagement_scheduler_advance(&batch.scheduler, 10u) == 0, "advance batch 10");

    EXPECT(step.outcomes.count == 1u, "outcome step count");
    EXPECT(batch.outcomes.count == 1u, "outcome batch count");
    EXPECT(step.outcomes.outcomes[0].casualty_count == batch.outcomes.outcomes[0].casualty_count,
           "batch vs step casualty mismatch");
    return 0;
}

static int test_casualty_conservation(void)
{
    war2_test_context t;
    u64 bodies[8];
    u32 before_a;
    u32 before_b;
    u32 after_a;
    u32 after_b;

    war2_context_init(&t);
    EXPECT(war2_seed_supply_store(&t, 100u, 99u, 10u) == 0, "store atk");
    EXPECT(war2_seed_supply_store(&t, 200u, 99u, 10u) == 0, "store def");
    EXPECT(war2_seed_force(&t, 1u, 11u, 8u, 500u, 2u, 100u) == 0, "force atk");
    EXPECT(war2_seed_force(&t, 2u, 12u, 8u, 501u, 2u, 200u) == 0, "force def");
    EXPECT(war2_seed_bodies(&t.life, 100u, 1000u, 4u, bodies) == 4u, "bodies atk");
    EXPECT(war2_seed_bodies(&t.life, 200u, 2000u, 4u, bodies + 4u) == 4u, "bodies def");
    war2_set_casualty_source(&t, 0u, 1u, bodies, 4u);
    war2_set_casualty_source(&t, 1u, 2u, bodies + 4u, 4u);

    {
        military_cohort* ca = military_cohort_find(&t.military, 11u);
        military_cohort* cb = military_cohort_find(&t.military, 12u);
        EXPECT(ca != 0, "find cohort atk");
        EXPECT(cb != 0, "find cohort def");
        before_a = ca->count;
        before_b = cb->count;
    }

    EXPECT(war2_register_engagement(&t, 3u, 1u, 2u, 99u, 1u) == 0, "engage");
    EXPECT(engagement_scheduler_register(&t.scheduler, &t.engagements.engagements[0]) == 0, "sched");
    EXPECT(engagement_scheduler_advance(&t.scheduler, 10u) == 0, "advance");

    {
        military_cohort* ca = military_cohort_find(&t.military, 11u);
        military_cohort* cb = military_cohort_find(&t.military, 12u);
        EXPECT(ca != 0, "find cohort atk after");
        EXPECT(cb != 0, "find cohort def after");
        after_a = ca->count;
        after_b = cb->count;
    }
    EXPECT(after_a <= before_a, "attacker count increased");
    EXPECT(after_b <= before_b, "defender count increased");
    EXPECT((before_a - after_a) + (before_b - after_b) == t.outcomes.outcomes[0].casualty_count,
           "casualty conservation mismatch");
    return 0;
}

static int test_logistics_depletion(void)
{
    war2_test_context supplied;
    war2_test_context depleted;
    u64 bodies_sup[8];
    u64 bodies_dep[8];
    u32 before_sup;
    u32 before_dep;
    u32 after_sup;
    u32 after_dep;

    war2_context_init(&supplied);
    war2_context_init(&depleted);
    EXPECT(war2_seed_supply_store(&supplied, 100u, 99u, 10u) == 0, "supply store sup");
    EXPECT(war2_seed_supply_store(&supplied, 200u, 99u, 10u) == 0, "supply store sup def");
    EXPECT(war2_seed_supply_store(&depleted, 100u, 99u, 0u) == 0, "supply store dep");
    EXPECT(war2_seed_supply_store(&depleted, 200u, 99u, 10u) == 0, "supply store dep def");

    EXPECT(war2_seed_force(&supplied, 1u, 11u, 8u, 500u, 2u, 100u) == 0, "force sup atk");
    EXPECT(war2_seed_force(&supplied, 2u, 12u, 8u, 501u, 2u, 200u) == 0, "force sup def");
    EXPECT(war2_seed_force(&depleted, 1u, 11u, 8u, 500u, 2u, 100u) == 0, "force dep atk");
    EXPECT(war2_seed_force(&depleted, 2u, 12u, 8u, 501u, 2u, 200u) == 0, "force dep def");

    EXPECT(war2_seed_bodies(&supplied.life, 100u, 1000u, 4u, bodies_sup) == 4u, "bodies sup atk");
    EXPECT(war2_seed_bodies(&supplied.life, 200u, 2000u, 4u, bodies_sup + 4u) == 4u, "bodies sup def");
    EXPECT(war2_seed_bodies(&depleted.life, 100u, 1000u, 4u, bodies_dep) == 4u, "bodies dep atk");
    EXPECT(war2_seed_bodies(&depleted.life, 200u, 2000u, 4u, bodies_dep + 4u) == 4u, "bodies dep def");

    war2_set_casualty_source(&supplied, 0u, 1u, bodies_sup, 4u);
    war2_set_casualty_source(&supplied, 1u, 2u, bodies_sup + 4u, 4u);
    war2_set_casualty_source(&depleted, 0u, 1u, bodies_dep, 4u);
    war2_set_casualty_source(&depleted, 1u, 2u, bodies_dep + 4u, 4u);

    {
        military_cohort* ca = military_cohort_find(&supplied.military, 11u);
        military_cohort* cb = military_cohort_find(&depleted.military, 11u);
        EXPECT(ca != 0, "find cohort sup atk");
        EXPECT(cb != 0, "find cohort dep atk");
        before_sup = ca->count;
        before_dep = cb->count;
    }

    EXPECT(war2_register_engagement(&supplied, 4u, 1u, 2u, 99u, 1u) == 0, "engage sup");
    EXPECT(war2_register_engagement(&depleted, 4u, 1u, 2u, 99u, 1u) == 0, "engage dep");
    EXPECT(engagement_scheduler_register(&supplied.scheduler, &supplied.engagements.engagements[0]) == 0, "sched sup");
    EXPECT(engagement_scheduler_register(&depleted.scheduler, &depleted.engagements.engagements[0]) == 0, "sched dep");
    EXPECT(engagement_scheduler_advance(&supplied.scheduler, 10u) == 0, "advance sup");
    EXPECT(engagement_scheduler_advance(&depleted.scheduler, 10u) == 0, "advance dep");

    {
        military_cohort* ca = military_cohort_find(&supplied.military, 11u);
        military_cohort* cb = military_cohort_find(&depleted.military, 11u);
        EXPECT(ca != 0, "find cohort sup atk after");
        EXPECT(cb != 0, "find cohort dep atk after");
        after_sup = ca->count;
        after_dep = cb->count;
    }
    EXPECT((before_dep - after_dep) >= (before_sup - after_sup), "depleted supply not worse");
    return 0;
}

static int test_epistemic_delay(void)
{
    engagement_outcome outcome;
    engagement_outcome_summary summary;
    dom_epistemic_view unknown;
    dom_epistemic_view known;

    memset(&outcome, 0, sizeof(outcome));
    outcome.casualty_count = 7u;
    outcome.equipment_loss_count = 3u;
    outcome.morale_delta = -50;
    outcome.legitimacy_delta = -10;

    memset(&unknown, 0, sizeof(unknown));
    unknown.state = DOM_EPI_UNKNOWN;
    unknown.uncertainty_q16 = 0xFFFFu;
    unknown.is_uncertain = 1;

    memset(&known, 0, sizeof(known));
    known.state = DOM_EPI_KNOWN;
    known.uncertainty_q16 = 0u;
    known.is_uncertain = 0;

    EXPECT(engagement_outcome_estimate_from_view(&unknown, &outcome, &summary) == 0,
           "estimate unknown");
    EXPECT(summary.is_exact == 0, "unknown should be inexact");
    EXPECT(summary.casualty_count != outcome.casualty_count, "unknown casualty should differ");

    EXPECT(engagement_outcome_estimate_from_view(&known, &outcome, &summary) == 0,
           "estimate known");
    EXPECT(summary.is_exact == 1, "known should be exact");
    EXPECT(summary.casualty_count == outcome.casualty_count, "known casualty mismatch");
    return 0;
}

int main(void)
{
    if (test_deterministic_resolution() != 0) return 1;
    if (test_batch_vs_step_equivalence() != 0) return 1;
    if (test_casualty_conservation() != 0) return 1;
    if (test_logistics_depletion() != 0) return 1;
    if (test_epistemic_delay() != 0) return 1;
    return 0;
}
