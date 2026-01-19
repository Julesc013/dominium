/*
AGENT3 aggregation, refinement, and collapse tests.
*/
#include "dominium/agents/agent_aggregate.h"
#include "dominium/agents/agent_refinement.h"
#include "dominium/agents/agent_collapse.h"
#include "dominium/agents/agent_goal.h"
#include "dominium/agents/agent_planner.h"
#include "dominium/agents/delegation.h"

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

static int test_aggregate_vs_individual_equivalence(void)
{
    agent_goal goals[4];
    agent_goal_registry reg;
    agent_context individual_ctx;
    agent_goal_eval_result ind_res;
    agent_goal_eval_result agg_res;
    agent_belief_state beliefs[2];
    aggregate_belief_summary summary;
    aggregate_agent agg;
    agent_context agg_ctx;
    agent_plan plan;
    agent_plan collapsed;
    agent_plan_options options;
    agent_refusal_code refusal;

    agent_goal_registry_init(&reg, goals, 4u, 1u);
    seed_goal(&reg, 1u, AGENT_GOAL_SURVIVE, 200u, AGENT_CAP_MOVE);
    seed_goal(&reg, 2u, AGENT_GOAL_RESEARCH, 150u, AGENT_CAP_RESEARCH);

    agent_belief_init(&beliefs[0], 100u, AGENT_KNOW_RESOURCE, 700u, 100u, 0u);
    agent_belief_init(&beliefs[1], 101u, AGENT_KNOW_RESOURCE, 700u, 100u, 0u);
    EXPECT(aggregate_beliefs_from_states(beliefs, 2u, &summary) == 0, "aggregate beliefs");

    memset(&agg, 0, sizeof(agg));
    agg.aggregate_agent_id = 1u;
    agg.doctrine_ref = 0u;
    agg.belief_summary = summary;
    agg.cohort_count = 2u;

    memset(&individual_ctx, 0, sizeof(individual_ctx));
    individual_ctx.capability_mask = AGENT_CAP_MOVE;
    individual_ctx.knowledge_mask = AGENT_KNOW_RESOURCE;
    individual_ctx.hunger_level = 700u;

    EXPECT(agent_evaluator_choose_goal(&reg, &individual_ctx, 0u, &ind_res) == 0,
           "individual goal");

    EXPECT(agent_aggregate_make_context(&agg, &agg_ctx) == 0, "aggregate context");
    agg_ctx.capability_mask = AGENT_CAP_MOVE;
    agg_ctx.knowledge_mask = AGENT_KNOW_RESOURCE;
    agg_ctx.known_resource_ref = 50u;

    EXPECT(agent_evaluator_choose_goal(&reg, &agg_ctx, 0u, &agg_res) == 0,
           "aggregate goal");
    EXPECT(ind_res.goal && agg_res.goal, "goals missing");
    EXPECT(ind_res.goal->type == agg_res.goal->type, "goal type mismatch");

    memset(&options, 0, sizeof(options));
    options.max_steps = 2u;
    options.plan_id = 99u;
    EXPECT(agent_planner_build(agg_res.goal, &agg_ctx, &options, 0u, &plan, &refusal) == 0,
           "aggregate plan");
    EXPECT(agent_cohort_plan_collapse(&plan, agg.cohort_count, &collapsed) == 0,
           "collapse plan");
    EXPECT(collapsed.step_count == plan.step_count, "collapsed step count mismatch");
    EXPECT(collapsed.steps[1].quantity == plan.steps[1].quantity * agg.cohort_count,
           "collapsed quantity mismatch");
    return 0;
}

static int test_deterministic_refinement_selection(void)
{
    agent_refine_candidate candidates_a[4];
    agent_refine_candidate candidates_b[4];
    u64 selected_a[3];
    u64 selected_b[3];
    u32 count_a = 3u;
    u32 count_b = 3u;

    candidates_a[0].agent_id = 10u; candidates_a[0].role_rank = 2u;
    candidates_a[1].agent_id = 5u;  candidates_a[1].role_rank = 2u;
    candidates_a[2].agent_id = 7u;  candidates_a[2].role_rank = 3u;
    candidates_a[3].agent_id = 2u;  candidates_a[3].role_rank = 1u;

    candidates_b[0] = candidates_a[3];
    candidates_b[1] = candidates_a[2];
    candidates_b[2] = candidates_a[0];
    candidates_b[3] = candidates_a[1];

    EXPECT(agent_refinement_select(candidates_a, 4u, 3u, selected_a, &count_a) == 0,
           "select a");
    EXPECT(agent_refinement_select(candidates_b, 4u, 3u, selected_b, &count_b) == 0,
           "select b");
    EXPECT(count_a == 3u && count_b == 3u, "selection count mismatch");
    EXPECT(selected_a[0] == 7u, "expected top rank id");
    EXPECT(selected_a[1] == 5u, "expected second id");
    EXPECT(selected_a[2] == 10u, "expected third id");
    EXPECT(selected_a[0] == selected_b[0], "selection mismatch 0");
    EXPECT(selected_a[1] == selected_b[1], "selection mismatch 1");
    EXPECT(selected_a[2] == selected_b[2], "selection mismatch 2");
    return 0;
}

static int test_deterministic_collapse(void)
{
    aggregate_agent agg_a;
    aggregate_agent agg_b;
    agent_belief_state beliefs_a[3];
    agent_belief_state beliefs_b[3];
    agent_goal_status goals_a[3];
    agent_goal_status goals_b[3];
    agent_refusal_code refusal;

    agent_belief_init(&beliefs_a[0], 1u, AGENT_KNOW_RESOURCE, 200u, 50u, 0u);
    agent_belief_init(&beliefs_a[1], 2u, AGENT_KNOW_RESOURCE | AGENT_KNOW_THREAT, 600u, 150u, 0u);
    agent_belief_init(&beliefs_a[2], 3u, AGENT_KNOW_RESOURCE, 400u, 100u, 0u);
    beliefs_b[0] = beliefs_a[2];
    beliefs_b[1] = beliefs_a[0];
    beliefs_b[2] = beliefs_a[1];

    goals_a[0].goal_type = AGENT_GOAL_SURVIVE; goals_a[0].is_satisfied = 0u;
    goals_a[1].goal_type = AGENT_GOAL_SURVIVE; goals_a[1].is_satisfied = 1u;
    goals_a[2].goal_type = AGENT_GOAL_DEFEND;  goals_a[2].is_satisfied = 0u;
    goals_b[0] = goals_a[2];
    goals_b[1] = goals_a[0];
    goals_b[2] = goals_a[1];

    memset(&agg_a, 0, sizeof(agg_a));
    memset(&agg_b, 0, sizeof(agg_b));
    EXPECT(agent_collapse_from_individuals(&agg_a, beliefs_a, 3u, goals_a, 3u, 5u, &refusal) == 0,
           "collapse a");
    EXPECT(agent_collapse_from_individuals(&agg_b, beliefs_b, 3u, goals_b, 3u, 5u, &refusal) == 0,
           "collapse b");
    EXPECT(agg_a.belief_summary.hunger_avg == agg_b.belief_summary.hunger_avg, "avg mismatch");
    EXPECT(agg_a.belief_summary.hunger_min == agg_b.belief_summary.hunger_min, "min mismatch");
    EXPECT(agg_a.belief_summary.hunger_max == agg_b.belief_summary.hunger_max, "max mismatch");
    EXPECT(agg_a.belief_summary.knowledge_mask == agg_b.belief_summary.knowledge_mask, "knowledge mismatch");
    EXPECT(agg_a.goal_summary.goal_counts[AGENT_GOAL_SURVIVE] ==
           agg_b.goal_summary.goal_counts[AGENT_GOAL_SURVIVE], "goal count mismatch");
    return 0;
}

static int test_no_agent_presence_requirement(void)
{
    aggregate_belief_summary summary;
    aggregate_agent agg;
    agent_refusal_code refusal;

    EXPECT(aggregate_beliefs_from_states(0, 0u, &summary) == 0, "empty aggregate");
    EXPECT(summary.count == 0u, "summary count should be zero");
    EXPECT(summary.hunger_avg == 0u, "empty avg should be zero");
    memset(&agg, 0, sizeof(agg));
    EXPECT(agent_collapse_from_individuals(&agg, 0, 0u, 0, 0u, 0u, &refusal) == 0,
           "collapse with no agents");
    EXPECT(agg.cohort_count == 0u, "cohort count should be zero");
    return 0;
}

static int test_batch_vs_step_equivalence(void)
{
    aggregate_agent storage_step[1];
    aggregate_agent storage_batch[1];
    agent_aggregate_registry reg_step;
    agent_aggregate_registry reg_batch;
    agent_refinement_event events_step[2];
    agent_refinement_event events_batch[2];
    agent_refusal_code refusal;

    agent_aggregate_registry_init(&reg_step, storage_step, 1u, 1u);
    agent_aggregate_registry_init(&reg_batch, storage_batch, 1u, 1u);
    EXPECT(agent_aggregate_register(&reg_step, 1u, 99u, 0u, 5u, 1u) == 0, "register step");
    EXPECT(agent_aggregate_register(&reg_batch, 1u, 99u, 0u, 5u, 1u) == 0, "register batch");

    memset(events_step, 0, sizeof(events_step));
    events_step[0].event_id = 1u;
    events_step[0].aggregate_agent_id = 1u;
    events_step[0].trigger_act = 5u;
    events_step[0].type = AGENT_REFINE_EVENT_REFINE;
    events_step[0].desired_count = 3u;
    events_step[1].event_id = 2u;
    events_step[1].aggregate_agent_id = 1u;
    events_step[1].trigger_act = 10u;
    events_step[1].type = AGENT_REFINE_EVENT_COLLAPSE;
    events_step[1].desired_count = 0u;

    events_batch[0] = events_step[0];
    events_batch[1] = events_step[1];

    EXPECT(agent_refinement_process_events(&reg_step, events_step, 2u, 5u, &refusal) == 0,
           "step process 5");
    EXPECT(agent_refinement_process_events(&reg_step, events_step, 2u, 10u, &refusal) == 0,
           "step process 10");
    EXPECT(agent_refinement_process_events(&reg_batch, events_batch, 2u, 10u, &refusal) == 0,
           "batch process 10");

    EXPECT(reg_step.agents[0].refined_count == reg_batch.agents[0].refined_count,
           "refined count mismatch");
    EXPECT(reg_step.agents[0].refined_count == 0u, "expected collapsed refined count");
    return 0;
}

int main(void)
{
    if (test_aggregate_vs_individual_equivalence() != 0) return 1;
    if (test_deterministic_refinement_selection() != 0) return 1;
    if (test_deterministic_collapse() != 0) return 1;
    if (test_no_agent_presence_requirement() != 0) return 1;
    if (test_batch_vs_step_equivalence() != 0) return 1;
    return 0;
}
