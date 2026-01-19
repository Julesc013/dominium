/*
AGENT1 goal evaluation and planning tests.
*/
#include "dominium/agents/agent_belief_update.h"
#include "dominium/agents/agent_evaluator.h"
#include "dominium/agents/agent_goal.h"
#include "dominium/agents/agent_planner.h"
#include "dominium/agents/agent_schedule.h"

#include <stdio.h>
#include <string.h>

#define EXPECT(cond, msg) do { \
    if (!(cond)) { \
        fprintf(stderr, "FAIL: %s\n", msg); \
        return 1; \
    } \
} while (0)

typedef struct schedule_counter {
    u32 count;
} schedule_counter;

static int agent_test_think(void* user, agent_schedule_entry* entry, dom_act_time_t now_act)
{
    schedule_counter* counter = (schedule_counter*)user;
    (void)entry;
    (void)now_act;
    if (counter) {
        counter->count += 1u;
    }
    return 0;
}

static void agent_seed_goal_registry(agent_goal_registry* reg,
                                     agent_goal* storage,
                                     u32 capacity)
{
    agent_goal_preconditions pre;
    agent_goal_registry_init(reg, storage, capacity, 1u);
    memset(&pre, 0, sizeof(pre));
    pre.required_capabilities = AGENT_CAP_MOVE;
    (void)agent_goal_register(reg, 10u, AGENT_GOAL_SURVIVE, 100u, &pre, 0u, 0u);
    pre.required_capabilities = AGENT_CAP_RESEARCH;
    (void)agent_goal_register(reg, 20u, AGENT_GOAL_RESEARCH, 200u, &pre, 0u, 0u);
}

static int test_goal_determinism(void)
{
    agent_goal goals_a[4];
    agent_goal goals_b[4];
    agent_goal_registry reg_a;
    agent_goal_registry reg_b;
    agent_context ctx;
    agent_goal_eval_result ra;
    agent_goal_eval_result rb;

    agent_seed_goal_registry(&reg_a, goals_a, 4u);
    agent_seed_goal_registry(&reg_b, goals_b, 4u);

    memset(&ctx, 0, sizeof(ctx));
    ctx.capability_mask = AGENT_CAP_MOVE | AGENT_CAP_RESEARCH;
    ctx.hunger_level = 800u;

    EXPECT(agent_evaluator_choose_goal(&reg_a, &ctx, 0u, &ra) == 0, "choose goal a");
    EXPECT(agent_evaluator_choose_goal(&reg_b, &ctx, 0u, &rb) == 0, "choose goal b");
    EXPECT(ra.goal && rb.goal, "goals should exist");
    EXPECT(ra.goal->goal_id == rb.goal->goal_id, "goal id mismatch");
    EXPECT(ra.computed_priority == rb.computed_priority, "priority mismatch");
    return 0;
}

static int test_bounded_planning(void)
{
    agent_goal goal;
    agent_goal_preconditions pre;
    agent_context ctx;
    agent_plan plan;
    agent_plan_options options;
    agent_refusal_code refusal;

    memset(&pre, 0, sizeof(pre));
    pre.required_capabilities = AGENT_CAP_MOVE;
    memset(&goal, 0, sizeof(goal));
    goal.goal_id = 5u;
    goal.type = AGENT_GOAL_SURVIVE;
    goal.base_priority = 500u;
    goal.preconditions = pre;

    memset(&ctx, 0, sizeof(ctx));
    ctx.capability_mask = AGENT_CAP_MOVE;
    ctx.knowledge_mask = AGENT_KNOW_RESOURCE;
    ctx.known_resource_ref = 99u;

    memset(&options, 0, sizeof(options));
    options.max_steps = 1u;
    options.plan_id = 100u;
    EXPECT(agent_planner_build(&goal, &ctx, &options, 0u, &plan, &refusal) != 0,
           "bounded plan should fail");
    EXPECT(refusal == AGENT_REFUSAL_GOAL_NOT_FEASIBLE, "expected bounded refusal");

    options.max_steps = 2u;
    EXPECT(agent_planner_build(&goal, &ctx, &options, 0u, &plan, &refusal) == 0,
           "bounded plan should pass");
    EXPECT(plan.step_count == 2u, "plan step count mismatch");
    return 0;
}

static int test_epistemic_behavior(void)
{
    agent_goal goal;
    agent_goal_preconditions pre;
    agent_context ctx;
    agent_plan plan;
    agent_plan_options options;
    agent_refusal_code refusal;
    agent_belief_state belief;
    agent_command_outcome outcome;

    memset(&pre, 0, sizeof(pre));
    pre.required_capabilities = AGENT_CAP_MOVE;
    memset(&goal, 0, sizeof(goal));
    goal.goal_id = 7u;
    goal.type = AGENT_GOAL_SURVIVE;
    goal.base_priority = 400u;
    goal.preconditions = pre;

    agent_belief_init(&belief, 1u, AGENT_KNOW_RESOURCE, 200u, 0u, 0u);

    memset(&ctx, 0, sizeof(ctx));
    ctx.capability_mask = AGENT_CAP_MOVE;
    ctx.knowledge_mask = belief.knowledge_mask;
    ctx.known_resource_ref = 55u;

    memset(&options, 0, sizeof(options));
    options.max_steps = 2u;
    options.plan_id = 200u;
    EXPECT(agent_planner_build(&goal, &ctx, &options, 0u, &plan, &refusal) == 0,
           "plan should succeed before belief update");

    memset(&outcome, 0, sizeof(outcome));
    outcome.command_type = AGENT_CMD_ACQUIRE;
    outcome.success = 0;
    outcome.refusal = AGENT_REFUSAL_INSUFFICIENT_KNOWLEDGE;
    outcome.knowledge_clear_mask = AGENT_KNOW_RESOURCE;
    EXPECT(agent_belief_apply_command_outcome(&belief, &outcome, 5u) == 0,
           "apply outcome");
    EXPECT((belief.knowledge_mask & AGENT_KNOW_RESOURCE) == 0u, "knowledge should clear");

    ctx.knowledge_mask = belief.knowledge_mask;
    EXPECT(agent_planner_build(&goal, &ctx, &options, 6u, &plan, &refusal) != 0,
           "plan should fail after knowledge loss");
    EXPECT(refusal == AGENT_REFUSAL_INSUFFICIENT_KNOWLEDGE, "expected knowledge refusal");
    return 0;
}

static int test_schedule_batch_vs_step(void)
{
    agent_schedule step;
    agent_schedule batch;
    dom_time_event step_events[16];
    dom_time_event batch_events[16];
    dg_due_entry step_due_entries[8];
    dg_due_entry batch_due_entries[8];
    agent_schedule_due_user step_due_users[8];
    agent_schedule_due_user batch_due_users[8];
    agent_schedule_entry step_entries[4];
    agent_schedule_entry batch_entries[4];
    schedule_counter step_counter;
    schedule_counter batch_counter;
    agent_schedule_callbacks step_cb;
    agent_schedule_callbacks batch_cb;
    agent_schedule_entry* step_a;
    agent_schedule_entry* step_b;
    agent_schedule_entry* batch_a;
    agent_schedule_entry* batch_b;

    memset(&step_counter, 0, sizeof(step_counter));
    memset(&batch_counter, 0, sizeof(batch_counter));
    memset(&step_cb, 0, sizeof(step_cb));
    memset(&batch_cb, 0, sizeof(batch_cb));
    step_cb.on_think = agent_test_think;
    step_cb.user = &step_counter;
    batch_cb.on_think = agent_test_think;
    batch_cb.user = &batch_counter;

    EXPECT(agent_schedule_init(&step, step_events, 16u, step_due_entries, step_due_users, 8u,
                               0u, step_entries, 4u) == 0, "init step sched");
    EXPECT(agent_schedule_init(&batch, batch_events, 16u, batch_due_entries, batch_due_users, 8u,
                               0u, batch_entries, 4u) == 0, "init batch sched");
    agent_schedule_set_callbacks(&step, &step_cb);
    agent_schedule_set_callbacks(&batch, &batch_cb);

    EXPECT(agent_schedule_register(&step, 1u, 5u, 5u) == 0, "register step agent 1");
    EXPECT(agent_schedule_register(&step, 2u, 5u, 5u) == 0, "register step agent 2");
    EXPECT(agent_schedule_register(&batch, 1u, 5u, 5u) == 0, "register batch agent 1");
    EXPECT(agent_schedule_register(&batch, 2u, 5u, 5u) == 0, "register batch agent 2");

    EXPECT(agent_schedule_advance(&step, 5u) == 0, "advance step 5");
    EXPECT(agent_schedule_advance(&step, 10u) == 0, "advance step 10");
    EXPECT(agent_schedule_advance(&batch, 10u) == 0, "advance batch 10");

    step_a = agent_schedule_find(&step, 1u);
    step_b = agent_schedule_find(&step, 2u);
    batch_a = agent_schedule_find(&batch, 1u);
    batch_b = agent_schedule_find(&batch, 2u);

    EXPECT(step_a && step_b && batch_a && batch_b, "entries missing");
    EXPECT(step_a->next_think_act == batch_a->next_think_act, "agent 1 next mismatch");
    EXPECT(step_b->next_think_act == batch_b->next_think_act, "agent 2 next mismatch");
    EXPECT(step_counter.count == batch_counter.count, "processed count mismatch");
    EXPECT(step_counter.count == 4u, "expected two agents processed twice");
    return 0;
}

static int test_agent_absence(void)
{
    agent_schedule sched;
    dom_time_event events[8];
    dg_due_entry due_entries[4];
    agent_schedule_due_user due_users[4];
    agent_schedule_entry schedule_entries[2];
    EXPECT(agent_schedule_init(&sched, events, 8u, due_entries, due_users, 4u, 0u,
                               schedule_entries, 2u) == 0, "init schedule");
    EXPECT(agent_schedule_advance(&sched, 10u) == 0, "advance empty schedule");
    EXPECT(agent_schedule_next_due(&sched) == DG_DUE_TICK_NONE, "empty next due should be none");
    EXPECT(sched.processed_last == 0u, "processed count should be zero");
    return 0;
}

int main(void)
{
    if (test_goal_determinism() != 0) return 1;
    if (test_bounded_planning() != 0) return 1;
    if (test_epistemic_behavior() != 0) return 1;
    if (test_schedule_batch_vs_step() != 0) return 1;
    if (test_agent_absence() != 0) return 1;
    return 0;
}
