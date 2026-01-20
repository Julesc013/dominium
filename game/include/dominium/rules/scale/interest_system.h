/*
FILE: include/dominium/rules/scale/interest_system.h
MODULE: Dominium
LAYER / SUBSYSTEM: Game / scale rules
RESPONSIBILITY: Work IR-based interest management system (authoritative, IR-only).
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Task emission and ordering are deterministic.
*/
#ifndef DOMINIUM_RULES_SCALE_INTEREST_SYSTEM_H
#define DOMINIUM_RULES_SCALE_INTEREST_SYSTEM_H

#include "dominium/execution/system_iface.h"
#include "dominium/interest_sources.h"
#include "dominium/fidelity.h"
#include "dominium/rules/scale/relevance_transitions.h"

enum dom_interest_task_op {
    DOM_INTEREST_TASK_COLLECT_SOURCES = 1,
    DOM_INTEREST_TASK_MERGE = 2,
    DOM_INTEREST_TASK_APPLY_HYSTERESIS = 3,
    DOM_INTEREST_TASK_BUILD_REQUESTS = 4
};

typedef struct dom_interest_source_feed {
    dom_interest_source_list list;
    u64 set_id;
} dom_interest_source_feed;

typedef struct dom_interest_inputs {
    dom_interest_source_feed sources[DOM_INTEREST_SOURCE_COUNT];
    dom_interest_policy policy;
    dom_fidelity_tier refine_tier;
    dom_fidelity_tier collapse_tier;
    u32 request_reason;
} dom_interest_inputs;

typedef struct dom_interest_buffers {
    dom_interest_set* scratch_set;
    dom_interest_set* merged_set;
    dom_interest_state* relevance_states;
    u32 relevance_count;
    dom_interest_transition* transitions;
    u32 transition_capacity;
    dom_fidelity_request* requests;
    u32 request_capacity;
    u64 scratch_set_id;
    u64 merged_set_id;
    u64 state_set_id;
    u64 transition_set_id;
    u64 request_set_id;
} dom_interest_buffers;

typedef struct dom_interest_task_params {
    u32 op;
    u32 source_kind;
    u32 start_index;
    u32 count;
    u32 reason;
    u32 refine_tier;
    u32 collapse_tier;
} dom_interest_task_params;

typedef enum dom_interest_migration_state {
    DOM_INTEREST_STATE_IR_ONLY = 3
} dom_interest_migration_state;

class InterestSystem : public ISimSystem {
public:
    InterestSystem();

    int init(const dom_interest_inputs* inputs,
             const dom_interest_buffers* buffers);

    void set_inputs(const dom_interest_inputs* inputs);
    void set_buffers(const dom_interest_buffers* buffers);
    void set_allowed_sources_mask(u32 mask);
    void set_next_due_tick(dom_act_time_t tick);
    void set_migration_state(dom_interest_migration_state state);

    dom_interest_migration_state migration_state() const;
    u32 last_emitted_task_count() const;
    u32 last_emitted_source_mask() const;
    dom_interest_runtime_state* runtime_state();
    const dom_interest_runtime_state* runtime_state() const;

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
    dom_interest_migration_state migration_state_;
    u32 allowed_sources_mask_;
    u32 last_emitted_task_count_;
    u32 last_emitted_source_mask_;
    d_bool cycle_in_progress_;
    dom_interest_task_params params_[DOM_INTEREST_SOURCE_COUNT + 3];
    dom_interest_runtime_state runtime_;

    const dom_interest_inputs* inputs_;
    const dom_interest_buffers* buffers_;
};

#endif /* DOMINIUM_RULES_SCALE_INTEREST_SYSTEM_H */
