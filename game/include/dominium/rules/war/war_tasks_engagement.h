/*
FILE: include/dominium/rules/war/war_tasks_engagement.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / war rules
RESPONSIBILITY: Work IR task helpers for war engagement pipelines.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C89/C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Engagement task ordering and outputs are deterministic.
*/
#ifndef DOMINIUM_RULES_WAR_WAR_TASKS_ENGAGEMENT_H
#define DOMINIUM_RULES_WAR_WAR_TASKS_ENGAGEMENT_H

#include "domino/core/types.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef enum dom_war_engagement_status {
    DOM_WAR_ENGAGEMENT_PENDING = 0,
    DOM_WAR_ENGAGEMENT_ADMITTED = 1,
    DOM_WAR_ENGAGEMENT_RESOLVED = 2,
    DOM_WAR_ENGAGEMENT_REFUSED = 3
} dom_war_engagement_status;

typedef struct dom_war_engagement_item {
    u64 engagement_id;
    u64 attacker_force_id;
    u64 defender_force_id;
    u32 objective;
    u32 supply_qty;
    u32 status;
    u64 provenance_ref;
} dom_war_engagement_item;

typedef struct dom_war_engagement_outcome {
    u64 outcome_id;
    u64 engagement_id;
    u64 winner_force_id;
    u64 loser_force_id;
    u32 casualty_count;
    u32 equipment_loss_count;
    i32 morale_delta;
    i32 readiness_delta;
    u64 provenance_ref;
} dom_war_engagement_outcome;

typedef struct dom_war_outcome_list {
    dom_war_engagement_outcome* outcomes;
    u32 count;
    u32 capacity;
    u64 next_id;
} dom_war_outcome_list;

typedef enum dom_war_audit_kind {
    DOM_WAR_AUDIT_ENGAGEMENT_ADMIT = 1,
    DOM_WAR_AUDIT_ENGAGEMENT_REFUSE = 2,
    DOM_WAR_AUDIT_ENGAGEMENT_RESOLVE = 3,
    DOM_WAR_AUDIT_CASUALTY_APPLY = 4,
    DOM_WAR_AUDIT_EQUIPMENT_APPLY = 5,
    DOM_WAR_AUDIT_MORALE_UPDATE = 6,
    DOM_WAR_AUDIT_OCCUPATION_MAINTAIN = 7,
    DOM_WAR_AUDIT_RESISTANCE_UPDATE = 8,
    DOM_WAR_AUDIT_DISRUPTION_APPLY = 9,
    DOM_WAR_AUDIT_ROUTE_CONTROL_UPDATE = 10,
    DOM_WAR_AUDIT_BLOCKADE_APPLY = 11,
    DOM_WAR_AUDIT_INTERDICTION_SCHEDULE = 12,
    DOM_WAR_AUDIT_INTERDICTION_RESOLVE = 13
} dom_war_audit_kind;

typedef struct dom_war_audit_entry {
    u64 event_id;
    u32 kind;
    u64 primary_id;
    i64 amount;
} dom_war_audit_entry;

typedef struct dom_war_audit_log {
    dom_war_audit_entry* entries;
    u32 count;
    u32 capacity;
    u64 next_event_id;
} dom_war_audit_log;

typedef struct dom_war_casualty_entry {
    u64 engagement_id;
    u32 casualty_count;
    u64 provenance_ref;
} dom_war_casualty_entry;

typedef struct dom_war_casualty_log {
    dom_war_casualty_entry* entries;
    u32 count;
    u32 capacity;
} dom_war_casualty_log;

typedef struct dom_war_equipment_loss_entry {
    u64 engagement_id;
    u32 equipment_loss_count;
    u64 provenance_ref;
} dom_war_equipment_loss_entry;

typedef struct dom_war_equipment_log {
    dom_war_equipment_loss_entry* entries;
    u32 count;
    u32 capacity;
} dom_war_equipment_log;

typedef struct dom_war_force_state {
    u64 force_id;
    i32 morale;
    i32 readiness;
} dom_war_force_state;

typedef struct dom_war_morale_state {
    dom_war_force_state* entries;
    u32 count;
    u32 capacity;
} dom_war_morale_state;

typedef struct dom_war_runtime_state {
    u32 engagement_cursor;
    u32 occupation_cursor;
    u32 resistance_cursor;
    u32 disruption_cursor;
    u32 route_cursor;
    u32 blockade_cursor;
    u32 interdiction_cursor;
} dom_war_runtime_state;

void dom_war_runtime_reset(dom_war_runtime_state* state);

void dom_war_audit_init(dom_war_audit_log* log,
                        dom_war_audit_entry* storage,
                        u32 capacity,
                        u64 start_id);
int dom_war_audit_record(dom_war_audit_log* log,
                         u32 kind,
                         u64 primary_id,
                         i64 amount);

void dom_war_outcome_list_init(dom_war_outcome_list* list,
                               dom_war_engagement_outcome* storage,
                               u32 capacity,
                               u64 start_id);
int dom_war_outcome_append(dom_war_outcome_list* list,
                           const dom_war_engagement_outcome* outcome,
                           u64* out_id);

void dom_war_casualty_log_init(dom_war_casualty_log* log,
                               dom_war_casualty_entry* storage,
                               u32 capacity);
int dom_war_casualty_record(dom_war_casualty_log* log,
                            u64 engagement_id,
                            u32 casualty_count,
                            u64 provenance_ref);

void dom_war_equipment_log_init(dom_war_equipment_log* log,
                                dom_war_equipment_loss_entry* storage,
                                u32 capacity);
int dom_war_equipment_record(dom_war_equipment_log* log,
                             u64 engagement_id,
                             u32 equipment_loss_count,
                             u64 provenance_ref);

void dom_war_morale_state_init(dom_war_morale_state* state,
                               dom_war_force_state* storage,
                               u32 capacity);
dom_war_force_state* dom_war_morale_find(dom_war_morale_state* state,
                                         u64 force_id);
dom_war_force_state* dom_war_morale_ensure(dom_war_morale_state* state,
                                           u64 force_id);

u32 dom_war_engagement_admit_slice(dom_war_engagement_item* items,
                                   u32 item_count,
                                   u32 start_index,
                                   u32 max_count,
                                   dom_war_audit_log* audit);

u32 dom_war_engagement_resolve_slice(dom_war_engagement_item* items,
                                     u32 item_count,
                                     u32 start_index,
                                     u32 max_count,
                                     dom_war_outcome_list* outcomes,
                                     dom_war_audit_log* audit);

u32 dom_war_apply_casualties_slice(const dom_war_outcome_list* outcomes,
                                   u32 start_index,
                                   u32 max_count,
                                   dom_war_casualty_log* log,
                                   dom_war_audit_log* audit);

u32 dom_war_apply_equipment_losses_slice(const dom_war_outcome_list* outcomes,
                                         u32 start_index,
                                         u32 max_count,
                                         dom_war_equipment_log* log,
                                         dom_war_audit_log* audit);

u32 dom_war_update_morale_readiness_slice(const dom_war_outcome_list* outcomes,
                                          u32 start_index,
                                          u32 max_count,
                                          dom_war_morale_state* morale,
                                          dom_war_audit_log* audit);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_RULES_WAR_WAR_TASKS_ENGAGEMENT_H */
