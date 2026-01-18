/*
FILE: include/dominium/rules/scale/interstellar_logistics.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / scale
RESPONSIBILITY: Defines interstellar logistics flows and scheduler.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C89/C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Flow ordering and arrival processing are deterministic.
*/
#ifndef DOMINIUM_RULES_SCALE_INTERSTELLAR_LOGISTICS_H
#define DOMINIUM_RULES_SCALE_INTERSTELLAR_LOGISTICS_H

#include "domino/core/dom_time_core.h"
#include "domino/sim/dg_due_sched.h"
#include "domino/core/types.h"
#include "dominium/rules/scale/scale_logistics_types.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct scale_interstellar_flow {
    u64 flow_id;
    u64 src_domain_id;
    u64 dst_domain_id;
    u64 asset_id;
    u64 qty;
    dom_act_time_t departure_act;
    dom_act_time_t arrival_act;
    u64 capacity_ref;
    u64 provenance_summary;
    dom_act_time_t next_due_tick;
    scale_flow_status status;
} scale_interstellar_flow;

typedef struct scale_interstellar_registry {
    scale_interstellar_flow* flows;
    u32 count;
    u32 capacity;
} scale_interstellar_registry;

void scale_interstellar_registry_init(scale_interstellar_registry* reg,
                                      scale_interstellar_flow* storage,
                                      u32 capacity);
int scale_interstellar_register(scale_interstellar_registry* reg,
                                u64 flow_id,
                                u64 src_domain_id,
                                u64 dst_domain_id,
                                u64 asset_id,
                                u64 qty,
                                dom_act_time_t departure_act,
                                dom_act_time_t arrival_act,
                                u64 capacity_ref,
                                u64 provenance_summary);
scale_interstellar_flow* scale_interstellar_find(scale_interstellar_registry* reg,
                                                 u64 flow_id);

u32 scale_interstellar_travel_time(u32 distance_units,
                                   u32 tech_level,
                                   u32 warp);
dom_act_time_t scale_interstellar_compute_arrival(dom_act_time_t departure_act,
                                                  u32 distance_units,
                                                  u32 tech_level,
                                                  u32 warp);

typedef struct scale_interstellar_hook {
    int (*on_arrival)(void* user, const scale_interstellar_flow* flow);
    void* user;
} scale_interstellar_hook;

typedef struct scale_interstellar_due_user {
    struct scale_interstellar_scheduler* scheduler;
    scale_interstellar_flow* flow;
} scale_interstellar_due_user;

typedef struct scale_interstellar_scheduler {
    dg_due_scheduler due;
    dom_time_event* due_events;
    dg_due_entry* due_entries;
    scale_interstellar_due_user* due_users;
    scale_interstellar_registry* registry;
    scale_interstellar_hook hook;
    u32 processed_last;
    u32 processed_total;
} scale_interstellar_scheduler;

int scale_interstellar_scheduler_init(scale_interstellar_scheduler* sched,
                                      dom_time_event* event_storage,
                                      u32 event_capacity,
                                      dg_due_entry* entry_storage,
                                      scale_interstellar_due_user* user_storage,
                                      u32 entry_capacity,
                                      dom_act_time_t start_tick,
                                      scale_interstellar_registry* registry);
void scale_interstellar_set_hook(scale_interstellar_scheduler* sched,
                                 const scale_interstellar_hook* hook);
int scale_interstellar_scheduler_register(scale_interstellar_scheduler* sched,
                                          scale_interstellar_flow* flow);
int scale_interstellar_scheduler_advance(scale_interstellar_scheduler* sched,
                                         dom_act_time_t target_tick);
dom_act_time_t scale_interstellar_scheduler_next_due(const scale_interstellar_scheduler* sched);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_RULES_SCALE_INTERSTELLAR_LOGISTICS_H */
