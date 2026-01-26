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

#include "dominium/agents/agent_authority.h"
#include "dominium/agents/agent_belief_update.h"
#include "dominium/agents/agent_constraint.h"
#include "dominium/agents/agent_contract.h"
#include "dominium/agents/agent_planner.h"
#include "dominium/agents/delegation.h"
#include "domino/core/dom_time_core.h"
#include "domino/core/types.h"
#include "domino/provenance.h"

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
    DOM_AGENT_AUDIT_COLLAPSE = 9,
    DOM_AGENT_AUDIT_GOAL_OSCILLATE = 10,
    DOM_AGENT_AUDIT_COMMAND_OUTCOME = 11,
    DOM_AGENT_AUDIT_INSTITUTION_FORM = 12,
    DOM_AGENT_AUDIT_INSTITUTION_COLLAPSE = 13,
    DOM_AGENT_AUDIT_AUTHORITY_GRANT = 14,
    DOM_AGENT_AUDIT_AUTHORITY_REVOKE = 15,
    DOM_AGENT_AUDIT_CONSTRAINT_APPLY = 16,
    DOM_AGENT_AUDIT_CONSTRAINT_BLOCK = 17,
    DOM_AGENT_AUDIT_CONTRACT_BIND = 18,
    DOM_AGENT_AUDIT_CONTRACT_FAIL = 19,
    DOM_AGENT_AUDIT_CONFLICT_BEGIN = 20,
    DOM_AGENT_AUDIT_CONFLICT_RESOLVE = 21,
    DOM_AGENT_AUDIT_HISTORY_RECORD = 22
} dom_agent_audit_kind;

typedef struct dom_agent_audit_entry {
    u64 event_id;
    u64 agent_id;
    dom_act_time_t act_time;
    dom_provenance_id provenance_id;
    u32 kind;
    u64 subject_id;
    u64 related_id;
    i64 amount;
} dom_agent_audit_entry;

typedef struct dom_agent_audit_log {
    dom_agent_audit_entry* entries;
    u32 count;
    u32 capacity;
    u64 next_event_id;
    dom_act_time_t current_act;
    dom_provenance_id provenance_id;
} dom_agent_audit_log;

void dom_agent_audit_init(dom_agent_audit_log* log,
                          dom_agent_audit_entry* storage,
                          u32 capacity,
                          u64 start_id);
void dom_agent_audit_set_context(dom_agent_audit_log* log,
                                 dom_act_time_t act_time,
                                 dom_provenance_id provenance_id);
int dom_agent_audit_record(dom_agent_audit_log* log,
                           u64 agent_id,
                           u32 kind,
                           u64 subject_id,
                           u64 related_id,
                           i64 amount);

typedef struct dom_agent_schedule_item {
    u64 agent_id;
    dom_act_time_t next_due_tick;
    u32 status;
    u32 compute_budget;
    u64 active_goal_id;
    u64 active_plan_id;
    u32 resume_step;
} dom_agent_schedule_item;

typedef struct dom_agent_belief {
    u64 agent_id;
    u32 knowledge_mask;
    u32 hunger_level;
    u32 threat_level;
    u32 risk_tolerance_q16;
    u32 epistemic_confidence_q16;
    u64 known_resource_ref;
    u64 known_threat_ref;
    u64 known_destination_ref;
} dom_agent_belief;

typedef struct dom_agent_goal_choice {
    u64 agent_id;
    u64 goal_id;
    u32 priority;
    u32 confidence_q16;
    u32 refusal;
    u32 flags;
} dom_agent_goal_choice;

typedef struct dom_agent_goal_buffer {
    dom_agent_goal_choice* entries;
    u32 count;
    u32 capacity;
} dom_agent_goal_buffer;

typedef struct dom_agent_plan {
    agent_plan plan;
    u64 agent_id;
    u32 valid;
    u32 refusal;
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
    u64 plan_id;
    u64 goal_id;
    u32 step_index;
    dom_process_id process_id;
    u32 process_kind;
    u64 target_id;
    u32 required_capability_mask;
    u32 required_authority_mask;
    u32 expected_cost_units;
    u32 epistemic_gap_mask;
    u32 confidence_q16;
    u32 failure_mode_id;
    u32 flags;
} dom_agent_command;

typedef struct dom_agent_command_buffer {
    dom_agent_command* entries;
    u32 count;
    u32 capacity;
    u64 next_id;
} dom_agent_command_buffer;

typedef struct dom_agent_capability {
    u64 agent_id;
    u32 capability_mask;
    u32 authority_mask;
} dom_agent_capability;

typedef struct dom_agent_command_outcome {
    u64 command_id;
    u64 agent_id;
    u64 plan_id;
    u64 goal_id;
    u32 step_index;
    int success;
    u32 failure_mode_id;
    u32 refusal;
    u32 knowledge_clear_mask;
    i32 hunger_delta;
    i32 threat_delta;
} dom_agent_command_outcome;

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
                                   agent_goal_registry* goals,
                                   const dom_agent_belief* beliefs,
                                   u32 belief_count,
                                   const dom_agent_capability* caps,
                                   u32 cap_count,
                                   dom_agent_goal_buffer* goals_out,
                                   dom_agent_audit_log* audit);

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
                                 dom_agent_audit_log* audit);

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
                                  dom_agent_audit_log* audit);

u32 dom_agent_emit_commands_slice(dom_agent_plan_buffer* plans,
                                  u32 start_index,
                                  u32 max_count,
                                  dom_agent_command_buffer* commands,
                                  dom_agent_audit_log* audit);

int dom_agent_apply_command_outcome(agent_goal_registry* goals,
                                    agent_belief_state* beliefs,
                                    u32 belief_count,
                                    const dom_agent_command_outcome* outcome,
                                    dom_act_time_t now_act,
                                    dom_agent_audit_log* audit);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_RULES_AGENTS_AGENT_PLANNING_TASKS_H */
