/*
FILE: source/dominium/game/runtime/dom_transfer_scheduler.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / game/runtime/transfer_scheduler
RESPONSIBILITY: Deterministic transfer scheduling and arrival updates.
ALLOWED DEPENDENCIES: `include/domino/**`, `source/dominium/**`, C++98 STL.
FORBIDDEN DEPENDENCIES: OS headers; non-deterministic inputs.
*/
#ifndef DOM_TRANSFER_SCHEDULER_H
#define DOM_TRANSFER_SCHEDULER_H

#include "domino/core/types.h"
#include "runtime/dom_route_graph.h"
#include "runtime/dom_station_registry.h"

#ifdef __cplusplus
extern "C" {
#endif

enum {
    DOM_TRANSFER_OK = 0,
    DOM_TRANSFER_ERR = -1,
    DOM_TRANSFER_INVALID_ARGUMENT = -2,
    DOM_TRANSFER_NOT_FOUND = -3,
    DOM_TRANSFER_INVALID_DATA = -4,
    DOM_TRANSFER_CAPACITY_EXCEEDED = -5,
    DOM_TRANSFER_INSUFFICIENT = -6,
    DOM_TRANSFER_OVERFLOW = -7
};

typedef u64 dom_transfer_id;

typedef struct dom_transfer_entry {
    dom_resource_id resource_id;
    i64 quantity;
} dom_transfer_entry;

typedef struct dom_transfer_info {
    dom_transfer_id transfer_id;
    dom_route_id route_id;
    u64 start_tick;
    u64 arrival_tick;
    u32 entry_count;
    u64 total_units;
} dom_transfer_info;

typedef struct dom_transfer_scheduler dom_transfer_scheduler;

dom_transfer_scheduler *dom_transfer_scheduler_create(void);
void dom_transfer_scheduler_destroy(dom_transfer_scheduler *sched);
int dom_transfer_scheduler_init(dom_transfer_scheduler *sched);

int dom_transfer_schedule(dom_transfer_scheduler *sched,
                          const dom_route_graph *routes,
                          dom_station_registry *stations,
                          dom_route_id route_id,
                          const dom_transfer_entry *entries,
                          u32 entry_count,
                          u64 current_tick,
                          dom_transfer_id *out_id);
int dom_transfer_add_loaded(dom_transfer_scheduler *sched,
                            const dom_route_graph *routes,
                            dom_route_id route_id,
                            dom_transfer_id transfer_id,
                            u64 start_tick,
                            u64 arrival_tick,
                            const dom_transfer_entry *entries,
                            u32 entry_count,
                            u64 total_units);
int dom_transfer_update(dom_transfer_scheduler *sched,
                        const dom_route_graph *routes,
                        dom_station_registry *stations,
                        u64 current_tick);

int dom_transfer_list(const dom_transfer_scheduler *sched,
                      dom_transfer_info *out_list,
                      u32 max_entries,
                      u32 *out_count);
int dom_transfer_get_entries(const dom_transfer_scheduler *sched,
                             dom_transfer_id transfer_id,
                             dom_transfer_entry *out_entries,
                             u32 max_entries,
                             u32 *out_count);
u32 dom_transfer_count(const dom_transfer_scheduler *sched);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOM_TRANSFER_SCHEDULER_H */
