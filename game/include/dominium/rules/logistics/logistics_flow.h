/*
FILE: include/dominium/rules/logistics/logistics_flow.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / logistics
RESPONSIBILITY: Defines logistics flows and deterministic scheduling.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C89/C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Flow ordering and arrival processing are deterministic.
*/
#ifndef DOMINIUM_RULES_LOGISTICS_FLOW_H
#define DOMINIUM_RULES_LOGISTICS_FLOW_H

#include "domino/sim/dg_due_sched.h"
#include "dominium/rules/city/city_refusal_codes.h"
#include "dominium/rules/infrastructure/store_model.h"
#include "dominium/rules/logistics/transport_capacity.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef enum logistics_flow_status {
    LOG_FLOW_ACTIVE = 0,
    LOG_FLOW_ARRIVED = 1,
    LOG_FLOW_CANCELLED = 2
} logistics_flow_status;

typedef struct logistics_flow {
    u64 flow_id;
    u64 src_store_ref;
    u64 dst_store_ref;
    u64 asset_id;
    u32 qty;
    dom_act_time_t departure_act;
    dom_act_time_t arrival_act;
    u64 capacity_ref;
    u64 provenance_summary;
    logistics_flow_status status;
} logistics_flow;

typedef struct logistics_flow_registry {
    logistics_flow* flows;
    u32 count;
    u32 capacity;
    u64 next_flow_id;
} logistics_flow_registry;

typedef struct logistics_flow_input {
    u64 flow_id;
    u64 src_store_ref;
    u64 dst_store_ref;
    u64 asset_id;
    u32 qty;
    dom_act_time_t departure_act;
    dom_act_time_t arrival_act;
    u64 capacity_ref;
    u64 provenance_summary;
} logistics_flow_input;

void logistics_flow_registry_init(logistics_flow_registry* reg,
                                  logistics_flow* storage,
                                  u32 capacity,
                                  u64 start_flow_id);
logistics_flow* logistics_flow_find(logistics_flow_registry* reg, u64 flow_id);
int logistics_flow_schedule(logistics_flow_registry* reg,
                            const logistics_flow_input* input,
                            infra_store_registry* stores,
                            transport_capacity_registry* capacities,
                            civ1_refusal_code* out_refusal);
int logistics_flow_apply_arrival(logistics_flow* flow,
                                 infra_store_registry* stores,
                                 transport_capacity_registry* capacities);

typedef struct logistics_flow_scheduler logistics_flow_scheduler;

typedef struct logistics_flow_due_user {
    logistics_flow_scheduler* scheduler;
    logistics_flow* flow;
} logistics_flow_due_user;

typedef struct logistics_flow_scheduler {
    dg_due_scheduler due;
    dom_time_event* due_events;
    dg_due_entry* due_entries;
    logistics_flow_due_user* due_users;
    logistics_flow_registry* flows;
    infra_store_registry* stores;
    transport_capacity_registry* capacities;
    u32 processed_last;
    u32 processed_total;
} logistics_flow_scheduler;

int logistics_flow_scheduler_init(logistics_flow_scheduler* sched,
                                  dom_time_event* event_storage,
                                  u32 event_capacity,
                                  dg_due_entry* entry_storage,
                                  logistics_flow_due_user* user_storage,
                                  u32 entry_capacity,
                                  dom_act_time_t start_tick,
                                  logistics_flow_registry* flows,
                                  infra_store_registry* stores,
                                  transport_capacity_registry* capacities);
int logistics_flow_scheduler_register(logistics_flow_scheduler* sched,
                                      logistics_flow* flow);
int logistics_flow_scheduler_advance(logistics_flow_scheduler* sched,
                                     dom_act_time_t target_tick);
dom_act_time_t logistics_flow_scheduler_next_due(const logistics_flow_scheduler* sched);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_RULES_LOGISTICS_FLOW_H */
