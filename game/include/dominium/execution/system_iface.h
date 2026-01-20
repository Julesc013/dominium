/*
FILE: include/dominium/execution/system_iface.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / execution
RESPONSIBILITY: Game-side system interface for Work IR emission.
ALLOWED DEPENDENCIES: `game/include/**`, `engine/include/**` public headers, and C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
DETERMINISM: Systems must emit deterministic Work IR and Access IR.
*/
#ifndef DOMINIUM_EXECUTION_SYSTEM_IFACE_H
#define DOMINIUM_EXECUTION_SYSTEM_IFACE_H

#include "domino/core/types.h"
#include "domino/core/dom_time_core.h"
#include "dominium/fidelity.h"

struct dom_work_graph_builder;
struct dom_access_set_builder;

class ISimSystem {
public:
    virtual ~ISimSystem() {}
    virtual u64 system_id() const = 0;
    virtual d_bool is_sim_affecting() const = 0;
    virtual const u32* law_targets(u32* out_count) const = 0;
    virtual dom_act_time_t get_next_due_tick() const = 0;
    virtual int emit_tasks(dom_act_time_t act_now,
                           dom_act_time_t act_target,
                           dom_work_graph_builder* graph_builder,
                           dom_access_set_builder* access_builder) = 0;
    virtual void degrade(dom_fidelity_tier tier, u32 reason) = 0;

    void set_budget_hint(u32 hint) { budget_hint_ = hint; }
    u32 budget_hint() const { return budget_hint_; }

protected:
    ISimSystem() : budget_hint_(0u) {}

private:
    u32 budget_hint_;
};

#endif /* DOMINIUM_EXECUTION_SYSTEM_IFACE_H */
