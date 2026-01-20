/*
FILE: include/dominium/rules/governance/governance_system.h
MODULE: Dominium
LAYER / SUBSYSTEM: Game / governance rules
RESPONSIBILITY: Work IR-based governance system (authoritative, IR-only).
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Task emission and ordering are deterministic.
*/
#ifndef DOMINIUM_RULES_GOVERNANCE_GOVERNANCE_SYSTEM_H
#define DOMINIUM_RULES_GOVERNANCE_GOVERNANCE_SYSTEM_H

#include "dominium/execution/system_iface.h"
#include "dominium/rules/governance/legitimacy_tasks.h"
#include "dominium/fidelity.h"

enum dom_governance_task_op {
    DOM_GOV_TASK_POLICY_APPLY = 1,
    DOM_GOV_TASK_LEGITIMACY_UPDATE = 2,
    DOM_GOV_TASK_AUTHORITY_ENFORCEMENT = 3,
    DOM_GOV_TASK_LAW_LIFECYCLE = 4
};

typedef struct dom_governance_inputs {
    policy_registry* policies;
    jurisdiction_registry* jurisdictions;
    legitimacy_registry* legitimacies;
    enforcement_capacity_registry* enforcement;
    dom_governance_law_registry* law_registry;

    const dom_governance_legitimacy_event* legitimacy_events;
    u32 legitimacy_event_count;
    u64 legitimacy_event_set_id;

    const dom_governance_authority_action* authority_actions;
    u32 authority_action_count;
    u64 authority_action_set_id;

    const dom_governance_law_lifecycle_event* lifecycle_events;
    u32 lifecycle_event_count;
    u64 lifecycle_event_set_id;
} dom_governance_inputs;

typedef struct dom_governance_buffers {
    dom_governance_audit_log* audit_log;
    u64 policy_set_id;
    u64 legitimacy_set_id;
    u64 enforcement_set_id;
    u64 law_state_set_id;
    u64 audit_set_id;
} dom_governance_buffers;

typedef struct dom_governance_task_params {
    u32 op;
    u32 start_index;
    u32 count;
} dom_governance_task_params;

typedef enum dom_governance_migration_state {
    DOM_GOVERNANCE_STATE_IR_ONLY = 3
} dom_governance_migration_state;

class GovernanceSystem : public ISimSystem {
public:
    GovernanceSystem();

    int init(const dom_governance_inputs* inputs,
             const dom_governance_buffers* buffers);

    void set_inputs(const dom_governance_inputs* inputs);
    void set_buffers(const dom_governance_buffers* buffers);
    void set_allowed_ops_mask(u32 mask);
    void set_next_due_tick(dom_act_time_t tick);
    void set_migration_state(dom_governance_migration_state state);

    dom_governance_migration_state migration_state() const;
    u32 last_emitted_task_count() const;
    dom_governance_runtime_state* runtime_state();
    const dom_governance_runtime_state* runtime_state() const;

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
    dom_governance_migration_state migration_state_;
    u32 allowed_ops_mask_;
    u32 last_emitted_task_count_;
    d_bool cycle_in_progress_;
    dom_governance_task_params params_[4];
    dom_governance_runtime_state runtime_;

    const dom_governance_inputs* inputs_;
    const dom_governance_buffers* buffers_;
};

#endif /* DOMINIUM_RULES_GOVERNANCE_GOVERNANCE_SYSTEM_H */
