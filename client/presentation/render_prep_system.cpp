/*
FILE: client/presentation/render_prep_system.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Client / presentation
RESPONSIBILITY: Render prep Work IR emission (derived tasks only).
ALLOWED DEPENDENCIES: engine/include/**, game/include/** public headers, and C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
DETERMINISM: Task emission and degradation are deterministic.
*/
#include "render_prep_system.h"

#include "dominium/execution/work_graph_builder.h"
#include "dominium/execution/access_set_builder.h"
#include "domino/execution/task_node.h"
#include "domino/execution/cost_model.h"

enum {
    DOM_RENDER_PREP_COMPONENT_PACKED_VIEW = 7001u,
    DOM_RENDER_PREP_COMPONENT_VIS_MASK = 7002u,
    DOM_RENDER_PREP_COMPONENT_INSTANCE_BUF = 7003u,
    DOM_RENDER_PREP_COMPONENT_DRAW_LIST = 7004u,
    DOM_RENDER_PREP_FIELD_DEFAULT = 1u
};

static u32 dom_render_prep_fnv1a32(const char* text)
{
    const unsigned char* bytes = (const unsigned char*)(text ? text : "");
    u32 hash = 2166136261u;
    while (*bytes) {
        hash ^= (u32)(*bytes++);
        hash *= 16777619u;
    }
    return hash;
}

static u64 dom_render_prep_fnv1a64(const char* text)
{
    const unsigned char* bytes = (const unsigned char*)(text ? text : "");
    u64 hash = 1469598103934665603ULL;
    while (*bytes) {
        hash ^= (u64)(*bytes++);
        hash *= 1099511628211ULL;
    }
    return hash;
}

static u32 dom_render_prep_task_fidelity(dom_fidelity_tier tier)
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

static u32 dom_render_prep_allowed_ops(dom_fidelity_tier tier)
{
    switch (tier) {
        case DOM_FIDELITY_FOCUS:
        case DOM_FIDELITY_MICRO:
            return (1u << DOM_RENDER_PREP_OP_BUILD_VISIBILITY_MASK) |
                   (1u << DOM_RENDER_PREP_OP_BUILD_INSTANCE_LIST) |
                   (1u << DOM_RENDER_PREP_OP_BUILD_DRAW_LIST);
        case DOM_FIDELITY_MESO:
            return (1u << DOM_RENDER_PREP_OP_BUILD_VISIBILITY_MASK) |
                   (1u << DOM_RENDER_PREP_OP_BUILD_DRAW_LIST);
        case DOM_FIDELITY_MACRO:
            return (1u << DOM_RENDER_PREP_OP_BUILD_DRAW_LIST);
        case DOM_FIDELITY_LATENT:
        default:
            return 0u;
    }
}

static u32 dom_render_prep_select_ops(u32 allowed_mask, u32 budget_hint)
{
    u32 selected = 0u;
    u32 picked = 0u;
    u32 limit = budget_hint == 0u ? 3u : budget_hint;
    static const u32 priority_ops[3] = {
        DOM_RENDER_PREP_OP_BUILD_DRAW_LIST,
        DOM_RENDER_PREP_OP_BUILD_VISIBILITY_MASK,
        DOM_RENDER_PREP_OP_BUILD_INSTANCE_LIST
    };
    u32 i;

    if (allowed_mask == 0u || limit == 0u) {
        return 0u;
    }

    for (i = 0u; i < 3u; ++i) {
        u32 op = priority_ops[i];
        u32 bit = (1u << op);
        if ((allowed_mask & bit) == 0u) {
            continue;
        }
        selected |= bit;
        picked += 1u;
        if (picked >= limit) {
            break;
        }
    }
    return selected;
}

static int dom_render_prep_emit_one(dom_work_graph_builder* graph_builder,
                                    dom_access_set_builder* access_builder,
                                    u64 system_id,
                                    u32 op,
                                    u32 phase_id,
                                    const dom_render_prep_inputs* inputs,
                                    const dom_render_prep_buffers* buffers,
                                    dom_render_prep_task_params* params,
                                    u32 fidelity,
                                    u64 law_scope_ref,
                                    const u32* law_targets,
                                    u32 law_target_count,
                                    const dom_frame_graph_desc* graph_desc)
{
    u32 local_id;
    u64 task_id;
    u64 access_id;
    u64 cost_id;
    dom_task_node node;
    dom_cost_model cost;
    dom_access_range range;

    switch (op) {
        case DOM_RENDER_PREP_OP_BUILD_VISIBILITY_MASK: local_id = 1u; break;
        case DOM_RENDER_PREP_OP_BUILD_INSTANCE_LIST: local_id = 2u; break;
        case DOM_RENDER_PREP_OP_BUILD_DRAW_LIST: local_id = 3u; break;
        default: return -1;
    }

    task_id = dom_work_graph_builder_make_id(system_id, local_id, DOM_WORK_ID_TASK);
    access_id = dom_work_graph_builder_make_id(system_id, local_id, DOM_WORK_ID_ACCESS);
    cost_id = dom_work_graph_builder_make_id(system_id, local_id, DOM_WORK_ID_COST);

    params->op = op;
    params->fidelity = fidelity;
    params->pass_count = graph_desc ? graph_desc->pass_count : 0u;
    params->flags = graph_desc ? graph_desc->flags : 0u;
    params->frame_graph_id = graph_desc ? graph_desc->graph_id : 0u;

    node.task_id = task_id;
    node.system_id = system_id;
    node.category = DOM_TASK_DERIVED;
    node.determinism_class = DOM_DET_DERIVED;
    node.fidelity_tier = fidelity;
    node.next_due_tick = DOM_EXEC_TICK_INVALID;
    node.access_set_id = access_id;
    node.cost_model_id = cost_id;
    node.law_targets = law_targets;
    node.law_target_count = law_target_count;
    node.phase_id = phase_id;
    node.commit_key = dom_work_graph_builder_make_commit_key(phase_id, task_id, 0u);
    node.law_scope_ref = law_scope_ref;
    node.actor_ref = 0u;
    node.capability_set_ref = 0u;
    node.policy_params = params;
    node.policy_params_size = (u32)sizeof(*params);

    cost.cost_id = cost_id;
    cost.cpu_upper_bound = (op == DOM_RENDER_PREP_OP_BUILD_INSTANCE_LIST) ? 6u : 4u;
    cost.memory_upper_bound = 2u;
    cost.bandwidth_upper_bound = 1u;
    cost.latency_class = DOM_LATENCY_HIGH;
    cost.degradation_priority = 1;

    if (dom_work_graph_builder_add_cost_model(graph_builder, &cost) != 0) {
        return -2;
    }
    if (!dom_access_set_builder_begin(access_builder, access_id, DOM_REDUCE_NONE, 0)) {
        return -3;
    }

    if (op == DOM_RENDER_PREP_OP_BUILD_VISIBILITY_MASK ||
        op == DOM_RENDER_PREP_OP_BUILD_INSTANCE_LIST) {
        range.kind = DOM_RANGE_COMPONENT_SET;
        range.component_id = DOM_RENDER_PREP_COMPONENT_PACKED_VIEW;
        range.field_id = DOM_RENDER_PREP_FIELD_DEFAULT;
        range.start_id = 0u;
        range.end_id = 0u;
        range.set_id = inputs ? inputs->packed_view_set_id : 0u;
        if (dom_access_set_builder_add_read(access_builder, &range) != 0) {
            return -4;
        }
    }

    if (op == DOM_RENDER_PREP_OP_BUILD_INSTANCE_LIST ||
        op == DOM_RENDER_PREP_OP_BUILD_DRAW_LIST) {
        range.kind = DOM_RANGE_SINGLE;
        range.component_id = DOM_RENDER_PREP_COMPONENT_VIS_MASK;
        range.field_id = DOM_RENDER_PREP_FIELD_DEFAULT;
        range.start_id = buffers ? buffers->visibility_buffer_id : 0u;
        range.end_id = range.start_id;
        range.set_id = 0u;
        if (dom_access_set_builder_add_read(access_builder, &range) != 0) {
            return -5;
        }
    }

    if (op == DOM_RENDER_PREP_OP_BUILD_DRAW_LIST) {
        range.kind = DOM_RANGE_SINGLE;
        range.component_id = DOM_RENDER_PREP_COMPONENT_INSTANCE_BUF;
        range.field_id = DOM_RENDER_PREP_FIELD_DEFAULT;
        range.start_id = buffers ? buffers->instance_buffer_id : 0u;
        range.end_id = range.start_id;
        range.set_id = 0u;
        if (dom_access_set_builder_add_read(access_builder, &range) != 0) {
            return -6;
        }
    }

    if (op == DOM_RENDER_PREP_OP_BUILD_VISIBILITY_MASK) {
        range.kind = DOM_RANGE_SINGLE;
        range.component_id = DOM_RENDER_PREP_COMPONENT_VIS_MASK;
        range.field_id = DOM_RENDER_PREP_FIELD_DEFAULT;
        range.start_id = buffers ? buffers->visibility_buffer_id : 0u;
        range.end_id = range.start_id;
        range.set_id = 0u;
        if (dom_access_set_builder_add_write(access_builder, &range) != 0) {
            return -7;
        }
    } else if (op == DOM_RENDER_PREP_OP_BUILD_INSTANCE_LIST) {
        range.kind = DOM_RANGE_SINGLE;
        range.component_id = DOM_RENDER_PREP_COMPONENT_INSTANCE_BUF;
        range.field_id = DOM_RENDER_PREP_FIELD_DEFAULT;
        range.start_id = buffers ? buffers->instance_buffer_id : 0u;
        range.end_id = range.start_id;
        range.set_id = 0u;
        if (dom_access_set_builder_add_write(access_builder, &range) != 0) {
            return -8;
        }
    } else if (op == DOM_RENDER_PREP_OP_BUILD_DRAW_LIST) {
        range.kind = DOM_RANGE_SINGLE;
        range.component_id = DOM_RENDER_PREP_COMPONENT_DRAW_LIST;
        range.field_id = DOM_RENDER_PREP_FIELD_DEFAULT;
        range.start_id = buffers ? buffers->draw_list_buffer_id : 0u;
        range.end_id = range.start_id;
        range.set_id = 0u;
        if (dom_access_set_builder_add_write(access_builder, &range) != 0) {
            return -9;
        }
    }

    if (dom_access_set_builder_finalize(access_builder) != 0) {
        return -10;
    }
    if (dom_work_graph_builder_add_task(graph_builder, &node) != 0) {
        return -11;
    }
    return 0;
}

RenderPrepSystem::RenderPrepSystem()
    : system_id_(0u),
      law_target_count_(0u),
      law_scope_ref_(1u),
      tier_(DOM_FIDELITY_MACRO),
      next_due_tick_(DOM_TIME_ACT_MAX),
      presentation_enabled_(D_TRUE),
      migration_state_(DOM_RENDER_PREP_STATE_IR_ONLY),
      last_emitted_task_count_(0u),
      inputs_(0),
      buffers_(0)
{
    u32 i;
    system_id_ = dom_render_prep_fnv1a64("RENDER_PREP");
    law_targets_[0] = dom_render_prep_fnv1a32("EXEC.DERIVED_TASK");
    law_targets_[1] = dom_render_prep_fnv1a32("UI.PRESENTATION");
    law_target_count_ = 2u;
    dom_frame_graph_builder_init(&graph_builder_, dom_render_prep_fnv1a64("RENDER_PREP_FRAME_GRAPH"));
    last_graph_ = graph_builder_.last_desc;
    for (i = 0u; i < 3u; ++i) {
        params_[i].op = 0u;
        params_[i].fidelity = 0u;
        params_[i].pass_count = 0u;
        params_[i].flags = 0u;
        params_[i].frame_graph_id = 0u;
    }
}

int RenderPrepSystem::init(const dom_render_prep_inputs* inputs,
                           const dom_render_prep_buffers* buffers)
{
    inputs_ = inputs;
    buffers_ = buffers;
    return 0;
}

void RenderPrepSystem::set_inputs(const dom_render_prep_inputs* inputs)
{
    inputs_ = inputs;
}

void RenderPrepSystem::set_buffers(const dom_render_prep_buffers* buffers)
{
    buffers_ = buffers;
}

void RenderPrepSystem::set_presentation_enabled(d_bool enabled)
{
    presentation_enabled_ = enabled ? D_TRUE : D_FALSE;
}

void RenderPrepSystem::set_next_due_tick(dom_act_time_t tick)
{
    next_due_tick_ = tick;
}

dom_render_prep_migration_state RenderPrepSystem::migration_state() const
{
    return migration_state_;
}

u32 RenderPrepSystem::last_emitted_task_count() const
{
    return last_emitted_task_count_;
}

u64 RenderPrepSystem::last_frame_id() const
{
    return last_graph_.graph_id;
}

u64 RenderPrepSystem::system_id() const
{
    return system_id_;
}

d_bool RenderPrepSystem::is_sim_affecting() const
{
    return D_FALSE;
}

const u32* RenderPrepSystem::law_targets(u32* out_count) const
{
    if (out_count) {
        *out_count = law_target_count_;
    }
    return law_targets_;
}

dom_act_time_t RenderPrepSystem::get_next_due_tick() const
{
    return next_due_tick_;
}

void RenderPrepSystem::degrade(dom_fidelity_tier tier, u32 reason)
{
    (void)reason;
    tier_ = tier;
}

int RenderPrepSystem::emit_tasks(dom_act_time_t act_now,
                                 dom_act_time_t act_target,
                                 dom_work_graph_builder* graph_builder,
                                 dom_access_set_builder* access_builder)
{
    u32 allowed;
    u32 selected;
    u32 fidelity;
    dom_frame_graph_desc graph_desc;
    (void)act_now;
    (void)act_target;

    last_emitted_task_count_ = 0u;
    if (!graph_builder || !access_builder) {
        return -1;
    }
    if (presentation_enabled_ != D_TRUE) {
        return 0;
    }
    if (!inputs_ || !buffers_) {
        return 0;
    }

    allowed = dom_render_prep_allowed_ops(tier_);
    selected = dom_render_prep_select_ops(allowed, budget_hint());
    if (selected == 0u) {
        return 0;
    }

    dom_frame_graph_builder_build(&graph_builder_, inputs_, tier_, &graph_desc);
    last_graph_ = graph_desc;
    fidelity = dom_render_prep_task_fidelity(tier_);

    if (selected & (1u << DOM_RENDER_PREP_OP_BUILD_VISIBILITY_MASK)) {
        if (dom_render_prep_emit_one(graph_builder, access_builder, system_id_,
                                     DOM_RENDER_PREP_OP_BUILD_VISIBILITY_MASK, 0u,
                                     inputs_, buffers_, &params_[0],
                                     fidelity, law_scope_ref_, law_targets_,
                                     law_target_count_, &graph_desc) != 0) {
            return -2;
        }
        last_emitted_task_count_ += 1u;
    }
    if (selected & (1u << DOM_RENDER_PREP_OP_BUILD_INSTANCE_LIST)) {
        if (dom_render_prep_emit_one(graph_builder, access_builder, system_id_,
                                     DOM_RENDER_PREP_OP_BUILD_INSTANCE_LIST, 1u,
                                     inputs_, buffers_, &params_[1],
                                     fidelity, law_scope_ref_, law_targets_,
                                     law_target_count_, &graph_desc) != 0) {
            return -3;
        }
        last_emitted_task_count_ += 1u;
    }
    if (selected & (1u << DOM_RENDER_PREP_OP_BUILD_DRAW_LIST)) {
        if (dom_render_prep_emit_one(graph_builder, access_builder, system_id_,
                                     DOM_RENDER_PREP_OP_BUILD_DRAW_LIST, 2u,
                                     inputs_, buffers_, &params_[2],
                                     fidelity, law_scope_ref_, law_targets_,
                                     law_target_count_, &graph_desc) != 0) {
            return -4;
        }
        last_emitted_task_count_ += 1u;
    }

    return 0;
}
