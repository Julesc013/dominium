/*
LIFE birth pipeline tests (LIFE3).
*/
#include "dominium/life/birth_pipeline.h"
#include "dominium/life/lineage.h"

#include <stdio.h>
#include <string.h>

#define EXPECT(cond, msg) do { \
    if (!(cond)) { \
        fprintf(stderr, "FAIL: %s\n", msg); \
        return 1; \
    } \
} while (0)

typedef struct life_birth_test_context {
    life_gestation_state gestation_storage[8];
    life_birth_event birth_storage[8];
    life_lineage_record lineage_storage[8];
    life_cohort_entry cohort_storage[8];
    life_person_record person_storage[8];
    life_body_record body_storage[8];
    life_audit_entry audit_storage[16];
    dom_time_event due_event_storage[16];
    dg_due_entry due_entry_storage[8];
    life_birth_due_user due_user_storage[8];

    life_gestation_registry gestations;
    life_birth_event_list births;
    life_lineage_registry lineage;
    life_cohort_registry cohorts;
    life_person_registry persons;
    life_body_registry bodies;
    life_audit_log audit_log;
    life_id_gen person_ids;
    life_id_gen body_ids;
    life_birth_scheduler scheduler;
    life_birth_context ctx;
    life_reproduction_rules rules;
} life_birth_test_context;

static void life_birth_test_init(life_birth_test_context* t,
                                 dom_act_time_t start_tick,
                                 dom_act_time_t gestation_ticks)
{
    memset(t, 0, sizeof(*t));
    life_gestation_registry_init(&t->gestations, t->gestation_storage, 8u, 1u);
    life_birth_event_list_init(&t->births, t->birth_storage, 8u, 1u);
    life_lineage_registry_init(&t->lineage, t->lineage_storage, 8u);
    life_cohort_registry_init(&t->cohorts, t->cohort_storage, 8u);
    life_person_registry_init(&t->persons, t->person_storage, 8u);
    life_body_registry_init(&t->bodies, t->body_storage, 8u);
    life_audit_log_init(&t->audit_log, t->audit_storage, 16u, 1u);
    life_id_gen_init(&t->person_ids, 100u);
    life_id_gen_init(&t->body_ids, 200u);

    t->rules.min_parents = 1u;
    t->rules.max_parents = 2u;
    t->rules.gestation_ticks = gestation_ticks;
    t->rules.allow_unknown_parents = 1u;

    (void)life_birth_scheduler_init(&t->scheduler,
                                    t->due_event_storage,
                                    16u,
                                    t->due_entry_storage,
                                    t->due_user_storage,
                                    8u,
                                    start_tick,
                                    &t->gestations,
                                    &t->births,
                                    &t->lineage,
                                    &t->cohorts,
                                    &t->persons,
                                    &t->bodies,
                                    &t->person_ids,
                                    &t->body_ids,
                                    &t->audit_log,
                                    0,
                                    0);

    t->ctx.gestations = &t->gestations;
    t->ctx.scheduler = &t->scheduler;
    t->ctx.births = &t->births;
    t->ctx.lineage = &t->lineage;
    t->ctx.cohorts = &t->cohorts;
    t->ctx.persons = &t->persons;
    t->ctx.bodies = &t->bodies;
    t->ctx.person_ids = &t->person_ids;
    t->ctx.body_ids = &t->body_ids;
    t->ctx.audit_log = &t->audit_log;
    t->ctx.reproduction_rules = &t->rules;
    t->ctx.authority = 0;
    t->ctx.notice_cb = 0;
    t->ctx.notice_user = 0;
}

static int test_deterministic_birth_schedule(void)
{
    life_birth_test_context a;
    life_birth_test_context b;
    life_birth_request req;
    life_birth_refusal_code refusal;
    u64 gestation_id_a = 0u;
    u64 gestation_id_b = 0u;
    life_gestation_state* gestation_a;
    life_gestation_state* gestation_b;

    life_birth_test_init(&a, 0, 10);
    life_birth_test_init(&b, 0, 10);

    memset(&req, 0, sizeof(req));
    req.parent_ids[0] = 1u;
    req.parent_ids[1] = 2u;
    req.parent_count = 2u;
    req.parent_certainty[0] = LIFE_LINEAGE_EXACT;
    req.parent_certainty[1] = LIFE_LINEAGE_EXACT;
    req.act_time = 5;
    req.needs.has_food = 1u;
    req.needs.has_shelter = 1u;

    EXPECT(life_request_birth(&a.ctx, &req, &refusal, &gestation_id_a) == 0, "birth A failed");
    EXPECT(refusal == LIFE_BIRTH_REFUSAL_NONE, "birth A refusal");
    EXPECT(life_request_birth(&b.ctx, &req, &refusal, &gestation_id_b) == 0, "birth B failed");
    EXPECT(refusal == LIFE_BIRTH_REFUSAL_NONE, "birth B refusal");

    gestation_a = life_gestation_find_by_id(&a.gestations, gestation_id_a);
    gestation_b = life_gestation_find_by_id(&b.gestations, gestation_id_b);
    EXPECT(gestation_a != 0 && gestation_b != 0, "gestation missing");
    EXPECT(gestation_a->expected_end_act == gestation_b->expected_end_act, "schedule mismatch");
    return 0;
}

static int test_resource_constraints(void)
{
    life_birth_test_context t;
    life_birth_request req;
    life_birth_refusal_code refusal;

    life_birth_test_init(&t, 0, 10);
    memset(&req, 0, sizeof(req));
    req.parent_ids[0] = 1u;
    req.parent_count = 1u;
    req.parent_certainty[0] = LIFE_LINEAGE_EXACT;
    req.act_time = 0;
    req.needs.has_food = 0u;
    req.needs.has_shelter = 1u;

    EXPECT(life_request_birth(&t.ctx, &req, &refusal, 0) == 1, "expected refusal");
    EXPECT(refusal == LIFE_BIRTH_REFUSAL_INSUFFICIENT_RESOURCES, "resource refusal mismatch");
    return 0;
}

static int test_lineage_determinism(void)
{
    life_birth_test_context a;
    life_birth_test_context b;
    life_birth_request req_a;
    life_birth_request req_b;
    life_birth_refusal_code refusal;

    life_birth_test_init(&a, 0, 5);
    life_birth_test_init(&b, 0, 5);

    memset(&req_a, 0, sizeof(req_a));
    req_a.parent_ids[0] = 9u;
    req_a.parent_ids[1] = 4u;
    req_a.parent_count = 2u;
    req_a.parent_certainty[0] = LIFE_LINEAGE_EXACT;
    req_a.parent_certainty[1] = LIFE_LINEAGE_EXACT;
    req_a.act_time = 10;
    req_a.needs.has_food = 1u;
    req_a.needs.has_shelter = 1u;

    req_b = req_a;
    req_b.parent_ids[0] = 4u;
    req_b.parent_ids[1] = 9u;

    EXPECT(life_request_birth(&a.ctx, &req_a, &refusal, 0) == 0, "birth A");
    EXPECT(life_request_birth(&b.ctx, &req_b, &refusal, 0) == 0, "birth B");

    EXPECT(life_birth_scheduler_advance(&a.scheduler, 20) == 0, "advance A");
    EXPECT(life_birth_scheduler_advance(&b.scheduler, 20) == 0, "advance B");

    EXPECT(a.lineage.count == 1u && b.lineage.count == 1u, "lineage count mismatch");
    EXPECT(a.lineage.records[0].parent_ids[0] == b.lineage.records[0].parent_ids[0], "lineage parent0 mismatch");
    EXPECT(a.lineage.records[0].parent_ids[1] == b.lineage.records[0].parent_ids[1], "lineage parent1 mismatch");
    return 0;
}

static int test_cohort_micro_invariance(void)
{
    life_birth_test_context t;
    life_birth_request req;
    life_birth_refusal_code refusal;
    u64 count_before = 0u;
    u64 count_after = 0u;

    life_birth_test_init(&t, 0, 3);
    memset(&req, 0, sizeof(req));
    req.parent_ids[0] = 1u;
    req.parent_count = 1u;
    req.parent_certainty[0] = LIFE_LINEAGE_EXACT;
    req.act_time = 0;
    req.needs.has_food = 1u;
    req.needs.has_shelter = 1u;
    req.cohort_id = 42u;
    req.micro_active = 0u;

    EXPECT(life_request_birth(&t.ctx, &req, &refusal, 0) == 0, "macro birth");
    EXPECT(life_birth_scheduler_advance(&t.scheduler, 10) == 0, "advance");
    EXPECT(life_cohort_get_count(&t.cohorts, 42u, &count_before) == 1, "cohort count missing");
    EXPECT(count_before == 1u, "cohort count unexpected");

    req.act_time = 20;
    req.micro_active = 1u;
    EXPECT(life_request_birth(&t.ctx, &req, &refusal, 0) == 0, "micro birth");
    EXPECT(life_birth_scheduler_advance(&t.scheduler, 30) == 0, "advance micro");
    EXPECT(life_cohort_get_count(&t.cohorts, 42u, &count_after) == 1, "cohort count missing after");
    EXPECT(count_after == count_before, "cohort count changed on micro birth");
    return 0;
}

static void birth_notice_counter(void* user, const life_birth_notice* notice)
{
    u32* count = (u32*)user;
    (void)notice;
    if (count) {
        *count += 1u;
    }
}

static int test_epistemic_gating(void)
{
    life_birth_test_context t;
    life_birth_request req;
    life_birth_refusal_code refusal;
    u32 notice_count = 0u;

    life_birth_test_init(&t, 0, 2);
    memset(&req, 0, sizeof(req));
    req.parent_ids[0] = 1u;
    req.parent_count = 1u;
    req.parent_certainty[0] = LIFE_LINEAGE_EXACT;
    req.act_time = 0;
    req.needs.has_food = 1u;
    req.needs.has_shelter = 1u;

    EXPECT(life_request_birth(&t.ctx, &req, &refusal, 0) == 0, "birth request");
    EXPECT(life_birth_scheduler_advance(&t.scheduler, 5) == 0, "advance");
    EXPECT(notice_count == 0u, "notice should not fire without callback");

    life_birth_test_init(&t, 0, 2);
    t.ctx.notice_cb = birth_notice_counter;
    t.ctx.notice_user = &notice_count;
    t.scheduler.notice_cb = birth_notice_counter;
    t.scheduler.notice_user = &notice_count;
    notice_count = 0u;
    EXPECT(life_request_birth(&t.ctx, &req, &refusal, 0) == 0, "birth request cb");
    EXPECT(life_birth_scheduler_advance(&t.scheduler, 5) == 0, "advance cb");
    EXPECT(notice_count == 1u, "notice callback expected");
    return 0;
}

static int test_batch_vs_step_equivalence(void)
{
    life_birth_test_context a;
    life_birth_test_context b;
    life_birth_request req;
    life_birth_refusal_code refusal;

    life_birth_test_init(&a, 0, 4);
    life_birth_test_init(&b, 0, 4);

    memset(&req, 0, sizeof(req));
    req.parent_ids[0] = 3u;
    req.parent_count = 1u;
    req.parent_certainty[0] = LIFE_LINEAGE_EXACT;
    req.act_time = 10;
    req.needs.has_food = 1u;
    req.needs.has_shelter = 1u;

    EXPECT(life_request_birth(&a.ctx, &req, &refusal, 0) == 0, "birth A");
    EXPECT(life_request_birth(&b.ctx, &req, &refusal, 0) == 0, "birth B");

    EXPECT(life_birth_scheduler_advance(&a.scheduler, 13) == 0, "advance A1");
    EXPECT(a.births.count == 0u, "unexpected birth A");
    EXPECT(life_birth_scheduler_advance(&a.scheduler, 20) == 0, "advance A2");

    EXPECT(life_birth_scheduler_advance(&b.scheduler, 20) == 0, "advance B");
    EXPECT(a.births.count == b.births.count, "birth count mismatch");
    EXPECT(a.births.count == 1u, "expected one birth");
    EXPECT(a.births.events[0].child_person_id == b.births.events[0].child_person_id,
           "birth child mismatch");
    return 0;
}

int main(void)
{
    if (test_deterministic_birth_schedule() != 0) return 1;
    if (test_resource_constraints() != 0) return 1;
    if (test_lineage_determinism() != 0) return 1;
    if (test_cohort_micro_invariance() != 0) return 1;
    if (test_epistemic_gating() != 0) return 1;
    if (test_batch_vs_step_equivalence() != 0) return 1;
    return 0;
}
