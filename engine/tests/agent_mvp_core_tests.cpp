/*
Agent MVP core tests (AGENT1/TestX).
*/
#include "dominium/agents/agent_goal.h"
#include "dominium/agents/agent_evaluator.h"
#include "dominium/agents/agent_planner.h"
#include "dominium/agents/agent_belief_update.h"
#include "dominium/rules/agents/agent_planning_tasks.h"

#include <stdio.h>
#include <string.h>

#define EXPECT(cond, msg) do { \
    if (!(cond)) { \
        fprintf(stderr, "FAIL: %s\n", msg); \
        return 1; \
    } \
} while (0)

static u64 register_goal(agent_goal_registry* reg,
                         u64 agent_id,
                         u32 type,
                         u32 base_priority,
                         u32 urgency,
                         u32 required_knowledge,
                         u32 flags,
                         u32 abandon_after_failures)
{
    agent_goal_desc desc;
    u64 goal_id = 0u;
    memset(&desc, 0, sizeof(desc));
    desc.agent_id = agent_id;
    desc.type = type;
    desc.base_priority = base_priority;
    desc.urgency = urgency;
    desc.preconditions.required_knowledge = required_knowledge;
    desc.flags = flags;
    desc.abandon_after_failures = abandon_after_failures;
    (void)agent_goal_register(reg, &desc, &goal_id);
    return goal_id;
}

static void build_context_from_belief(agent_context* ctx,
                                      u64 agent_id,
                                      const dom_agent_belief* belief,
                                      u32 cap_mask,
                                      u32 auth_mask)
{
    memset(ctx, 0, sizeof(*ctx));
    ctx->agent_id = agent_id;
    ctx->capability_mask = cap_mask;
    ctx->authority_mask = auth_mask;
    ctx->risk_tolerance_q16 = AGENT_CONFIDENCE_MAX;
    if (belief) {
        ctx->knowledge_mask = belief->knowledge_mask;
        ctx->hunger_level = belief->hunger_level;
        ctx->threat_level = belief->threat_level;
        ctx->risk_tolerance_q16 = belief->risk_tolerance_q16;
        ctx->epistemic_confidence_q16 = belief->epistemic_confidence_q16;
        ctx->known_resource_ref = belief->known_resource_ref;
        ctx->known_threat_ref = belief->known_threat_ref;
        ctx->known_destination_ref = belief->known_destination_ref;
    }
}

static int test_multiple_goals(void)
{
    agent_goal goals_storage[4];
    agent_goal_registry reg;
    agent_goal_eval_result eval;
    agent_context ctx;
    u64 goal_a;
    u64 goal_b;

    agent_goal_registry_init(&reg, goals_storage, 4u, 1u);
    goal_a = register_goal(&reg, 1u, AGENT_GOAL_SURVIVE, 100u, 50u, 0u, 0u, 0u);
    goal_b = register_goal(&reg, 1u, AGENT_GOAL_ACQUIRE, 400u, 0u, 0u, 0u, 0u);
    EXPECT(goal_a != 0u && goal_b != 0u, "goal registration");

    memset(&ctx, 0, sizeof(ctx));
    ctx.agent_id = 1u;
    ctx.capability_mask = AGENT_CAP_MOVE | AGENT_CAP_TRADE;
    ctx.authority_mask = AGENT_AUTH_BASIC | AGENT_AUTH_TRADE;

    EXPECT(agent_evaluator_choose_goal(&reg, &ctx, 10u, &eval) == 0, "goal evaluation");
    EXPECT(eval.goal && eval.goal->goal_id == goal_b, "goal arbitration selects highest priority");
    return 0;
}

static int test_subjective_knowledge_only(void)
{
    agent_goal goals_storage[2];
    agent_goal_registry reg;
    agent_goal_desc desc;
    agent_goal* goal;
    agent_context ctx;
    agent_plan plan;
    agent_refusal_code refusal = AGENT_REFUSAL_NONE;

    agent_goal_registry_init(&reg, goals_storage, 2u, 1u);
    memset(&desc, 0, sizeof(desc));
    desc.agent_id = 2u;
    desc.type = AGENT_GOAL_ACQUIRE;
    desc.preconditions.required_knowledge = AGENT_KNOW_RESOURCE;
    desc.flags = AGENT_GOAL_FLAG_REQUIRE_KNOWLEDGE;
    EXPECT(agent_goal_register(&reg, &desc, 0) == 0, "goal register for knowledge test");
    goal = agent_goal_find(&reg, 1u);
    EXPECT(goal != 0, "goal lookup for knowledge test");

    memset(&ctx, 0, sizeof(ctx));
    ctx.agent_id = 2u;
    ctx.capability_mask = AGENT_CAP_MOVE;
    ctx.authority_mask = AGENT_AUTH_BASIC;
    ctx.knowledge_mask = 0u;

    EXPECT(agent_planner_build(goal, &ctx, 0, 5u, &plan, &refusal) != 0, "planner rejects missing knowledge");
    EXPECT(refusal == AGENT_REFUSAL_INSUFFICIENT_KNOWLEDGE, "planner uses subjective knowledge");
    return 0;
}

static int test_divergent_beliefs(void)
{
    agent_goal goals_storage[2];
    agent_goal_registry reg;
    agent_goal* goal_a;
    agent_goal* goal_b;
    agent_goal_desc desc;
    u64 goal_id_a;
    u64 goal_id_b;
    dom_agent_belief belief_a;
    dom_agent_belief belief_b;
    agent_context ctx_a;
    agent_context ctx_b;
    agent_plan plan_a;
    agent_plan plan_b;

    agent_goal_registry_init(&reg, goals_storage, 2u, 1u);
    memset(&desc, 0, sizeof(desc));
    desc.agent_id = 10u;
    desc.type = AGENT_GOAL_ACQUIRE;
    desc.preconditions.required_knowledge = AGENT_KNOW_RESOURCE;
    desc.flags = AGENT_GOAL_FLAG_REQUIRE_KNOWLEDGE;
    EXPECT(agent_goal_register(&reg, &desc, &goal_id_a) == 0, "goal register for divergence A");
    desc.agent_id = 11u;
    EXPECT(agent_goal_register(&reg, &desc, &goal_id_b) == 0, "goal register for divergence B");
    goal_a = agent_goal_find(&reg, goal_id_a);
    goal_b = agent_goal_find(&reg, goal_id_b);
    EXPECT(goal_a != 0 && goal_b != 0, "goal lookup for divergence");

    memset(&belief_a, 0, sizeof(belief_a));
    belief_a.agent_id = 10u;
    belief_a.knowledge_mask = AGENT_KNOW_RESOURCE;
    belief_a.known_resource_ref = 1001u;

    memset(&belief_b, 0, sizeof(belief_b));
    belief_b.agent_id = 11u;
    belief_b.knowledge_mask = AGENT_KNOW_RESOURCE;
    belief_b.known_resource_ref = 2002u;

    build_context_from_belief(&ctx_a, 10u, &belief_a, AGENT_CAP_MOVE, AGENT_AUTH_BASIC);
    build_context_from_belief(&ctx_b, 11u, &belief_b, AGENT_CAP_MOVE, AGENT_AUTH_BASIC);

    EXPECT(agent_planner_build(goal_a, &ctx_a, 0, 1u, &plan_a, 0) == 0, "planner builds for agent A");
    EXPECT(agent_planner_build(goal_b, &ctx_b, 0, 1u, &plan_b, 0) == 0, "planner builds for agent B");
    EXPECT(plan_a.steps[0].target_ref != plan_b.steps[0].target_ref, "divergent beliefs diverge plans");
    return 0;
}

static int test_failure_affects_planning(void)
{
    agent_goal goals_storage[4];
    agent_goal_registry reg;
    agent_goal_eval_result eval;
    agent_context ctx;
    u64 goal_a;
    u64 goal_b;
    agent_goal* goal_ptr;

    agent_goal_registry_init(&reg, goals_storage, 4u, 1u);
    goal_a = register_goal(&reg, 20u, AGENT_GOAL_ACQUIRE, 500u, 0u, 0u, 0u, 1u);
    goal_b = register_goal(&reg, 20u, AGENT_GOAL_DEFEND, 100u, 0u, 0u, 0u, 0u);
    EXPECT(goal_a != 0u && goal_b != 0u, "goal register for failure");

    memset(&ctx, 0, sizeof(ctx));
    ctx.agent_id = 20u;
    ctx.capability_mask = AGENT_CAP_MOVE | AGENT_CAP_DEFEND;
    ctx.authority_mask = AGENT_AUTH_BASIC | AGENT_AUTH_MILITARY;

    EXPECT(agent_evaluator_choose_goal(&reg, &ctx, 1u, &eval) == 0, "pre-failure eval");
    EXPECT(eval.goal && eval.goal->goal_id == goal_a, "highest priority goal selected");

    goal_ptr = agent_goal_find(&reg, goal_a);
    EXPECT(goal_ptr != 0, "goal lookup for failure");
    agent_goal_record_failure(goal_ptr, 2u);

    EXPECT(agent_evaluator_choose_goal(&reg, &ctx, 3u, &eval) == 0, "post-failure eval");
    EXPECT(eval.goal && eval.goal->goal_id == goal_b, "failure changes goal selection");
    return 0;
}

static int test_wrong_belief_repeats_failure(void)
{
    agent_goal goals_storage[2];
    agent_goal_registry reg;
    agent_goal_desc desc;
    agent_goal* goal;
    dom_agent_belief belief;
    agent_context ctx;
    agent_plan plan_a;
    agent_plan plan_b;

    agent_goal_registry_init(&reg, goals_storage, 2u, 1u);
    memset(&desc, 0, sizeof(desc));
    desc.agent_id = 30u;
    desc.type = AGENT_GOAL_ACQUIRE;
    desc.preconditions.required_knowledge = AGENT_KNOW_RESOURCE;
    desc.flags = AGENT_GOAL_FLAG_REQUIRE_KNOWLEDGE;
    desc.abandon_after_failures = 3u;
    EXPECT(agent_goal_register(&reg, &desc, 0) == 0, "goal register for wrong belief");
    goal = agent_goal_find(&reg, 1u);
    EXPECT(goal != 0, "goal lookup for wrong belief");

    memset(&belief, 0, sizeof(belief));
    belief.agent_id = 30u;
    belief.knowledge_mask = AGENT_KNOW_RESOURCE;
    belief.known_resource_ref = 999u;

    build_context_from_belief(&ctx, 30u, &belief, AGENT_CAP_MOVE, AGENT_AUTH_BASIC);
    EXPECT(agent_planner_build(goal, &ctx, 0, 1u, &plan_a, 0) == 0, "plan built before failure");
    agent_goal_record_failure(goal, 5u);
    EXPECT(agent_planner_build(goal, &ctx, 0, 7u, &plan_b, 0) == 0, "plan built after failure");
    EXPECT(plan_a.steps[0].target_ref == plan_b.steps[0].target_ref, "wrong belief repeats target");
    return 0;
}

static int test_failure_updates_belief(void)
{
    agent_goal goals_storage[2];
    agent_goal_registry reg;
    agent_goal_desc desc;
    agent_goal* goal;
    agent_belief_state belief_state;
    agent_context ctx;
    agent_plan plan;
    agent_refusal_code refusal = AGENT_REFUSAL_NONE;
    dom_agent_command_outcome outcome;

    agent_goal_registry_init(&reg, goals_storage, 2u, 1u);
    memset(&desc, 0, sizeof(desc));
    desc.agent_id = 35u;
    desc.type = AGENT_GOAL_ACQUIRE;
    desc.preconditions.required_knowledge = AGENT_KNOW_RESOURCE;
    desc.flags = AGENT_GOAL_FLAG_REQUIRE_KNOWLEDGE;
    EXPECT(agent_goal_register(&reg, &desc, 0) == 0, "goal register for belief update");
    goal = agent_goal_find(&reg, 1u);
    EXPECT(goal != 0, "goal lookup for belief update");

    agent_belief_init(&belief_state, 35u, AGENT_KNOW_RESOURCE, 0u, 0u, 1u);

    memset(&ctx, 0, sizeof(ctx));
    ctx.agent_id = 35u;
    ctx.knowledge_mask = belief_state.knowledge_mask;
    ctx.known_resource_ref = 333u;
    ctx.capability_mask = AGENT_CAP_MOVE;
    ctx.authority_mask = AGENT_AUTH_BASIC;

    EXPECT(agent_planner_build(goal, &ctx, 0, 2u, &plan, &refusal) == 0, "plan before belief update");

    memset(&outcome, 0, sizeof(outcome));
    outcome.agent_id = 35u;
    outcome.goal_id = goal->goal_id;
    outcome.success = 0;
    outcome.refusal = AGENT_REFUSAL_INSUFFICIENT_KNOWLEDGE;
    outcome.knowledge_clear_mask = AGENT_KNOW_RESOURCE;
    dom_agent_apply_command_outcome(&reg, &belief_state, 1u, &outcome, 3u, 0);

    ctx.knowledge_mask = belief_state.knowledge_mask;
    ctx.known_resource_ref = 0u;
    EXPECT(agent_planner_build(goal, &ctx, 0, 4u, &plan, &refusal) != 0, "plan changes after belief update");
    EXPECT(refusal == AGENT_REFUSAL_INSUFFICIENT_KNOWLEDGE, "belief update drives refusal");
    return 0;
}

static int test_memory_decay_changes_behavior(void)
{
    agent_belief_entry entries[2];
    agent_belief_store store;
    agent_goal goals_storage[2];
    agent_goal_registry reg;
    agent_goal_desc desc;
    agent_goal* goal;
    agent_context ctx;
    agent_plan plan;
    u32 mask_before;
    u32 mask_after;

    agent_belief_store_init(&store, entries, 2u, 1u, 40000u, 1000u);
    {
        agent_belief_event evt;
        memset(&evt, 0, sizeof(evt));
        evt.agent_id = 40u;
        evt.knowledge_ref = 555u;
        evt.topic_id = AGENT_BELIEF_TOPIC_RESOURCE;
        evt.kind = AGENT_BELIEF_EVENT_OBSERVE;
        evt.confidence_q16 = AGENT_CONFIDENCE_MAX;
        evt.observed_act = 1u;
        agent_belief_store_apply_event(&store, &evt, 1u);
    }

    agent_goal_registry_init(&reg, goals_storage, 2u, 1u);
    memset(&desc, 0, sizeof(desc));
    desc.agent_id = 40u;
    desc.type = AGENT_GOAL_ACQUIRE;
    desc.preconditions.required_knowledge = AGENT_KNOW_RESOURCE;
    desc.flags = AGENT_GOAL_FLAG_REQUIRE_KNOWLEDGE;
    EXPECT(agent_goal_register(&reg, &desc, 0) == 0, "goal register for decay");
    goal = agent_goal_find(&reg, 1u);
    EXPECT(goal != 0, "goal lookup for decay");

    mask_before = agent_belief_store_mask(&store, 40u);
    memset(&ctx, 0, sizeof(ctx));
    ctx.agent_id = 40u;
    ctx.knowledge_mask = mask_before;
    ctx.known_resource_ref = 555u;
    ctx.capability_mask = AGENT_CAP_MOVE;
    ctx.authority_mask = AGENT_AUTH_BASIC;
    EXPECT(agent_planner_build(goal, &ctx, 0, 2u, &plan, 0) == 0, "plan before decay");

    agent_belief_store_decay(&store, 1u);
    agent_belief_store_decay(&store, 3u);
    mask_after = agent_belief_store_mask(&store, 40u);
    ctx.knowledge_mask = mask_after;
    EXPECT(agent_planner_build(goal, &ctx, 0, 12u, &plan, 0) != 0, "plan blocked after decay");
    return 0;
}

static int test_history_and_determinism(void)
{
    agent_goal goals_storage_a[2];
    agent_goal goals_storage_b[2];
    agent_goal_registry reg_a;
    agent_goal_registry reg_b;
    dom_agent_schedule_item schedule[1];
    dom_agent_belief belief[1];
    dom_agent_capability cap[1];
    dom_agent_goal_choice goal_choices[1];
    dom_agent_goal_buffer goal_buf;
    dom_agent_plan plan_storage[1];
    dom_agent_plan_buffer plan_buf;
    dom_agent_audit_entry audit_entries_a[8];
    dom_agent_audit_entry audit_entries_b[8];
    dom_agent_audit_log audit_a;
    dom_agent_audit_log audit_b;
    u64 goal_id;
    u32 i;

    agent_goal_registry_init(&reg_a, goals_storage_a, 2u, 1u);
    agent_goal_registry_init(&reg_b, goals_storage_b, 2u, 1u);
    goal_id = register_goal(&reg_a, 50u, AGENT_GOAL_ACQUIRE, 200u, 0u, 0u, 0u, 0u);
    register_goal(&reg_b, 50u, AGENT_GOAL_ACQUIRE, 200u, 0u, 0u, 0u, 0u);
    EXPECT(goal_id != 0u, "goal register for history");

    memset(schedule, 0, sizeof(schedule));
    schedule[0].agent_id = 50u;
    schedule[0].next_due_tick = 10u;
    schedule[0].compute_budget = 2u;

    memset(belief, 0, sizeof(belief));
    belief[0].agent_id = 50u;
    belief[0].knowledge_mask = AGENT_KNOW_RESOURCE;
    belief[0].known_resource_ref = 888u;

    memset(cap, 0, sizeof(cap));
    cap[0].agent_id = 50u;
    cap[0].capability_mask = AGENT_CAP_MOVE;
    cap[0].authority_mask = AGENT_AUTH_BASIC;

    dom_agent_goal_buffer_init(&goal_buf, goal_choices, 1u);
    dom_agent_plan_buffer_init(&plan_buf, plan_storage, 1u, 1u);
    dom_agent_audit_init(&audit_a, audit_entries_a, 8u, 1u);
    dom_agent_audit_init(&audit_b, audit_entries_b, 8u, 1u);
    dom_agent_audit_set_context(&audit_a, 10u, 42u);
    dom_agent_audit_set_context(&audit_b, 10u, 42u);

    dom_agent_evaluate_goals_slice(schedule, 1u, 0u, 1u, &reg_a,
                                   belief, 1u, cap, 1u, &goal_buf, &audit_a);
    dom_agent_plan_actions_slice(&goal_buf, 0u, 1u, &reg_a,
                                 belief, 1u, cap, 1u, schedule, 1u, &plan_buf, &audit_a);

    dom_agent_evaluate_goals_slice(schedule, 1u, 0u, 1u, &reg_b,
                                   belief, 1u, cap, 1u, &goal_buf, &audit_b);
    dom_agent_plan_actions_slice(&goal_buf, 0u, 1u, &reg_b,
                                 belief, 1u, cap, 1u, schedule, 1u, &plan_buf, &audit_b);

    EXPECT(audit_a.count > 0u, "history generated");
    EXPECT(audit_a.entries[0].act_time == 10u, "history timestamp recorded");
    EXPECT(audit_a.entries[0].provenance_id == 42u, "history provenance recorded");
    EXPECT(audit_a.count == audit_b.count, "determinism count");
    for (i = 0u; i < audit_a.count; ++i) {
        EXPECT(audit_a.entries[i].kind == audit_b.entries[i].kind, "determinism kind");
        EXPECT(audit_a.entries[i].agent_id == audit_b.entries[i].agent_id, "determinism agent");
        EXPECT(audit_a.entries[i].subject_id == audit_b.entries[i].subject_id, "determinism subject");
        EXPECT(audit_a.entries[i].related_id == audit_b.entries[i].related_id, "determinism related");
        EXPECT(audit_a.entries[i].amount == audit_b.entries[i].amount, "determinism amount");
    }
    return 0;
}

int main(void)
{
    if (test_multiple_goals() != 0) {
        return 1;
    }
    if (test_subjective_knowledge_only() != 0) {
        return 1;
    }
    if (test_divergent_beliefs() != 0) {
        return 1;
    }
    if (test_failure_affects_planning() != 0) {
        return 1;
    }
    if (test_wrong_belief_repeats_failure() != 0) {
        return 1;
    }
    if (test_failure_updates_belief() != 0) {
        return 1;
    }
    if (test_memory_decay_changes_behavior() != 0) {
        return 1;
    }
    if (test_history_and_determinism() != 0) {
        return 1;
    }
    return 0;
}
