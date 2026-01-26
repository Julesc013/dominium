/*
CIV2 governance tests.
*/
#include "dominium/rules/governance/enforcement_capacity.h"
#include "dominium/rules/governance/jurisdiction_model.h"
#include "dominium/rules/governance/legitimacy_model.h"
#include "dominium/rules/governance/org_governance_binding.h"
#include "dominium/rules/governance/policy_model.h"
#include "dominium/rules/governance/policy_scheduler.h"

#include <stdio.h>
#include <string.h>

#define EXPECT(cond, msg) do { \
    if (!(cond)) { \
        fprintf(stderr, "FAIL: %s\n", msg); \
        return 1; \
    } \
} while (0)

static int test_jurisdiction_determinism(void)
{
    jurisdiction_record storage_a[4];
    jurisdiction_record storage_b[4];
    jurisdiction_registry a;
    jurisdiction_registry b;

    jurisdiction_registry_init(&a, storage_a, 4u);
    jurisdiction_registry_init(&b, storage_b, 4u);

    EXPECT(jurisdiction_register(&a, 2u, 10u, 1u, 1u) == 0, "reg a2");
    EXPECT(jurisdiction_register(&a, 1u, 10u, 1u, 1u) == 0, "reg a1");
    EXPECT(jurisdiction_register(&b, 1u, 10u, 1u, 1u) == 0, "reg b1");
    EXPECT(jurisdiction_register(&b, 2u, 10u, 1u, 1u) == 0, "reg b2");

    EXPECT(a.count == b.count, "jurisdiction count mismatch");
    EXPECT(a.records[0].jurisdiction_id == b.records[0].jurisdiction_id, "order mismatch 0");
    EXPECT(a.records[1].jurisdiction_id == b.records[1].jurisdiction_id, "order mismatch 1");
    return 0;
}

static int test_next_due_tick_enforcement(void)
{
    policy_record policies[4];
    policy_registry policy_reg;
    jurisdiction_record juris_storage[2];
    jurisdiction_registry juris_reg;
    legitimacy_state legit_storage[2];
    legitimacy_registry legit_reg;
    enforcement_capacity cap_storage[2];
    enforcement_capacity_registry cap_reg;
    dom_time_event events[16];
    dg_due_entry entries[4];
    policy_due_user users[4];
    policy_scheduler sched;
    policy_record p1;
    policy_record p2;
    policy_record p3;

    policy_registry_init(&policy_reg, policies, 4u);
    jurisdiction_registry_init(&juris_reg, juris_storage, 2u);
    legitimacy_registry_init(&legit_reg, legit_storage, 2u);
    enforcement_capacity_registry_init(&cap_reg, cap_storage, 2u);

    EXPECT(jurisdiction_register(&juris_reg, 1u, 1u, 1u, 1u) == 0, "juris register");
    EXPECT(legitimacy_register(&legit_reg, 10u, 800u, 1000u, 700u, 400u, 200u) == 0, "legit register");
    EXPECT(enforcement_capacity_register(&cap_reg, 20u, 5u, 1u, 1u, 0u) == 0, "cap register");
    EXPECT(jurisdiction_set_refs(&juris_reg, 1u, 10u, 20u) == 0, "set refs");

    memset(&p1, 0, sizeof(p1));
    p1.policy_id = 1u;
    p1.jurisdiction_id = 1u;
    p1.type = POLICY_TAXATION;
    p1.schedule.start_act = 5u;
    p1.schedule.interval_act = 10u;
    p1.legitimacy_min = 100u;
    p1.capacity_min = 1u;
    EXPECT(policy_register(&policy_reg, &p1) == 0, "policy p1");

    memset(&p2, 0, sizeof(p2));
    p2.policy_id = 2u;
    p2.jurisdiction_id = 1u;
    p2.type = POLICY_CURFEW;
    p2.schedule.start_act = 100u;
    p2.schedule.interval_act = 10u;
    p2.legitimacy_min = 100u;
    p2.capacity_min = 1u;
    EXPECT(policy_register(&policy_reg, &p2) == 0, "policy p2");

    memset(&p3, 0, sizeof(p3));
    p3.policy_id = 3u;
    p3.jurisdiction_id = 1u;
    p3.type = POLICY_PROPERTY_ENFORCEMENT;
    p3.schedule.start_act = 1000u;
    p3.schedule.interval_act = 10u;
    p3.legitimacy_min = 100u;
    p3.capacity_min = 1u;
    EXPECT(policy_register(&policy_reg, &p3) == 0, "policy p3");

    EXPECT(policy_scheduler_init(&sched, events, 16u, entries, users, 4u, 0u,
                                 &policy_reg, &juris_reg, &legit_reg, &cap_reg) == 0,
           "scheduler init");
    EXPECT(policy_scheduler_register(&sched, &policy_reg.policies[0]) == 0, "register p1");
    EXPECT(policy_scheduler_register(&sched, &policy_reg.policies[1]) == 0, "register p2");
    EXPECT(policy_scheduler_register(&sched, &policy_reg.policies[2]) == 0, "register p3");

    EXPECT(policy_scheduler_advance(&sched, 5u) == 0, "advance to due");
    EXPECT(sched.processed_last == 1u, "processed unexpected policies");
    return 0;
}

static int test_legitimacy_batch_equivalence(void)
{
    legitimacy_state states_step[2];
    legitimacy_state states_batch[2];
    legitimacy_registry registry_step;
    legitimacy_registry registry_batch;
    legitimacy_scheduler step;
    legitimacy_scheduler batch;
    legitimacy_event events_step[8];
    legitimacy_event events_batch[8];
    dom_time_event due_events_step[16];
    dom_time_event due_events_batch[16];
    dg_due_entry due_entries_step[8];
    dg_due_entry due_entries_batch[8];
    legitimacy_due_user due_users_step[8];
    legitimacy_due_user due_users_batch[8];

    legitimacy_registry_init(&registry_step, states_step, 2u);
    legitimacy_registry_init(&registry_batch, states_batch, 2u);
    EXPECT(legitimacy_register(&registry_step, 1u, 500u, 1000u, 700u, 400u, 200u) == 0, "legit reg step");
    EXPECT(legitimacy_register(&registry_batch, 1u, 500u, 1000u, 700u, 400u, 200u) == 0, "legit reg batch");

    EXPECT(legitimacy_scheduler_init(&step, due_events_step, 16u, due_entries_step,
                                     due_users_step, 8u, 0u, events_step, 8u, &registry_step, 1u) == 0,
           "step scheduler init");
    EXPECT(legitimacy_scheduler_init(&batch, due_events_batch, 16u, due_entries_batch,
                                     due_users_batch, 8u, 0u, events_batch, 8u, &registry_batch, 1u) == 0,
           "batch scheduler init");

    EXPECT(legitimacy_schedule_event(&step, 1u, 50, 5u) == 0, "step event 1");
    EXPECT(legitimacy_schedule_event(&step, 1u, -20, 10u) == 0, "step event 2");
    EXPECT(legitimacy_schedule_event(&batch, 1u, 50, 5u) == 0, "batch event 1");
    EXPECT(legitimacy_schedule_event(&batch, 1u, -20, 10u) == 0, "batch event 2");

    EXPECT(legitimacy_scheduler_advance(&step, 5u) == 0, "step advance 5");
    EXPECT(legitimacy_scheduler_advance(&step, 10u) == 0, "step advance 10");
    EXPECT(legitimacy_scheduler_advance(&batch, 10u) == 0, "batch advance 10");

    EXPECT(registry_step.states[0].value == registry_batch.states[0].value, "batch equivalence mismatch");
    EXPECT(registry_step.states[0].value == 530u, "legitimacy value mismatch");
    return 0;
}

static int test_policy_schedule_determinism(void)
{
    policy_record policy;
    memset(&policy, 0, sizeof(policy));
    policy.policy_id = 7u;
    policy.schedule.start_act = 5u;
    policy.schedule.interval_act = 10u;
    EXPECT(policy_next_due(&policy, 0u) == 5u, "next due before start");
    policy.next_due_tick = 5u;
    EXPECT(policy_next_due(&policy, 6u) == 5u, "next due uses cached");
    policy.next_due_tick = DG_DUE_TICK_NONE;
    EXPECT(policy_next_due(&policy, 16u) == 25u, "next due interval");
    return 0;
}

static int test_standard_resolution_order(void)
{
    standard_resolution_context ctx;
    memset(&ctx, 0, sizeof(ctx));
    ctx.explicit_standard_id = 11u;
    ctx.org_standard_id = 22u;
    ctx.jurisdiction_standard_id = 33u;
    ctx.personal_standard_id = 44u;
    ctx.fallback_standard_id = 55u;
    EXPECT(governance_resolve_standard(&ctx) == 11u, "explicit not preferred");
    ctx.explicit_standard_id = 0u;
    EXPECT(governance_resolve_standard(&ctx) == 22u, "org not preferred");
    ctx.org_standard_id = 0u;
    EXPECT(governance_resolve_standard(&ctx) == 33u, "jurisdiction not preferred");
    ctx.jurisdiction_standard_id = 0u;
    EXPECT(governance_resolve_standard(&ctx) == 44u, "personal not preferred");
    ctx.personal_standard_id = 0u;
    EXPECT(governance_resolve_standard(&ctx) == 55u, "fallback not used");
    return 0;
}

static int test_epistemic_policy_unknown(void)
{
    u64 known_ids[2] = { 3u, 5u };
    governance_epistemic_set set;
    set.known_policy_ids = known_ids;
    set.count = 2u;
    EXPECT(policy_epistemic_knows(&set, 3u) == 1, "known policy missing");
    EXPECT(policy_epistemic_knows(&set, 4u) == 0, "unknown policy reported");
    return 0;
}

int main(void)
{
    if (test_jurisdiction_determinism() != 0) return 1;
    if (test_next_due_tick_enforcement() != 0) return 1;
    if (test_legitimacy_batch_equivalence() != 0) return 1;
    if (test_policy_schedule_determinism() != 0) return 1;
    if (test_standard_resolution_order() != 0) return 1;
    if (test_epistemic_policy_unknown() != 0) return 1;
    return 0;
}
