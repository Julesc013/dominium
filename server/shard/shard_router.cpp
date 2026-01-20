/*
FILE: server/shard/shard_router.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Server / shard
RESPONSIBILITY: Deterministic cross-shard routing implementation.
*/
#include "shard_router.h"

#ifdef __cplusplus
extern "C" {
#endif

static d_bool dom_shard_router_has_target(const dom_shard_registry* registry,
                                          dom_shard_id target)
{
    u32 i;
    if (!registry || !registry->shards) {
        return D_FALSE;
    }
    for (i = 0u; i < registry->count; ++i) {
        if (registry->shards[i].shard_id == target) {
            return D_TRUE;
        }
    }
    return D_FALSE;
}

void dom_shard_router_init(dom_shard_router* router,
                           const dom_shard_registry* registry,
                           dom_shard_message* storage,
                           u32 capacity)
{
    if (!router) {
        return;
    }
    router->registry = registry;
    dom_shard_message_queue_init(&router->queue, storage, capacity);
}

int dom_shard_router_route(dom_shard_router* router,
                           const dom_shard_message* message)
{
    if (!router || !message) {
        return -1;
    }
    if (!dom_shard_router_has_target(router->registry, message->target_shard)) {
        return -2;
    }
    return dom_shard_message_queue_push(&router->queue, message);
}

int dom_shard_router_pop_ready(dom_shard_router* router,
                               dom_act_time_t now,
                               dom_shard_message* out_message)
{
    if (!router) {
        return -1;
    }
    return dom_shard_message_queue_pop_ready(&router->queue, now, out_message);
}

#ifdef __cplusplus
} /* extern "C" */
#endif
