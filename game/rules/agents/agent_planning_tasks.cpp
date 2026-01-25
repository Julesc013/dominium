/*
FILE: game/rules/agents/agent_planning_tasks.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Game / agents
RESPONSIBILITY: Implements agent planning and command emission helpers.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Planning and command emission are deterministic.
*/
#include "dominium/rules/agents/agent_planning_tasks.h"

#include <string.h>

void dom_agent_audit_init(dom_agent_audit_log* log,
                          dom_agent_audit_entry* storage,
                          u32 capacity,
                          u64 start_id)
{
    if (!log) {
        return;
    }
    log->entries = storage;
    log->count = 0u;
    log->capacity = capacity;
    log->next_event_id = start_id ? start_id : 1u;
    log->current_act = 0u;
    log->provenance_id = 0u;
    if (storage && capacity > 0u) {
        memset(storage, 0, sizeof(dom_agent_audit_entry) * (size_t)capacity);
    }
}

void dom_agent_audit_set_context(dom_agent_audit_log* log,
                                 dom_act_time_t act_time,
                                 dom_provenance_id provenance_id)
{
    if (!log) {
        return;
    }
    log->current_act = act_time;
    log->provenance_id = provenance_id;
}

int dom_agent_audit_record(dom_agent_audit_log* log,
                           u64 agent_id,
                           u32 kind,
                           u64 subject_id,
                           u64 related_id,
                           i64 amount)
{
    dom_agent_audit_entry* entry;
    if (!log || !log->entries) {
        return -1;
    }
    if (log->count >= log->capacity) {
        return -2;
    }
    entry = &log->entries[log->count++];
    entry->event_id = log->next_event_id++;
    entry->agent_id = agent_id;
    entry->act_time = log->current_act;
    entry->provenance_id = log->provenance_id;
    entry->kind = kind;
    entry->subject_id = subject_id;
    entry->related_id = related_id;
    entry->amount = amount;
    return 0;
}

void dom_agent_goal_buffer_init(dom_agent_goal_buffer* buffer,
                                dom_agent_goal_choice* storage,
                                u32 capacity)
{
    if (!buffer) {
        return;
    }
    buffer->entries = storage;
    buffer->count = 0u;
    buffer->capacity = capacity;
    if (storage && capacity > 0u) {
        memset(storage, 0, sizeof(dom_agent_goal_choice) * (size_t)capacity);
    }
}

void dom_agent_goal_buffer_reset(dom_agent_goal_buffer* buffer)
{
    if (!buffer) {
        return;
    }
    buffer->count = 0u;
}

int dom_agent_goal_buffer_set(dom_agent_goal_buffer* buffer,
                              u32 index,
                              const dom_agent_goal_choice* choice)
{
    if (!buffer || !choice || !buffer->entries) {
        return -1;
    }
    if (index >= buffer->capacity) {
        return -2;
    }
    buffer->entries[index] = *choice;
    if (index + 1u > buffer->count) {
        buffer->count = index + 1u;
    }
    return 0;
}

void dom_agent_plan_buffer_init(dom_agent_plan_buffer* buffer,
                                dom_agent_plan* storage,
                                u32 capacity,
                                u64 start_id)
{
    if (!buffer) {
        return;
    }
    buffer->entries = storage;
    buffer->count = 0u;
    buffer->capacity = capacity;
    buffer->next_id = start_id ? start_id : 1u;
    if (storage && capacity > 0u) {
        memset(storage, 0, sizeof(dom_agent_plan) * (size_t)capacity);
    }
}

void dom_agent_plan_buffer_reset(dom_agent_plan_buffer* buffer)
{
    if (!buffer) {
        return;
    }
    buffer->count = 0u;
}

int dom_agent_plan_buffer_set(dom_agent_plan_buffer* buffer,
                              u32 index,
                              const dom_agent_plan* plan)
{
    if (!buffer || !plan || !buffer->entries) {
        return -1;
    }
    if (index >= buffer->capacity) {
        return -2;
    }
    buffer->entries[index] = *plan;
    if (index + 1u > buffer->count) {
        buffer->count = index + 1u;
    }
    return 0;
}

void dom_agent_command_buffer_init(dom_agent_command_buffer* buffer,
                                   dom_agent_command* storage,
                                   u32 capacity,
                                   u64 start_id)
{
    if (!buffer) {
        return;
    }
    buffer->entries = storage;
    buffer->count = 0u;
    buffer->capacity = capacity;
    buffer->next_id = start_id ? start_id : 1u;
    if (storage && capacity > 0u) {
        memset(storage, 0, sizeof(dom_agent_command) * (size_t)capacity);
    }
}

void dom_agent_command_buffer_reset(dom_agent_command_buffer* buffer)
{
    if (!buffer) {
        return;
    }
    buffer->count = 0u;
}

int dom_agent_command_buffer_append(dom_agent_command_buffer* buffer,
                                    const dom_agent_command* command)
{
    dom_agent_command* entry;
    if (!buffer || !command || !buffer->entries) {
        return -1;
    }
    if (buffer->count >= buffer->capacity) {
        return -2;
    }
    entry = &buffer->entries[buffer->count++];
    *entry = *command;
    return 0;
}

static const dom_agent_belief* dom_agent_find_belief(const dom_agent_belief* beliefs,
                                                     u32 belief_count,
                                                     u64 agent_id)
{
    u32 i;
    if (!beliefs) {
        return 0;
    }
    for (i = 0u; i < belief_count; ++i) {
        if (beliefs[i].agent_id == agent_id) {
            return &beliefs[i];
        }
    }
    return 0;
}

static const dom_agent_capability* dom_agent_find_cap(const dom_agent_capability* caps,
                                                      u32 cap_count,
                                                      u64 agent_id)
{
    u32 i;
    if (!caps) {
        return 0;
    }
    for (i = 0u; i < cap_count; ++i) {
        if (caps[i].agent_id == agent_id) {
            return &caps[i];
        }
    }
    return 0;
}

static const dom_agent_schedule_item* dom_agent_schedule_at(const dom_agent_schedule_item* schedule,
                                                            u32 schedule_count,
                                                            u32 index)
{
    if (!schedule || index >= schedule_count) {
        return 0;
    }
    return &schedule[index];
}

static void dom_agent_build_context(agent_context* ctx,
                                    u64 agent_id,
                                    const dom_agent_belief* beliefs,
                                    u32 belief_count,
                                    const dom_agent_capability* caps,
                                    u32 cap_count)
{
    const dom_agent_belief* belief = dom_agent_find_belief(beliefs, belief_count, agent_id);
    const dom_agent_capability* cap = dom_agent_find_cap(caps, cap_count, agent_id);
    if (!ctx) {
        return;
    }
    memset(ctx, 0, sizeof(*ctx));
    ctx->agent_id = agent_id;
    ctx->risk_tolerance_q16 = AGENT_CONFIDENCE_MAX;
    if (cap) {
        ctx->capability_mask = cap->capability_mask;
        ctx->authority_mask = cap->authority_mask;
    }
    if (belief) {
        ctx->knowledge_mask = belief->knowledge_mask;
        ctx->hunger_level = belief->hunger_level;
        ctx->threat_level = belief->threat_level;
        if (belief->risk_tolerance_q16 > 0u) {
            ctx->risk_tolerance_q16 = belief->risk_tolerance_q16;
        }
        ctx->epistemic_confidence_q16 = belief->epistemic_confidence_q16;
        ctx->known_resource_ref = belief->known_resource_ref;
        ctx->known_threat_ref = belief->known_threat_ref;
        ctx->known_destination_ref = belief->known_destination_ref;
    }
}

u32 dom_agent_evaluate_goals_slice(const dom_agent_schedule_item* schedule,
                                   u32 schedule_count,
                                   u32 start_index,
                                   u32 max_count,
                                   agent_goal_registry* goals,
                                   const dom_agent_belief* beliefs,
                                   u32 belief_count,
                                   const dom_agent_capability* caps,
                                   u32 cap_count,
                                   dom_agent_goal_buffer* goals_out,
                                   dom_agent_audit_log* audit)
{
    u32 i;
    u32 end;
    if (!schedule || !goals_out || start_index >= schedule_count || max_count == 0u) {
        return 0u;
    }
    end = start_index + max_count;
    if (end > schedule_count) {
        end = schedule_count;
    }
    for (i = start_index; i < end; ++i) {
        dom_agent_goal_choice choice;
        agent_goal_eval_result eval;
        agent_context ctx;
        const dom_agent_schedule_item* sched = &schedule[i];
        int eval_res;

        memset(&choice, 0, sizeof(choice));
        choice.agent_id = sched->agent_id;
        choice.goal_id = 0u;
        choice.priority = 0u;
        choice.confidence_q16 = 0u;
        choice.refusal = AGENT_REFUSAL_GOAL_NOT_FEASIBLE;
        choice.flags = 0u;

        dom_agent_build_context(&ctx, sched->agent_id, beliefs, belief_count, caps, cap_count);
        eval_res = agent_evaluator_choose_goal(goals, &ctx, sched->next_due_tick, &eval);
        if (eval_res == 0 && eval.goal) {
            choice.goal_id = eval.goal->goal_id;
            choice.priority = eval.computed_priority;
            choice.confidence_q16 = eval.confidence_q16;
            choice.refusal = eval.refusal;
        } else {
            choice.refusal = eval.refusal;
        }
        if (dom_agent_goal_buffer_set(goals_out, i, &choice) == 0 && audit) {
            dom_agent_audit_record(audit,
                                   choice.agent_id,
                                   DOM_AGENT_AUDIT_GOAL_EVAL,
                                   choice.goal_id,
                                   0u,
                                   (i64)choice.priority);
        }

        if (goals && sched->active_goal_id != 0u && choice.goal_id != 0u &&
            sched->active_goal_id != choice.goal_id) {
            agent_goal* active = agent_goal_find(goals, sched->active_goal_id);
            if (active && active->conflict_group != 0u && eval.goal &&
                eval.goal->conflict_group == active->conflict_group) {
                agent_goal_record_oscillation(active, sched->next_due_tick);
                if (audit) {
                    dom_agent_audit_record(audit,
                                           active->agent_id,
                                           DOM_AGENT_AUDIT_GOAL_OSCILLATE,
                                           active->goal_id,
                                           choice.goal_id,
                                           (i64)active->oscillation_count);
                }
            }
        }
    }
    return end - start_index;
}

u32 dom_agent_plan_actions_slice(const dom_agent_goal_buffer* goals,
                                 u32 start_index,
                                 u32 max_count,
                                 agent_goal_registry* goal_registry,
                                 const dom_agent_belief* beliefs,
                                 u32 belief_count,
                                 const dom_agent_capability* caps,
                                 u32 cap_count,
                                 const dom_agent_schedule_item* schedule,
                                 u32 schedule_count,
                                 dom_agent_plan_buffer* plans,
                                 dom_agent_audit_log* audit)
{
    u32 i;
    u32 end;
    if (!goals || !plans || start_index >= goals->count || max_count == 0u) {
        return 0u;
    }
    end = start_index + max_count;
    if (end > goals->count) {
        end = goals->count;
    }
    for (i = start_index; i < end; ++i) {
        const dom_agent_goal_choice* choice = &goals->entries[i];
        const dom_agent_schedule_item* sched = dom_agent_schedule_at(schedule, schedule_count, i);
        agent_context ctx;
        agent_plan plan;
        agent_plan_options options;
        agent_refusal_code refusal = AGENT_REFUSAL_NONE;
        dom_agent_plan entry;
        const agent_goal* goal;
        dom_act_time_t now_act = sched ? sched->next_due_tick : 0u;
        int plan_res;

        if (choice->goal_id == 0u || !goal_registry) {
            continue;
        }

        goal = agent_goal_find(goal_registry, choice->goal_id);
        if (!goal) {
            continue;
        }

        memset(&options, 0, sizeof(options));
        if (sched) {
            options.compute_budget = sched->compute_budget;
            options.resume_step = sched->resume_step;
            options.plan_id = sched->active_plan_id;
        }

        memset(&plan, 0, sizeof(plan));
        dom_agent_build_context(&ctx, choice->agent_id, beliefs, belief_count, caps, cap_count);
        plan_res = agent_planner_build(goal, &ctx, &options, now_act, &plan, &refusal);

        memset(&entry, 0, sizeof(entry));
        entry.plan = plan;
        entry.agent_id = choice->agent_id;
        entry.valid = (plan_res == 0) ? 1u : 0u;
        entry.refusal = (u32)refusal;

        if (dom_agent_plan_buffer_set(plans, i, &entry) == 0 && audit) {
            if (plan_res == 0) {
                dom_agent_audit_record(audit,
                                       choice->agent_id,
                                       DOM_AGENT_AUDIT_PLAN_CREATE,
                                       plan.plan_id,
                                       plan.goal_id,
                                       (i64)plan.estimated_cost);
            } else {
                dom_agent_audit_record(audit,
                                       choice->agent_id,
                                       DOM_AGENT_AUDIT_PLAN_REFUSE,
                                       goal->goal_id,
                                       (u64)refusal,
                                       0);
            }
        }

        if (plan_res != 0 && goal_registry) {
            agent_goal* mutable_goal = agent_goal_find(goal_registry, goal->goal_id);
            if (mutable_goal) {
                agent_goal_record_failure(mutable_goal, now_act);
            }
        }
    }
    return end - start_index;
}

u32 dom_agent_validate_plan_slice(dom_agent_plan_buffer* plans,
                                  u32 start_index,
                                  u32 max_count,
                                  const dom_agent_capability* caps,
                                  u32 cap_count,
                                  const agent_authority_registry* authority,
                                  const agent_constraint_registry* constraints,
                                  const agent_contract_registry* contracts,
                                  const agent_delegation_registry* delegations,
                                  agent_goal_registry* goal_registry,
                                  dom_agent_audit_log* audit)
{
    u32 i;
    u32 end;
    if (!plans || !plans->entries || start_index >= plans->count || max_count == 0u) {
        return 0u;
    }
    end = start_index + max_count;
    if (end > plans->count) {
        end = plans->count;
    }
    for (i = start_index; i < end; ++i) {
        dom_agent_plan* plan = &plans->entries[i];
        const dom_agent_capability* cap;
        u32 refusal = AGENT_REFUSAL_NONE;
        dom_act_time_t now_act = audit ? audit->current_act : 0u;
        if (plan->valid == 0u || plan->plan.plan_id == 0u) {
            continue;
        }
        cap = dom_agent_find_cap(caps, cap_count, plan->agent_id);
        if (!cap) {
            plan->valid = 0u;
            refusal = AGENT_REFUSAL_INSUFFICIENT_CAPABILITY;
        } else {
            u32 effective_auth = cap->authority_mask;
            if (authority) {
                effective_auth = agent_authority_effective_mask(authority,
                                                                plan->agent_id,
                                                                effective_auth,
                                                                now_act);
            }
            if ((cap->capability_mask & plan->plan.required_capability_mask) !=
                plan->plan.required_capability_mask) {
                plan->valid = 0u;
                refusal = AGENT_REFUSAL_INSUFFICIENT_CAPABILITY;
            } else if ((effective_auth & plan->plan.required_authority_mask) !=
                       plan->plan.required_authority_mask) {
                u32 missing = plan->plan.required_authority_mask & ~effective_auth;
                agent_refusal_code del_refusal = AGENT_REFUSAL_NONE;
                agent_delegation* delegation = 0;
                u32 step_ok = 1u;
                if (delegations) {
                    delegation = agent_delegation_find_for_delegatee((agent_delegation_registry*)delegations,
                                                                     plan->agent_id, now_act);
                }
                if (!delegation ||
                    (delegation->delegation_kind & AGENT_DELEGATION_AUTHORITY) == 0u ||
                    (delegation->authority_mask & missing) != missing) {
                    plan->valid = 0u;
                    refusal = AGENT_REFUSAL_INSUFFICIENT_AUTHORITY;
                } else {
                    u32 s;
                    for (s = 0u; s < plan->plan.step_count; ++s) {
                        if (!agent_delegation_allows_process(delegation,
                                                             plan->plan.steps[s].process_kind,
                                                             now_act,
                                                             &del_refusal)) {
                            step_ok = 0u;
                            break;
                        }
                    }
                    if (!step_ok) {
                        plan->valid = 0u;
                        refusal = del_refusal;
                    }
                }
            }
        }

        if (plan->valid != 0u) {
            u32 s;
            u64 institution_id = 0u;
            if (constraints) {
                for (s = 0u; s < plan->plan.step_count; ++s) {
                    if (!agent_constraint_allows_process(constraints,
                                                         plan->agent_id,
                                                         plan->plan.steps[s].process_kind,
                                                         now_act,
                                                         &institution_id)) {
                        plan->valid = 0u;
                        refusal = AGENT_REFUSAL_CONSTRAINT_DENIED;
                        if (audit) {
                            dom_agent_audit_record(audit,
                                                   plan->agent_id,
                                                   DOM_AGENT_AUDIT_CONSTRAINT_BLOCK,
                                                   plan->plan.steps[s].process_id,
                                                   institution_id,
                                                   (i64)plan->plan.steps[s].process_kind);
                        }
                        break;
                    }
                }
            }
        }

        if (plan->valid != 0u && contracts) {
            u64 contract_id = 0u;
            if (!agent_contract_check_plan(contracts,
                                           plan->agent_id,
                                           &plan->plan,
                                           now_act,
                                           &contract_id)) {
                plan->valid = 0u;
                refusal = AGENT_REFUSAL_CONTRACT_VIOLATION;
                if (audit) {
                    dom_agent_audit_record(audit,
                                           plan->agent_id,
                                           DOM_AGENT_AUDIT_CONTRACT_FAIL,
                                           plan->plan.plan_id,
                                           contract_id,
                                           0);
                }
                if (contracts) {
                    agent_contract* contract = agent_contract_find((agent_contract_registry*)contracts,
                                                                   contract_id);
                    if (contract) {
                        agent_contract_record_failure(contract, now_act);
                    }
                }
            }
        }

        if (plan->valid == 0u) {
            plan->refusal = refusal;
            if (audit) {
                dom_agent_audit_record(audit,
                                       plan->agent_id,
                                       DOM_AGENT_AUDIT_PLAN_REFUSE,
                                       plan->plan.plan_id,
                                       (u64)refusal,
                                       0);
            }
            if (goal_registry) {
                agent_goal* goal = agent_goal_find(goal_registry, plan->plan.goal_id);
                if (goal) {
                    agent_goal_record_failure(goal, now_act);
                }
            }
        }
    }
    return end - start_index;
}

u32 dom_agent_emit_commands_slice(dom_agent_plan_buffer* plans,
                                  u32 start_index,
                                  u32 max_count,
                                  dom_agent_command_buffer* commands,
                                  dom_agent_audit_log* audit)
{
    u32 i;
    u32 end;
    if (!plans || !plans->entries || !commands || start_index >= plans->count || max_count == 0u) {
        return 0u;
    }
    end = start_index + max_count;
    if (end > plans->count) {
        end = plans->count;
    }
    for (i = start_index; i < end; ++i) {
        dom_agent_plan* plan_entry = &plans->entries[i];
        dom_agent_command cmd;
        const agent_process_step* step;
        if (plan_entry->valid == 0u || plan_entry->plan.plan_id == 0u) {
            continue;
        }
        if (plan_entry->plan.step_cursor >= plan_entry->plan.step_count) {
            plan_entry->valid = 0u;
            continue;
        }
        step = &plan_entry->plan.steps[plan_entry->plan.step_cursor];
        memset(&cmd, 0, sizeof(cmd));
        cmd.command_id = commands->next_id++;
        cmd.agent_id = plan_entry->agent_id;
        cmd.plan_id = plan_entry->plan.plan_id;
        cmd.goal_id = plan_entry->plan.goal_id;
        cmd.step_index = plan_entry->plan.step_cursor;
        cmd.process_id = step->process_id;
        cmd.target_id = step->target_ref;
        cmd.required_capability_mask = step->required_capability_mask;
        cmd.required_authority_mask = step->required_authority_mask;
        cmd.expected_cost_units = step->expected_cost_units;
        cmd.epistemic_gap_mask = step->epistemic_gap_mask;
        cmd.confidence_q16 = step->confidence_q16;
        cmd.failure_mode_id = step->failure_mode_id;
        cmd.flags = step->flags;

        if (dom_agent_command_buffer_append(commands, &cmd) == 0) {
            if (audit) {
                dom_agent_audit_record(audit,
                                       cmd.agent_id,
                                       DOM_AGENT_AUDIT_COMMAND_EMIT,
                                       cmd.command_id,
                                       cmd.plan_id,
                                       (i64)cmd.step_index);
            }
            plan_entry->plan.step_cursor += 1u;
            if (plan_entry->plan.step_cursor >= plan_entry->plan.step_count) {
                plan_entry->valid = 0u;
            }
        }
    }
    return end - start_index;
}

static agent_belief_state* dom_agent_find_belief_state(agent_belief_state* beliefs,
                                                       u32 belief_count,
                                                       u64 agent_id)
{
    u32 i;
    if (!beliefs) {
        return 0;
    }
    for (i = 0u; i < belief_count; ++i) {
        if (beliefs[i].agent_id == agent_id) {
            return &beliefs[i];
        }
    }
    return 0;
}

int dom_agent_apply_command_outcome(agent_goal_registry* goals,
                                    agent_belief_state* beliefs,
                                    u32 belief_count,
                                    const dom_agent_command_outcome* outcome,
                                    dom_act_time_t now_act,
                                    dom_agent_audit_log* audit)
{
    agent_command_outcome cmd_outcome;
    if (!outcome) {
        return -1;
    }
    if (beliefs) {
        agent_belief_state* state = dom_agent_find_belief_state(beliefs, belief_count, outcome->agent_id);
        if (state) {
            memset(&cmd_outcome, 0, sizeof(cmd_outcome));
            cmd_outcome.command_type = 0u;
            cmd_outcome.success = outcome->success ? 1 : 0;
            cmd_outcome.refusal = (agent_refusal_code)outcome->refusal;
            cmd_outcome.knowledge_clear_mask = outcome->knowledge_clear_mask;
            cmd_outcome.hunger_delta = outcome->hunger_delta;
            cmd_outcome.threat_delta = outcome->threat_delta;
            agent_belief_apply_command_outcome(state, &cmd_outcome, now_act);
        }
    }
    if (!outcome->success && goals) {
        agent_goal* goal = agent_goal_find(goals, outcome->goal_id);
        if (goal) {
            agent_goal_record_failure(goal, now_act);
        }
    }
    if (audit) {
        i64 amount = outcome->success ? 1 : -(i64)outcome->failure_mode_id;
        dom_agent_audit_record(audit,
                               outcome->agent_id,
                               DOM_AGENT_AUDIT_COMMAND_OUTCOME,
                               outcome->command_id,
                               outcome->goal_id,
                               amount);
    }
    return 0;
}
