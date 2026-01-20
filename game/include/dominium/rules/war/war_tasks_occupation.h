/*
FILE: include/dominium/rules/war/war_tasks_occupation.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / war rules
RESPONSIBILITY: Work IR task helpers for occupation and resistance updates.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C89/C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Occupation/resistance updates are deterministic.
*/
#ifndef DOMINIUM_RULES_WAR_WAR_TASKS_OCCUPATION_H
#define DOMINIUM_RULES_WAR_WAR_TASKS_OCCUPATION_H

#include "dominium/rules/war/war_tasks_engagement.h"
#include "domino/core/dom_time_core.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef enum dom_war_occupation_status {
    DOM_WAR_OCCUPATION_ACTIVE = 0,
    DOM_WAR_OCCUPATION_ENDED = 1
} dom_war_occupation_status;

typedef enum dom_war_resistance_status {
    DOM_WAR_RESISTANCE_LATENT = 0,
    DOM_WAR_RESISTANCE_ACTIVE = 1,
    DOM_WAR_RESISTANCE_SUPPRESSED = 2
} dom_war_resistance_status;

typedef enum dom_war_disruption_status {
    DOM_WAR_DISRUPTION_PENDING = 0,
    DOM_WAR_DISRUPTION_APPLIED = 1
} dom_war_disruption_status;

typedef struct dom_war_occupation_item {
    u64 occupation_id;
    u64 territory_id;
    u32 control_level;
    i32 control_delta;
    u32 supply_qty;
    u32 status;
    dom_act_time_t next_due_tick;
    u64 provenance_ref;
} dom_war_occupation_item;

typedef struct dom_war_resistance_item {
    u64 resistance_id;
    u64 territory_id;
    u32 pressure;
    i32 pressure_delta;
    u32 status;
    dom_act_time_t next_due_tick;
    u64 provenance_ref;
} dom_war_resistance_item;

typedef struct dom_war_disruption_item {
    u64 disruption_id;
    u64 territory_id;
    u32 severity;
    i32 severity_delta;
    u32 status;
    dom_act_time_t next_due_tick;
    u64 provenance_ref;
} dom_war_disruption_item;

u32 dom_war_occupation_maintain_slice(dom_war_occupation_item* items,
                                      u32 item_count,
                                      u32 start_index,
                                      u32 max_count,
                                      dom_war_audit_log* audit,
                                      dom_act_time_t now_tick);

u32 dom_war_resistance_update_slice(dom_war_resistance_item* items,
                                    u32 item_count,
                                    u32 start_index,
                                    u32 max_count,
                                    dom_war_audit_log* audit,
                                    dom_act_time_t now_tick);

u32 dom_war_disruption_apply_slice(dom_war_disruption_item* items,
                                   u32 item_count,
                                   u32 start_index,
                                   u32 max_count,
                                   dom_war_audit_log* audit,
                                   dom_act_time_t now_tick);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_RULES_WAR_WAR_TASKS_OCCUPATION_H */
