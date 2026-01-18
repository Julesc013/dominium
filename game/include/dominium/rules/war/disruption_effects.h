/*
FILE: include/dominium/rules/war/disruption_effects.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / war rules
RESPONSIBILITY: Defines deterministic disruption events and application hooks.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C89/C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Disruption application is deterministic and event-driven.
*/
#ifndef DOMINIUM_RULES_WAR_DISRUPTION_EFFECTS_H
#define DOMINIUM_RULES_WAR_DISRUPTION_EFFECTS_H

#include "domino/core/dom_time_core.h"
#include "domino/core/types.h"
#include "dominium/rules/governance/legitimacy_model.h"
#include "dominium/rules/infrastructure/store_model.h"
#include "dominium/rules/logistics/transport_capacity.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef enum disruption_effect_type {
    DISRUPTION_EFFECT_SABOTAGE = 0,
    DISRUPTION_EFFECT_STRIKE = 1,
    DISRUPTION_EFFECT_AMBUSH = 2
} disruption_effect_type;

typedef enum disruption_status {
    DISRUPTION_STATUS_SCHEDULED = 0,
    DISRUPTION_STATUS_APPLIED = 1
} disruption_status;

typedef struct disruption_event {
    u64 disruption_id;
    u64 territory_id;
    u32 effect_type;
    dom_act_time_t scheduled_act;
    u64 transport_capacity_id;
    u32 capacity_delta;
    u32 delay_ticks;
    u64 supply_store_ref;
    u64 supply_asset_id;
    u32 supply_qty;
    u64 legitimacy_id;
    i32 legitimacy_delta;
    u32 status;
    u64 provenance_ref;
} disruption_event;

typedef struct disruption_event_list {
    disruption_event* events;
    u32 count;
    u32 capacity;
    u64 next_id;
} disruption_event_list;

typedef struct disruption_effects_context {
    infra_store_registry* stores;
    transport_capacity_registry* transport;
    legitimacy_registry* legitimacy;
} disruption_effects_context;

void disruption_event_list_init(disruption_event_list* list,
                                disruption_event* storage,
                                u32 capacity,
                                u64 start_id);
disruption_event* disruption_event_find(disruption_event_list* list,
                                        u64 disruption_id);
int disruption_event_schedule(disruption_event_list* list,
                              const disruption_event* input,
                              u64* out_id);

int disruption_apply(disruption_event* event,
                     disruption_effects_context* ctx);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_RULES_WAR_DISRUPTION_EFFECTS_H */
