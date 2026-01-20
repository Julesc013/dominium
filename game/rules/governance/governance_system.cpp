/*
FILE: game/rules/governance/governance_system.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Game / governance rules
RESPONSIBILITY: Work IR-based governance emission (authoritative tasks only).
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Task emission order and budgeting are deterministic.
*/
#include "dominium/rules/governance/governance_system.h"

#include "dominium/execution/work_graph_builder.h"
#include "dominium/execution/access_set_builder.h"
#include "domino/execution/task_node.h"
#include "domino/execution/cost_model.h"
#include "domino/core/dom_time_core.h"

#include <string.h>

enum {
    DOM_GOV_COMPONENT_POLICY = 5401u,
    DOM_GOV_COMPONENT_LEGITIMACY = 5402u,
    DOM_GOV_COMPONENT_ENFORCEMENT = 5403u,
    DOM_GOV_COMPONENT_LIFECYCLE = 5404u,
    DOM_GOV_COMPONENT_AUDIT = 5405u,
    DOM_GOV_FIELD_DEFAULT = 1u
};

static u32 dom_gov_fnv1a32(const char* text)
{
    const unsigned char* bytes = (const unsigned char*)(text ? text : "");
    u32 hash = 2166136261u;
    while (*bytes) {
        hash ^= (u32)(*bytes++);
        hash *= 16777619u;
    }
    return hash;
}

static u64 dom_gov_fnv1a64(const char* text)
{
    const unsigned char* bytes = (const unsigned char*)(text ? text : "");
    u64 hash = 1469598103934665603ULL;
    while (*bytes) {
        hash ^= (u64)(*bytes++);
        hash *= 1099511628211ULL;
    }
    return hash;
}

static u32 dom_gov_task_fidelity(dom_fidelity_tier tier)
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

static u32 dom_gov_default_budget(dom_fidelity_tier tier)
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

static u32 dom_gov_default_cadence(dom_fidelity_tier tier)
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

static dom_act_time_t dom_gov_next_due(dom_act_time_t now, u32 cadence, d_bool has_work)
{
    if (!has_work || cadence == 0u) {
        return DOM_TIME_ACT_MAX;
    }
    if (now > (DOM_TIME_ACT_MAX - cadence)) {
        return DOM_TIME_ACT_MAX;
    }
    return now + (dom_act_time_t)cadence;
}

static u32 dom_gov_local_id_for_op(u32 op)
{
    return op;
}

GovernanceSystem::GovernanceSystem()
    : system_id_(0u),
      law_target_count_(0u),
      law_scope_ref_(1u),
      tier_(DOM_FIDELITY_MACRO),
      next_due_tick_(DOM_TIME_ACT_MAX),
      migration_state_(DOM_GOVERNANCE_STATE_IR_ONLY),
      allowed_ops_mask_(0xFFFFFFFFu),
      last_emitted_task_count_(0u),
      cycle_in_progress_(D_FALSE),
      inputs_(0),
      buffers_(0)
{
    u32 i;
    system_id_ = dom_gov_fnv1a64("GOVERNANCE");
    law_targets_[0] = dom_gov_fnv1a32("GOVERNANCE.MACRO");
    law_targets_[1] = dom_gov_fnv1a32("EXEC.AUTH_TASK");
    law_target_count_ = 2u;
    for (i = 0u; i < 4u; ++i) {
        params_[i].op = 0u;
        params_[i].start_index = 0u;
        params_[i].count = 0u;
    }
    memset(&runtime_, 0, sizeof(runtime_));
    dom_governance_runtime_reset(&runtime_);
}

int GovernanceSystem::init(const dom_governance_inputs* inputs,
                           const dom_governance_buffers* buffers)
{
    inputs_ = inputs;
    buffers_ = buffers;
    dom_governance_runtime_reset(&runtime_);
    return 0;
}

void GovernanceSystem::set_inputs(const dom_governance_inputs* inputs)
{
    inputs_ = inputs;
}

void GovernanceSystem::set_buffers(const dom_governance_buffers* buffers)
{
    buffers_ = buffers;
}

void GovernanceSystem::set_allowed_ops_mask(u32 mask)
{
    allowed_ops_mask_ = mask;
}

void GovernanceSystem::set_next_due_tick(dom_act_time_t tick)
{
    next_due_tick_ = tick;
}

void GovernanceSystem::set_migration_state(dom_governance_migration_state state)
{
    migration_state_ = state;
}

dom_governance_migration_state GovernanceSystem::migration_state() const
{
    return migration_state_;
}

u32 GovernanceSystem::last_emitted_task_count() const
{
    return last_emitted_task_count_;
}

dom_governance_runtime_state* GovernanceSystem::runtime_state()
{
    return &runtime_;
}

const dom_governance_runtime_state* GovernanceSystem::runtime_state() const
{
    return &runtime_;
}

u64 GovernanceSystem::system_id() const
{
    return system_id_;
}

d_bool GovernanceSystem::is_sim_affecting() const
{
    return D_TRUE;
}

const u32* GovernanceSystem::law_targets(u32* out_count) const
{
    if (out_count) {
        *out_count = law_target_count_;
    }
    return law_targets_;
}

dom_act_time_t GovernanceSystem::get_next_due_tick() const
{
    return next_due_tick_;
}

void GovernanceSystem::degrade(dom_fidelity_tier tier, u32 reason)
{
    (void)reason;
    tier_ = tier;
}

int GovernanceSystem::emit_tasks(dom_act_time_t act_now,
                                 dom_act_time_t act_target,
                                 dom_work_graph_builder* graph_builder,
                                 dom_access_set_builder* access_builder)
{
    struct op_desc {
        u32 op;
        u32 phase_id;
        u32 count;
        u32* cursor;
        u64 set_id;
        u32 component_id;
    };
    op_desc ops[4];
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
    if (!buffers_->audit_log) {
        return 0;
    }

    budget = dom_gov_default_budget(tier_);
    if (budget_hint() > 0u) {
        if (budget == 0u || budget_hint() < budget) {
            budget = budget_hint();
        }
    }

    if (cycle_in_progress_ == D_FALSE) {
        dom_governance_runtime_reset(&runtime_);
        cycle_in_progress_ = D_TRUE;
    }

    ops[0].op = DOM_GOV_TASK_POLICY_APPLY;
    ops[0].phase_id = 0u;
    ops[0].count = inputs_->policies ? inputs_->policies->count : 0u;
    ops[0].cursor = &runtime_.policy_cursor;
    ops[0].set_id = buffers_->policy_set_id;
    ops[0].component_id = DOM_GOV_COMPONENT_POLICY;

    ops[1].op = DOM_GOV_TASK_LEGITIMACY_UPDATE;
    ops[1].phase_id = 1u;
    ops[1].count = inputs_->legitimacy_event_count;
    ops[1].cursor = &runtime_.legitimacy_cursor;
    ops[1].set_id = inputs_->legitimacy_event_set_id;
    ops[1].component_id = DOM_GOV_COMPONENT_LEGITIMACY;

    ops[2].op = DOM_GOV_TASK_AUTHORITY_ENFORCEMENT;
    ops[2].phase_id = 2u;
    ops[2].count = inputs_->authority_action_count;
    ops[2].cursor = &runtime_.authority_cursor;
    ops[2].set_id = inputs_->authority_action_set_id;
    ops[2].component_id = DOM_GOV_COMPONENT_ENFORCEMENT;

    ops[3].op = DOM_GOV_TASK_LAW_LIFECYCLE;
    ops[3].phase_id = 3u;
    ops[3].count = inputs_->lifecycle_event_count;
    ops[3].cursor = &runtime_.lifecycle_cursor;
    ops[3].set_id = inputs_->lifecycle_event_set_id;
    ops[3].component_id = DOM_GOV_COMPONENT_LIFECYCLE;

    for (i = 0u; i < 4u; ++i) {
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
        dom_governance_task_params* params;

        if (budget == 0u) {
            break;
        }
        if ((allowed_ops_mask_ & (1u << op->op)) == 0u) {
            continue;
        }
        if (op->count == 0u) {
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

        local_id = dom_gov_local_id_for_op(op->op);
        task_id = dom_work_graph_builder_make_id(system_id_, local_id, DOM_WORK_ID_TASK);
        access_id = dom_work_graph_builder_make_id(system_id_, local_id, DOM_WORK_ID_ACCESS);
        cost_id = dom_work_graph_builder_make_id(system_id_, local_id, DOM_WORK_ID_COST);

        node.task_id = task_id;
        node.system_id = system_id_;
        node.category = DOM_TASK_AUTHORITATIVE;
        node.determinism_class = DOM_DET_STRICT;
        node.fidelity_tier = dom_gov_task_fidelity(tier_);
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
        range.field_id = DOM_GOV_FIELD_DEFAULT;
        range.start_id = 0u;
        range.end_id = 0u;
        range.set_id = op->set_id;
        if (dom_access_set_builder_add_read(access_builder, &range) != 0) {
            return -4;
        }

        if (op->op == DOM_GOV_TASK_POLICY_APPLY) {
            range.component_id = DOM_GOV_COMPONENT_POLICY;
            range.set_id = buffers_->policy_set_id;
            if (dom_access_set_builder_add_write(access_builder, &range) != 0) {
                return -5;
            }
            range.component_id = DOM_GOV_COMPONENT_LEGITIMACY;
            range.set_id = buffers_->legitimacy_set_id;
            if (dom_access_set_builder_add_read(access_builder, &range) != 0) {
                return -6;
            }
            range.component_id = DOM_GOV_COMPONENT_ENFORCEMENT;
            range.set_id = buffers_->enforcement_set_id;
            if (dom_access_set_builder_add_read(access_builder, &range) != 0) {
                return -7;
            }
        } else if (op->op == DOM_GOV_TASK_LEGITIMACY_UPDATE) {
            range.component_id = DOM_GOV_COMPONENT_LEGITIMACY;
            range.set_id = buffers_->legitimacy_set_id;
            if (dom_access_set_builder_add_write(access_builder, &range) != 0) {
                return -8;
            }
        } else if (op->op == DOM_GOV_TASK_AUTHORITY_ENFORCEMENT) {
            range.component_id = DOM_GOV_COMPONENT_ENFORCEMENT;
            range.set_id = buffers_->enforcement_set_id;
            if (dom_access_set_builder_add_read(access_builder, &range) != 0) {
                return -9;
            }
        } else if (op->op == DOM_GOV_TASK_LAW_LIFECYCLE) {
            range.component_id = DOM_GOV_COMPONENT_LIFECYCLE;
            range.set_id = buffers_->law_state_set_id;
            if (dom_access_set_builder_add_write(access_builder, &range) != 0) {
                return -10;
            }
        }

        range.component_id = DOM_GOV_COMPONENT_AUDIT;
        range.set_id = buffers_->audit_set_id;
        if (dom_access_set_builder_add_write(access_builder, &range) != 0) {
            return -11;
        }
        if (dom_access_set_builder_finalize(access_builder) != 0) {
            return -12;
        }
        if (dom_work_graph_builder_add_task(graph_builder, &node) != 0) {
            return -13;
        }
        if (prev_task_id != 0u) {
            edge.from_task_id = prev_task_id;
            edge.to_task_id = task_id;
            edge.reason_id = 0u;
            if (dom_work_graph_builder_add_dependency(graph_builder, &edge) != 0) {
                return -14;
            }
        }
        prev_task_id = task_id;
        last_emitted_task_count_ += 1u;
        *op->cursor = cursor + slice;
        budget -= slice;
    }

    for (i = 0u; i < 4u; ++i) {
        const op_desc* op = &ops[i];
        if (op->count == 0u) {
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
        dom_governance_runtime_reset(&runtime_);
        cycle_in_progress_ = D_FALSE;
    }

    cadence = dom_gov_default_cadence(tier_);
    next_due_tick_ = dom_gov_next_due(act_now, cadence, has_work ? D_TRUE : cycle_in_progress_);
    return 0;
}
