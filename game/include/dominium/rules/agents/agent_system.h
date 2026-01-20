/*
FILE: include/dominium/rules/agents/agent_system.h
MODULE: Dominium
LAYER / SUBSYSTEM: Game / agents
RESPONSIBILITY: Work IR-based agent system (authoritative, IR-only).
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Task emission and ordering are deterministic.
*/
#ifndef DOMINIUM_RULES_AGENTS_AGENT_SYSTEM_H
#define DOMINIUM_RULES_AGENTS_AGENT_SYSTEM_H

#include "dominium/execution/system_iface.h"
#include "dominium/rules/agents/agent_planning_tasks.h"
#include "dominium/rules/agents/agent_doctrine_tasks.h"
#include "dominium/rules/agents/agent_aggregation_tasks.h"
#include "dominium/fidelity.h"

enum dom_agent_task_op {
    DOM_AGENT_TASK_EVALUATE_GOALS = 1,
    DOM_AGENT_TASK_PLAN_ACTIONS = 2,
    DOM_AGENT_TASK_VALIDATE_PLAN = 3,
    DOM_AGENT_TASK_EMIT_COMMANDS = 4,
    DOM_AGENT_TASK_APPLY_DOCTRINE = 5,
    DOM_AGENT_TASK_UPDATE_ROLES = 6,
    DOM_AGENT_TASK_AGGREGATE_COHORTS = 7,
    DOM_AGENT_TASK_REFINE_INDIVIDUALS = 8,
    DOM_AGENT_TASK_COLLAPSE_INDIVIDUALS = 9
};

typedef struct dom_agent_inputs {
    const dom_agent_schedule_item* schedule;
    u32 schedule_count;
    u64 schedule_set_id;

    const dom_agent_belief* beliefs;
    u32 belief_count;
    u64 belief_set_id;

    const dom_agent_capability* capabilities;
    u32 capability_count;
    u64 capability_set_id;

    const dom_agent_doctrine_entry* doctrines;
    u32 doctrine_count;
    u64 doctrine_set_id;

    dom_agent_population_item* population;
    u32 population_count;
    u64 population_set_id;

    const dom_agent_aggregation_policy* aggregation_policy;
} dom_agent_inputs;

typedef struct dom_agent_buffers {
    dom_agent_goal_buffer* goals;
    dom_agent_plan_buffer* plans;
    dom_agent_command_buffer* commands;
    dom_agent_role_buffer* roles;
    dom_agent_cohort_buffer* cohorts;
    dom_agent_audit_log* audit_log;
    u64 goal_set_id;
    u64 plan_set_id;
    u64 command_set_id;
    u64 role_set_id;
    u64 cohort_set_id;
    u64 audit_set_id;
} dom_agent_buffers;

typedef struct dom_agent_task_params {
    u32 op;
    u32 start_index;
    u32 count;
} dom_agent_task_params;

typedef enum dom_agent_migration_state {
    DOM_AGENT_STATE_IR_ONLY = 3
} dom_agent_migration_state;

typedef struct dom_agent_runtime_state {
    u32 schedule_cursor;
    u32 doctrine_cursor;
    u32 population_cursor;
} dom_agent_runtime_state;

class AgentSystem : public ISimSystem {
public:
    AgentSystem();

    int init(const dom_agent_inputs* inputs,
             const dom_agent_buffers* buffers);

    void set_inputs(const dom_agent_inputs* inputs);
    void set_buffers(const dom_agent_buffers* buffers);
    void set_allowed_ops_mask(u32 mask);
    void set_next_due_tick(dom_act_time_t tick);
    void set_migration_state(dom_agent_migration_state state);

    dom_agent_migration_state migration_state() const;
    u32 last_emitted_task_count() const;
    dom_agent_runtime_state* runtime_state();
    const dom_agent_runtime_state* runtime_state() const;

    virtual u64 system_id() const;
    virtual d_bool is_sim_affecting() const;
    virtual const u32* law_targets(u32* out_count) const;
    virtual dom_act_time_t get_next_due_tick() const;
    virtual int emit_tasks(dom_act_time_t act_now,
                           dom_act_time_t act_target,
                           dom_work_graph_builder* graph_builder,
                           dom_access_set_builder* access_builder);
    virtual void degrade(dom_fidelity_tier tier, u32 reason);

private:
    u64 system_id_;
    u32 law_targets_[2];
    u32 law_target_count_;
    u64 law_scope_ref_;
    dom_fidelity_tier tier_;
    dom_act_time_t next_due_tick_;
    dom_agent_migration_state migration_state_;
    u32 allowed_ops_mask_;
    u32 last_emitted_task_count_;
    d_bool cycle_in_progress_;
    dom_agent_task_params params_[9];
    dom_agent_runtime_state runtime_;

    const dom_agent_inputs* inputs_;
    const dom_agent_buffers* buffers_;
};

#endif /* DOMINIUM_RULES_AGENTS_AGENT_SYSTEM_H */
