/*
FILE: server/shard/message_bus.h
MODULE: Dominium
LAYER / SUBSYSTEM: Server / shard
RESPONSIBILITY: Deterministic cross-shard message bus.
ALLOWED DEPENDENCIES: engine public headers only.
FORBIDDEN DEPENDENCIES: game headers, OS/platform headers.
*/
#ifndef DOMINIUM_SERVER_SHARD_MESSAGE_BUS_H
#define DOMINIUM_SERVER_SHARD_MESSAGE_BUS_H

#include "shard_api.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct dom_shard_message_bus {
    dom_shard_message_queue queue;
} dom_shard_message_bus;

void dom_shard_message_bus_init(dom_shard_message_bus* bus,
                                dom_shard_message* storage,
                                u32 capacity);
int dom_shard_message_bus_enqueue(dom_shard_message_bus* bus,
                                  const dom_shard_message* message);
int dom_shard_message_bus_pop_ready(dom_shard_message_bus* bus,
                                    dom_act_time_t now,
                                    dom_shard_message* out_message);
u32 dom_shard_message_bus_count(const dom_shard_message_bus* bus);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_SERVER_SHARD_MESSAGE_BUS_H */
