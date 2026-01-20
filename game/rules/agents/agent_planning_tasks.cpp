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
    if (storage && capacity > 0u) {
        memset(storage, 0, sizeof(dom_agent_audit_entry) * (size_t)capacity);
    }
}

int dom_agent_audit_record(dom_agent_audit_log* log,
                           u32 kind,
                           u64 primary_id,
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
    entry->kind = kind;
    entry->primary_id = primary_id;
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

static const dom_agent_belief* dom_agent_best_belief(const dom_agent_belief* beliefs,
                                                     u32 belief_count,
                                                     u64 agent_id)
{
    const dom_agent_belief* best = 0;
    u32 i;
    if (!beliefs) {
        return 0;
    }
    for (i = 0u; i < belief_count; ++i) {
        const dom_agent_belief* b = &beliefs[i];
        if (b->agent_id != agent_id) {
            continue;
        }
        if (!best || b->weight > best->weight ||
            (b->weight == best->weight && b->belief_code < best->belief_code)) {
            best = b;
        }
    }
    return best;
}

u32 dom_agent_evaluate_goals_slice(const dom_agent_schedule_item* schedule,
                                   u32 schedule_count,
                                   u32 start_index,
                                   u32 max_count,
                                   const dom_agent_belief* beliefs,
                                   u32 belief_count,
                                   dom_agent_goal_buffer* goals,
                                   dom_agent_audit_log* audit)
{
    u32 i;
    u32 end;
    if (!schedule || !goals || start_index >= schedule_count || max_count == 0u) {
        return 0u;
    }
    end = start_index + max_count;
    if (end > schedule_count) {
        end = schedule_count;
    }
    for (i = start_index; i < end; ++i) {
        dom_agent_goal_choice choice;
        const dom_agent_belief* best = dom_agent_best_belief(beliefs, belief_count, schedule[i].agent_id);
        choice.agent_id = schedule[i].agent_id;
        choice.goal_code = best ? best->belief_code : 0u;
        choice.priority = best ? best->weight : 0u;
        if (dom_agent_goal_buffer_set(goals, i, &choice) == 0 && audit) {
            dom_agent_audit_record(audit, DOM_AGENT_AUDIT_GOAL_EVAL,
                                   choice.agent_id, (i64)choice.goal_code);
        }
    }
    return end - start_index;
}

static u64 dom_agent_plan_id_for(u64 agent_id, u32 goal_code, u32 action_code)
{
    u64 hash = 1469598103934665603ULL;
    hash ^= agent_id;
    hash *= 1099511628211ULL;
    hash ^= (u64)goal_code;
    hash *= 1099511628211ULL;
    hash ^= (u64)action_code;
    hash *= 1099511628211ULL;
    return hash ? hash : 1u;
}

u32 dom_agent_plan_actions_slice(const dom_agent_goal_buffer* goals,
                                 u32 start_index,
                                 u32 max_count,
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
        dom_agent_plan plan;
        const dom_agent_goal_choice* goal = &goals->entries[i];
        if (goal->goal_code == 0u) {
            continue;
        }
        plan.agent_id = goal->agent_id;
        plan.goal_code = goal->goal_code;
        plan.action_code = goal->goal_code & 31u;
        plan.plan_id = dom_agent_plan_id_for(plan.agent_id, plan.goal_code, plan.action_code);
        plan.valid = 1u;
        if (dom_agent_plan_buffer_set(plans, i, &plan) == 0 && audit) {
            dom_agent_audit_record(audit, DOM_AGENT_AUDIT_PLAN_CREATE,
                                   plan.agent_id, (i64)plan.action_code);
        }
    }
    return end - start_index;
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

u32 dom_agent_validate_plan_slice(dom_agent_plan_buffer* plans,
                                  u32 start_index,
                                  u32 max_count,
                                  const dom_agent_capability* caps,
                                  u32 cap_count,
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
        u32 mask;
        if (plan->plan_id == 0u || plan->valid == 0u) {
            continue;
        }
        cap = dom_agent_find_cap(caps, cap_count, plan->agent_id);
        mask = cap ? cap->allowed_action_mask : 0u;
        if (plan->action_code >= 32u || (mask & (1u << plan->action_code)) == 0u) {
            plan->valid = 0u;
            if (audit) {
                dom_agent_audit_record(audit, DOM_AGENT_AUDIT_PLAN_REFUSE,
                                       plan->agent_id, (i64)plan->action_code);
            }
        }
    }
    return end - start_index;
}

u32 dom_agent_emit_commands_slice(const dom_agent_plan_buffer* plans,
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
        const dom_agent_plan* plan = &plans->entries[i];
        dom_agent_command cmd;
        if (plan->plan_id == 0u || plan->valid == 0u) {
            continue;
        }
        cmd.command_id = commands->next_id++;
        cmd.agent_id = plan->agent_id;
        cmd.action_code = plan->action_code;
        cmd.target_id = (u64)plan->goal_code;
        if (dom_agent_command_buffer_append(commands, &cmd) == 0 && audit) {
            dom_agent_audit_record(audit, DOM_AGENT_AUDIT_COMMAND_EMIT,
                                   cmd.agent_id, (i64)cmd.action_code);
        }
    }
    return end - start_index;
}
