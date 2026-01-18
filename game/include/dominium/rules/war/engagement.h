/*
FILE: include/dominium/rules/war/engagement.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / war rules
RESPONSIBILITY: Defines engagement records, outcomes, and registries.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C89/C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Engagement ordering and outcomes are deterministic.
*/
#ifndef DOMINIUM_RULES_WAR_ENGAGEMENT_H
#define DOMINIUM_RULES_WAR_ENGAGEMENT_H

#include "domino/core/dom_time_core.h"
#include "domino/core/types.h"

#ifdef __cplusplus
extern "C" {
#endif

#define ENGAGEMENT_MAX_PARTICIPANTS 8u
#define ENGAGEMENT_MAX_ENV_MODIFIERS 8u
#define ENGAGEMENT_MAX_CASUALTIES 64u
#define ENGAGEMENT_MAX_EQUIPMENT_LOSSES 16u

typedef enum engagement_objective {
    ENGAGEMENT_OBJECTIVE_ATTACK = 0,
    ENGAGEMENT_OBJECTIVE_DEFEND = 1,
    ENGAGEMENT_OBJECTIVE_RAID = 2,
    ENGAGEMENT_OBJECTIVE_BLOCKADE = 3
} engagement_objective;

typedef enum engagement_role {
    ENGAGEMENT_ROLE_ATTACKER = 0,
    ENGAGEMENT_ROLE_DEFENDER = 1
} engagement_role;

typedef enum engagement_status {
    ENGAGEMENT_STATUS_SCHEDULED = 0,
    ENGAGEMENT_STATUS_RESOLVED = 1
} engagement_status;

typedef enum engagement_refusal_code {
    ENGAGEMENT_REFUSAL_NONE = 0,
    ENGAGEMENT_REFUSAL_ALREADY_RESOLVED = 1,
    ENGAGEMENT_REFUSAL_PARTICIPANT_NOT_READY = 2,
    ENGAGEMENT_REFUSAL_INSUFFICIENT_SUPPLY = 3,
    ENGAGEMENT_REFUSAL_OBJECTIVE_INVALID = 4,
    ENGAGEMENT_REFUSAL_OUT_OF_DOMAIN = 5
} engagement_refusal_code;

const char* engagement_refusal_to_string(engagement_refusal_code code);

typedef struct engagement_participant {
    u64 force_id;
    u64 legitimacy_id;
    u32 role;
    u64 supply_store_ref;
} engagement_participant;

typedef struct engagement {
    u64 engagement_id;
    u32 domain_scope;
    engagement_participant participants[ENGAGEMENT_MAX_PARTICIPANTS];
    u32 participant_count;
    dom_act_time_t start_act;
    dom_act_time_t resolution_act;
    u32 objective;
    u64 environment_modifiers[ENGAGEMENT_MAX_ENV_MODIFIERS];
    u32 environment_modifier_count;
    dom_act_time_t next_due_tick;
    u64 provenance_ref;
    u64 supply_asset_id;
    u32 supply_qty;
    u32 status;
} engagement;

typedef struct engagement_registry {
    engagement* engagements;
    u32 count;
    u32 capacity;
    u64 next_id;
} engagement_registry;

void engagement_registry_init(engagement_registry* reg,
                              engagement* storage,
                              u32 capacity,
                              u64 start_id);
engagement* engagement_find(engagement_registry* reg,
                            u64 engagement_id);
int engagement_register(engagement_registry* reg,
                        const engagement* input,
                        u64* out_id);

typedef struct engagement_equipment_loss {
    u64 equipment_id;
    u32 qty;
} engagement_equipment_loss;

typedef struct engagement_outcome {
    u64 outcome_id;
    u64 engagement_id;
    u64 winner_force_id;
    u64 loser_force_id;
    u64 casualty_event_ids[ENGAGEMENT_MAX_CASUALTIES];
    u32 casualty_count;
    engagement_equipment_loss equipment_losses[ENGAGEMENT_MAX_EQUIPMENT_LOSSES];
    u32 equipment_loss_count;
    i32 morale_delta;
    i32 legitimacy_delta;
    u32 logistics_consumed;
    u64 provenance_summary;
} engagement_outcome;

typedef struct engagement_outcome_list {
    engagement_outcome* outcomes;
    u32 count;
    u32 capacity;
    u64 next_id;
} engagement_outcome_list;

void engagement_outcome_list_init(engagement_outcome_list* list,
                                  engagement_outcome* storage,
                                  u32 capacity,
                                  u64 start_id);
int engagement_outcome_append(engagement_outcome_list* list,
                              const engagement_outcome* outcome,
                              u64* out_id);
const engagement_outcome* engagement_outcome_find(const engagement_outcome_list* list,
                                                  u64 outcome_id);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_RULES_WAR_ENGAGEMENT_H */
