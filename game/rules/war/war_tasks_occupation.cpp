/*
FILE: game/rules/war/war_tasks_occupation.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Game / war rules
RESPONSIBILITY: Implements occupation/resistance/disruption task helpers.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Occupation/resistance updates are deterministic.
*/
#include "dominium/rules/war/war_tasks_occupation.h"

static u32 dom_war_clamp_u32(i32 value)
{
    if (value < 0) {
        return 0u;
    }
    return (u32)value;
}

u32 dom_war_occupation_maintain_slice(dom_war_occupation_item* items,
                                      u32 item_count,
                                      u32 start_index,
                                      u32 max_count,
                                      dom_war_audit_log* audit,
                                      dom_act_time_t now_tick)
{
    u32 i;
    u32 end;
    if (!items || start_index >= item_count || max_count == 0u) {
        return 0u;
    }
    end = start_index + max_count;
    if (end > item_count) {
        end = item_count;
    }
    for (i = start_index; i < end; ++i) {
        dom_war_occupation_item* item = &items[i];
        if (item->status != DOM_WAR_OCCUPATION_ACTIVE) {
            continue;
        }
        if (item->supply_qty == 0u) {
            item->status = DOM_WAR_OCCUPATION_ENDED;
            item->next_due_tick = DOM_TIME_ACT_MAX;
        } else {
            item->control_level = dom_war_clamp_u32((i32)item->control_level + item->control_delta);
            item->next_due_tick = now_tick;
        }
        if (audit) {
            dom_war_audit_record(audit, DOM_WAR_AUDIT_OCCUPATION_MAINTAIN,
                                 item->occupation_id, (i64)item->control_level);
        }
    }
    return end - start_index;
}

u32 dom_war_resistance_update_slice(dom_war_resistance_item* items,
                                    u32 item_count,
                                    u32 start_index,
                                    u32 max_count,
                                    dom_war_audit_log* audit,
                                    dom_act_time_t now_tick)
{
    u32 i;
    u32 end;
    if (!items || start_index >= item_count || max_count == 0u) {
        return 0u;
    }
    end = start_index + max_count;
    if (end > item_count) {
        end = item_count;
    }
    for (i = start_index; i < end; ++i) {
        dom_war_resistance_item* item = &items[i];
        item->pressure = dom_war_clamp_u32((i32)item->pressure + item->pressure_delta);
        if (item->pressure >= 500u) {
            item->status = DOM_WAR_RESISTANCE_ACTIVE;
        } else if (item->pressure == 0u) {
            item->status = DOM_WAR_RESISTANCE_SUPPRESSED;
        } else {
            item->status = DOM_WAR_RESISTANCE_LATENT;
        }
        item->next_due_tick = now_tick;
        if (audit) {
            dom_war_audit_record(audit, DOM_WAR_AUDIT_RESISTANCE_UPDATE,
                                 item->resistance_id, (i64)item->pressure);
        }
    }
    return end - start_index;
}

u32 dom_war_disruption_apply_slice(dom_war_disruption_item* items,
                                   u32 item_count,
                                   u32 start_index,
                                   u32 max_count,
                                   dom_war_audit_log* audit,
                                   dom_act_time_t now_tick)
{
    u32 i;
    u32 end;
    if (!items || start_index >= item_count || max_count == 0u) {
        return 0u;
    }
    end = start_index + max_count;
    if (end > item_count) {
        end = item_count;
    }
    for (i = start_index; i < end; ++i) {
        dom_war_disruption_item* item = &items[i];
        if (item->status == DOM_WAR_DISRUPTION_APPLIED) {
            continue;
        }
        item->severity = dom_war_clamp_u32((i32)item->severity + item->severity_delta);
        item->status = DOM_WAR_DISRUPTION_APPLIED;
        item->next_due_tick = now_tick;
        if (audit) {
            dom_war_audit_record(audit, DOM_WAR_AUDIT_DISRUPTION_APPLY,
                                 item->disruption_id, (i64)item->severity);
        }
    }
    return end - start_index;
}
