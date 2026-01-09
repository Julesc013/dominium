/*
FILE: source/dominium/game/runtime/dom_ai_planner_events.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / game/runtime/ai_planner_events
RESPONSIBILITY: Deterministic macro-event planner for AI factions.
*/
#include "runtime/dom_ai_planner_events.h"

#include "dominium/core_tlv.h"

namespace {

static const u64 DEFAULT_EVENT_LEAD_TICKS = 600ull;

struct SysCtx {
    dom_system_id id;
    int found;
};

static void collect_system_cb(const dom_system_info *info, void *user) {
    SysCtx *ctx_ptr = static_cast<SysCtx *>(user);
    if (!ctx_ptr || !info) {
        return;
    }
    if (!ctx_ptr->found || info->id < ctx_ptr->id) {
        ctx_ptr->id = info->id;
        ctx_ptr->found = 1;
    }
}

static int pick_target_system(const dom_faction_info *faction,
                              const dom_system_registry *systems,
                              dom_system_id *out_system) {
    SysCtx ctx;
    if (!faction || !out_system) {
        return 0;
    }
    *out_system = 0ull;
    if (faction->home_scope_kind == DOM_MACRO_SCOPE_SYSTEM) {
        *out_system = (dom_system_id)faction->home_scope_id;
        return *out_system != 0ull;
    }
    if (!systems) {
        return 0;
    }
    ctx.id = 0ull;
    ctx.found = 0;
    (void)dom_system_registry_iterate(systems, collect_system_cb, &ctx);
    if (!ctx.found) {
        return 0;
    }
    *out_system = ctx.id;
    return 1;
}

static int find_shortage_resource(const dom_macro_economy *economy,
                                  dom_system_id system_id,
                                  dom_resource_id *out_resource) {
    dom_macro_rate_entry list[64];
    u32 count = 0u;
    if (!economy || !out_resource) {
        return 0;
    }
    *out_resource = 0ull;
    if (dom_macro_economy_list_demand(economy,
                                      DOM_MACRO_SCOPE_SYSTEM,
                                      system_id,
                                      list,
                                      64u,
                                      &count) != DOM_MACRO_ECONOMY_OK) {
        return 0;
    }
    for (u32 i = 0u; i < count; ++i) {
        i64 prod = 0;
        i64 dem = 0;
        dom_resource_id resource_id = list[i].resource_id;
        if (dom_macro_economy_rate_get(economy,
                                       DOM_MACRO_SCOPE_SYSTEM,
                                       system_id,
                                       resource_id,
                                       &prod,
                                       &dem) != DOM_MACRO_ECONOMY_OK) {
            continue;
        }
        if (dem > prod) {
            *out_resource = resource_id;
            return 1;
        }
    }
    return 0;
}

struct EventScopeCtx {
    u32 scope_kind;
    u64 scope_id;
    int found;
};

static void find_scope_event_cb(const dom_macro_event_info *info, void *user) {
    EventScopeCtx *ctx = static_cast<EventScopeCtx *>(user);
    if (!ctx || !info) {
        return;
    }
    if (info->scope_kind == ctx->scope_kind && info->scope_id == ctx->scope_id) {
        ctx->found = 1;
    }
}

static u64 hash_fields(u64 a, u64 b, u64 c, u64 d) {
    unsigned char buf[32];
    dom::core_tlv::tlv_write_u64_le(&buf[0], a);
    dom::core_tlv::tlv_write_u64_le(&buf[8], b);
    dom::core_tlv::tlv_write_u64_le(&buf[16], c);
    dom::core_tlv::tlv_write_u64_le(&buf[24], d);
    return dom::core_tlv::tlv_fnv1a64(buf, sizeof(buf));
}

} // namespace

int dom_ai_planner_events_run(const dom_faction_info *faction,
                              const dom_macro_economy *economy,
                              const dom_macro_events *events,
                              const dom_system_registry *systems,
                              u64 tick,
                              u32 max_ops,
                              dom_ai_planner_events_result *out_result) {
    dom_system_id target_system = 0ull;
    dom_resource_id shortage = 0ull;

    if (!faction || !economy || !events || !systems || !out_result) {
        return DOM_AI_SCHEDULER_INVALID_ARGUMENT;
    }

    out_result->events.clear();
    out_result->ops_used = 0u;
    out_result->reason_code = DOM_AI_REASON_NONE;

    if (max_ops == 0u) {
        out_result->reason_code = DOM_AI_REASON_BUDGET_HIT;
        return DOM_AI_SCHEDULER_OK;
    }

    if (!(faction->policy_flags & DOM_FACTION_POLICY_ALLOW_EVENTS)) {
        return DOM_AI_SCHEDULER_OK;
    }
    if (!pick_target_system(faction, systems, &target_system)) {
        return DOM_AI_SCHEDULER_OK;
    }
    if (!find_shortage_resource(economy, target_system, &shortage)) {
        return DOM_AI_SCHEDULER_OK;
    }

    {
        EventScopeCtx ctx;
        ctx.scope_kind = DOM_MACRO_SCOPE_SYSTEM;
        ctx.scope_id = target_system;
        ctx.found = 0;
        (void)dom_macro_events_iterate(events, find_scope_event_cb, &ctx);
        if (ctx.found) {
            return DOM_AI_SCHEDULER_OK;
        }
    }

    {
        dom_ai_planned_event planned;
        planned.effects.clear();
        dom_macro_event_effect effect;
        effect.resource_id = shortage;
        effect.production_delta = 1;
        effect.demand_delta = 0;
        effect.flags_set = 0u;
        effect.flags_clear = 0u;
        planned.effects.push_back(effect);

        planned.desc.event_id = hash_fields(faction->faction_id,
                                            target_system,
                                            shortage,
                                            tick);
        planned.desc.scope_kind = DOM_MACRO_SCOPE_SYSTEM;
        planned.desc.scope_id = target_system;
        planned.desc.trigger_tick = tick + DEFAULT_EVENT_LEAD_TICKS;
        planned.desc.effect_count = (u32)planned.effects.size();
        planned.desc.effects = planned.effects.empty() ? 0 : &planned.effects[0];

        out_result->events.push_back(planned);
        out_result->ops_used = 1u;
        out_result->reason_code = DOM_AI_REASON_ACTIONS;
    }

    return DOM_AI_SCHEDULER_OK;
}
