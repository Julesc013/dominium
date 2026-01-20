/*
FILE: include/dominium/rules/scale/world_streaming_system.h
MODULE: Dominium
LAYER / SUBSYSTEM: Game / scale rules
RESPONSIBILITY: Work IR-based world streaming system (derived, schedulable).
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Task emission and plan selection are deterministic.
*/
#ifndef DOMINIUM_RULES_SCALE_WORLD_STREAMING_SYSTEM_H
#define DOMINIUM_RULES_SCALE_WORLD_STREAMING_SYSTEM_H

#include "dominium/execution/system_iface.h"
#include "dominium/interest_set.h"
#include "dominium/fidelity.h"

enum dom_streaming_op {
    DOM_STREAM_OP_LOAD_CHUNK = 1,
    DOM_STREAM_OP_UNLOAD_CHUNK = 2
};

typedef struct dom_streaming_request {
    u32 op;
    u64 chunk_id;
} dom_streaming_request;

typedef struct dom_streaming_cache {
    u64* loaded_chunk_ids;
    u32 loaded_count;
    u32 loaded_capacity;
} dom_streaming_cache;

typedef enum dom_streaming_migration_state {
    DOM_STREAMING_STATE_LEGACY = 1,
    DOM_STREAMING_STATE_DUAL = 2,
    DOM_STREAMING_STATE_IR_ONLY = 3
} dom_streaming_migration_state;

class WorldStreamingSystem : public ISimSystem {
public:
    WorldStreamingSystem();

    int init(const dom_interest_set* interest_set,
             const dom_streaming_cache* cache,
             u64 interest_set_id,
             dom_streaming_request* ir_storage,
             u32 ir_capacity,
             dom_streaming_request* legacy_storage,
             u32 legacy_capacity);

    void set_interest_set(const dom_interest_set* interest_set, u64 interest_set_id);
    void set_cache(const dom_streaming_cache* cache);
    void set_next_due_tick(dom_act_time_t tick);
    void set_migration_state(dom_streaming_migration_state state);

    dom_streaming_migration_state migration_state() const;
    u32 mismatch_count() const;

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
    dom_streaming_migration_state migration_state_;
    u32 mismatch_count_;

    const dom_interest_set* interest_set_;
    u64 interest_set_id_;
    const dom_streaming_cache* cache_;

    dom_streaming_request* ir_requests_;
    u32 ir_capacity_;
    u32 ir_count_;

    dom_streaming_request* legacy_requests_;
    u32 legacy_capacity_;
    u32 legacy_count_;
};

#endif /* DOMINIUM_RULES_SCALE_WORLD_STREAMING_SYSTEM_H */
