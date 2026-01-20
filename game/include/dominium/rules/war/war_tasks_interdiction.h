/*
FILE: include/dominium/rules/war/war_tasks_interdiction.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / war rules
RESPONSIBILITY: Work IR task helpers for interdiction and route control updates.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C89/C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Interdiction updates are deterministic.
*/
#ifndef DOMINIUM_RULES_WAR_WAR_TASKS_INTERDICTION_H
#define DOMINIUM_RULES_WAR_WAR_TASKS_INTERDICTION_H

#include "dominium/rules/war/war_tasks_engagement.h"
#include "domino/core/dom_time_core.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef enum dom_war_interdiction_status {
    DOM_WAR_INTERDICTION_PENDING = 0,
    DOM_WAR_INTERDICTION_SCHEDULED = 1,
    DOM_WAR_INTERDICTION_RESOLVED = 2,
    DOM_WAR_INTERDICTION_REFUSED = 3
} dom_war_interdiction_status;

typedef struct dom_war_route_control_item {
    u64 route_id;
    u32 control_level;
    i32 control_delta;
    u32 status;
    dom_act_time_t next_due_tick;
    u64 provenance_ref;
} dom_war_route_control_item;

typedef struct dom_war_blockade_item {
    u64 blockade_id;
    u64 route_id;
    u32 flow_limit;
    i32 flow_delta;
    u32 status;
    dom_act_time_t next_due_tick;
    u64 provenance_ref;
} dom_war_blockade_item;

typedef struct dom_war_interdiction_item {
    u64 interdiction_id;
    u64 route_id;
    u64 attacker_force_id;
    u64 defender_force_id;
    u32 status;
    dom_act_time_t schedule_act;
    dom_act_time_t next_due_tick;
    u64 provenance_ref;
} dom_war_interdiction_item;

u32 dom_war_route_control_update_slice(dom_war_route_control_item* items,
                                       u32 item_count,
                                       u32 start_index,
                                       u32 max_count,
                                       dom_war_audit_log* audit,
                                       dom_act_time_t now_tick);

u32 dom_war_blockade_apply_slice(dom_war_blockade_item* items,
                                 u32 item_count,
                                 u32 start_index,
                                 u32 max_count,
                                 dom_war_audit_log* audit,
                                 dom_act_time_t now_tick);

u32 dom_war_interdiction_schedule_slice(dom_war_interdiction_item* items,
                                        u32 item_count,
                                        u32 start_index,
                                        u32 max_count,
                                        dom_war_audit_log* audit,
                                        dom_act_time_t now_tick);

u32 dom_war_interdiction_resolve_slice(dom_war_interdiction_item* items,
                                       u32 item_count,
                                       u32 start_index,
                                       u32 max_count,
                                       dom_war_audit_log* audit,
                                       dom_act_time_t now_tick);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_RULES_WAR_WAR_TASKS_INTERDICTION_H */
