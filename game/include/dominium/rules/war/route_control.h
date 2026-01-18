/*
FILE: include/dominium/rules/war/route_control.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / war rules
RESPONSIBILITY: Defines deterministic route control records and shard message ordering.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C89/C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Route control ordering and message queues are deterministic.
*/
#ifndef DOMINIUM_RULES_WAR_ROUTE_CONTROL_H
#define DOMINIUM_RULES_WAR_ROUTE_CONTROL_H

#include "domino/core/dom_time_core.h"
#include "domino/core/types.h"
#include "dominium/epistemic.h"

#ifdef __cplusplus
extern "C" {
#endif

#define ROUTE_CONTROL_SCALE 1000u

typedef enum route_access_policy {
    ROUTE_ACCESS_ALLOW = 0,
    ROUTE_ACCESS_DENY = 1,
    ROUTE_ACCESS_THROTTLE = 2,
    ROUTE_ACCESS_INSPECT = 3
} route_access_policy;

typedef struct route_control {
    u64 route_id;
    u64 controlling_force_ref;
    u32 control_strength;
    u32 access_policy;
    dom_act_time_t next_due_tick;
} route_control;

typedef struct route_control_registry {
    route_control* controls;
    u32 count;
    u32 capacity;
} route_control_registry;

typedef struct route_control_estimate {
    u64 controller_id;
    u32 control_strength;
    u32 access_policy;
    u32 uncertainty_q16;
    int is_exact;
} route_control_estimate;

void route_control_registry_init(route_control_registry* reg,
                                 route_control* storage,
                                 u32 capacity);
route_control* route_control_find(route_control_registry* reg,
                                  u64 route_id);
int route_control_register(route_control_registry* reg,
                           u64 route_id,
                           u64 controller_id,
                           u32 control_strength,
                           u32 access_policy);
int route_control_apply_delta(route_control_registry* reg,
                              u64 route_id,
                              i32 delta);
int route_control_set_policy(route_control_registry* reg,
                             u64 route_id,
                             u32 access_policy);

int route_control_estimate_from_view(const dom_epistemic_view* view,
                                     const route_control* actual,
                                     route_control_estimate* out);

typedef struct route_control_message {
    u64 message_id;
    u64 route_id;
    u64 controller_id;
    u32 control_strength;
    u32 access_policy;
    dom_act_time_t arrival_act;
    u64 order_key;
    u64 provenance_ref;
} route_control_message;

typedef struct route_control_message_queue {
    route_control_message* messages;
    u32 count;
    u32 capacity;
    u64 next_id;
} route_control_message_queue;

void route_control_message_queue_init(route_control_message_queue* queue,
                                      route_control_message* storage,
                                      u32 capacity,
                                      u64 start_id);
int route_control_message_queue_push(route_control_message_queue* queue,
                                     const route_control_message* input,
                                     u64* out_id);
const route_control_message* route_control_message_at(const route_control_message_queue* queue,
                                                      u32 index);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_RULES_WAR_ROUTE_CONTROL_H */
