/*
FILE: include/dominium/rules/war/war_system.h
MODULE: Dominium
LAYER / SUBSYSTEM: Game / war rules
RESPONSIBILITY: Work IR-based war system (authoritative, IR-only).
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Task emission and ordering are deterministic.
*/
#ifndef DOMINIUM_RULES_WAR_WAR_SYSTEM_H
#define DOMINIUM_RULES_WAR_WAR_SYSTEM_H

#include "dominium/execution/system_iface.h"
#include "dominium/rules/war/war_tasks_engagement.h"
#include "dominium/rules/war/war_tasks_occupation.h"
#include "dominium/rules/war/war_tasks_interdiction.h"
#include "dominium/fidelity.h"

enum dom_war_task_op {
    DOM_WAR_TASK_ENGAGEMENT_ADMIT = 1,
    DOM_WAR_TASK_ENGAGEMENT_RESOLVE = 2,
    DOM_WAR_TASK_APPLY_CASUALTIES = 3,
    DOM_WAR_TASK_APPLY_EQUIPMENT_LOSSES = 4,
    DOM_WAR_TASK_UPDATE_MORALE_READINESS = 5,
    DOM_WAR_TASK_OCCUPATION_MAINTAIN = 6,
    DOM_WAR_TASK_RESISTANCE_UPDATE = 7,
    DOM_WAR_TASK_DISRUPTION_APPLY = 8,
    DOM_WAR_TASK_ROUTE_CONTROL_UPDATE = 9,
    DOM_WAR_TASK_BLOCKADE_APPLY = 10,
    DOM_WAR_TASK_INTERDICTION_SCHEDULE = 11,
    DOM_WAR_TASK_INTERDICTION_RESOLVE = 12
};

typedef struct dom_war_inputs {
    dom_war_engagement_item* engagements;
    u32 engagement_count;
    u64 engagement_set_id;

    dom_war_occupation_item* occupations;
    u32 occupation_count;
    u64 occupation_set_id;

    dom_war_resistance_item* resistances;
    u32 resistance_count;
    u64 resistance_set_id;

    dom_war_disruption_item* disruptions;
    u32 disruption_count;
    u64 disruption_set_id;

    dom_war_route_control_item* routes;
    u32 route_count;
    u64 route_set_id;

    dom_war_blockade_item* blockades;
    u32 blockade_count;
    u64 blockade_set_id;

    dom_war_interdiction_item* interdictions;
    u32 interdiction_count;
    u64 interdiction_set_id;
} dom_war_inputs;

typedef struct dom_war_buffers {
    dom_war_outcome_list* outcomes;
    dom_war_casualty_log* casualties;
    dom_war_equipment_log* equipment_losses;
    dom_war_morale_state* morale;
    dom_war_audit_log* audit_log;
    u64 outcome_set_id;
    u64 casualty_set_id;
    u64 equipment_set_id;
    u64 morale_set_id;
    u64 audit_set_id;
} dom_war_buffers;

typedef struct dom_war_task_params {
    u32 op;
    u32 start_index;
    u32 count;
} dom_war_task_params;

typedef enum dom_war_migration_state {
    DOM_WAR_STATE_IR_ONLY = 3
} dom_war_migration_state;

class WarSystem : public ISimSystem {
public:
    WarSystem();

    int init(const dom_war_inputs* inputs,
             const dom_war_buffers* buffers);

    void set_inputs(const dom_war_inputs* inputs);
    void set_buffers(const dom_war_buffers* buffers);
    void set_allowed_ops_mask(u32 mask);
    void set_next_due_tick(dom_act_time_t tick);
    void set_migration_state(dom_war_migration_state state);

    dom_war_migration_state migration_state() const;
    u32 last_emitted_task_count() const;
    dom_war_runtime_state* runtime_state();
    const dom_war_runtime_state* runtime_state() const;

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
    dom_war_migration_state migration_state_;
    u32 allowed_ops_mask_;
    u32 last_emitted_task_count_;
    d_bool cycle_in_progress_;
    dom_war_task_params params_[12];
    dom_war_runtime_state runtime_;

    const dom_war_inputs* inputs_;
    const dom_war_buffers* buffers_;
};

#endif /* DOMINIUM_RULES_WAR_WAR_SYSTEM_H */
