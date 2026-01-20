/*
FILE: server/shard/shard_router.h
MODULE: Dominium
LAYER / SUBSYSTEM: Server / shard
RESPONSIBILITY: Deterministic routing for cross-shard messages.
ALLOWED DEPENDENCIES: engine public headers only.
FORBIDDEN DEPENDENCIES: game headers, OS/platform headers.
*/
#ifndef DOMINIUM_SERVER_SHARD_ROUTER_H
#define DOMINIUM_SERVER_SHARD_ROUTER_H

#include "shard_api.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct dom_shard_router {
    const dom_shard_registry* registry;
    dom_shard_message_queue queue;
} dom_shard_router;

void dom_shard_router_init(dom_shard_router* router,
                           const dom_shard_registry* registry,
                           dom_shard_message* storage,
                           u32 capacity);
int dom_shard_router_route(dom_shard_router* router,
                           const dom_shard_message* message);
int dom_shard_router_pop_ready(dom_shard_router* router,
                               dom_act_time_t now,
                               dom_shard_message* out_message);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_SERVER_SHARD_ROUTER_H */
