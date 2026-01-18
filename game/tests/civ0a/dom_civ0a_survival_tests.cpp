/*
CIV0a survival loop tests.
*/
#include "dominium/rules/survival/cohort_model.h"
#include "dominium/rules/survival/consumption_scheduler.h"
#include "dominium/rules/survival/needs_model.h"
#include "dominium/rules/survival/survival_production_actions.h"

#include <stdio.h>
#include <string.h>

#define EXPECT(cond, msg) do { \
    if (!(cond)) { \
        fprintf(stderr, "FAIL: %s\n", msg); \
        return 1; \
    } \
} while (0)

typedef struct civ0a_test_context {
    survival_cohort cohorts_storage[128];
    survival_needs_entry needs_storage[128];
    dom_time_event consumption_event_storage[256];
    dg_due_entry consumption_entry_storage[128];
    survival_consumption_due_user consumption_user_storage[128];

    survival_production_action actions_storage[64];
    dom_time_event production_event_storage[128];
    dg_due_entry production_entry_storage[64];
    survival_production_due_user production_user_storage[64];

    survival_cohort_registry cohorts;
    survival_needs_registry needs;
    survival_consumption_scheduler consumption;
    survival_production_action_registry actions;
    survival_production_scheduler production;
    survival_needs_params params;
} civ0a_test_context;

static void civ0a_test_context_init(civ0a_test_context* t, dom_act_time_t start_tick)
{
    memset(t, 0, sizeof(*t));
    survival_cohort_registry_init(&t->cohorts, t->cohorts_storage, 128u);
    survival_needs_registry_init(&t->needs, t->needs_storage, 128u);
    survival_needs_params_default(&t->params);
    t->params.consumption_interval = 5;
    t->params.hunger_max = 4;
    t->params.thirst_max = 3;
    (void)survival_consumption_scheduler_init(&t->consumption,
                                              t->consumption_event_storage,
                                              256u,
                                              t->consumption_entry_storage,
                                              t->consumption_user_storage,
                                              128u,
                                              start_tick,
                                              &t->cohorts,
                                              &t->needs,
                                              &t->params);
    survival_production_action_registry_init(&t->actions, t->actions_storage, 64u, 1u);
    (void)survival_production_scheduler_init(&t->production,
                                             t->production_event_storage,
                                             128u,
                                             t->production_entry_storage,
                                             t->production_user_storage,
                                             64u,
                                             start_tick,
                                             &t->cohorts,
                                             &t->needs,
                                             &t->actions);
}

static int test_consumption_determinism(void)
{
    civ0a_test_context a;
    civ0a_test_context b;
    survival_cohort* ca;
    survival_cohort* cb;
    survival_needs_state* na;
    survival_needs_state* nb;

    civ0a_test_context_init(&a, 0);
    civ0a_test_context_init(&b, 0);
    EXPECT(survival_cohort_register(&a.cohorts, 1u, 2u, 10u) == 0, "register A");
    EXPECT(survival_cohort_register(&b.cohorts, 1u, 2u, 10u) == 0, "register B");
    ca = survival_cohort_find(&a.cohorts, 1u);
    cb = survival_cohort_find(&b.cohorts, 1u);
    EXPECT(ca && cb, "cohort lookup");

    EXPECT(survival_consumption_register_cohort(&a.consumption, ca) == 0, "register consumption A");
    EXPECT(survival_consumption_register_cohort(&b.consumption, cb) == 0, "register consumption B");

    na = survival_needs_get(&a.needs, 1u);
    nb = survival_needs_get(&b.needs, 1u);
    EXPECT(na && nb, "needs lookup");
    na->food_store = 10u;
    na->water_store = 10u;
    nb->food_store = 10u;
    nb->water_store = 10u;

    EXPECT(survival_consumption_advance(&a.consumption, 5) == 0, "advance A");
    EXPECT(survival_consumption_advance(&b.consumption, 5) == 0, "advance B");

    EXPECT(na->food_store == nb->food_store, "food store mismatch");
    EXPECT(na->water_store == nb->water_store, "water store mismatch");
    EXPECT(na->hunger_level == nb->hunger_level, "hunger mismatch");
    EXPECT(na->thirst_level == nb->thirst_level, "thirst mismatch");
    EXPECT(ca->next_due_tick == cb->next_due_tick, "next due mismatch");
    return 0;
}

static int test_batch_vs_step_equivalence(void)
{
    civ0a_test_context step;
    civ0a_test_context batch;
    survival_cohort* cs;
    survival_cohort* cb;
    survival_needs_state* ns;
    survival_needs_state* nb;
    dom_act_time_t tick;

    civ0a_test_context_init(&step, 0);
    civ0a_test_context_init(&batch, 0);
    EXPECT(survival_cohort_register(&step.cohorts, 2u, 1u, 11u) == 0, "register step");
    EXPECT(survival_cohort_register(&batch.cohorts, 2u, 1u, 11u) == 0, "register batch");
    cs = survival_cohort_find(&step.cohorts, 2u);
    cb = survival_cohort_find(&batch.cohorts, 2u);
    EXPECT(survival_consumption_register_cohort(&step.consumption, cs) == 0, "register step consumption");
    EXPECT(survival_consumption_register_cohort(&batch.consumption, cb) == 0, "register batch consumption");

    ns = survival_needs_get(&step.needs, 2u);
    nb = survival_needs_get(&batch.needs, 2u);
    ns->food_store = 50u;
    ns->water_store = 50u;
    nb->food_store = 50u;
    nb->water_store = 50u;

    for (tick = 5; tick <= 100; tick += 5) {
        EXPECT(survival_consumption_advance(&step.consumption, tick) == 0, "step advance");
    }
    EXPECT(survival_consumption_advance(&batch.consumption, 100) == 0, "batch advance");

    EXPECT(ns->food_store == nb->food_store, "food store mismatch");
    EXPECT(ns->water_store == nb->water_store, "water store mismatch");
    EXPECT(ns->hunger_level == nb->hunger_level, "hunger mismatch");
    EXPECT(ns->thirst_level == nb->thirst_level, "thirst mismatch");
    EXPECT(cs->count == cb->count, "count mismatch");
    return 0;
}

typedef struct death_counter {
    u32 deaths;
    u32 cause;
} death_counter;

static int death_hook_emit(void* user,
                           u64 cohort_id,
                           u32 count,
                           dom_act_time_t act_time,
                           u32 cause_code)
{
    death_counter* counter = (death_counter*)user;
    (void)cohort_id;
    (void)act_time;
    if (counter) {
        counter->deaths += count;
        counter->cause = cause_code;
    }
    return 0;
}

static int test_starvation_death_trigger(void)
{
    civ0a_test_context t;
    survival_cohort* cohort;
    survival_needs_state* needs;
    survival_death_hook hook;
    death_counter counter;

    civ0a_test_context_init(&t, 0);
    t.params.hunger_max = 1;
    (void)survival_consumption_scheduler_init(&t.consumption,
                                              t.consumption_event_storage,
                                              256u,
                                              t.consumption_entry_storage,
                                              t.consumption_user_storage,
                                              128u,
                                              0,
                                              &t.cohorts,
                                              &t.needs,
                                              &t.params);
    EXPECT(survival_cohort_register(&t.cohorts, 3u, 1u, 12u) == 0, "register cohort");
    cohort = survival_cohort_find(&t.cohorts, 3u);
    EXPECT(survival_consumption_register_cohort(&t.consumption, cohort) == 0, "register consumption");
    needs = survival_needs_get(&t.needs, 3u);
    needs->food_store = 0u;
    needs->water_store = 10u;

    counter.deaths = 0u;
    counter.cause = 0u;
    hook.emit = death_hook_emit;
    hook.user = &counter;
    survival_consumption_set_death_hook(&t.consumption, &hook);

    EXPECT(survival_consumption_advance(&t.consumption, 5) == 0, "advance");
    EXPECT(counter.deaths == 1u, "expected death");
    EXPECT(counter.cause == SURVIVAL_DEATH_CAUSE_STARVATION, "expected starvation cause");
    EXPECT(cohort->count == 0u, "cohort count not reduced");
    return 0;
}

static int test_production_action_completion(void)
{
    civ0a_test_context t;
    survival_production_action_input input;
    survival_production_refusal_code refusal;
    survival_needs_state* needs;

    civ0a_test_context_init(&t, 0);
    EXPECT(survival_cohort_register(&t.cohorts, 4u, 2u, 13u) == 0, "register cohort");
    needs = survival_needs_get(&t.needs, 4u);
    if (!needs) {
        survival_needs_register(&t.needs, 4u, 0);
        needs = survival_needs_get(&t.needs, 4u);
    }
    EXPECT(needs != 0, "needs missing");

    memset(&input, 0, sizeof(input));
    input.cohort_id = 4u;
    input.type = SURVIVAL_ACTION_GATHER_FOOD;
    input.start_tick = 0;
    input.duration_ticks = 10;
    input.output_food = 12u;
    input.provenance_ref = 77u;
    EXPECT(survival_production_schedule_action(&t.production, &input, &refusal, 0) == 0, "schedule action");
    EXPECT(refusal == SURVIVAL_REFUSAL_NONE, "unexpected refusal");

    EXPECT(survival_production_advance(&t.production, 10) == 0, "advance production");
    EXPECT(needs->food_store == 12u, "food not produced");
    EXPECT(needs->last_production_provenance == 77u, "provenance not recorded");
    return 0;
}

static int test_no_global_iteration(void)
{
    civ0a_test_context t;
    u32 i;
    survival_cohort* cohort;

    civ0a_test_context_init(&t, 0);
    for (i = 0u; i < 50u; ++i) {
        u64 id = 100u + i;
        EXPECT(survival_cohort_register(&t.cohorts, id, 1u, 20u) == 0, "register cohort");
        cohort = survival_cohort_find(&t.cohorts, id);
        if (i == 0u) {
            cohort->next_due_tick = 5;
        } else {
            cohort->next_due_tick = 1000;
        }
        EXPECT(survival_consumption_register_cohort(&t.consumption, cohort) == 0, "register consumption");
    }
    EXPECT(survival_consumption_advance(&t.consumption, 5) == 0, "advance consumption");
    EXPECT(t.consumption.processed_last == 1u, "processed unexpected cohorts");
    return 0;
}

int main(void)
{
    if (test_consumption_determinism() != 0) return 1;
    if (test_batch_vs_step_equivalence() != 0) return 1;
    if (test_starvation_death_trigger() != 0) return 1;
    if (test_production_action_completion() != 0) return 1;
    if (test_no_global_iteration() != 0) return 1;
    return 0;
}
