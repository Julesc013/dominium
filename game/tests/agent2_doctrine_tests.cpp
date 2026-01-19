/*
AGENT2 doctrine, roles, and delegation tests.
*/
#include "dominium/agents/agent_evaluator.h"
#include "dominium/agents/agent_goal.h"
#include "dominium/agents/agent_planner.h"
#include "dominium/agents/agent_role.h"
#include "dominium/agents/delegation.h"
#include "dominium/agents/doctrine.h"
#include "dominium/agents/doctrine_scheduler.h"

#include <stdio.h>
#include <string.h>

#define EXPECT(cond, msg) do { \
    if (!(cond)) { \
        fprintf(stderr, "FAIL: %s\n", msg); \
        return 1; \
    } \
} while (0)

static void seed_goal(agent_goal_registry* reg,
                      u64 id,
                      u32 type,
                      u32 priority,
                      u32 caps)
{
    agent_goal_preconditions pre;
    memset(&pre, 0, sizeof(pre));
    pre.required_capabilities = caps;
    (void)agent_goal_register(reg, id, type, priority, &pre, 0u, 0u);
}

static void seed_doctrine(agent_doctrine* doctrine,
                          u64 id,
                          u32 allowed,
                          u32 forbidden)
{
    memset(doctrine, 0, sizeof(*doctrine));
    doctrine->doctrine_id = id;
    doctrine->scope = DOCTRINE_SCOPE_AGENT;
    doctrine->allowed_goal_types = allowed;
    doctrine->forbidden_goal_types = forbidden;
}

static int test_doctrine_filtering_determinism(void)
{
    agent_goal goals_a[4];
    agent_goal goals_b[4];
    agent_goal_registry reg_a;
    agent_goal_registry reg_b;
    agent_doctrine doctrines_a[2];
    agent_doctrine doctrines_b[2];
    agent_doctrine_registry docs_a;
    agent_doctrine_registry docs_b;
    agent_context ctx;
    agent_goal_eval_result ra;
    agent_goal_eval_result rb;
    agent_doctrine doc;

    agent_goal_registry_init(&reg_a, goals_a, 4u, 1u);
    agent_goal_registry_init(&reg_b, goals_b, 4u, 1u);
    seed_goal(&reg_a, 1u, AGENT_GOAL_SURVIVE, 100u, 0u);
    seed_goal(&reg_a, 2u, AGENT_GOAL_RESEARCH, 200u, AGENT_CAP_RESEARCH);
    seed_goal(&reg_a, 3u, AGENT_GOAL_TRADE, 150u, 0u);
    seed_goal(&reg_b, 1u, AGENT_GOAL_SURVIVE, 100u, 0u);
    seed_goal(&reg_b, 2u, AGENT_GOAL_RESEARCH, 200u, AGENT_CAP_RESEARCH);
    seed_goal(&reg_b, 3u, AGENT_GOAL_TRADE, 150u, 0u);

    agent_doctrine_registry_init(&docs_a, doctrines_a, 2u);
    agent_doctrine_registry_init(&docs_b, doctrines_b, 2u);
    seed_doctrine(&doc, 10u, AGENT_GOAL_BIT(AGENT_GOAL_RESEARCH), 0u);
    EXPECT(agent_doctrine_register(&docs_a, &doc) == 0, "register doctrine a");
    EXPECT(agent_doctrine_register(&docs_b, &doc) == 0, "register doctrine b");

    memset(&ctx, 0, sizeof(ctx));
    ctx.capability_mask = AGENT_CAP_RESEARCH;
    ctx.explicit_doctrine_ref = 10u;

    EXPECT(agent_evaluator_choose_goal_with_doctrine(&reg_a, &docs_a, 0, &ctx, 0u, &ra) == 0,
           "choose goal a");
    EXPECT(agent_evaluator_choose_goal_with_doctrine(&reg_b, &docs_b, 0, &ctx, 0u, &rb) == 0,
           "choose goal b");
    EXPECT(ra.goal && rb.goal, "goal results missing");
    EXPECT(ra.goal->goal_id == rb.goal->goal_id, "goal id mismatch");
    EXPECT(ra.goal->type == AGENT_GOAL_RESEARCH, "expected research goal");
    EXPECT(ra.computed_priority == rb.computed_priority, "priority mismatch");
    return 0;
}

static int test_priority_modification_determinism(void)
{
    agent_goal goals[4];
    agent_goal_registry reg;
    agent_doctrine doctrines[2];
    agent_doctrine_registry docs;
    agent_doctrine doc;
    agent_context ctx;
    agent_goal_eval_result result;

    agent_goal_registry_init(&reg, goals, 4u, 1u);
    seed_goal(&reg, 1u, AGENT_GOAL_SURVIVE, 100u, 0u);
    seed_goal(&reg, 2u, AGENT_GOAL_RESEARCH, 100u, 0u);

    agent_doctrine_registry_init(&docs, doctrines, 2u);
    seed_doctrine(&doc, 11u, AGENT_GOAL_BIT(AGENT_GOAL_SURVIVE) | AGENT_GOAL_BIT(AGENT_GOAL_RESEARCH), 0u);
    doc.priority_modifiers[AGENT_GOAL_RESEARCH] = 250;
    EXPECT(agent_doctrine_register(&docs, &doc) == 0, "register doctrine");

    memset(&ctx, 0, sizeof(ctx));
    ctx.explicit_doctrine_ref = 11u;

    EXPECT(agent_evaluator_choose_goal_with_doctrine(&reg, &docs, 0, &ctx, 0u, &result) == 0,
           "choose goal with modifier");
    EXPECT(result.goal, "goal missing");
    EXPECT(result.goal->type == AGENT_GOAL_RESEARCH, "expected research goal");
    EXPECT(result.computed_priority == 350u, "priority modifier not applied");
    return 0;
}

static int test_conflicting_doctrine_resolution(void)
{
    agent_goal goals[4];
    agent_goal_registry reg;
    agent_doctrine doctrines[4];
    agent_doctrine_registry docs;
    agent_role roles[2];
    agent_role_registry roles_reg;
    agent_doctrine explicit_doc;
    agent_doctrine role_doc;
    agent_context ctx;
    agent_goal_eval_result result;

    agent_goal_registry_init(&reg, goals, 4u, 1u);
    seed_goal(&reg, 1u, AGENT_GOAL_RESEARCH, 200u, 0u);
    seed_goal(&reg, 2u, AGENT_GOAL_TRADE, 150u, 0u);

    agent_doctrine_registry_init(&docs, doctrines, 4u);
    seed_doctrine(&explicit_doc, 20u, AGENT_GOAL_BIT(AGENT_GOAL_TRADE), 0u);
    seed_doctrine(&role_doc, 21u, AGENT_GOAL_BIT(AGENT_GOAL_RESEARCH), 0u);
    EXPECT(agent_doctrine_register(&docs, &explicit_doc) == 0, "register explicit doctrine");
    EXPECT(agent_doctrine_register(&docs, &role_doc) == 0, "register role doctrine");

    agent_role_registry_init(&roles_reg, roles, 2u);
    EXPECT(agent_role_register(&roles_reg, 5u, 21u, 0u, 0u) == 0, "register role");

    memset(&ctx, 0, sizeof(ctx));
    ctx.role_id = 5u;
    ctx.explicit_doctrine_ref = 20u;

    EXPECT(agent_evaluator_choose_goal_with_doctrine(&reg, &docs, &roles_reg, &ctx, 0u, &result) == 0,
           "choose goal with conflict");
    EXPECT(result.goal, "goal missing");
    EXPECT(result.applied_doctrine_ref == 20u, "explicit doctrine not applied");
    EXPECT(result.goal->type == AGENT_GOAL_TRADE, "expected trade goal");
    return 0;
}

static int test_cohort_autonomy_collapse(void)
{
    agent_goal goal;
    agent_goal_preconditions pre;
    agent_context ctx;
    agent_plan plan;
    agent_plan collapsed;
    agent_plan_options options;
    agent_refusal_code refusal;

    memset(&pre, 0, sizeof(pre));
    pre.required_capabilities = AGENT_CAP_MOVE;
    memset(&goal, 0, sizeof(goal));
    goal.goal_id = 30u;
    goal.type = AGENT_GOAL_SURVIVE;
    goal.base_priority = 100u;
    goal.preconditions = pre;

    memset(&ctx, 0, sizeof(ctx));
    ctx.capability_mask = AGENT_CAP_MOVE;
    ctx.knowledge_mask = AGENT_KNOW_RESOURCE;
    ctx.known_resource_ref = 99u;

    memset(&options, 0, sizeof(options));
    options.max_steps = 2u;
    options.plan_id = 500u;

    EXPECT(agent_planner_build(&goal, &ctx, &options, 0u, &plan, &refusal) == 0,
           "plan build");
    EXPECT(agent_cohort_plan_collapse(&plan, 5u, &collapsed) == 0,
           "plan collapse");
    EXPECT(collapsed.step_count == plan.step_count, "step count mismatch");
    EXPECT(collapsed.steps[1].quantity == 5u, "quantity not scaled");
    EXPECT(collapsed.estimated_cost == plan.estimated_cost * 5u, "cost not scaled");
    return 0;
}

static int test_doctrine_batch_vs_step(void)
{
    agent_doctrine_registry reg_step;
    agent_doctrine_registry reg_batch;
    agent_doctrine doctrines_step[4];
    agent_doctrine doctrines_batch[4];
    doctrine_scheduler sched_step;
    doctrine_scheduler sched_batch;
    doctrine_event events_step[4];
    doctrine_event events_batch[4];
    dom_time_event due_events_step[8];
    dom_time_event due_events_batch[8];
    dg_due_entry due_entries_step[4];
    dg_due_entry due_entries_batch[4];
    doctrine_due_user due_users_step[4];
    doctrine_due_user due_users_batch[4];
    agent_doctrine doc_a;
    agent_doctrine doc_b;
    agent_doctrine* step_doc;
    agent_doctrine* batch_doc;

    agent_doctrine_registry_init(&reg_step, doctrines_step, 4u);
    agent_doctrine_registry_init(&reg_batch, doctrines_batch, 4u);
    EXPECT(doctrine_scheduler_init(&sched_step, due_events_step, 8u, due_entries_step, due_users_step,
                                   4u, 0u, events_step, 4u, &reg_step, 1u) == 0,
           "init step sched");
    EXPECT(doctrine_scheduler_init(&sched_batch, due_events_batch, 8u, due_entries_batch, due_users_batch,
                                   4u, 0u, events_batch, 4u, &reg_batch, 1u) == 0,
           "init batch sched");

    seed_doctrine(&doc_a, 40u, AGENT_GOAL_BIT(AGENT_GOAL_SURVIVE), 0u);
    doc_a.priority_modifiers[AGENT_GOAL_SURVIVE] = 10;
    seed_doctrine(&doc_b, 40u, AGENT_GOAL_BIT(AGENT_GOAL_RESEARCH), 0u);
    doc_b.priority_modifiers[AGENT_GOAL_RESEARCH] = 25;

    EXPECT(doctrine_schedule_apply(&sched_step, &doc_a, 5u) == 0, "schedule step a");
    EXPECT(doctrine_schedule_apply(&sched_step, &doc_b, 10u) == 0, "schedule step b");
    EXPECT(doctrine_schedule_apply(&sched_batch, &doc_a, 5u) == 0, "schedule batch a");
    EXPECT(doctrine_schedule_apply(&sched_batch, &doc_b, 10u) == 0, "schedule batch b");

    EXPECT(doctrine_scheduler_advance(&sched_step, 5u) == 0, "advance step 5");
    EXPECT(doctrine_scheduler_advance(&sched_step, 10u) == 0, "advance step 10");
    EXPECT(doctrine_scheduler_advance(&sched_batch, 10u) == 0, "advance batch 10");

    step_doc = agent_doctrine_find(&reg_step, 40u);
    batch_doc = agent_doctrine_find(&reg_batch, 40u);
    EXPECT(step_doc && batch_doc, "doctrine missing");
    EXPECT(step_doc->allowed_goal_types == batch_doc->allowed_goal_types, "allowed mismatch");
    EXPECT(step_doc->priority_modifiers[AGENT_GOAL_RESEARCH] ==
           batch_doc->priority_modifiers[AGENT_GOAL_RESEARCH], "modifier mismatch");
    return 0;
}

static int test_no_doctrine_no_autonomy(void)
{
    agent_goal goals[2];
    agent_goal_registry reg;
    agent_doctrine doctrines[2];
    agent_doctrine_registry docs;
    agent_context ctx;
    agent_goal_eval_result result;

    agent_goal_registry_init(&reg, goals, 2u, 1u);
    seed_goal(&reg, 1u, AGENT_GOAL_SURVIVE, 100u, 0u);
    agent_doctrine_registry_init(&docs, doctrines, 2u);

    memset(&ctx, 0, sizeof(ctx));
    EXPECT(agent_evaluator_choose_goal_with_doctrine(&reg, &docs, 0, &ctx, 0u, &result) != 0,
           "expected refusal without doctrine");
    EXPECT(result.refusal == AGENT_REFUSAL_DOCTRINE_NOT_AUTHORIZED, "expected doctrine refusal");
    EXPECT(result.goal == 0, "goal should be null");
    return 0;
}

int main(void)
{
    if (test_doctrine_filtering_determinism() != 0) return 1;
    if (test_priority_modification_determinism() != 0) return 1;
    if (test_conflicting_doctrine_resolution() != 0) return 1;
    if (test_cohort_autonomy_collapse() != 0) return 1;
    if (test_doctrine_batch_vs_step() != 0) return 1;
    if (test_no_doctrine_no_autonomy() != 0) return 1;
    return 0;
}
