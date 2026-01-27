/*
FILE: server/shard/dom_cross_shard_log.h
MODULE: Dominium
LAYER / SUBSYSTEM: Server / shard
RESPONSIBILITY: Deterministic cross-shard message log helpers.
ALLOWED DEPENDENCIES: engine public headers only.
FORBIDDEN DEPENDENCIES: game headers, OS/platform headers.
*/
#ifndef DOMINIUM_SERVER_SHARD_DOM_CROSS_SHARD_LOG_H
#define DOMINIUM_SERVER_SHARD_DOM_CROSS_SHARD_LOG_H

#include "domino/core/types.h"
#include "domino/core/dom_time_core.h"

#include "shard_api.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct dom_cross_shard_message {
    u64 message_id;
    u64 idempotency_key;
    dom_shard_id origin_shard_id;
    dom_shard_id dest_shard_id;
    u64 domain_id;
    dom_act_time_t origin_tick;
    dom_act_time_t delivery_tick;
    u64 causal_key;
    u64 order_key;
    u32 message_kind;
    u32 sequence;
    u64 payload_hash;
} dom_cross_shard_message;

typedef struct dom_cross_shard_idempotency_entry {
    dom_shard_id dest_shard_id;
    u64 idempotency_key;
} dom_cross_shard_idempotency_entry;

typedef struct dom_cross_shard_log {
    dom_cross_shard_message* messages;
    u32 message_count;
    u32 message_capacity;
    u32 message_overflow;

    dom_cross_shard_idempotency_entry* idempotency_entries;
    u32 idempotency_count;
    u32 idempotency_capacity;
} dom_cross_shard_log;

void dom_cross_shard_log_init(dom_cross_shard_log* log,
                              dom_cross_shard_message* message_storage,
                              u32 message_capacity,
                              dom_cross_shard_idempotency_entry* idempotency_storage,
                              u32 idempotency_capacity);
void dom_cross_shard_log_clear(dom_cross_shard_log* log);

int dom_cross_shard_log_append(dom_cross_shard_log* log,
                               const dom_cross_shard_message* message);
int dom_cross_shard_log_pop_next_ready(dom_cross_shard_log* log,
                                       dom_act_time_t up_to_tick,
                                       dom_cross_shard_message* out_message,
                                       u32* out_skipped_idempotent);

u64 dom_cross_shard_log_hash(const dom_cross_shard_log* log);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_SERVER_SHARD_DOM_CROSS_SHARD_LOG_H */

