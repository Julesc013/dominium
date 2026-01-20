/*
FILE: game/rules/scale/interest_system.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Game / scale rules
RESPONSIBILITY: Work IR-based interest management emission (authoritative tasks only).
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Task emission order and budgeting are deterministic.
*/
#include "dominium/rules/scale/interest_system.h"

#include "dominium/execution/work_graph_builder.h"
#include "dominium/execution/access_set_builder.h"
#include "domino/execution/task_node.h"
#include "domino/execution/cost_model.h"
#include "domino/core/dom_time_core.h"

#include <string.h>

enum {
    DOM_INTEREST_COMPONENT_SOURCE_FEED = 5201u,
    DOM_INTEREST_COMPONENT_STATE = 5202u,
    DOM_INTEREST_COMPONENT_TRANSITION = 5203u,
    DOM_INTEREST_COMPONENT_FIDELITY_REQUEST = 5204u,
    DOM_INTEREST_FIELD_DEFAULT = 1u,
    DOM_INTEREST_FIELD_SOURCE_BASE = 10u
};

static u32 dom_interest_fnv1a32(const char* text)
{
    const unsigned char* bytes = (const unsigned char*)(text ? text : "");
    u32 hash = 2166136261u;
    while (*bytes) {
        hash ^= (u32)(*bytes++);
        hash *= 16777619u;
    }
    return hash;
}

static u64 dom_interest_fnv1a64(const char* text)
{
    const unsigned char* bytes = (const unsigned char*)(text ? text : "");
    u64 hash = 1469598103934665603ULL;
    while (*bytes) {
        hash ^= (u64)(*bytes++);
        hash *= 1099511628211ULL;
    }
    return hash;
}

static u32 dom_interest_task_fidelity(dom_fidelity_tier tier)
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

static u32 dom_interest_default_budget(dom_fidelity_tier tier)
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

static u32 dom_interest_default_cadence(dom_fidelity_tier tier)
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

static dom_act_time_t dom_interest_next_due(dom_act_time_t now,
                                            u32 cadence,
                                            d_bool has_work)
{
    if (!has_work || cadence == 0u) {
        return DOM_TIME_ACT_MAX;
    }
    if (now > (DOM_TIME_ACT_MAX - cadence)) {
        return DOM_TIME_ACT_MAX;
    }
    return now + (dom_act_time_t)cadence;
}

static dom_interest_reason dom_interest_reason_for_source(dom_interest_source_kind kind)
{
    switch (kind) {
        case DOM_INTEREST_SOURCE_PLAYER_FOCUS: return DOM_INTEREST_REASON_PLAYER_FOCUS;
        case DOM_INTEREST_SOURCE_COMMAND_INTENT: return DOM_INTEREST_REASON_COMMAND_INTENT;
        case DOM_INTEREST_SOURCE_LOGISTICS: return DOM_INTEREST_REASON_LOGISTICS_ROUTE;
        case DOM_INTEREST_SOURCE_SENSOR_COMMS: return DOM_INTEREST_REASON_SENSOR_COMMS;
        case DOM_INTEREST_SOURCE_HAZARD_CONFLICT: return DOM_INTEREST_REASON_HAZARD_CONFLICT;
        case DOM_INTEREST_SOURCE_GOVERNANCE_SCOPE: return DOM_INTEREST_REASON_GOVERNANCE_SCOPE;
        default: return DOM_INTEREST_REASON_PLAYER_FOCUS;
    }
}

static d_bool dom_interest_source_valid(const dom_interest_source_feed* feed)
{
    if (!feed) {
        return D_FALSE;
    }
    if (!feed->list.ids || feed->list.count == 0u) {
        return D_FALSE;
    }
    return D_TRUE;
}

static u32 dom_interest_collect_local_id(dom_interest_source_kind kind)
{
    return 1u + (u32)kind;
}

static u32 dom_interest_merge_local_id(void) { return 20u; }
static u32 dom_interest_hysteresis_local_id(void) { return 21u; }
static u32 dom_interest_transition_local_id(void) { return 22u; }

static void dom_interest_bind_buffers(dom_interest_runtime_state* runtime,
                                      const dom_interest_buffers* buffers)
{
    if (!runtime || !buffers) {
        return;
    }
    runtime->scratch_set = buffers->scratch_set;
    runtime->merged_set = buffers->merged_set;
    runtime->relevance_states = buffers->relevance_states;
    runtime->relevance_count = buffers->relevance_count;
    runtime->transitions = buffers->transitions;
    runtime->transition_capacity = buffers->transition_capacity;
    runtime->fidelity_requests = buffers->requests;
    runtime->request_capacity = buffers->request_capacity;
}

InterestSystem::InterestSystem()
    : system_id_(0u),
      law_target_count_(0u),
      law_scope_ref_(1u),
      tier_(DOM_FIDELITY_MACRO),
      next_due_tick_(DOM_TIME_ACT_MAX),
      migration_state_(DOM_INTEREST_STATE_IR_ONLY),
      allowed_sources_mask_(0xFFFFFFFFu),
      last_emitted_task_count_(0u),
      last_emitted_source_mask_(0u),
      cycle_in_progress_(D_FALSE),
      inputs_(0),
      buffers_(0)
{
    u32 i;
    system_id_ = dom_interest_fnv1a64("INTEREST");
    law_targets_[0] = dom_interest_fnv1a32("SCALE.INTEREST");
    law_targets_[1] = dom_interest_fnv1a32("EXEC.AUTH_TASK");
    law_target_count_ = 2u;
    for (i = 0u; i < DOM_INTEREST_SOURCE_COUNT + 3u; ++i) {
        params_[i].op = 0u;
        params_[i].source_kind = 0u;
        params_[i].start_index = 0u;
        params_[i].count = 0u;
        params_[i].reason = 0u;
        params_[i].refine_tier = 0u;
        params_[i].collapse_tier = 0u;
    }
    memset(&runtime_, 0, sizeof(runtime_));
    dom_interest_runtime_reset(&runtime_);
}

int InterestSystem::init(const dom_interest_inputs* inputs,
                         const dom_interest_buffers* buffers)
{
    inputs_ = inputs;
    buffers_ = buffers;
    dom_interest_bind_buffers(&runtime_, buffers_);
    dom_interest_runtime_reset(&runtime_);
    return 0;
}

void InterestSystem::set_inputs(const dom_interest_inputs* inputs)
{
    inputs_ = inputs;
}

void InterestSystem::set_buffers(const dom_interest_buffers* buffers)
{
    buffers_ = buffers;
    dom_interest_bind_buffers(&runtime_, buffers_);
}

void InterestSystem::set_allowed_sources_mask(u32 mask)
{
    allowed_sources_mask_ = mask;
}

void InterestSystem::set_next_due_tick(dom_act_time_t tick)
{
    next_due_tick_ = tick;
}

void InterestSystem::set_migration_state(dom_interest_migration_state state)
{
    migration_state_ = state;
}

dom_interest_migration_state InterestSystem::migration_state() const
{
    return migration_state_;
}

u32 InterestSystem::last_emitted_task_count() const
{
    return last_emitted_task_count_;
}

u32 InterestSystem::last_emitted_source_mask() const
{
    return last_emitted_source_mask_;
}

dom_interest_runtime_state* InterestSystem::runtime_state()
{
    return &runtime_;
}

const dom_interest_runtime_state* InterestSystem::runtime_state() const
{
    return &runtime_;
}

u64 InterestSystem::system_id() const
{
    return system_id_;
}

d_bool InterestSystem::is_sim_affecting() const
{
    return D_TRUE;
}

const u32* InterestSystem::law_targets(u32* out_count) const
{
    if (out_count) {
        *out_count = law_target_count_;
    }
    return law_targets_;
}

dom_act_time_t InterestSystem::get_next_due_tick() const
{
    return next_due_tick_;
}

void InterestSystem::degrade(dom_fidelity_tier tier, u32 reason)
{
    (void)reason;
    tier_ = tier;
}

int InterestSystem::emit_tasks(dom_act_time_t act_now,
                               dom_act_time_t act_target,
                               dom_work_graph_builder* graph_builder,
                               dom_access_set_builder* access_builder)
{
    static const dom_interest_source_kind priority_order[] = {
        DOM_INTEREST_SOURCE_PLAYER_FOCUS,
        DOM_INTEREST_SOURCE_COMMAND_INTENT,
        DOM_INTEREST_SOURCE_LOGISTICS,
        DOM_INTEREST_SOURCE_SENSOR_COMMS,
        DOM_INTEREST_SOURCE_HAZARD_CONFLICT,
        DOM_INTEREST_SOURCE_GOVERNANCE_SCOPE
    };
    u64 collect_task_ids[DOM_INTEREST_SOURCE_COUNT];
    u32 collect_task_count = 0u;
    u32 i;
    u32 budget;
    u32 cadence;
    d_bool has_sources = D_FALSE;
    d_bool cycle_complete = D_TRUE;

    (void)act_target;
    last_emitted_task_count_ = 0u;
    last_emitted_source_mask_ = 0u;

    if (!graph_builder || !access_builder) {
        return -1;
    }
    if (!inputs_ || !buffers_) {
        return 0;
    }
    if (!buffers_->scratch_set || !buffers_->merged_set) {
        return 0;
    }
    dom_interest_bind_buffers(&runtime_, buffers_);

    budget = dom_interest_default_budget(tier_);
    if (budget_hint() > 0u) {
        if (budget == 0u || budget_hint() < budget) {
            budget = budget_hint();
        }
    }
    if ((allowed_sources_mask_ & (1u << DOM_INTEREST_SOURCE_PLAYER_FOCUS)) &&
        inputs_->sources[DOM_INTEREST_SOURCE_PLAYER_FOCUS].list.count > 0u &&
        budget == 0u) {
        budget = 1u;
    }

    if (cycle_in_progress_ == D_FALSE) {
        dom_interest_runtime_reset(&runtime_);
        cycle_in_progress_ = D_TRUE;
    }

    for (i = 0u; i < DOM_INTEREST_SOURCE_COUNT; ++i) {
        dom_interest_source_kind kind = priority_order[i];
        const dom_interest_source_feed* feed;
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
        dom_interest_task_params* params;
        if (budget == 0u) {
            break;
        }
        if ((allowed_sources_mask_ & (1u << kind)) == 0u) {
            continue;
        }
        feed = &inputs_->sources[kind];
        if (!dom_interest_source_valid(feed)) {
            continue;
        }
        has_sources = D_TRUE;
        cursor = runtime_.source_cursor[kind];
        if (cursor >= feed->list.count) {
            cursor = 0u;
            runtime_.source_cursor[kind] = 0u;
        }
        remaining = feed->list.count - cursor;
        if (remaining == 0u) {
            continue;
        }
        slice = remaining;
        if (slice > budget) {
            slice = budget;
        }
        params = &params_[kind];
        params->op = DOM_INTEREST_TASK_COLLECT_SOURCES;
        params->source_kind = (u32)kind;
        params->start_index = cursor;
        params->count = slice;
        params->reason = (u32)dom_interest_reason_for_source(kind);
        params->refine_tier = (u32)inputs_->refine_tier;
        params->collapse_tier = (u32)inputs_->collapse_tier;

        local_id = dom_interest_collect_local_id(kind);
        task_id = dom_work_graph_builder_make_id(system_id_, local_id, DOM_WORK_ID_TASK);
        access_id = dom_work_graph_builder_make_id(system_id_, local_id, DOM_WORK_ID_ACCESS);
        cost_id = dom_work_graph_builder_make_id(system_id_, local_id, DOM_WORK_ID_COST);

        node.task_id = task_id;
        node.system_id = system_id_;
        node.category = DOM_TASK_AUTHORITATIVE;
        node.determinism_class = DOM_DET_STRICT;
        node.fidelity_tier = dom_interest_task_fidelity(tier_);
        node.next_due_tick = DOM_EXEC_TICK_INVALID;
        node.access_set_id = access_id;
        node.cost_model_id = cost_id;
        node.law_targets = law_targets_;
        node.law_target_count = law_target_count_;
        node.phase_id = 0u;
        node.commit_key = dom_work_graph_builder_make_commit_key(0u, task_id, 0u);
        node.law_scope_ref = law_scope_ref_;
        node.actor_ref = 0u;
        node.capability_set_ref = 0u;
        node.policy_params = params;
        node.policy_params_size = (u32)sizeof(*params);

        cost.cost_id = cost_id;
        cost.cpu_upper_bound = slice;
        cost.memory_upper_bound = 1u;
        cost.bandwidth_upper_bound = 1u;
        cost.latency_class = DOM_LATENCY_MEDIUM;
        cost.degradation_priority = 1;

        if (dom_work_graph_builder_add_cost_model(graph_builder, &cost) != 0) {
            return -2;
        }
        if (!dom_access_set_builder_begin(access_builder, access_id, DOM_REDUCE_NONE, 0)) {
            return -3;
        }

        range.kind = DOM_RANGE_COMPONENT_SET;
        range.component_id = DOM_INTEREST_COMPONENT_SOURCE_FEED;
        range.field_id = DOM_INTEREST_FIELD_SOURCE_BASE + (u32)kind;
        range.start_id = 0u;
        range.end_id = 0u;
        range.set_id = feed->set_id;
        if (dom_access_set_builder_add_read(access_builder, &range) != 0) {
            return -4;
        }

        range.kind = DOM_RANGE_INTEREST_SET;
        range.component_id = 0u;
        range.field_id = 0u;
        range.start_id = 0u;
        range.end_id = 0u;
        range.set_id = buffers_->scratch_set_id;
        if (dom_access_set_builder_add_write(access_builder, &range) != 0) {
            return -5;
        }
        if (dom_access_set_builder_finalize(access_builder) != 0) {
            return -6;
        }
        if (dom_work_graph_builder_add_task(graph_builder, &node) != 0) {
            return -7;
        }

        collect_task_ids[collect_task_count++] = task_id;
        last_emitted_task_count_ += 1u;
        last_emitted_source_mask_ |= (1u << kind);
        budget -= slice;
        runtime_.source_cursor[kind] = cursor + slice;
    }

    for (i = 0u; i < DOM_INTEREST_SOURCE_COUNT; ++i) {
        dom_interest_source_kind kind = (dom_interest_source_kind)i;
        const dom_interest_source_feed* feed = &inputs_->sources[kind];
        if ((allowed_sources_mask_ & (1u << kind)) == 0u) {
            continue;
        }
        if (!dom_interest_source_valid(feed)) {
            continue;
        }
        has_sources = D_TRUE;
        if (runtime_.source_cursor[kind] < feed->list.count) {
            cycle_complete = D_FALSE;
        }
    }

    if (cycle_complete == D_TRUE && collect_task_count > 0u) {
        dom_task_node node;
        dom_cost_model cost;
        dom_access_range range;
        dom_dependency_edge edge;
        dom_interest_task_params* params;
        u64 task_id;
        u64 access_id;
        u64 cost_id;
        u32 local_id;

        params = &params_[DOM_INTEREST_SOURCE_COUNT];
        params->op = DOM_INTEREST_TASK_MERGE;
        params->source_kind = 0u;
        params->start_index = 0u;
        params->count = 0u;
        params->reason = 0u;
        params->refine_tier = (u32)inputs_->refine_tier;
        params->collapse_tier = (u32)inputs_->collapse_tier;

        local_id = dom_interest_merge_local_id();
        task_id = dom_work_graph_builder_make_id(system_id_, local_id, DOM_WORK_ID_TASK);
        access_id = dom_work_graph_builder_make_id(system_id_, local_id, DOM_WORK_ID_ACCESS);
        cost_id = dom_work_graph_builder_make_id(system_id_, local_id, DOM_WORK_ID_COST);

        node.task_id = task_id;
        node.system_id = system_id_;
        node.category = DOM_TASK_AUTHORITATIVE;
        node.determinism_class = DOM_DET_STRICT;
        node.fidelity_tier = dom_interest_task_fidelity(tier_);
        node.next_due_tick = DOM_EXEC_TICK_INVALID;
        node.access_set_id = access_id;
        node.cost_model_id = cost_id;
        node.law_targets = law_targets_;
        node.law_target_count = law_target_count_;
        node.phase_id = 1u;
        node.commit_key = dom_work_graph_builder_make_commit_key(1u, task_id, 0u);
        node.law_scope_ref = law_scope_ref_;
        node.actor_ref = 0u;
        node.capability_set_ref = 0u;
        node.policy_params = params;
        node.policy_params_size = (u32)sizeof(*params);

        cost.cost_id = cost_id;
        cost.cpu_upper_bound = 4u;
        cost.memory_upper_bound = 2u;
        cost.bandwidth_upper_bound = 1u;
        cost.latency_class = DOM_LATENCY_LOW;
        cost.degradation_priority = 0;

        if (dom_work_graph_builder_add_cost_model(graph_builder, &cost) != 0) {
            return -8;
        }
        if (!dom_access_set_builder_begin(access_builder, access_id, DOM_REDUCE_NONE, 0)) {
            return -9;
        }
        range.kind = DOM_RANGE_INTEREST_SET;
        range.component_id = 0u;
        range.field_id = 0u;
        range.start_id = 0u;
        range.end_id = 0u;
        range.set_id = buffers_->scratch_set_id;
        if (dom_access_set_builder_add_read(access_builder, &range) != 0) {
            return -10;
        }
        range.set_id = buffers_->merged_set_id;
        if (dom_access_set_builder_add_write(access_builder, &range) != 0) {
            return -11;
        }
        if (dom_access_set_builder_finalize(access_builder) != 0) {
            return -12;
        }
        if (dom_work_graph_builder_add_task(graph_builder, &node) != 0) {
            return -13;
        }
        last_emitted_task_count_ += 1u;

        for (i = 0u; i < collect_task_count; ++i) {
            edge.from_task_id = collect_task_ids[i];
            edge.to_task_id = task_id;
            edge.reason_id = 0u;
            if (dom_work_graph_builder_add_dependency(graph_builder, &edge) != 0) {
                return -14;
            }
        }

        params = &params_[DOM_INTEREST_SOURCE_COUNT + 1u];
        params->op = DOM_INTEREST_TASK_APPLY_HYSTERESIS;
        params->source_kind = 0u;
        params->start_index = 0u;
        params->count = 0u;
        params->reason = 0u;
        params->refine_tier = (u32)inputs_->refine_tier;
        params->collapse_tier = (u32)inputs_->collapse_tier;

        local_id = dom_interest_hysteresis_local_id();
        task_id = dom_work_graph_builder_make_id(system_id_, local_id, DOM_WORK_ID_TASK);
        access_id = dom_work_graph_builder_make_id(system_id_, local_id, DOM_WORK_ID_ACCESS);
        cost_id = dom_work_graph_builder_make_id(system_id_, local_id, DOM_WORK_ID_COST);

        node.task_id = task_id;
        node.system_id = system_id_;
        node.category = DOM_TASK_AUTHORITATIVE;
        node.determinism_class = DOM_DET_STRICT;
        node.fidelity_tier = dom_interest_task_fidelity(tier_);
        node.next_due_tick = DOM_EXEC_TICK_INVALID;
        node.access_set_id = access_id;
        node.cost_model_id = cost_id;
        node.law_targets = law_targets_;
        node.law_target_count = law_target_count_;
        node.phase_id = 2u;
        node.commit_key = dom_work_graph_builder_make_commit_key(2u, task_id, 0u);
        node.law_scope_ref = law_scope_ref_;
        node.actor_ref = 0u;
        node.capability_set_ref = 0u;
        node.policy_params = params;
        node.policy_params_size = (u32)sizeof(*params);

        cost.cost_id = cost_id;
        cost.cpu_upper_bound = 3u;
        cost.memory_upper_bound = 2u;
        cost.bandwidth_upper_bound = 1u;
        cost.latency_class = DOM_LATENCY_LOW;
        cost.degradation_priority = 0;

        if (dom_work_graph_builder_add_cost_model(graph_builder, &cost) != 0) {
            return -15;
        }
        if (!dom_access_set_builder_begin(access_builder, access_id, DOM_REDUCE_NONE, 0)) {
            return -16;
        }
        range.kind = DOM_RANGE_INTEREST_SET;
        range.component_id = 0u;
        range.field_id = 0u;
        range.start_id = 0u;
        range.end_id = 0u;
        range.set_id = buffers_->merged_set_id;
        if (dom_access_set_builder_add_read(access_builder, &range) != 0) {
            return -17;
        }
        range.kind = DOM_RANGE_COMPONENT_SET;
        range.component_id = DOM_INTEREST_COMPONENT_STATE;
        range.field_id = DOM_INTEREST_FIELD_DEFAULT;
        range.start_id = 0u;
        range.end_id = 0u;
        range.set_id = buffers_->state_set_id;
        if (dom_access_set_builder_add_read(access_builder, &range) != 0) {
            return -18;
        }
        if (dom_access_set_builder_add_write(access_builder, &range) != 0) {
            return -19;
        }
        range.component_id = DOM_INTEREST_COMPONENT_TRANSITION;
        range.set_id = buffers_->transition_set_id;
        if (dom_access_set_builder_add_write(access_builder, &range) != 0) {
            return -20;
        }
        if (dom_access_set_builder_finalize(access_builder) != 0) {
            return -21;
        }
        if (dom_work_graph_builder_add_task(graph_builder, &node) != 0) {
            return -22;
        }
        last_emitted_task_count_ += 1u;

        edge.from_task_id = dom_work_graph_builder_make_id(system_id_, dom_interest_merge_local_id(), DOM_WORK_ID_TASK);
        edge.to_task_id = task_id;
        edge.reason_id = 0u;
        if (dom_work_graph_builder_add_dependency(graph_builder, &edge) != 0) {
            return -23;
        }

        params = &params_[DOM_INTEREST_SOURCE_COUNT + 2u];
        params->op = DOM_INTEREST_TASK_BUILD_REQUESTS;
        params->source_kind = 0u;
        params->start_index = 0u;
        params->count = 0u;
        params->reason = inputs_->request_reason;
        params->refine_tier = (u32)inputs_->refine_tier;
        params->collapse_tier = (u32)inputs_->collapse_tier;

        local_id = dom_interest_transition_local_id();
        task_id = dom_work_graph_builder_make_id(system_id_, local_id, DOM_WORK_ID_TASK);
        access_id = dom_work_graph_builder_make_id(system_id_, local_id, DOM_WORK_ID_ACCESS);
        cost_id = dom_work_graph_builder_make_id(system_id_, local_id, DOM_WORK_ID_COST);

        node.task_id = task_id;
        node.system_id = system_id_;
        node.category = DOM_TASK_AUTHORITATIVE;
        node.determinism_class = DOM_DET_STRICT;
        node.fidelity_tier = dom_interest_task_fidelity(tier_);
        node.next_due_tick = DOM_EXEC_TICK_INVALID;
        node.access_set_id = access_id;
        node.cost_model_id = cost_id;
        node.law_targets = law_targets_;
        node.law_target_count = law_target_count_;
        node.phase_id = 3u;
        node.commit_key = dom_work_graph_builder_make_commit_key(3u, task_id, 0u);
        node.law_scope_ref = law_scope_ref_;
        node.actor_ref = 0u;
        node.capability_set_ref = 0u;
        node.policy_params = params;
        node.policy_params_size = (u32)sizeof(*params);

        cost.cost_id = cost_id;
        cost.cpu_upper_bound = 2u;
        cost.memory_upper_bound = 1u;
        cost.bandwidth_upper_bound = 1u;
        cost.latency_class = DOM_LATENCY_LOW;
        cost.degradation_priority = 0;

        if (dom_work_graph_builder_add_cost_model(graph_builder, &cost) != 0) {
            return -24;
        }
        if (!dom_access_set_builder_begin(access_builder, access_id, DOM_REDUCE_NONE, 0)) {
            return -25;
        }
        range.kind = DOM_RANGE_COMPONENT_SET;
        range.component_id = DOM_INTEREST_COMPONENT_TRANSITION;
        range.field_id = DOM_INTEREST_FIELD_DEFAULT;
        range.start_id = 0u;
        range.end_id = 0u;
        range.set_id = buffers_->transition_set_id;
        if (dom_access_set_builder_add_read(access_builder, &range) != 0) {
            return -26;
        }
        range.component_id = DOM_INTEREST_COMPONENT_FIDELITY_REQUEST;
        range.set_id = buffers_->request_set_id;
        if (dom_access_set_builder_add_write(access_builder, &range) != 0) {
            return -27;
        }
        if (dom_access_set_builder_finalize(access_builder) != 0) {
            return -28;
        }
        if (dom_work_graph_builder_add_task(graph_builder, &node) != 0) {
            return -29;
        }
        last_emitted_task_count_ += 1u;

        edge.from_task_id = dom_work_graph_builder_make_id(system_id_, dom_interest_hysteresis_local_id(), DOM_WORK_ID_TASK);
        edge.to_task_id = task_id;
        edge.reason_id = 0u;
        if (dom_work_graph_builder_add_dependency(graph_builder, &edge) != 0) {
            return -30;
        }

        for (i = 0u; i < DOM_INTEREST_SOURCE_COUNT; ++i) {
            runtime_.source_cursor[i] = 0u;
        }
        cycle_in_progress_ = D_FALSE;
    }

    if (has_sources == D_FALSE) {
        cycle_in_progress_ = D_FALSE;
    }

    cadence = dom_interest_default_cadence(tier_);
    next_due_tick_ = dom_interest_next_due(act_now, cadence, has_sources ? D_TRUE : cycle_in_progress_);
    return 0;
}
