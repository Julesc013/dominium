/*
FILE: game/rules/war/war_tasks_interdiction.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Game / war rules
RESPONSIBILITY: Implements interdiction and route control task helpers.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Interdiction updates are deterministic.
*/
#include "dominium/rules/war/war_tasks_interdiction.h"

static u32 dom_war_clamp_u32(i32 value)
{
    if (value < 0) {
        return 0u;
    }
    return (u32)value;
}

u32 dom_war_route_control_update_slice(dom_war_route_control_item* items,
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
        dom_war_route_control_item* item = &items[i];
        item->control_level = dom_war_clamp_u32((i32)item->control_level + item->control_delta);
        item->next_due_tick = now_tick;
        if (audit) {
            dom_war_audit_record(audit, DOM_WAR_AUDIT_ROUTE_CONTROL_UPDATE,
                                 item->route_id, (i64)item->control_level);
        }
    }
    return end - start_index;
}

u32 dom_war_blockade_apply_slice(dom_war_blockade_item* items,
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
        dom_war_blockade_item* item = &items[i];
        item->flow_limit = dom_war_clamp_u32((i32)item->flow_limit + item->flow_delta);
        item->next_due_tick = now_tick;
        if (audit) {
            dom_war_audit_record(audit, DOM_WAR_AUDIT_BLOCKADE_APPLY,
                                 item->blockade_id, (i64)item->flow_limit);
        }
    }
    return end - start_index;
}

u32 dom_war_interdiction_schedule_slice(dom_war_interdiction_item* items,
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
        dom_war_interdiction_item* item = &items[i];
        if (item->status != DOM_WAR_INTERDICTION_PENDING) {
            continue;
        }
        if (item->attacker_force_id == 0u || item->defender_force_id == 0u) {
            item->status = DOM_WAR_INTERDICTION_REFUSED;
            item->next_due_tick = DOM_TIME_ACT_MAX;
            if (audit) {
                dom_war_audit_record(audit, DOM_WAR_AUDIT_INTERDICTION_SCHEDULE,
                                     item->interdiction_id, 0);
            }
            continue;
        }
        item->status = DOM_WAR_INTERDICTION_SCHEDULED;
        item->schedule_act = now_tick;
        item->next_due_tick = now_tick;
        if (audit) {
            dom_war_audit_record(audit, DOM_WAR_AUDIT_INTERDICTION_SCHEDULE,
                                 item->interdiction_id, 1);
        }
    }
    return end - start_index;
}

u32 dom_war_interdiction_resolve_slice(dom_war_interdiction_item* items,
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
        dom_war_interdiction_item* item = &items[i];
        if (item->status != DOM_WAR_INTERDICTION_SCHEDULED) {
            continue;
        }
        item->status = DOM_WAR_INTERDICTION_RESOLVED;
        item->next_due_tick = now_tick;
        if (audit) {
            dom_war_audit_record(audit, DOM_WAR_AUDIT_INTERDICTION_RESOLVE,
                                 item->interdiction_id, 0);
        }
    }
    return end - start_index;
}
