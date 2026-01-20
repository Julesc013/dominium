/*
FILE: game/rules/war/war_system.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Game / war rules
RESPONSIBILITY: Work IR-based war emission (authoritative tasks only).
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Task emission order and budgeting are deterministic.
*/
#include "dominium/rules/war/war_system.h"

#include "dominium/execution/work_graph_builder.h"
#include "dominium/execution/access_set_builder.h"
#include "domino/execution/task_node.h"
#include "domino/execution/cost_model.h"
#include "domino/core/dom_time_core.h"

#include <string.h>

enum {
    DOM_WAR_COMPONENT_ENGAGEMENT = 5501u,
    DOM_WAR_COMPONENT_OUTCOME = 5502u,
    DOM_WAR_COMPONENT_CASUALTY = 5503u,
    DOM_WAR_COMPONENT_EQUIPMENT = 5504u,
    DOM_WAR_COMPONENT_MORALE = 5505u,
    DOM_WAR_COMPONENT_OCCUPATION = 5506u,
    DOM_WAR_COMPONENT_RESISTANCE = 5507u,
    DOM_WAR_COMPONENT_DISRUPTION = 5508u,
    DOM_WAR_COMPONENT_ROUTE_CONTROL = 5509u,
    DOM_WAR_COMPONENT_BLOCKADE = 5510u,
    DOM_WAR_COMPONENT_INTERDICTION = 5511u,
    DOM_WAR_COMPONENT_AUDIT = 5512u,
    DOM_WAR_FIELD_DEFAULT = 1u
};

static u32 dom_war_fnv1a32(const char* text)
{
    const unsigned char* bytes = (const unsigned char*)(text ? text : "");
    u32 hash = 2166136261u;
    while (*bytes) {
        hash ^= (u32)(*bytes++);
        hash *= 16777619u;
    }
    return hash;
}

static u64 dom_war_fnv1a64(const char* text)
{
    const unsigned char* bytes = (const unsigned char*)(text ? text : "");
    u64 hash = 1469598103934665603ULL;
    while (*bytes) {
        hash ^= (u64)(*bytes++);
        hash *= 1099511628211ULL;
    }
    return hash;
}

static u32 dom_war_task_fidelity(dom_fidelity_tier tier)
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

static u32 dom_war_default_budget(dom_fidelity_tier tier)
{
    switch (tier) {
        case DOM_FIDELITY_FOCUS: return 12u;
        case DOM_FIDELITY_MICRO: return 8u;
        case DOM_FIDELITY_MESO: return 6u;
        case DOM_FIDELITY_MACRO: return 4u;
        case DOM_FIDELITY_LATENT:
        default:
            return 0u;
    }
}

static u32 dom_war_default_cadence(dom_fidelity_tier tier)
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

static dom_act_time_t dom_war_next_due(dom_act_time_t now, u32 cadence, d_bool has_work)
{
    if (!has_work || cadence == 0u) {
        return DOM_TIME_ACT_MAX;
    }
    if (now > (DOM_TIME_ACT_MAX - cadence)) {
        return DOM_TIME_ACT_MAX;
    }
    return now + (dom_act_time_t)cadence;
}

static u32 dom_war_local_id_for_op(u32 op)
{
    return op;
}

static dom_war_task_params* dom_war_params_for_op(dom_war_task_params* params,
                                                  u32 op)
{
    if (!params || op == 0u || op > 12u) {
        return 0;
    }
    return &params[op - 1u];
}

WarSystem::WarSystem()
    : system_id_(0u),
      law_target_count_(0u),
      law_scope_ref_(1u),
      tier_(DOM_FIDELITY_MACRO),
      next_due_tick_(DOM_TIME_ACT_MAX),
      migration_state_(DOM_WAR_STATE_IR_ONLY),
      allowed_ops_mask_(0xFFFFFFFFu),
      last_emitted_task_count_(0u),
      cycle_in_progress_(D_FALSE),
      inputs_(0),
      buffers_(0)
{
    u32 i;
    system_id_ = dom_war_fnv1a64("WAR");
    law_targets_[0] = dom_war_fnv1a32("WAR.ENGAGEMENT");
    law_targets_[1] = dom_war_fnv1a32("EXEC.AUTH_TASK");
    law_target_count_ = 2u;
    for (i = 0u; i < 12u; ++i) {
        params_[i].op = 0u;
        params_[i].start_index = 0u;
        params_[i].count = 0u;
    }
    memset(&runtime_, 0, sizeof(runtime_));
    dom_war_runtime_reset(&runtime_);
}

int WarSystem::init(const dom_war_inputs* inputs,
                    const dom_war_buffers* buffers)
{
    inputs_ = inputs;
    buffers_ = buffers;
    dom_war_runtime_reset(&runtime_);
    return 0;
}

void WarSystem::set_inputs(const dom_war_inputs* inputs)
{
    inputs_ = inputs;
}

void WarSystem::set_buffers(const dom_war_buffers* buffers)
{
    buffers_ = buffers;
}

void WarSystem::set_allowed_ops_mask(u32 mask)
{
    allowed_ops_mask_ = mask;
}

void WarSystem::set_next_due_tick(dom_act_time_t tick)
{
    next_due_tick_ = tick;
}

void WarSystem::set_migration_state(dom_war_migration_state state)
{
    migration_state_ = state;
}

dom_war_migration_state WarSystem::migration_state() const
{
    return migration_state_;
}

u32 WarSystem::last_emitted_task_count() const
{
    return last_emitted_task_count_;
}

dom_war_runtime_state* WarSystem::runtime_state()
{
    return &runtime_;
}

const dom_war_runtime_state* WarSystem::runtime_state() const
{
    return &runtime_;
}

u64 WarSystem::system_id() const
{
    return system_id_;
}

d_bool WarSystem::is_sim_affecting() const
{
    return D_TRUE;
}

const u32* WarSystem::law_targets(u32* out_count) const
{
    if (out_count) {
        *out_count = law_target_count_;
    }
    return law_targets_;
}

dom_act_time_t WarSystem::get_next_due_tick() const
{
    return next_due_tick_;
}

void WarSystem::degrade(dom_fidelity_tier tier, u32 reason)
{
    (void)reason;
    tier_ = tier;
}

static int dom_war_emit_task_node(dom_work_graph_builder* graph_builder,
                                  dom_access_set_builder* access_builder,
                                  const dom_task_node* node,
                                  const dom_cost_model* cost,
                                  const dom_access_range* reads,
                                  u32 read_count,
                                  const dom_access_range* writes,
                                  u32 write_count)
{
    u32 i;
    if (dom_work_graph_builder_add_cost_model(graph_builder, cost) != 0) {
        return -1;
    }
    if (!dom_access_set_builder_begin(access_builder, node->access_set_id, DOM_REDUCE_NONE, 0)) {
        return -2;
    }
    for (i = 0u; i < read_count; ++i) {
        if (dom_access_set_builder_add_read(access_builder, &reads[i]) != 0) {
            return -3;
        }
    }
    for (i = 0u; i < write_count; ++i) {
        if (dom_access_set_builder_add_write(access_builder, &writes[i]) != 0) {
            return -4;
        }
    }
    if (dom_access_set_builder_finalize(access_builder) != 0) {
        return -5;
    }
    if (dom_work_graph_builder_add_task(graph_builder, node) != 0) {
        return -6;
    }
    return 0;
}

int WarSystem::emit_tasks(dom_act_time_t act_now,
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
    op_desc ops[7];
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

    budget = dom_war_default_budget(tier_);
    if (budget_hint() > 0u) {
        if (budget == 0u || budget_hint() < budget) {
            budget = budget_hint();
        }
    }

    if (cycle_in_progress_ == D_FALSE) {
        dom_war_runtime_reset(&runtime_);
        cycle_in_progress_ = D_TRUE;
    }

    if (inputs_->engagements && inputs_->engagement_count > 0u) {
        u32 cursor = runtime_.engagement_cursor;
        u32 remaining;
        u32 slice;
        d_bool emitted_any = D_FALSE;
        if (cursor >= inputs_->engagement_count) {
            cursor = 0u;
            runtime_.engagement_cursor = 0u;
        }
        remaining = inputs_->engagement_count - cursor;
        if (remaining > 0u && budget > 0u) {
            slice = remaining;
            if (slice > budget) {
                slice = budget;
            }

            for (i = 0u; i < 5u; ++i) {
                u32 op = DOM_WAR_TASK_ENGAGEMENT_ADMIT + i;
                u32 local_id;
                u64 task_id;
                u64 access_id;
                u64 cost_id;
                dom_task_node node;
                dom_cost_model cost;
                dom_access_range reads[2];
                dom_access_range writes[3];
                u32 read_count = 0u;
                u32 write_count = 0u;
                dom_war_task_params* params;
                if ((allowed_ops_mask_ & (1u << op)) == 0u) {
                    continue;
                }
                if (!buffers_->audit_log) {
                    continue;
                }
                if ((op == DOM_WAR_TASK_ENGAGEMENT_RESOLVE ||
                     op == DOM_WAR_TASK_APPLY_CASUALTIES ||
                     op == DOM_WAR_TASK_APPLY_EQUIPMENT_LOSSES ||
                     op == DOM_WAR_TASK_UPDATE_MORALE_READINESS) &&
                    !buffers_->outcomes) {
                    continue;
                }
                if (op == DOM_WAR_TASK_APPLY_CASUALTIES && !buffers_->casualties) {
                    continue;
                }
                if (op == DOM_WAR_TASK_APPLY_EQUIPMENT_LOSSES && !buffers_->equipment_losses) {
                    continue;
                }
                if (op == DOM_WAR_TASK_UPDATE_MORALE_READINESS && !buffers_->morale) {
                    continue;
                }

                params = dom_war_params_for_op(params_, op);
                if (!params) {
                    continue;
                }
                params->op = op;
                params->start_index = cursor;
                params->count = slice;

                local_id = dom_war_local_id_for_op(op);
                task_id = dom_work_graph_builder_make_id(system_id_, local_id, DOM_WORK_ID_TASK);
                access_id = dom_work_graph_builder_make_id(system_id_, local_id, DOM_WORK_ID_ACCESS);
                cost_id = dom_work_graph_builder_make_id(system_id_, local_id, DOM_WORK_ID_COST);

                node.task_id = task_id;
                node.system_id = system_id_;
                node.category = DOM_TASK_AUTHORITATIVE;
                node.determinism_class = DOM_DET_STRICT;
                node.fidelity_tier = dom_war_task_fidelity(tier_);
                node.next_due_tick = DOM_EXEC_TICK_INVALID;
                node.access_set_id = access_id;
                node.cost_model_id = cost_id;
                node.law_targets = law_targets_;
                node.law_target_count = law_target_count_;
                node.phase_id = op - 1u;
                node.commit_key = dom_work_graph_builder_make_commit_key(node.phase_id, task_id, 0u);
                node.law_scope_ref = law_scope_ref_;
                node.actor_ref = 0u;
                node.capability_set_ref = 0u;
                node.policy_params = params;
                node.policy_params_size = (u32)sizeof(*params);

                cost.cost_id = cost_id;
                cost.cpu_upper_bound = slice;
                cost.memory_upper_bound = 2u;
                cost.bandwidth_upper_bound = 1u;
                cost.latency_class = DOM_LATENCY_MEDIUM;
                cost.degradation_priority = 1;

                if (op == DOM_WAR_TASK_ENGAGEMENT_ADMIT ||
                    op == DOM_WAR_TASK_ENGAGEMENT_RESOLVE) {
                    reads[read_count].kind = DOM_RANGE_COMPONENT_SET;
                    reads[read_count].component_id = DOM_WAR_COMPONENT_ENGAGEMENT;
                    reads[read_count].field_id = DOM_WAR_FIELD_DEFAULT;
                    reads[read_count].start_id = 0u;
                    reads[read_count].end_id = 0u;
                    reads[read_count].set_id = inputs_->engagement_set_id;
                    read_count += 1u;
                }

                if (op == DOM_WAR_TASK_ENGAGEMENT_RESOLVE) {
                    writes[write_count].kind = DOM_RANGE_COMPONENT_SET;
                    writes[write_count].component_id = DOM_WAR_COMPONENT_OUTCOME;
                    writes[write_count].field_id = DOM_WAR_FIELD_DEFAULT;
                    writes[write_count].start_id = 0u;
                    writes[write_count].end_id = 0u;
                    writes[write_count].set_id = buffers_->outcome_set_id;
                    write_count += 1u;
                }
                if (op == DOM_WAR_TASK_APPLY_CASUALTIES) {
                    reads[read_count].kind = DOM_RANGE_COMPONENT_SET;
                    reads[read_count].component_id = DOM_WAR_COMPONENT_OUTCOME;
                    reads[read_count].field_id = DOM_WAR_FIELD_DEFAULT;
                    reads[read_count].start_id = 0u;
                    reads[read_count].end_id = 0u;
                    reads[read_count].set_id = buffers_->outcome_set_id;
                    read_count += 1u;
                    writes[write_count].kind = DOM_RANGE_COMPONENT_SET;
                    writes[write_count].component_id = DOM_WAR_COMPONENT_CASUALTY;
                    writes[write_count].field_id = DOM_WAR_FIELD_DEFAULT;
                    writes[write_count].start_id = 0u;
                    writes[write_count].end_id = 0u;
                    writes[write_count].set_id = buffers_->casualty_set_id;
                    write_count += 1u;
                }
                if (op == DOM_WAR_TASK_APPLY_EQUIPMENT_LOSSES) {
                    reads[read_count].kind = DOM_RANGE_COMPONENT_SET;
                    reads[read_count].component_id = DOM_WAR_COMPONENT_OUTCOME;
                    reads[read_count].field_id = DOM_WAR_FIELD_DEFAULT;
                    reads[read_count].start_id = 0u;
                    reads[read_count].end_id = 0u;
                    reads[read_count].set_id = buffers_->outcome_set_id;
                    read_count += 1u;
                    writes[write_count].kind = DOM_RANGE_COMPONENT_SET;
                    writes[write_count].component_id = DOM_WAR_COMPONENT_EQUIPMENT;
                    writes[write_count].field_id = DOM_WAR_FIELD_DEFAULT;
                    writes[write_count].start_id = 0u;
                    writes[write_count].end_id = 0u;
                    writes[write_count].set_id = buffers_->equipment_set_id;
                    write_count += 1u;
                }
                if (op == DOM_WAR_TASK_UPDATE_MORALE_READINESS) {
                    reads[read_count].kind = DOM_RANGE_COMPONENT_SET;
                    reads[read_count].component_id = DOM_WAR_COMPONENT_OUTCOME;
                    reads[read_count].field_id = DOM_WAR_FIELD_DEFAULT;
                    reads[read_count].start_id = 0u;
                    reads[read_count].end_id = 0u;
                    reads[read_count].set_id = buffers_->outcome_set_id;
                    read_count += 1u;
                    writes[write_count].kind = DOM_RANGE_COMPONENT_SET;
                    writes[write_count].component_id = DOM_WAR_COMPONENT_MORALE;
                    writes[write_count].field_id = DOM_WAR_FIELD_DEFAULT;
                    writes[write_count].start_id = 0u;
                    writes[write_count].end_id = 0u;
                    writes[write_count].set_id = buffers_->morale_set_id;
                    write_count += 1u;
                }

                if (op == DOM_WAR_TASK_ENGAGEMENT_ADMIT ||
                    op == DOM_WAR_TASK_ENGAGEMENT_RESOLVE) {
                    writes[write_count].kind = DOM_RANGE_COMPONENT_SET;
                    writes[write_count].component_id = DOM_WAR_COMPONENT_ENGAGEMENT;
                    writes[write_count].field_id = DOM_WAR_FIELD_DEFAULT;
                    writes[write_count].start_id = 0u;
                    writes[write_count].end_id = 0u;
                    writes[write_count].set_id = inputs_->engagement_set_id;
                    write_count += 1u;
                }

                writes[write_count].kind = DOM_RANGE_COMPONENT_SET;
                writes[write_count].component_id = DOM_WAR_COMPONENT_AUDIT;
                writes[write_count].field_id = DOM_WAR_FIELD_DEFAULT;
                writes[write_count].start_id = 0u;
                writes[write_count].end_id = 0u;
                writes[write_count].set_id = buffers_->audit_set_id;
                write_count += 1u;

                if (dom_war_emit_task_node(graph_builder, access_builder, &node, &cost,
                                           reads, read_count, writes, write_count) != 0) {
                    return -2;
                }
                if (prev_task_id != 0u) {
                    dom_dependency_edge edge;
                    edge.from_task_id = prev_task_id;
                    edge.to_task_id = task_id;
                    edge.reason_id = 0u;
                    if (dom_work_graph_builder_add_dependency(graph_builder, &edge) != 0) {
                        return -3;
                    }
                }
                prev_task_id = task_id;
                last_emitted_task_count_ += 1u;
                emitted_any = D_TRUE;
            }

            if (emitted_any) {
                runtime_.engagement_cursor = cursor + slice;
                budget -= slice;
            }
        }
    }

    ops[0].op = DOM_WAR_TASK_OCCUPATION_MAINTAIN;
    ops[0].phase_id = 6u;
    ops[0].count = inputs_->occupation_count;
    ops[0].cursor = &runtime_.occupation_cursor;
    ops[0].set_id = inputs_->occupation_set_id;
    ops[0].component_id = DOM_WAR_COMPONENT_OCCUPATION;

    ops[1].op = DOM_WAR_TASK_RESISTANCE_UPDATE;
    ops[1].phase_id = 7u;
    ops[1].count = inputs_->resistance_count;
    ops[1].cursor = &runtime_.resistance_cursor;
    ops[1].set_id = inputs_->resistance_set_id;
    ops[1].component_id = DOM_WAR_COMPONENT_RESISTANCE;

    ops[2].op = DOM_WAR_TASK_DISRUPTION_APPLY;
    ops[2].phase_id = 8u;
    ops[2].count = inputs_->disruption_count;
    ops[2].cursor = &runtime_.disruption_cursor;
    ops[2].set_id = inputs_->disruption_set_id;
    ops[2].component_id = DOM_WAR_COMPONENT_DISRUPTION;

    ops[3].op = DOM_WAR_TASK_ROUTE_CONTROL_UPDATE;
    ops[3].phase_id = 9u;
    ops[3].count = inputs_->route_count;
    ops[3].cursor = &runtime_.route_cursor;
    ops[3].set_id = inputs_->route_set_id;
    ops[3].component_id = DOM_WAR_COMPONENT_ROUTE_CONTROL;

    ops[4].op = DOM_WAR_TASK_BLOCKADE_APPLY;
    ops[4].phase_id = 10u;
    ops[4].count = inputs_->blockade_count;
    ops[4].cursor = &runtime_.blockade_cursor;
    ops[4].set_id = inputs_->blockade_set_id;
    ops[4].component_id = DOM_WAR_COMPONENT_BLOCKADE;

    ops[5].op = DOM_WAR_TASK_INTERDICTION_SCHEDULE;
    ops[5].phase_id = 11u;
    ops[5].count = inputs_->interdiction_count;
    ops[5].cursor = &runtime_.interdiction_cursor;
    ops[5].set_id = inputs_->interdiction_set_id;
    ops[5].component_id = DOM_WAR_COMPONENT_INTERDICTION;

    ops[6].op = DOM_WAR_TASK_INTERDICTION_RESOLVE;
    ops[6].phase_id = 12u;
    ops[6].count = inputs_->interdiction_count;
    ops[6].cursor = &runtime_.interdiction_cursor;
    ops[6].set_id = inputs_->interdiction_set_id;
    ops[6].component_id = DOM_WAR_COMPONENT_INTERDICTION;

    for (i = 0u; i < 7u; ++i) {
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
        dom_access_range reads[1];
        dom_access_range writes[2];
        dom_war_task_params* params;

        if (budget == 0u) {
            break;
        }
        if ((allowed_ops_mask_ & (1u << op->op)) == 0u) {
            continue;
        }
        if (op->count == 0u || op->set_id == 0u) {
            continue;
        }
        if (!buffers_->audit_log) {
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
        params = dom_war_params_for_op(params_, op->op);
        if (!params) {
            continue;
        }
        params->op = op->op;
        params->start_index = cursor;
        params->count = slice;

        local_id = dom_war_local_id_for_op(op->op);
        task_id = dom_work_graph_builder_make_id(system_id_, local_id, DOM_WORK_ID_TASK);
        access_id = dom_work_graph_builder_make_id(system_id_, local_id, DOM_WORK_ID_ACCESS);
        cost_id = dom_work_graph_builder_make_id(system_id_, local_id, DOM_WORK_ID_COST);

        node.task_id = task_id;
        node.system_id = system_id_;
        node.category = DOM_TASK_AUTHORITATIVE;
        node.determinism_class = DOM_DET_STRICT;
        node.fidelity_tier = dom_war_task_fidelity(tier_);
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

        reads[0].kind = DOM_RANGE_COMPONENT_SET;
        reads[0].component_id = op->component_id;
        reads[0].field_id = DOM_WAR_FIELD_DEFAULT;
        reads[0].start_id = 0u;
        reads[0].end_id = 0u;
        reads[0].set_id = op->set_id;

        writes[0].kind = DOM_RANGE_COMPONENT_SET;
        writes[0].component_id = op->component_id;
        writes[0].field_id = DOM_WAR_FIELD_DEFAULT;
        writes[0].start_id = 0u;
        writes[0].end_id = 0u;
        writes[0].set_id = op->set_id;

        writes[1].kind = DOM_RANGE_COMPONENT_SET;
        writes[1].component_id = DOM_WAR_COMPONENT_AUDIT;
        writes[1].field_id = DOM_WAR_FIELD_DEFAULT;
        writes[1].start_id = 0u;
        writes[1].end_id = 0u;
        writes[1].set_id = buffers_->audit_set_id;

        if (dom_war_emit_task_node(graph_builder, access_builder, &node, &cost,
                                   reads, 1u, writes, 2u) != 0) {
            return -4;
        }
        if (prev_task_id != 0u) {
            dom_dependency_edge edge;
            edge.from_task_id = prev_task_id;
            edge.to_task_id = task_id;
            edge.reason_id = 0u;
            if (dom_work_graph_builder_add_dependency(graph_builder, &edge) != 0) {
                return -5;
            }
        }
        prev_task_id = task_id;
        last_emitted_task_count_ += 1u;
        *op->cursor = cursor + slice;
        budget -= slice;
    }

    if (inputs_->engagement_count > 0u ||
        inputs_->occupation_count > 0u ||
        inputs_->resistance_count > 0u ||
        inputs_->disruption_count > 0u ||
        inputs_->route_count > 0u ||
        inputs_->blockade_count > 0u ||
        inputs_->interdiction_count > 0u) {
        has_work = D_TRUE;
    }

    if (inputs_->engagement_count > 0u &&
        runtime_.engagement_cursor < inputs_->engagement_count) {
        cycle_complete = D_FALSE;
    }
    if (inputs_->occupation_count > 0u &&
        runtime_.occupation_cursor < inputs_->occupation_count) {
        cycle_complete = D_FALSE;
    }
    if (inputs_->resistance_count > 0u &&
        runtime_.resistance_cursor < inputs_->resistance_count) {
        cycle_complete = D_FALSE;
    }
    if (inputs_->disruption_count > 0u &&
        runtime_.disruption_cursor < inputs_->disruption_count) {
        cycle_complete = D_FALSE;
    }
    if (inputs_->route_count > 0u &&
        runtime_.route_cursor < inputs_->route_count) {
        cycle_complete = D_FALSE;
    }
    if (inputs_->blockade_count > 0u &&
        runtime_.blockade_cursor < inputs_->blockade_count) {
        cycle_complete = D_FALSE;
    }
    if (inputs_->interdiction_count > 0u &&
        runtime_.interdiction_cursor < inputs_->interdiction_count) {
        cycle_complete = D_FALSE;
    }

    if (has_work == D_FALSE) {
        cycle_in_progress_ = D_FALSE;
    }

    if (cycle_complete == D_TRUE && has_work == D_TRUE) {
        dom_war_runtime_reset(&runtime_);
        cycle_in_progress_ = D_FALSE;
    }

    cadence = dom_war_default_cadence(tier_);
    next_due_tick_ = dom_war_next_due(act_now, cadence, has_work ? D_TRUE : cycle_in_progress_);
    return 0;
}
