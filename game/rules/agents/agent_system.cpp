/*
FILE: game/rules/agents/agent_system.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Game / agents
RESPONSIBILITY: Work IR-based agent emission (authoritative tasks only).
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Task emission order and budgeting are deterministic.
*/
#include "dominium/rules/agents/agent_system.h"

#include "dominium/execution/work_graph_builder.h"
#include "dominium/execution/access_set_builder.h"
#include "domino/execution/task_node.h"
#include "domino/execution/cost_model.h"
#include "domino/core/dom_time_core.h"

#include <string.h>

enum {
    DOM_AGENT_COMPONENT_SCHEDULE = 5601u,
    DOM_AGENT_COMPONENT_BELIEF = 5602u,
    DOM_AGENT_COMPONENT_DOCTRINE = 5603u,
    DOM_AGENT_COMPONENT_ROLE = 5604u,
    DOM_AGENT_COMPONENT_GOAL = 5605u,
    DOM_AGENT_COMPONENT_PLAN = 5606u,
    DOM_AGENT_COMPONENT_COMMAND = 5607u,
    DOM_AGENT_COMPONENT_CAPABILITY = 5608u,
    DOM_AGENT_COMPONENT_POPULATION = 5609u,
    DOM_AGENT_COMPONENT_COHORT = 5610u,
    DOM_AGENT_COMPONENT_AUDIT = 5611u,
    DOM_AGENT_FIELD_DEFAULT = 1u
};

static u32 dom_agent_fnv1a32(const char* text)
{
    const unsigned char* bytes = (const unsigned char*)(text ? text : "");
    u32 hash = 2166136261u;
    while (*bytes) {
        hash ^= (u32)(*bytes++);
        hash *= 16777619u;
    }
    return hash;
}

static u64 dom_agent_fnv1a64(const char* text)
{
    const unsigned char* bytes = (const unsigned char*)(text ? text : "");
    u64 hash = 1469598103934665603ULL;
    while (*bytes) {
        hash ^= (u64)(*bytes++);
        hash *= 1099511628211ULL;
    }
    return hash;
}

static u32 dom_agent_task_fidelity(dom_fidelity_tier tier)
{
    switch (tier) {
        case DOM_FIDELITY_LATENT: return DOM_FID_LATENT;
        case DOM_FIDELITY_MACRO: return DOM_FID_MACRO;
        case DOM_FIDELITY_MESO: return DOM_FID_MESO;
        case DOM_FIDELITY_MICRO: return DOM_FID_MICRO;
        case DOM_FIDELITY_FOCUS: return DOM_FID_FOCUS;
        default: return DOM_FID_LATENT;
    }
}

static u32 dom_agent_default_budget(dom_fidelity_tier tier)
{
    switch (tier) {
        case DOM_FIDELITY_FOCUS: return 12u;
        case DOM_FIDELITY_MICRO: return 8u;
        case DOM_FIDELITY_MESO: return 6u;
        case DOM_FIDELITY_MACRO: return 4u;
        case DOM_FIDELITY_LATENT:
        default:
            return 0u;
    }
}

static u32 dom_agent_default_cadence(dom_fidelity_tier tier)
{
    switch (tier) {
        case DOM_FIDELITY_FOCUS: return 1u;
        case DOM_FIDELITY_MICRO: return 2u;
        case DOM_FIDELITY_MESO: return 4u;
        case DOM_FIDELITY_MACRO: return 8u;
        case DOM_FIDELITY_LATENT:
        default:
            return 0u;
    }
}

static dom_act_time_t dom_agent_next_due(dom_act_time_t now, u32 cadence, d_bool has_work)
{
    if (!has_work || cadence == 0u) {
        return DOM_TIME_ACT_MAX;
    }
    if (now > (DOM_TIME_ACT_MAX - cadence)) {
        return DOM_TIME_ACT_MAX;
    }
    return now + (dom_act_time_t)cadence;
}

static u32 dom_agent_local_id_for_op(u32 op)
{
    return op;
}

static void dom_agent_runtime_reset(dom_agent_runtime_state* state)
{
    if (!state) {
        return;
    }
    state->schedule_cursor = 0u;
    state->doctrine_cursor = 0u;
    state->population_cursor = 0u;
}

static dom_agent_task_params* dom_agent_params_for_op(dom_agent_task_params* params,
                                                      u32 op)
{
    if (!params || op == 0u || op > 9u) {
        return 0;
    }
    return &params[op - 1u];
}

AgentSystem::AgentSystem()
    : system_id_(0u),
      law_target_count_(0u),
      law_scope_ref_(1u),
      tier_(DOM_FIDELITY_MACRO),
      next_due_tick_(DOM_TIME_ACT_MAX),
      migration_state_(DOM_AGENT_STATE_IR_ONLY),
      allowed_ops_mask_(0xFFFFFFFFu),
      last_emitted_task_count_(0u),
      cycle_in_progress_(D_FALSE),
      inputs_(0),
      buffers_(0)
{
    u32 i;
    system_id_ = dom_agent_fnv1a64("AGENTS");
    law_targets_[0] = dom_agent_fnv1a32("AGENT.PLANNING");
    law_targets_[1] = dom_agent_fnv1a32("EXEC.AUTH_TASK");
    law_target_count_ = 2u;
    for (i = 0u; i < 9u; ++i) {
        params_[i].op = 0u;
        params_[i].start_index = 0u;
        params_[i].count = 0u;
    }
    memset(&runtime_, 0, sizeof(runtime_));
    dom_agent_runtime_reset(&runtime_);
}

int AgentSystem::init(const dom_agent_inputs* inputs,
                      const dom_agent_buffers* buffers)
{
    inputs_ = inputs;
    buffers_ = buffers;
    dom_agent_runtime_reset(&runtime_);
    return 0;
}

void AgentSystem::set_inputs(const dom_agent_inputs* inputs)
{
    inputs_ = inputs;
}

void AgentSystem::set_buffers(const dom_agent_buffers* buffers)
{
    buffers_ = buffers;
}

void AgentSystem::set_allowed_ops_mask(u32 mask)
{
    allowed_ops_mask_ = mask;
}

void AgentSystem::set_next_due_tick(dom_act_time_t tick)
{
    next_due_tick_ = tick;
}

void AgentSystem::set_migration_state(dom_agent_migration_state state)
{
    migration_state_ = state;
}

dom_agent_migration_state AgentSystem::migration_state() const
{
    return migration_state_;
}

u32 AgentSystem::last_emitted_task_count() const
{
    return last_emitted_task_count_;
}

dom_agent_runtime_state* AgentSystem::runtime_state()
{
    return &runtime_;
}

const dom_agent_runtime_state* AgentSystem::runtime_state() const
{
    return &runtime_;
}

u64 AgentSystem::system_id() const
{
    return system_id_;
}

d_bool AgentSystem::is_sim_affecting() const
{
    return D_TRUE;
}

const u32* AgentSystem::law_targets(u32* out_count) const
{
    if (out_count) {
        *out_count = law_target_count_;
    }
    return law_targets_;
}

dom_act_time_t AgentSystem::get_next_due_tick() const
{
    return next_due_tick_;
}

void AgentSystem::degrade(dom_fidelity_tier tier, u32 reason)
{
    (void)reason;
    tier_ = tier;
}

static int dom_agent_emit_task_node(dom_work_graph_builder* graph_builder,
                                    dom_access_set_builder* access_builder,
                                    const dom_task_node* node,
                                    const dom_cost_model* cost,
                                    const dom_access_range* reads,
                                    u32 read_count,
                                    const dom_access_range* writes,
                                    u32 write_count)
{
    u32 i;
    if (dom_work_graph_builder_add_cost_model(graph_builder, cost) != 0) {
        return -1;
    }
    if (!dom_access_set_builder_begin(access_builder, node->access_set_id, DOM_REDUCE_NONE, 0)) {
        return -2;
    }
    for (i = 0u; i < read_count; ++i) {
        if (dom_access_set_builder_add_read(access_builder, &reads[i]) != 0) {
            return -3;
        }
    }
    for (i = 0u; i < write_count; ++i) {
        if (dom_access_set_builder_add_write(access_builder, &writes[i]) != 0) {
            return -4;
        }
    }
    if (dom_access_set_builder_finalize(access_builder) != 0) {
        return -5;
    }
    if (dom_work_graph_builder_add_task(graph_builder, node) != 0) {
        return -6;
    }
    return 0;
}

static void dom_agent_reset_buffers(const dom_agent_buffers* buffers)
{
    if (!buffers) {
        return;
    }
    if (buffers->goals) {
        dom_agent_goal_buffer_reset(buffers->goals);
    }
    if (buffers->plans) {
        dom_agent_plan_buffer_reset(buffers->plans);
    }
    if (buffers->commands) {
        dom_agent_command_buffer_reset(buffers->commands);
    }
    if (buffers->roles) {
        dom_agent_role_buffer_reset(buffers->roles);
    }
    if (buffers->cohorts) {
        dom_agent_cohort_buffer_reset(buffers->cohorts);
    }
}

int AgentSystem::emit_tasks(dom_act_time_t act_now,
                            dom_act_time_t act_target,
                            dom_work_graph_builder* graph_builder,
                            dom_access_set_builder* access_builder)
{
    u32 budget;
    u32 cadence;
    u64 prev_task_id = 0u;
    d_bool has_work = D_FALSE;
    d_bool cycle_complete = D_TRUE;

    (void)act_target;
    last_emitted_task_count_ = 0u;

    if (!graph_builder || !access_builder) {
        return -1;
    }
    if (!inputs_ || !buffers_) {
        return 0;
    }
    if (!buffers_->audit_log) {
        return 0;
    }

    budget = dom_agent_default_budget(tier_);
    if (budget_hint() > 0u) {
        if (budget == 0u || budget_hint() < budget) {
            budget = budget_hint();
        }
    }

    if (cycle_in_progress_ == D_FALSE) {
        dom_agent_runtime_reset(&runtime_);
        dom_agent_reset_buffers(buffers_);
        cycle_in_progress_ = D_TRUE;
    }

    if (inputs_->schedule && inputs_->schedule_count > 0u && budget > 0u) {
        u32 cursor = runtime_.schedule_cursor;
        u32 remaining;
        u32 slice;
        u32 ops[] = {
            DOM_AGENT_TASK_EVALUATE_GOALS,
            DOM_AGENT_TASK_PLAN_ACTIONS,
            DOM_AGENT_TASK_VALIDATE_PLAN,
            DOM_AGENT_TASK_EMIT_COMMANDS
        };
        u32 i;
        if (cursor >= inputs_->schedule_count) {
            cursor = 0u;
            runtime_.schedule_cursor = 0u;
        }
        remaining = inputs_->schedule_count - cursor;
        if (remaining > 0u) {
            slice = remaining;
            if (slice > budget) {
                slice = budget;
            }
            for (i = 0u; i < 4u; ++i) {
                u32 op = ops[i];
                u32 local_id;
                u64 task_id;
                u64 access_id;
                u64 cost_id;
                dom_task_node node;
                dom_cost_model cost;
                dom_access_range reads[2];
                dom_access_range writes[2];
                u32 read_count = 0u;
                u32 write_count = 0u;
                dom_agent_task_params* params;

                if ((allowed_ops_mask_ & (1u << op)) == 0u) {
                    continue;
                }
                if ((op == DOM_AGENT_TASK_EVALUATE_GOALS && (!buffers_->goals || !inputs_->beliefs)) ||
                    (op == DOM_AGENT_TASK_PLAN_ACTIONS && !buffers_->plans) ||
                    (op == DOM_AGENT_TASK_VALIDATE_PLAN && (!buffers_->plans || !inputs_->capabilities)) ||
                    (op == DOM_AGENT_TASK_EMIT_COMMANDS && !buffers_->commands)) {
                    continue;
                }

                params = dom_agent_params_for_op(params_, op);
                if (!params) {
                    continue;
                }
                params->op = op;
                params->start_index = cursor;
                params->count = slice;

                local_id = dom_agent_local_id_for_op(op);
                task_id = dom_work_graph_builder_make_id(system_id_, local_id, DOM_WORK_ID_TASK);
                access_id = dom_work_graph_builder_make_id(system_id_, local_id, DOM_WORK_ID_ACCESS);
                cost_id = dom_work_graph_builder_make_id(system_id_, local_id, DOM_WORK_ID_COST);

                node.task_id = task_id;
                node.system_id = system_id_;
                node.category = DOM_TASK_AUTHORITATIVE;
                node.determinism_class = DOM_DET_ORDERED;
                node.fidelity_tier = dom_agent_task_fidelity(tier_);
                node.next_due_tick = DOM_EXEC_TICK_INVALID;
                node.access_set_id = access_id;
                node.cost_model_id = cost_id;
                node.law_targets = law_targets_;
                node.law_target_count = law_target_count_;
                node.phase_id = op - 1u;
                node.commit_key = dom_work_graph_builder_make_commit_key(node.phase_id, task_id, 0u);
                node.law_scope_ref = law_scope_ref_;
                node.actor_ref = 0u;
                node.capability_set_ref = 0u;
                node.policy_params = params;
                node.policy_params_size = (u32)sizeof(*params);

                cost.cost_id = cost_id;
                cost.cpu_upper_bound = slice;
                cost.memory_upper_bound = 1u;
                cost.bandwidth_upper_bound = 1u;
                cost.latency_class = DOM_LATENCY_MEDIUM;
                cost.degradation_priority = 1;

                if (op == DOM_AGENT_TASK_EVALUATE_GOALS) {
                    reads[read_count].kind = DOM_RANGE_COMPONENT_SET;
                    reads[read_count].component_id = DOM_AGENT_COMPONENT_SCHEDULE;
                    reads[read_count].field_id = DOM_AGENT_FIELD_DEFAULT;
                    reads[read_count].start_id = 0u;
                    reads[read_count].end_id = 0u;
                    reads[read_count].set_id = inputs_->schedule_set_id;
                    read_count += 1u;

                    reads[read_count].kind = DOM_RANGE_COMPONENT_SET;
                    reads[read_count].component_id = DOM_AGENT_COMPONENT_BELIEF;
                    reads[read_count].field_id = DOM_AGENT_FIELD_DEFAULT;
                    reads[read_count].start_id = 0u;
                    reads[read_count].end_id = 0u;
                    reads[read_count].set_id = inputs_->belief_set_id;
                    read_count += 1u;

                    writes[write_count].kind = DOM_RANGE_COMPONENT_SET;
                    writes[write_count].component_id = DOM_AGENT_COMPONENT_GOAL;
                    writes[write_count].field_id = DOM_AGENT_FIELD_DEFAULT;
                    writes[write_count].start_id = 0u;
                    writes[write_count].end_id = 0u;
                    writes[write_count].set_id = buffers_->goal_set_id;
                    write_count += 1u;
                } else if (op == DOM_AGENT_TASK_PLAN_ACTIONS) {
                    reads[read_count].kind = DOM_RANGE_COMPONENT_SET;
                    reads[read_count].component_id = DOM_AGENT_COMPONENT_GOAL;
                    reads[read_count].field_id = DOM_AGENT_FIELD_DEFAULT;
                    reads[read_count].start_id = 0u;
                    reads[read_count].end_id = 0u;
                    reads[read_count].set_id = buffers_->goal_set_id;
                    read_count += 1u;

                    writes[write_count].kind = DOM_RANGE_COMPONENT_SET;
                    writes[write_count].component_id = DOM_AGENT_COMPONENT_PLAN;
                    writes[write_count].field_id = DOM_AGENT_FIELD_DEFAULT;
                    writes[write_count].start_id = 0u;
                    writes[write_count].end_id = 0u;
                    writes[write_count].set_id = buffers_->plan_set_id;
                    write_count += 1u;
                } else if (op == DOM_AGENT_TASK_VALIDATE_PLAN) {
                    reads[read_count].kind = DOM_RANGE_COMPONENT_SET;
                    reads[read_count].component_id = DOM_AGENT_COMPONENT_PLAN;
                    reads[read_count].field_id = DOM_AGENT_FIELD_DEFAULT;
                    reads[read_count].start_id = 0u;
                    reads[read_count].end_id = 0u;
                    reads[read_count].set_id = buffers_->plan_set_id;
                    read_count += 1u;

                    reads[read_count].kind = DOM_RANGE_COMPONENT_SET;
                    reads[read_count].component_id = DOM_AGENT_COMPONENT_CAPABILITY;
                    reads[read_count].field_id = DOM_AGENT_FIELD_DEFAULT;
                    reads[read_count].start_id = 0u;
                    reads[read_count].end_id = 0u;
                    reads[read_count].set_id = inputs_->capability_set_id;
                    read_count += 1u;

                    writes[write_count].kind = DOM_RANGE_COMPONENT_SET;
                    writes[write_count].component_id = DOM_AGENT_COMPONENT_PLAN;
                    writes[write_count].field_id = DOM_AGENT_FIELD_DEFAULT;
                    writes[write_count].start_id = 0u;
                    writes[write_count].end_id = 0u;
                    writes[write_count].set_id = buffers_->plan_set_id;
                    write_count += 1u;
                } else if (op == DOM_AGENT_TASK_EMIT_COMMANDS) {
                    reads[read_count].kind = DOM_RANGE_COMPONENT_SET;
                    reads[read_count].component_id = DOM_AGENT_COMPONENT_PLAN;
                    reads[read_count].field_id = DOM_AGENT_FIELD_DEFAULT;
                    reads[read_count].start_id = 0u;
                    reads[read_count].end_id = 0u;
                    reads[read_count].set_id = buffers_->plan_set_id;
                    read_count += 1u;

                    writes[write_count].kind = DOM_RANGE_COMPONENT_SET;
                    writes[write_count].component_id = DOM_AGENT_COMPONENT_COMMAND;
                    writes[write_count].field_id = DOM_AGENT_FIELD_DEFAULT;
                    writes[write_count].start_id = 0u;
                    writes[write_count].end_id = 0u;
                    writes[write_count].set_id = buffers_->command_set_id;
                    write_count += 1u;
                }

                writes[write_count].kind = DOM_RANGE_COMPONENT_SET;
                writes[write_count].component_id = DOM_AGENT_COMPONENT_AUDIT;
                writes[write_count].field_id = DOM_AGENT_FIELD_DEFAULT;
                writes[write_count].start_id = 0u;
                writes[write_count].end_id = 0u;
                writes[write_count].set_id = buffers_->audit_set_id;
                write_count += 1u;

                if (dom_agent_emit_task_node(graph_builder, access_builder, &node, &cost,
                                             reads, read_count, writes, write_count) != 0) {
                    return -2;
                }
                if (prev_task_id != 0u) {
                    dom_dependency_edge edge;
                    edge.from_task_id = prev_task_id;
                    edge.to_task_id = task_id;
                    edge.reason_id = 0u;
                    if (dom_work_graph_builder_add_dependency(graph_builder, &edge) != 0) {
                        return -3;
                    }
                }
                prev_task_id = task_id;
                last_emitted_task_count_ += 1u;
            }
            runtime_.schedule_cursor = cursor + slice;
            budget -= slice;
        }
    }

    if (inputs_->doctrines && inputs_->doctrine_count > 0u && budget > 0u) {
        u32 cursor = runtime_.doctrine_cursor;
        u32 remaining;
        u32 slice;
        u32 ops[] = { DOM_AGENT_TASK_APPLY_DOCTRINE, DOM_AGENT_TASK_UPDATE_ROLES };
        u32 i;
        if (cursor >= inputs_->doctrine_count) {
            cursor = 0u;
            runtime_.doctrine_cursor = 0u;
        }
        remaining = inputs_->doctrine_count - cursor;
        if (remaining > 0u) {
            slice = remaining;
            if (slice > budget) {
                slice = budget;
            }
            for (i = 0u; i < 2u; ++i) {
                u32 op = ops[i];
                u32 local_id;
                u64 task_id;
                u64 access_id;
                u64 cost_id;
                dom_task_node node;
                dom_cost_model cost;
                dom_access_range reads[2];
                dom_access_range writes[2];
                u32 read_count = 0u;
                u32 write_count = 0u;
                dom_agent_task_params* params;

                if ((allowed_ops_mask_ & (1u << op)) == 0u) {
                    continue;
                }
                if (!buffers_->roles) {
                    continue;
                }
                params = dom_agent_params_for_op(params_, op);
                if (!params) {
                    continue;
                }
                params->op = op;
                params->start_index = cursor;
                params->count = slice;

                local_id = dom_agent_local_id_for_op(op);
                task_id = dom_work_graph_builder_make_id(system_id_, local_id, DOM_WORK_ID_TASK);
                access_id = dom_work_graph_builder_make_id(system_id_, local_id, DOM_WORK_ID_ACCESS);
                cost_id = dom_work_graph_builder_make_id(system_id_, local_id, DOM_WORK_ID_COST);

                node.task_id = task_id;
                node.system_id = system_id_;
                node.category = DOM_TASK_AUTHORITATIVE;
                node.determinism_class = DOM_DET_ORDERED;
                node.fidelity_tier = dom_agent_task_fidelity(tier_);
                node.next_due_tick = DOM_EXEC_TICK_INVALID;
                node.access_set_id = access_id;
                node.cost_model_id = cost_id;
                node.law_targets = law_targets_;
                node.law_target_count = law_target_count_;
                node.phase_id = 5u + i;
                node.commit_key = dom_work_graph_builder_make_commit_key(node.phase_id, task_id, 0u);
                node.law_scope_ref = law_scope_ref_;
                node.actor_ref = 0u;
                node.capability_set_ref = 0u;
                node.policy_params = params;
                node.policy_params_size = (u32)sizeof(*params);

                cost.cost_id = cost_id;
                cost.cpu_upper_bound = slice;
                cost.memory_upper_bound = 1u;
                cost.bandwidth_upper_bound = 1u;
                cost.latency_class = DOM_LATENCY_LOW;
                cost.degradation_priority = 1;

                if (op == DOM_AGENT_TASK_APPLY_DOCTRINE) {
                    reads[read_count].kind = DOM_RANGE_COMPONENT_SET;
                    reads[read_count].component_id = DOM_AGENT_COMPONENT_DOCTRINE;
                    reads[read_count].field_id = DOM_AGENT_FIELD_DEFAULT;
                    reads[read_count].start_id = 0u;
                    reads[read_count].end_id = 0u;
                    reads[read_count].set_id = inputs_->doctrine_set_id;
                    read_count += 1u;
                } else {
                    reads[read_count].kind = DOM_RANGE_COMPONENT_SET;
                    reads[read_count].component_id = DOM_AGENT_COMPONENT_ROLE;
                    reads[read_count].field_id = DOM_AGENT_FIELD_DEFAULT;
                    reads[read_count].start_id = 0u;
                    reads[read_count].end_id = 0u;
                    reads[read_count].set_id = buffers_->role_set_id;
                    read_count += 1u;
                }

                writes[write_count].kind = DOM_RANGE_COMPONENT_SET;
                writes[write_count].component_id = DOM_AGENT_COMPONENT_ROLE;
                writes[write_count].field_id = DOM_AGENT_FIELD_DEFAULT;
                writes[write_count].start_id = 0u;
                writes[write_count].end_id = 0u;
                writes[write_count].set_id = buffers_->role_set_id;
                write_count += 1u;

                writes[write_count].kind = DOM_RANGE_COMPONENT_SET;
                writes[write_count].component_id = DOM_AGENT_COMPONENT_AUDIT;
                writes[write_count].field_id = DOM_AGENT_FIELD_DEFAULT;
                writes[write_count].start_id = 0u;
                writes[write_count].end_id = 0u;
                writes[write_count].set_id = buffers_->audit_set_id;
                write_count += 1u;

                if (dom_agent_emit_task_node(graph_builder, access_builder, &node, &cost,
                                             reads, read_count, writes, write_count) != 0) {
                    return -4;
                }
                if (prev_task_id != 0u) {
                    dom_dependency_edge edge;
                    edge.from_task_id = prev_task_id;
                    edge.to_task_id = task_id;
                    edge.reason_id = 0u;
                    if (dom_work_graph_builder_add_dependency(graph_builder, &edge) != 0) {
                        return -5;
                    }
                }
                prev_task_id = task_id;
                last_emitted_task_count_ += 1u;
            }
            runtime_.doctrine_cursor = cursor + slice;
            budget -= slice;
        }
    }

    if (inputs_->population && inputs_->population_count > 0u && budget > 0u) {
        u32 cursor = runtime_.population_cursor;
        u32 remaining;
        u32 slice;
        u32 ops[] = {
            DOM_AGENT_TASK_AGGREGATE_COHORTS,
            DOM_AGENT_TASK_REFINE_INDIVIDUALS,
            DOM_AGENT_TASK_COLLAPSE_INDIVIDUALS
        };
        u32 i;
        if (cursor >= inputs_->population_count) {
            cursor = 0u;
            runtime_.population_cursor = 0u;
        }
        remaining = inputs_->population_count - cursor;
        if (remaining > 0u) {
            slice = remaining;
            if (slice > budget) {
                slice = budget;
            }
            for (i = 0u; i < 3u; ++i) {
                u32 op = ops[i];
                u32 local_id;
                u64 task_id;
                u64 access_id;
                u64 cost_id;
                dom_task_node node;
                dom_cost_model cost;
                dom_access_range reads[1];
                dom_access_range writes[2];
                u32 read_count = 0u;
                u32 write_count = 0u;
                dom_agent_task_params* params;

                if ((allowed_ops_mask_ & (1u << op)) == 0u) {
                    continue;
                }
                if (op == DOM_AGENT_TASK_AGGREGATE_COHORTS && !buffers_->cohorts) {
                    continue;
                }
                params = dom_agent_params_for_op(params_, op);
                if (!params) {
                    continue;
                }
                params->op = op;
                params->start_index = cursor;
                params->count = slice;

                local_id = dom_agent_local_id_for_op(op);
                task_id = dom_work_graph_builder_make_id(system_id_, local_id, DOM_WORK_ID_TASK);
                access_id = dom_work_graph_builder_make_id(system_id_, local_id, DOM_WORK_ID_ACCESS);
                cost_id = dom_work_graph_builder_make_id(system_id_, local_id, DOM_WORK_ID_COST);

                node.task_id = task_id;
                node.system_id = system_id_;
                node.category = DOM_TASK_AUTHORITATIVE;
                node.determinism_class = DOM_DET_ORDERED;
                node.fidelity_tier = dom_agent_task_fidelity(tier_);
                node.next_due_tick = DOM_EXEC_TICK_INVALID;
                node.access_set_id = access_id;
                node.cost_model_id = cost_id;
                node.law_targets = law_targets_;
                node.law_target_count = law_target_count_;
                node.phase_id = 7u + i;
                node.commit_key = dom_work_graph_builder_make_commit_key(node.phase_id, task_id, 0u);
                node.law_scope_ref = law_scope_ref_;
                node.actor_ref = 0u;
                node.capability_set_ref = 0u;
                node.policy_params = params;
                node.policy_params_size = (u32)sizeof(*params);

                cost.cost_id = cost_id;
                cost.cpu_upper_bound = slice;
                cost.memory_upper_bound = 1u;
                cost.bandwidth_upper_bound = 1u;
                cost.latency_class = DOM_LATENCY_LOW;
                cost.degradation_priority = 1;

                reads[read_count].kind = DOM_RANGE_COMPONENT_SET;
                reads[read_count].component_id = DOM_AGENT_COMPONENT_POPULATION;
                reads[read_count].field_id = DOM_AGENT_FIELD_DEFAULT;
                reads[read_count].start_id = 0u;
                reads[read_count].end_id = 0u;
                reads[read_count].set_id = inputs_->population_set_id;
                read_count += 1u;

                writes[write_count].kind = DOM_RANGE_COMPONENT_SET;
                writes[write_count].component_id = DOM_AGENT_COMPONENT_POPULATION;
                writes[write_count].field_id = DOM_AGENT_FIELD_DEFAULT;
                writes[write_count].start_id = 0u;
                writes[write_count].end_id = 0u;
                writes[write_count].set_id = inputs_->population_set_id;
                if (op != DOM_AGENT_TASK_AGGREGATE_COHORTS) {
                    write_count += 1u;
                }

                if (op == DOM_AGENT_TASK_AGGREGATE_COHORTS) {
                    writes[write_count].kind = DOM_RANGE_COMPONENT_SET;
                    writes[write_count].component_id = DOM_AGENT_COMPONENT_COHORT;
                    writes[write_count].field_id = DOM_AGENT_FIELD_DEFAULT;
                    writes[write_count].start_id = 0u;
                    writes[write_count].end_id = 0u;
                    writes[write_count].set_id = buffers_->cohort_set_id;
                    write_count += 1u;
                }

                writes[write_count].kind = DOM_RANGE_COMPONENT_SET;
                writes[write_count].component_id = DOM_AGENT_COMPONENT_AUDIT;
                writes[write_count].field_id = DOM_AGENT_FIELD_DEFAULT;
                writes[write_count].start_id = 0u;
                writes[write_count].end_id = 0u;
                writes[write_count].set_id = buffers_->audit_set_id;
                write_count += 1u;

                if (dom_agent_emit_task_node(graph_builder, access_builder, &node, &cost,
                                             reads, read_count, writes, write_count) != 0) {
                    return -6;
                }
                if (prev_task_id != 0u) {
                    dom_dependency_edge edge;
                    edge.from_task_id = prev_task_id;
                    edge.to_task_id = task_id;
                    edge.reason_id = 0u;
                    if (dom_work_graph_builder_add_dependency(graph_builder, &edge) != 0) {
                        return -7;
                    }
                }
                prev_task_id = task_id;
                last_emitted_task_count_ += 1u;
            }
            runtime_.population_cursor = cursor + slice;
            budget -= slice;
        }
    }

    if ((inputs_->schedule && inputs_->schedule_count > 0u) ||
        (inputs_->doctrines && inputs_->doctrine_count > 0u) ||
        (inputs_->population && inputs_->population_count > 0u)) {
        has_work = D_TRUE;
    }

    if (inputs_->schedule && runtime_.schedule_cursor < inputs_->schedule_count) {
        cycle_complete = D_FALSE;
    }
    if (inputs_->doctrines && runtime_.doctrine_cursor < inputs_->doctrine_count) {
        cycle_complete = D_FALSE;
    }
    if (inputs_->population && runtime_.population_cursor < inputs_->population_count) {
        cycle_complete = D_FALSE;
    }

    if (has_work == D_FALSE) {
        cycle_in_progress_ = D_FALSE;
    }

    if (cycle_complete == D_TRUE && has_work == D_TRUE) {
        dom_agent_runtime_reset(&runtime_);
        cycle_in_progress_ = D_FALSE;
    }

    cadence = dom_agent_default_cadence(tier_);
    next_due_tick_ = dom_agent_next_due(act_now, cadence, has_work ? D_TRUE : cycle_in_progress_);
    return 0;
}
