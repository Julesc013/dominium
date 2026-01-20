/*
FILE: include/dominium/rules/economy/economy_system.h
MODULE: Dominium
LAYER / SUBSYSTEM: Game / economy rules
RESPONSIBILITY: Work IR-based economy system (authoritative, IR-only).
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Task emission and ordering are deterministic.
*/
#ifndef DOMINIUM_RULES_ECONOMY_ECONOMY_SYSTEM_H
#define DOMINIUM_RULES_ECONOMY_ECONOMY_SYSTEM_H

#include "dominium/execution/system_iface.h"
#include "dominium/rules/economy/ledger_tasks.h"
#include "dominium/fidelity.h"

enum dom_economy_task_op {
    DOM_ECON_TASK_LEDGER_TRANSFERS = 1,
    DOM_ECON_TASK_CONTRACT_SETTLEMENT = 2,
    DOM_ECON_TASK_PRODUCTION_STEP = 3,
    DOM_ECON_TASK_CONSUMPTION_STEP = 4,
    DOM_ECON_TASK_MAINTENANCE_DECAY = 5
};

typedef struct dom_economy_inputs {
    const dom_ledger_transfer* transfers;
    u32 transfer_count;
    u64 transfer_set_id;

    const dom_contract_settlement* contracts;
    u32 contract_count;
    u64 contract_set_id;

    const dom_production_step* production;
    u32 production_count;
    u64 production_set_id;

    const dom_consumption_step* consumption;
    u32 consumption_count;
    u64 consumption_set_id;

    const dom_maintenance_step* maintenance;
    u32 maintenance_count;
    u64 maintenance_set_id;
} dom_economy_inputs;

typedef struct dom_economy_buffers {
    dom_ledger_state* ledger;
    dom_economy_audit_log* audit_log;
    u64 ledger_set_id;
    u64 audit_set_id;
} dom_economy_buffers;

typedef struct dom_economy_task_params {
    u32 op;
    u32 start_index;
    u32 count;
} dom_economy_task_params;

typedef enum dom_economy_migration_state {
    DOM_ECONOMY_STATE_IR_ONLY = 3
} dom_economy_migration_state;

class EconomySystem : public ISimSystem {
public:
    EconomySystem();

    int init(const dom_economy_inputs* inputs,
             const dom_economy_buffers* buffers);

    void set_inputs(const dom_economy_inputs* inputs);
    void set_buffers(const dom_economy_buffers* buffers);
    void set_allowed_ops_mask(u32 mask);
    void set_next_due_tick(dom_act_time_t tick);
    void set_migration_state(dom_economy_migration_state state);

    dom_economy_migration_state migration_state() const;
    u32 last_emitted_task_count() const;
    dom_economy_runtime_state* runtime_state();
    const dom_economy_runtime_state* runtime_state() const;

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
    dom_economy_migration_state migration_state_;
    u32 allowed_ops_mask_;
    u32 last_emitted_task_count_;
    d_bool cycle_in_progress_;
    dom_economy_task_params params_[5];
    dom_economy_runtime_state runtime_;

    const dom_economy_inputs* inputs_;
    const dom_economy_buffers* buffers_;
};

#endif /* DOMINIUM_RULES_ECONOMY_ECONOMY_SYSTEM_H */
