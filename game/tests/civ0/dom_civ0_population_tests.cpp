/*
CIV0 population genesis tests.
*/
#include "dominium/rules/population/cohort_types.h"
#include "dominium/rules/population/demographics.h"
#include "dominium/rules/population/household_model.h"
#include "dominium/rules/population/migration_model.h"
#include "dominium/rules/population/population_projections.h"
#include "dominium/rules/population/population_scheduler.h"

#include <stdio.h>
#include <string.h>

#define EXPECT(cond, msg) do { \
    if (!(cond)) { \
        fprintf(stderr, "FAIL: %s\n", msg); \
        return 1; \
    } \
} while (0)

typedef struct civ0_test_context {
    population_cohort_state cohorts_storage[64];
    population_migration_flow flows_storage[64];
    dom_time_event due_events[128];
    dg_due_entry due_entries[64];
    population_due_user due_users[64];

    population_cohort_registry cohorts;
    population_migration_registry migrations;
    population_scheduler scheduler;
} civ0_test_context;

static void civ0_context_init(civ0_test_context* t, dom_act_time_t start_tick)
{
    memset(t, 0, sizeof(*t));
    population_cohort_registry_init(&t->cohorts, t->cohorts_storage, 64u);
    population_migration_registry_init(&t->migrations, t->flows_storage, 64u, 1u);
    (void)population_scheduler_init(&t->scheduler,
                                    t->due_events,
                                    128u,
                                    t->due_entries,
                                    t->due_users,
                                    64u,
                                    start_tick,
                                    &t->cohorts,
                                    &t->migrations);
}

static int test_cohort_ordering_determinism(void)
{
    population_cohort_key keys[3];
    population_refusal_code refusal;
    population_cohort_registry a;
    population_cohort_registry b;
    population_cohort_state storage_a[8];
    population_cohort_state storage_b[8];
    u32 i;

    memset(keys, 0, sizeof(keys));
    keys[0].body_id = 1u;
    keys[0].region_id = 10u;
    keys[1].body_id = 2u;
    keys[1].region_id = 20u;
    keys[2].body_id = 3u;
    keys[2].region_id = 30u;

    population_cohort_registry_init(&a, storage_a, 8u);
    population_cohort_registry_init(&b, storage_b, 8u);

    EXPECT(population_cohort_register(&a, &keys[0], 5u, 0u) == 0, "register a0");
    EXPECT(population_cohort_register(&a, &keys[1], 6u, 0u) == 0, "register a1");
    EXPECT(population_cohort_register(&a, &keys[2], 7u, 0u) == 0, "register a2");

    EXPECT(population_cohort_register(&b, &keys[2], 7u, 0u) == 0, "register b2");
    EXPECT(population_cohort_register(&b, &keys[0], 5u, 0u) == 0, "register b0");
    EXPECT(population_cohort_register(&b, &keys[1], 6u, 0u) == 0, "register b1");

    EXPECT(a.count == b.count, "cohort count mismatch");
    for (i = 0u; i < a.count; ++i) {
        EXPECT(a.cohorts[i].cohort_id == b.cohorts[i].cohort_id, "cohort order mismatch");
        EXPECT(population_demographics_validate(&a.cohorts[i], &refusal) == 0, "demographics A invalid");
        EXPECT(population_demographics_validate(&b.cohorts[i], &refusal) == 0, "demographics B invalid");
    }
    return 0;
}

typedef struct cohort_hook_ctx {
    u32 interval;
} cohort_hook_ctx;

static dom_act_time_t cohort_hook_process(void* user,
                                          population_cohort_state* cohort,
                                          dom_act_time_t due_tick)
{
    cohort_hook_ctx* ctx = (cohort_hook_ctx*)user;
    population_refusal_code refusal = POP_REFUSAL_NONE;
    (void)population_demographics_apply_delta(cohort, 1, (u64)due_tick, &refusal);
    return due_tick + (ctx ? ctx->interval : 1u);
}

static int test_batch_vs_step_equivalence(void)
{
    civ0_test_context step;
    civ0_test_context batch;
    population_cohort_state* cs;
    population_cohort_state* cb;
    population_cohort_key key;
    dom_act_time_t tick;
    cohort_hook_ctx hook_ctx;
    population_cohort_due_hook hook;

    memset(&key, 0, sizeof(key));
    key.body_id = 11u;
    key.region_id = 22u;

    civ0_context_init(&step, 0);
    civ0_context_init(&batch, 0);

    EXPECT(population_cohort_register(&step.cohorts, &key, 2u, 0u) == 0, "register step cohort");
    EXPECT(population_cohort_register(&batch.cohorts, &key, 2u, 0u) == 0, "register batch cohort");
    cs = population_cohort_find_by_key(&step.cohorts, &key);
    cb = population_cohort_find_by_key(&batch.cohorts, &key);
    EXPECT(cs && cb, "cohort lookup");
    cs->next_due_tick = 5;
    cb->next_due_tick = 5;
    EXPECT(population_scheduler_register_cohort(&step.scheduler, cs) == 0, "register step scheduler");
    EXPECT(population_scheduler_register_cohort(&batch.scheduler, cb) == 0, "register batch scheduler");

    hook_ctx.interval = 5u;
    hook.process = cohort_hook_process;
    hook.user = &hook_ctx;
    population_scheduler_set_cohort_hook(&step.scheduler, &hook);
    population_scheduler_set_cohort_hook(&batch.scheduler, &hook);

    for (tick = 5; tick <= 50; tick += 5) {
        EXPECT(population_scheduler_advance(&step.scheduler, tick) == 0, "step advance");
    }
    EXPECT(population_scheduler_advance(&batch.scheduler, 50) == 0, "batch advance");

    EXPECT(cs->count == cb->count, "batch vs step count mismatch");
    EXPECT(cs->next_due_tick == cb->next_due_tick, "batch vs step next due mismatch");
    return 0;
}

static int test_household_boundedness(void)
{
    population_household_registry reg;
    population_household storage[2];
    population_refusal_code refusal;
    u32 i;
    population_household* h;

    population_household_registry_init(&reg, storage, 2u);
    EXPECT(population_household_register(&reg, 100u, 200u, 300u) == 0, "register household");
    for (i = 0u; i < POPULATION_HOUSEHOLD_MAX_MEMBERS; ++i) {
        EXPECT(population_household_add_member(&reg, 100u, 1000u + i, &refusal) == 0, "add member");
    }
    h = population_household_find(&reg, 100u);
    EXPECT(h && h->member_count == POPULATION_HOUSEHOLD_MAX_MEMBERS, "member count max");
    EXPECT(population_household_add_member(&reg, 100u, 9999u, &refusal) != 0, "overflow member");
    EXPECT(refusal == POP_REFUSAL_HOUSEHOLD_TOO_LARGE, "expected household too large refusal");
    EXPECT(h->member_count == POPULATION_HOUSEHOLD_MAX_MEMBERS, "member count changed");
    return 0;
}

static int test_migration_determinism(void)
{
    civ0_test_context a;
    civ0_test_context b;
    population_cohort_key src_key;
    population_cohort_key dst_key;
    population_migration_input input;
    population_refusal_code refusal;
    population_cohort_state* asrc;
    population_cohort_state* adst;
    population_cohort_state* bsrc;
    population_cohort_state* bdst;

    memset(&src_key, 0, sizeof(src_key));
    memset(&dst_key, 0, sizeof(dst_key));
    src_key.body_id = 1u;
    src_key.region_id = 10u;
    dst_key.body_id = 2u;
    dst_key.region_id = 20u;

    civ0_context_init(&a, 0);
    civ0_context_init(&b, 0);
    EXPECT(population_cohort_register(&a.cohorts, &src_key, 10u, 0u) == 0, "register a src");
    EXPECT(population_cohort_register(&a.cohorts, &dst_key, 2u, 0u) == 0, "register a dst");
    EXPECT(population_cohort_register(&b.cohorts, &src_key, 10u, 0u) == 0, "register b src");
    EXPECT(population_cohort_register(&b.cohorts, &dst_key, 2u, 0u) == 0, "register b dst");

    memset(&input, 0, sizeof(input));
    input.src_key = src_key;
    input.dst_key = dst_key;
    input.count_delta = 3u;
    input.start_act = 0;
    input.arrival_act = 10;
    input.cause_code = 1u;

    EXPECT(population_migration_schedule(&a.migrations, &input, &refusal) == 0, "schedule a");
    EXPECT(population_migration_schedule(&b.migrations, &input, &refusal) == 0, "schedule b");

    EXPECT(population_scheduler_register_migration(&a.scheduler, &a.migrations.flows[0]) == 0, "register a migration");
    EXPECT(population_scheduler_register_migration(&b.scheduler, &b.migrations.flows[0]) == 0, "register b migration");
    EXPECT(population_scheduler_advance(&a.scheduler, 10) == 0, "advance a");
    EXPECT(population_scheduler_advance(&b.scheduler, 10) == 0, "advance b");

    asrc = population_cohort_find_by_key(&a.cohorts, &src_key);
    adst = population_cohort_find_by_key(&a.cohorts, &dst_key);
    bsrc = population_cohort_find_by_key(&b.cohorts, &src_key);
    bdst = population_cohort_find_by_key(&b.cohorts, &dst_key);
    EXPECT(asrc && adst && bsrc && bdst, "cohort lookup");
    EXPECT(asrc->count == bsrc->count, "migration src count mismatch");
    EXPECT(adst->count == bdst->count, "migration dst count mismatch");
    EXPECT(asrc->provenance_summary_hash == bsrc->provenance_summary_hash, "src provenance mismatch");
    EXPECT(adst->provenance_summary_hash == bdst->provenance_summary_hash, "dst provenance mismatch");
    return 0;
}

static int test_no_global_iteration(void)
{
    civ0_test_context t;
    population_cohort_key src_key;
    population_cohort_key dst_key;
    population_migration_input input;
    population_refusal_code refusal;
    u32 i;

    civ0_context_init(&t, 0);
    memset(&src_key, 0, sizeof(src_key));
    memset(&dst_key, 0, sizeof(dst_key));
    src_key.body_id = 10u;
    src_key.region_id = 1u;
    dst_key.body_id = 10u;
    dst_key.region_id = 2u;
    EXPECT(population_cohort_register(&t.cohorts, &src_key, 50u, 0u) == 0, "register src");
    EXPECT(population_cohort_register(&t.cohorts, &dst_key, 0u, 0u) == 0, "register dst");

    for (i = 0u; i < 10u; ++i) {
        memset(&input, 0, sizeof(input));
        input.src_key = src_key;
        input.dst_key = dst_key;
        input.count_delta = 1u;
        input.start_act = 0;
        input.arrival_act = (i == 0u) ? 5 : 1000;
        input.cause_code = 1u;
        input.flow_id = 1000u + (u64)i;
        EXPECT(population_migration_schedule(&t.migrations, &input, &refusal) == 0, "schedule migration");
        {
            population_migration_flow* flow = population_migration_find(&t.migrations, input.flow_id);
            EXPECT(flow != 0, "migration lookup");
            EXPECT(population_scheduler_register_migration(&t.scheduler, flow) == 0, "register migration");
        }
    }
    EXPECT(population_scheduler_advance(&t.scheduler, 5) == 0, "advance to due");
    EXPECT(t.scheduler.processed_last == 1u, "processed unexpected migrations");
    return 0;
}

static int test_epistemic_projection_unknown(void)
{
    population_projection_registry reg;
    population_projection storage[8];
    population_projection view;
    u64 cohort_id = 55u;

    population_projection_registry_init(&reg, storage, 8u);
    EXPECT(population_projection_get(&reg, cohort_id, &view) == 0, "projection get");
    EXPECT(view.is_known == 0, "expected unknown projection");
    EXPECT(population_projection_report(&reg, cohort_id, 10u, 12u, 5) == 0, "projection report");
    EXPECT(population_projection_get(&reg, cohort_id, &view) == 0, "projection get after report");
    EXPECT(view.is_known == 1, "expected known projection");
    EXPECT(view.known_min == 10u, "known min mismatch");
    EXPECT(view.known_max == 12u, "known max mismatch");
    return 0;
}

int main(void)
{
    if (test_cohort_ordering_determinism() != 0) return 1;
    if (test_batch_vs_step_equivalence() != 0) return 1;
    if (test_household_boundedness() != 0) return 1;
    if (test_migration_determinism() != 0) return 1;
    if (test_no_global_iteration() != 0) return 1;
    if (test_epistemic_projection_unknown() != 0) return 1;
    return 0;
}
