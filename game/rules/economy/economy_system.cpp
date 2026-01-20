/*
FILE: game/rules/economy/economy_system.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Game / economy rules
RESPONSIBILITY: Work IR-based economy emission (authoritative tasks only).
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Task emission order and budgeting are deterministic.
*/
#include "dominium/rules/economy/economy_system.h"

#include "dominium/execution/work_graph_builder.h"
#include "dominium/execution/access_set_builder.h"
#include "domino/execution/task_node.h"
#include "domino/execution/cost_model.h"
#include "domino/core/dom_time_core.h"

#include <string.h>

enum {
    DOM_ECON_COMPONENT_LEDGER = 5301u,
    DOM_ECON_COMPONENT_CONTRACTS = 5302u,
    DOM_ECON_COMPONENT_PRODUCTION = 5303u,
    DOM_ECON_COMPONENT_CONSUMPTION = 5304u,
    DOM_ECON_COMPONENT_MAINTENANCE = 5305u,
    DOM_ECON_COMPONENT_AUDIT = 5306u,
    DOM_ECON_FIELD_DEFAULT = 1u
};

static u32 dom_econ_fnv1a32(const char* text)
{
    const unsigned char* bytes = (const unsigned char*)(text ? text : "");
    u32 hash = 2166136261u;
    while (*bytes) {
        hash ^= (u32)(*bytes++);
        hash *= 16777619u;
    }
    return hash;
}

static u64 dom_econ_fnv1a64(const char* text)
{
    const unsigned char* bytes = (const unsigned char*)(text ? text : "");
    u64 hash = 1469598103934665603ULL;
    while (*bytes) {
        hash ^= (u64)(*bytes++);
        hash *= 1099511628211ULL;
    }
    return hash;
}

static u32 dom_econ_task_fidelity(dom_fidelity_tier tier)
{
    switch (tier) {
        case DOM_FIDELITY_LATENT: return DOM_FID_LATENT;
        case DOM_FIDELITY_MACRO: return DOM_FID_MACRO;
        case DOM_FIDELITY_MESO: return DOM_FID_MESO;
        case DOM_FIDELITY_MICRO: return DOM_FID_MICRO;
        case DOM_FIDELITY_FOCUS: return DOM_FID_FOCUS;
        default: return DOM_FID_LATENT;
    }
}

static u32 dom_econ_default_budget(dom_fidelity_tier tier)
{
    switch (tier) {
        case DOM_FIDELITY_FOCUS: return 16u;
        case DOM_FIDELITY_MICRO: return 12u;
        case DOM_FIDELITY_MESO: return 8u;
        case DOM_FIDELITY_MACRO: return 4u;
        case DOM_FIDELITY_LATENT:
        default:
            return 0u;
    }
}

static u32 dom_econ_default_cadence(dom_fidelity_tier tier)
{
    switch (tier) {
        case DOM_FIDELITY_FOCUS: return 1u;
        case DOM_FIDELITY_MICRO: return 2u;
        case DOM_FIDELITY_MESO: return 4u;
        case DOM_FIDELITY_MACRO: return 8u;
        case DOM_FIDELITY_LATENT:
        default:
            return 0u;
    }
}

static dom_act_time_t dom_econ_next_due(dom_act_time_t now, u32 cadence, d_bool has_work)
{
    if (!has_work || cadence == 0u) {
        return DOM_TIME_ACT_MAX;
    }
    if (now > (DOM_TIME_ACT_MAX - cadence)) {
        return DOM_TIME_ACT_MAX;
    }
    return now + (dom_act_time_t)cadence;
}

static u32 dom_econ_local_id_for_op(u32 op)
{
    return op;
}

EconomySystem::EconomySystem()
    : system_id_(0u),
      law_target_count_(0u),
      law_scope_ref_(1u),
      tier_(DOM_FIDELITY_MACRO),
      next_due_tick_(DOM_TIME_ACT_MAX),
      migration_state_(DOM_ECONOMY_STATE_IR_ONLY),
      allowed_ops_mask_(0xFFFFFFFFu),
      last_emitted_task_count_(0u),
      cycle_in_progress_(D_FALSE),
      inputs_(0),
      buffers_(0)
{
    u32 i;
    system_id_ = dom_econ_fnv1a64("ECONOMY");
    law_targets_[0] = dom_econ_fnv1a32("ECONOMY.MACRO");
    law_targets_[1] = dom_econ_fnv1a32("EXEC.AUTH_TASK");
    law_target_count_ = 2u;
    for (i = 0u; i < 5u; ++i) {
        params_[i].op = 0u;
        params_[i].start_index = 0u;
        params_[i].count = 0u;
    }
    memset(&runtime_, 0, sizeof(runtime_));
    dom_economy_runtime_reset(&runtime_);
}

int EconomySystem::init(const dom_economy_inputs* inputs,
                        const dom_economy_buffers* buffers)
{
    inputs_ = inputs;
    buffers_ = buffers;
    dom_economy_runtime_reset(&runtime_);
    return 0;
}

void EconomySystem::set_inputs(const dom_economy_inputs* inputs)
{
    inputs_ = inputs;
}

void EconomySystem::set_buffers(const dom_economy_buffers* buffers)
{
    buffers_ = buffers;
}

void EconomySystem::set_allowed_ops_mask(u32 mask)
{
    allowed_ops_mask_ = mask;
}

void EconomySystem::set_next_due_tick(dom_act_time_t tick)
{
    next_due_tick_ = tick;
}

void EconomySystem::set_migration_state(dom_economy_migration_state state)
{
    migration_state_ = state;
}

dom_economy_migration_state EconomySystem::migration_state() const
{
    return migration_state_;
}

u32 EconomySystem::last_emitted_task_count() const
{
    return last_emitted_task_count_;
}

dom_economy_runtime_state* EconomySystem::runtime_state()
{
    return &runtime_;
}

const dom_economy_runtime_state* EconomySystem::runtime_state() const
{
    return &runtime_;
}

u64 EconomySystem::system_id() const
{
    return system_id_;
}

d_bool EconomySystem::is_sim_affecting() const
{
    return D_TRUE;
}

const u32* EconomySystem::law_targets(u32* out_count) const
{
    if (out_count) {
        *out_count = law_target_count_;
    }
    return law_targets_;
}

dom_act_time_t EconomySystem::get_next_due_tick() const
{
    return next_due_tick_;
}

void EconomySystem::degrade(dom_fidelity_tier tier, u32 reason)
{
    (void)reason;
    tier_ = tier;
}

int EconomySystem::emit_tasks(dom_act_time_t act_now,
                              dom_act_time_t act_target,
                              dom_work_graph_builder* graph_builder,
                              dom_access_set_builder* access_builder)
{
    struct op_desc {
        u32 op;
        u32 phase_id;
        const void* entries;
        u32 count;
        u32* cursor;
        u64 set_id;
        u32 component_id;
    };
    op_desc ops[5];
    u32 budget;
    u32 cadence;
    u32 i;
    u64 prev_task_id = 0u;
    d_bool has_work = D_FALSE;
    d_bool cycle_complete = D_TRUE;

    (void)act_target;
    last_emitted_task_count_ = 0u;

    if (!graph_builder || !access_builder) {
        return -1;
    }
    if (!inputs_ || !buffers_) {
        return 0;
    }
    if (!buffers_->ledger || !buffers_->audit_log) {
        return 0;
    }

    budget = dom_econ_default_budget(tier_);
    if (budget_hint() > 0u) {
        if (budget == 0u || budget_hint() < budget) {
            budget = budget_hint();
        }
    }

    if (cycle_in_progress_ == D_FALSE) {
        dom_economy_runtime_reset(&runtime_);
        cycle_in_progress_ = D_TRUE;
    }

    ops[0].op = DOM_ECON_TASK_LEDGER_TRANSFERS;
    ops[0].phase_id = 0u;
    ops[0].entries = inputs_->transfers;
    ops[0].count = inputs_->transfer_count;
    ops[0].cursor = &runtime_.transfer_cursor;
    ops[0].set_id = inputs_->transfer_set_id;
    ops[0].component_id = DOM_ECON_COMPONENT_LEDGER;

    ops[1].op = DOM_ECON_TASK_CONTRACT_SETTLEMENT;
    ops[1].phase_id = 1u;
    ops[1].entries = inputs_->contracts;
    ops[1].count = inputs_->contract_count;
    ops[1].cursor = &runtime_.contract_cursor;
    ops[1].set_id = inputs_->contract_set_id;
    ops[1].component_id = DOM_ECON_COMPONENT_CONTRACTS;

    ops[2].op = DOM_ECON_TASK_PRODUCTION_STEP;
    ops[2].phase_id = 2u;
    ops[2].entries = inputs_->production;
    ops[2].count = inputs_->production_count;
    ops[2].cursor = &runtime_.production_cursor;
    ops[2].set_id = inputs_->production_set_id;
    ops[2].component_id = DOM_ECON_COMPONENT_PRODUCTION;

    ops[3].op = DOM_ECON_TASK_CONSUMPTION_STEP;
    ops[3].phase_id = 3u;
    ops[3].entries = inputs_->consumption;
    ops[3].count = inputs_->consumption_count;
    ops[3].cursor = &runtime_.consumption_cursor;
    ops[3].set_id = inputs_->consumption_set_id;
    ops[3].component_id = DOM_ECON_COMPONENT_CONSUMPTION;

    ops[4].op = DOM_ECON_TASK_MAINTENANCE_DECAY;
    ops[4].phase_id = 4u;
    ops[4].entries = inputs_->maintenance;
    ops[4].count = inputs_->maintenance_count;
    ops[4].cursor = &runtime_.maintenance_cursor;
    ops[4].set_id = inputs_->maintenance_set_id;
    ops[4].component_id = DOM_ECON_COMPONENT_MAINTENANCE;

    for (i = 0u; i < 5u; ++i) {
        op_desc* op = &ops[i];
        u32 cursor;
        u32 remaining;
        u32 slice;
        u32 local_id;
        u64 task_id;
        u64 access_id;
        u64 cost_id;
        dom_task_node node;
        dom_cost_model cost;
        dom_access_range range;
        dom_dependency_edge edge;
        dom_economy_task_params* params;

        if (budget == 0u) {
            break;
        }
        if ((allowed_ops_mask_ & (1u << op->op)) == 0u) {
            continue;
        }
        if (!op->entries || op->count == 0u) {
            continue;
        }
        cursor = *op->cursor;
        if (cursor >= op->count) {
            cursor = 0u;
            *op->cursor = 0u;
        }
        remaining = op->count - cursor;
        if (remaining == 0u) {
            continue;
        }
        slice = remaining;
        if (slice > budget) {
            slice = budget;
        }
        params = &params_[i];
        params->op = op->op;
        params->start_index = cursor;
        params->count = slice;

        local_id = dom_econ_local_id_for_op(op->op);
        task_id = dom_work_graph_builder_make_id(system_id_, local_id, DOM_WORK_ID_TASK);
        access_id = dom_work_graph_builder_make_id(system_id_, local_id, DOM_WORK_ID_ACCESS);
        cost_id = dom_work_graph_builder_make_id(system_id_, local_id, DOM_WORK_ID_COST);

        node.task_id = task_id;
        node.system_id = system_id_;
        node.category = DOM_TASK_AUTHORITATIVE;
        node.determinism_class = DOM_DET_STRICT;
        node.fidelity_tier = dom_econ_task_fidelity(tier_);
        node.next_due_tick = DOM_EXEC_TICK_INVALID;
        node.access_set_id = access_id;
        node.cost_model_id = cost_id;
        node.law_targets = law_targets_;
        node.law_target_count = law_target_count_;
        node.phase_id = op->phase_id;
        node.commit_key = dom_work_graph_builder_make_commit_key(op->phase_id, task_id, 0u);
        node.law_scope_ref = law_scope_ref_;
        node.actor_ref = 0u;
        node.capability_set_ref = 0u;
        node.policy_params = params;
        node.policy_params_size = (u32)sizeof(*params);

        cost.cost_id = cost_id;
        cost.cpu_upper_bound = slice;
        cost.memory_upper_bound = 1u;
        cost.bandwidth_upper_bound = 1u;
        cost.latency_class = DOM_LATENCY_LOW;
        cost.degradation_priority = 1;

        if (dom_work_graph_builder_add_cost_model(graph_builder, &cost) != 0) {
            return -2;
        }
        if (!dom_access_set_builder_begin(access_builder, access_id, DOM_REDUCE_NONE, 0)) {
            return -3;
        }
        range.kind = DOM_RANGE_COMPONENT_SET;
        range.component_id = op->component_id;
        range.field_id = DOM_ECON_FIELD_DEFAULT;
        range.start_id = 0u;
        range.end_id = 0u;
        range.set_id = op->set_id;
        if (dom_access_set_builder_add_read(access_builder, &range) != 0) {
            return -4;
        }

        range.component_id = DOM_ECON_COMPONENT_LEDGER;
        range.set_id = buffers_->ledger_set_id;
        if (dom_access_set_builder_add_write(access_builder, &range) != 0) {
            return -5;
        }
        range.component_id = DOM_ECON_COMPONENT_AUDIT;
        range.set_id = buffers_->audit_set_id;
        if (dom_access_set_builder_add_write(access_builder, &range) != 0) {
            return -6;
        }
        if (dom_access_set_builder_finalize(access_builder) != 0) {
            return -7;
        }
        if (dom_work_graph_builder_add_task(graph_builder, &node) != 0) {
            return -8;
        }
        if (prev_task_id != 0u) {
            edge.from_task_id = prev_task_id;
            edge.to_task_id = task_id;
            edge.reason_id = 0u;
            if (dom_work_graph_builder_add_dependency(graph_builder, &edge) != 0) {
                return -9;
            }
        }
        prev_task_id = task_id;
        last_emitted_task_count_ += 1u;
        *op->cursor = cursor + slice;
        budget -= slice;
    }

    for (i = 0u; i < 5u; ++i) {
        const op_desc* op = &ops[i];
        if (!op->entries || op->count == 0u) {
            continue;
        }
        has_work = D_TRUE;
        if (*op->cursor < op->count) {
            cycle_complete = D_FALSE;
        }
    }

    if (has_work == D_FALSE) {
        cycle_in_progress_ = D_FALSE;
    }

    if (cycle_complete == D_TRUE && has_work == D_TRUE) {
        dom_economy_runtime_reset(&runtime_);
        cycle_in_progress_ = D_FALSE;
    }

    cadence = dom_econ_default_cadence(tier_);
    next_due_tick_ = dom_econ_next_due(act_now, cadence, has_work ? D_TRUE : cycle_in_progress_);
    return 0;
}
