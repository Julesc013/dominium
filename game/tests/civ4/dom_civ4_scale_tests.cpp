/*
CIV4 scale and logistics tests.
*/
#include "dominium/rules/scale/domain_transitions.h"
#include "dominium/rules/scale/interplanetary_logistics.h"
#include "dominium/rules/scale/interstellar_logistics.h"
#include "dominium/rules/scale/scale_interest_binding.h"
#include "dominium/rules/scale/scale_time_warp.h"

#include <stdio.h>
#include <string.h>

#define EXPECT(cond, msg) do { \
    if (!(cond)) { \
        fprintf(stderr, "FAIL: %s\n", msg); \
        return 1; \
    } \
} while (0)

typedef struct arrival_log {
    u64 ids[8];
    u32 count;
} arrival_log;

static int log_interstellar_arrival(void* user, const scale_interstellar_flow* flow)
{
    arrival_log* log = (arrival_log*)user;
    if (!log || !flow) {
        return -1;
    }
    if (log->count < 8u) {
        log->ids[log->count++] = flow->flow_id;
    }
    return 0;
}

static int log_transition_arrival(void* user, const scale_domain_transition* transition)
{
    arrival_log* log = (arrival_log*)user;
    if (!log || !transition) {
        return -1;
    }
    if (log->count < 8u) {
        log->ids[log->count++] = transition->transition_id;
    }
    return 0;
}

static int test_deterministic_long_range_shipment(void)
{
    scale_interstellar_flow storage[4];
    scale_interstellar_registry reg;
    dom_time_event events[8];
    dg_due_entry entries[4];
    scale_interstellar_due_user users[4];
    scale_interstellar_scheduler sched;
    scale_interstellar_flow* f1;
    scale_interstellar_flow* f2;
    arrival_log log;
    scale_interstellar_hook hook;

    scale_interstellar_registry_init(&reg, storage, 4u);
    EXPECT(scale_interstellar_register(&reg, 2u, 1u, 9u, 100u, 5u, 10u, 50u, 0u, 0u) == 0,
           "flow 2 reg");
    EXPECT(scale_interstellar_register(&reg, 1u, 1u, 9u, 100u, 5u, 10u, 50u, 0u, 0u) == 0,
           "flow 1 reg");

    EXPECT(scale_interstellar_scheduler_init(&sched, events, 8u, entries, users, 4u, 0u, &reg) == 0,
           "sched init");
    f1 = scale_interstellar_find(&reg, 1u);
    f2 = scale_interstellar_find(&reg, 2u);
    EXPECT(f1 && f2, "find flows");
    EXPECT(scale_interstellar_scheduler_register(&sched, f2) == 0, "register f2");
    EXPECT(scale_interstellar_scheduler_register(&sched, f1) == 0, "register f1");

    memset(&log, 0, sizeof(log));
    hook.on_arrival = log_interstellar_arrival;
    hook.user = &log;
    scale_interstellar_set_hook(&sched, &hook);

    EXPECT(scale_interstellar_scheduler_advance(&sched, 50u) == 0, "advance");
    EXPECT(log.count == 2u, "arrival count");
    EXPECT(log.ids[0] == 1u, "arrival order 0");
    EXPECT(log.ids[1] == 2u, "arrival order 1");
    return 0;
}

static int test_batch_vs_step_equivalence(void)
{
    scale_interstellar_flow storage_step[2];
    scale_interstellar_flow storage_batch[2];
    scale_interstellar_registry reg_step;
    scale_interstellar_registry reg_batch;
    dom_time_event events_step[8];
    dom_time_event events_batch[8];
    dg_due_entry entries_step[2];
    dg_due_entry entries_batch[2];
    scale_interstellar_due_user users_step[2];
    scale_interstellar_due_user users_batch[2];
    scale_interstellar_scheduler sched_step;
    scale_interstellar_scheduler sched_batch;
    scale_interstellar_flow* flow_step;
    scale_interstellar_flow* flow_batch;
    dom_act_time_t arrival;

    scale_interstellar_registry_init(&reg_step, storage_step, 2u);
    scale_interstellar_registry_init(&reg_batch, storage_batch, 2u);
    arrival = scale_interstellar_compute_arrival(10u, 20u, 1u, 1u);
    EXPECT(scale_interstellar_register(&reg_step, 5u, 1u, 2u, 200u, 10u, 10u, arrival, 0u, 0u) == 0,
           "flow step reg");
    EXPECT(scale_interstellar_register(&reg_batch, 5u, 1u, 2u, 200u, 10u, 10u, arrival, 0u, 0u) == 0,
           "flow batch reg");

    EXPECT(scale_interstellar_scheduler_init(&sched_step, events_step, 8u, entries_step,
                                             users_step, 2u, 0u, &reg_step) == 0,
           "sched step init");
    EXPECT(scale_interstellar_scheduler_init(&sched_batch, events_batch, 8u, entries_batch,
                                             users_batch, 2u, 0u, &reg_batch) == 0,
           "sched batch init");
    flow_step = scale_interstellar_find(&reg_step, 5u);
    flow_batch = scale_interstellar_find(&reg_batch, 5u);
    EXPECT(flow_step && flow_batch, "find flow");
    EXPECT(scale_interstellar_scheduler_register(&sched_step, flow_step) == 0, "reg step");
    EXPECT(scale_interstellar_scheduler_register(&sched_batch, flow_batch) == 0, "reg batch");

    EXPECT(scale_interstellar_scheduler_advance(&sched_step, arrival - 1u) == 0, "step advance 1");
    EXPECT(flow_step->status == SCALE_FLOW_PENDING, "step pending");
    EXPECT(scale_interstellar_scheduler_advance(&sched_step, arrival) == 0, "step advance 2");
    EXPECT(flow_step->status == SCALE_FLOW_ARRIVED, "step arrived");
    EXPECT(scale_interstellar_scheduler_advance(&sched_batch, arrival) == 0, "batch advance");
    EXPECT(flow_batch->status == SCALE_FLOW_ARRIVED, "batch arrived");
    return 0;
}

static int test_interest_bound_refinement(void)
{
    scale_interest_binding bindings[4];
    scale_interest_registry reg;

    scale_interest_registry_init(&reg, bindings, 4u);
    EXPECT(scale_interest_register(&reg, 1u, 10u, 100u, 0u, 0u) == 0, "interest reg 1");
    EXPECT(scale_interest_domain_active(&reg, 10u, 1u) == 0, "interest inactive");
    EXPECT(scale_interest_set_strength(&reg, 1u, 5u) == 0, "set strength");
    EXPECT(scale_interest_should_refine(&reg, 10u, 3u) == 1, "refine expected");
    EXPECT(scale_interest_set_strength(&reg, 1u, 0u) == 0, "clear strength");
    EXPECT(scale_interest_domain_active(&reg, 10u, 1u) == 0, "inactive again");
    EXPECT(scale_interest_set_pinned(&reg, 1u, 1u) == 0, "pin");
    EXPECT(scale_interest_domain_active(&reg, 10u, 1u) == 1, "pin active");
    return 0;
}

static int test_time_warp_resolution(void)
{
    scale_time_warp_policy policy;
    u32 warp;
    memset(&policy, 0, sizeof(policy));
    policy.min_warp = 1u;
    policy.max_warp = 16u;
    policy.interest_cap = 4u;
    warp = scale_time_warp_resolve(&policy, 8u, 0);
    EXPECT(warp == 8u, "warp no interest");
    warp = scale_time_warp_resolve(&policy, 8u, 1);
    EXPECT(warp == 4u, "warp interest cap");
    warp = scale_time_warp_resolve(&policy, 0u, 0);
    EXPECT(warp == 1u, "warp default");
    return 0;
}

static int test_transition_handoff_order(void)
{
    scale_domain_transition storage[4];
    scale_transition_registry reg;
    dom_time_event events[8];
    dg_due_entry entries[4];
    scale_transition_due_user users[4];
    scale_transition_scheduler sched;
    scale_domain_transition* t1;
    scale_domain_transition* t2;
    arrival_log log;
    scale_transition_hook hook;

    scale_transition_registry_init(&reg, storage, 4u);
    EXPECT(scale_transition_register(&reg, 5u, 1u, 2u, 1u, 10u, 1u, 0u) == 0, "trans 5");
    EXPECT(scale_transition_register(&reg, 3u, 1u, 2u, 1u, 10u, 1u, 0u) == 0, "trans 3");

    EXPECT(scale_transition_scheduler_init(&sched, events, 8u, entries, users, 4u, 0u, &reg) == 0,
           "trans sched init");
    t1 = scale_transition_find(&reg, 3u);
    t2 = scale_transition_find(&reg, 5u);
    EXPECT(t1 && t2, "find transitions");
    EXPECT(scale_transition_scheduler_register(&sched, t2) == 0, "reg t2");
    EXPECT(scale_transition_scheduler_register(&sched, t1) == 0, "reg t1");

    memset(&log, 0, sizeof(log));
    hook.on_arrival = log_transition_arrival;
    hook.user = &log;
    scale_transition_set_hook(&sched, &hook);

    EXPECT(scale_transition_scheduler_advance(&sched, 10u) == 0, "trans advance");
    EXPECT(log.count == 2u, "trans arrival count");
    EXPECT(log.ids[0] == 3u, "trans order 0");
    EXPECT(log.ids[1] == 5u, "trans order 1");
    return 0;
}

int main(void)
{
    if (test_deterministic_long_range_shipment() != 0) return 1;
    if (test_batch_vs_step_equivalence() != 0) return 1;
    if (test_interest_bound_refinement() != 0) return 1;
    if (test_time_warp_resolution() != 0) return 1;
    if (test_transition_handoff_order() != 0) return 1;
    return 0;
}
