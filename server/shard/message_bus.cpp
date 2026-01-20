/*
FILE: server/shard/message_bus.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Server / shard
RESPONSIBILITY: Deterministic cross-shard message bus.
*/
#include "message_bus.h"

#ifdef __cplusplus
extern "C" {
#endif

void dom_shard_message_bus_init(dom_shard_message_bus* bus,
                                dom_shard_message* storage,
                                u32 capacity)
{
    if (!bus) {
        return;
    }
    dom_shard_message_queue_init(&bus->queue, storage, capacity);
}

int dom_shard_message_bus_enqueue(dom_shard_message_bus* bus,
                                  const dom_shard_message* message)
{
    if (!bus) {
        return -1;
    }
    return dom_shard_message_queue_push(&bus->queue, message);
}

int dom_shard_message_bus_pop_ready(dom_shard_message_bus* bus,
                                    dom_act_time_t now,
                                    dom_shard_message* out_message)
{
    if (!bus) {
        return -1;
    }
    return dom_shard_message_queue_pop_ready(&bus->queue, now, out_message);
}

u32 dom_shard_message_bus_count(const dom_shard_message_bus* bus)
{
    if (!bus) {
        return 0u;
    }
    return bus->queue.count;
}

#ifdef __cplusplus
} /* extern "C" */
#endif
