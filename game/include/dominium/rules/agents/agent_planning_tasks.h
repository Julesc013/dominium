/*
FILE: include/dominium/rules/agents/agent_planning_tasks.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / agents
RESPONSIBILITY: Work IR task helpers for agent planning and command emission.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C89/C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Planning and command emission are deterministic.
*/
#ifndef DOMINIUM_RULES_AGENTS_AGENT_PLANNING_TASKS_H
#define DOMINIUM_RULES_AGENTS_AGENT_PLANNING_TASKS_H

#include "domino/core/types.h"
#include "domino/core/dom_time_core.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef enum dom_agent_audit_kind {
    DOM_AGENT_AUDIT_GOAL_EVAL = 1,
    DOM_AGENT_AUDIT_PLAN_CREATE = 2,
    DOM_AGENT_AUDIT_PLAN_REFUSE = 3,
    DOM_AGENT_AUDIT_COMMAND_EMIT = 4,
    DOM_AGENT_AUDIT_DOCTRINE_APPLY = 5,
    DOM_AGENT_AUDIT_ROLE_UPDATE = 6,
    DOM_AGENT_AUDIT_AGGREGATE = 7,
    DOM_AGENT_AUDIT_REFINE = 8,
    DOM_AGENT_AUDIT_COLLAPSE = 9
} dom_agent_audit_kind;

typedef struct dom_agent_audit_entry {
    u64 event_id;
    u32 kind;
    u64 primary_id;
    i64 amount;
} dom_agent_audit_entry;

typedef struct dom_agent_audit_log {
    dom_agent_audit_entry* entries;
    u32 count;
    u32 capacity;
    u64 next_event_id;
} dom_agent_audit_log;

void dom_agent_audit_init(dom_agent_audit_log* log,
                          dom_agent_audit_entry* storage,
                          u32 capacity,
                          u64 start_id);
int dom_agent_audit_record(dom_agent_audit_log* log,
                           u32 kind,
                           u64 primary_id,
                           i64 amount);

typedef struct dom_agent_schedule_item {
    u64 agent_id;
    dom_act_time_t next_due_tick;
    u32 status;
} dom_agent_schedule_item;

typedef struct dom_agent_belief {
    u64 agent_id;
    u32 belief_code;
    u32 weight;
} dom_agent_belief;

typedef struct dom_agent_goal_choice {
    u64 agent_id;
    u32 goal_code;
    u32 priority;
} dom_agent_goal_choice;

typedef struct dom_agent_goal_buffer {
    dom_agent_goal_choice* entries;
    u32 count;
    u32 capacity;
} dom_agent_goal_buffer;

typedef struct dom_agent_plan {
    u64 plan_id;
    u64 agent_id;
    u32 goal_code;
    u32 action_code;
    u32 valid;
} dom_agent_plan;

typedef struct dom_agent_plan_buffer {
    dom_agent_plan* entries;
    u32 count;
    u32 capacity;
    u64 next_id;
} dom_agent_plan_buffer;

typedef struct dom_agent_command {
    u64 command_id;
    u64 agent_id;
    u32 action_code;
    u64 target_id;
} dom_agent_command;

typedef struct dom_agent_command_buffer {
    dom_agent_command* entries;
    u32 count;
    u32 capacity;
    u64 next_id;
} dom_agent_command_buffer;

typedef struct dom_agent_capability {
    u64 agent_id;
    u32 allowed_action_mask;
} dom_agent_capability;

void dom_agent_goal_buffer_init(dom_agent_goal_buffer* buffer,
                                dom_agent_goal_choice* storage,
                                u32 capacity);
void dom_agent_goal_buffer_reset(dom_agent_goal_buffer* buffer);
int dom_agent_goal_buffer_set(dom_agent_goal_buffer* buffer,
                              u32 index,
                              const dom_agent_goal_choice* choice);

void dom_agent_plan_buffer_init(dom_agent_plan_buffer* buffer,
                                dom_agent_plan* storage,
                                u32 capacity,
                                u64 start_id);
void dom_agent_plan_buffer_reset(dom_agent_plan_buffer* buffer);
int dom_agent_plan_buffer_set(dom_agent_plan_buffer* buffer,
                              u32 index,
                              const dom_agent_plan* plan);

void dom_agent_command_buffer_init(dom_agent_command_buffer* buffer,
                                   dom_agent_command* storage,
                                   u32 capacity,
                                   u64 start_id);
void dom_agent_command_buffer_reset(dom_agent_command_buffer* buffer);
int dom_agent_command_buffer_append(dom_agent_command_buffer* buffer,
                                    const dom_agent_command* command);

u32 dom_agent_evaluate_goals_slice(const dom_agent_schedule_item* schedule,
                                   u32 schedule_count,
                                   u32 start_index,
                                   u32 max_count,
                                   const dom_agent_belief* beliefs,
                                   u32 belief_count,
                                   dom_agent_goal_buffer* goals,
                                   dom_agent_audit_log* audit);

u32 dom_agent_plan_actions_slice(const dom_agent_goal_buffer* goals,
                                 u32 start_index,
                                 u32 max_count,
                                 dom_agent_plan_buffer* plans,
                                 dom_agent_audit_log* audit);

u32 dom_agent_validate_plan_slice(dom_agent_plan_buffer* plans,
                                  u32 start_index,
                                  u32 max_count,
                                  const dom_agent_capability* caps,
                                  u32 cap_count,
                                  dom_agent_audit_log* audit);

u32 dom_agent_emit_commands_slice(const dom_agent_plan_buffer* plans,
                                  u32 start_index,
                                  u32 max_count,
                                  dom_agent_command_buffer* commands,
                                  dom_agent_audit_log* audit);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_RULES_AGENTS_AGENT_PLANNING_TASKS_H */
