/*
FILE: game/core/sim/macro_due_scheduler_hooks.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Game / sim
RESPONSIBILITY: Implements macro due-scheduler hooks for survival and population subsystems.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Aggregation is deterministic.
*/
#include "dominium/sim/macro_due_scheduler_hooks.h"
#include "macro_due_emit.h"
#include "domino/execution/task_node.h"
#include "domino/execution/access_set.h"
#include "domino/execution/cost_model.h"
#include "domino/sim/dg_due_sched.h"

static u32 dom_macro_fnv1a32(const char* text)
{
    const unsigned char* bytes = (const unsigned char*)(text ? text : "");
    u32 hash = 2166136261u;
    while (*bytes) {
        hash ^= (u32)(*bytes++);
        hash *= 16777619u;
    }
    return hash;
}

static u32 dom_macro_task_fidelity(dom_fidelity_tier tier)
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

static u64 dom_macro_exec_tick(dom_act_time_t act_tick)
{
    if (act_tick < 0) {
        return DOM_EXEC_TICK_INVALID;
    }
    return (u64)act_tick;
}

static int dom_macro_emit_one(dom_work_graph_builder* graph_builder,
                              dom_access_set_builder* access_builder,
                              u64 system_id,
                              u32 local_id,
                              dom_act_time_t due_tick,
                              u32 component_id,
                              const u32* law_targets,
                              u32 law_target_count,
                              u32 fidelity_tier)
{
    dom_task_node node;
    dom_access_range range;
    dom_cost_model cost;
    u64 task_id = dom_work_graph_builder_make_id(system_id, local_id, DOM_WORK_ID_TASK);
    u64 access_id = dom_work_graph_builder_make_id(system_id, local_id, DOM_WORK_ID_ACCESS);
    u64 cost_id = dom_work_graph_builder_make_id(system_id, local_id, DOM_WORK_ID_COST);

    node.task_id = task_id;
    node.system_id = system_id;
    node.category = DOM_TASK_AUTHORITATIVE;
    node.determinism_class = DOM_DET_STRICT;
    node.fidelity_tier = fidelity_tier;
    node.next_due_tick = dom_macro_exec_tick(due_tick);
    node.access_set_id = access_id;
    node.cost_model_id = cost_id;
    node.law_targets = law_targets;
    node.law_target_count = law_target_count;
    node.phase_id = 0u;
    node.commit_key = dom_work_graph_builder_make_commit_key(0u, task_id, 0u);
    node.law_scope_ref = 0u;
    node.actor_ref = 0u;
    node.capability_set_ref = 0u;
    node.policy_params = (const void*)0;
    node.policy_params_size = 0u;

    cost.cost_id = cost_id;
    cost.cpu_upper_bound = 4u;
    cost.memory_upper_bound = 2u;
    cost.bandwidth_upper_bound = 1u;
    cost.latency_class = DOM_LATENCY_MEDIUM;
    cost.degradation_priority = 1;

    if (dom_work_graph_builder_add_cost_model(graph_builder, &cost) != 0) {
        return -1;
    }
    if (!dom_access_set_builder_begin(access_builder, access_id, DOM_REDUCE_NONE, 0)) {
        return -2;
    }
    range.kind = DOM_RANGE_COMPONENT_SET;
    range.component_id = component_id;
    range.field_id = 0u;
    range.start_id = 0u;
    range.end_id = 0u;
    range.set_id = 0u;
    if (dom_access_set_builder_add_read(access_builder, &range) != 0) {
        return -3;
    }
    if (dom_access_set_builder_add_write(access_builder, &range) != 0) {
        return -4;
    }
    if (dom_access_set_builder_finalize(access_builder) != 0) {
        return -5;
    }
    if (dom_work_graph_builder_add_task(graph_builder, &node) != 0) {
        return -6;
    }
    return 0;
}

static dom_act_time_t dom_macro_min_due(dom_act_time_t a, dom_act_time_t b)
{
    if (a == DG_DUE_TICK_NONE) {
        return b;
    }
    if (b == DG_DUE_TICK_NONE) {
        return a;
    }
    return (a < b) ? a : b;
}

dom_act_time_t dom_macro_next_due(const dom_macro_due_hooks* hooks)
{
    dom_act_time_t next = DG_DUE_TICK_NONE;
    if (!hooks) {
        return DG_DUE_TICK_NONE;
    }
    if (hooks->consumption) {
        next = dom_macro_min_due(next, survival_consumption_next_due(hooks->consumption));
    }
    if (hooks->production) {
        next = dom_macro_min_due(next, survival_production_next_due(hooks->production));
    }
    if (hooks->population) {
        next = dom_macro_min_due(next, population_scheduler_next_due(hooks->population));
    }
    return next;
}

int dom_macro_process_until(dom_macro_due_hooks* hooks, dom_act_time_t target_tick)
{
    if (!hooks) {
        return -1;
    }
    if (hooks->consumption) {
        if (survival_consumption_advance(hooks->consumption, target_tick) != 0) {
            return -2;
        }
    }
    if (hooks->production) {
        if (survival_production_advance(hooks->production, target_tick) != 0) {
            return -3;
        }
    }
    if (hooks->population) {
        if (population_scheduler_advance(hooks->population, target_tick) != 0) {
            return -4;
        }
    }
    return 0;
}

int dom_macro_due_emit_tasks(const dom_macro_due_hooks* hooks,
                             dom_act_time_t act_now,
                             dom_act_time_t act_target,
                             dom_work_graph_builder* graph_builder,
                             dom_access_set_builder* access_builder,
                             u64 system_id,
                             dom_fidelity_tier fidelity_tier)
{
    dom_act_time_t due;
    u32 fidelity = dom_macro_task_fidelity(fidelity_tier);
    static u32 law_targets[1];
    static int law_targets_ready = 0;

    (void)act_now;

    if (!hooks || !graph_builder || !access_builder || system_id == 0u) {
        return -1;
    }
    if (!law_targets_ready) {
        law_targets[0] = dom_macro_fnv1a32("EXEC.AUTH_TASK");
        law_targets_ready = 1;
    }

    if (hooks->consumption) {
        due = survival_consumption_next_due(hooks->consumption);
        if (due != DG_DUE_TICK_NONE && due <= act_target) {
            if (dom_macro_emit_one(graph_builder, access_builder, system_id, 1u, due,
                                   1101u, law_targets, 1u, fidelity) != 0) {
                return -2;
            }
        }
    }
    if (hooks->production) {
        due = survival_production_next_due(hooks->production);
        if (due != DG_DUE_TICK_NONE && due <= act_target) {
            if (dom_macro_emit_one(graph_builder, access_builder, system_id, 2u, due,
                                   1102u, law_targets, 1u, fidelity) != 0) {
                return -3;
            }
        }
    }
    if (hooks->population) {
        due = population_scheduler_next_due(hooks->population);
        if (due != DG_DUE_TICK_NONE && due <= act_target) {
            if (dom_macro_emit_one(graph_builder, access_builder, system_id, 3u, due,
                                   1103u, law_targets, 1u, fidelity) != 0) {
                return -4;
            }
        }
    }
    return 0;
}
