/*
FILE: server/shard/shard_api.h
MODULE: Dominium
LAYER / SUBSYSTEM: Server / shard
RESPONSIBILITY: Deterministic shard placement and messaging primitives.
ALLOWED DEPENDENCIES: engine public headers only.
FORBIDDEN DEPENDENCIES: game headers, OS/platform headers.
*/
#ifndef DOMINIUM_SERVER_SHARD_API_H
#define DOMINIUM_SERVER_SHARD_API_H

#include "domino/core/types.h"
#include "domino/core/dom_time_core.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef u32 dom_shard_id;

enum dom_shard_scope_kind {
    DOM_SHARD_SCOPE_ENTITY_RANGE = 1,
    DOM_SHARD_SCOPE_REGION_RANGE = 2,
    DOM_SHARD_SCOPE_SYSTEM_DOMAIN = 3
};

typedef struct dom_shard_ownership_scope {
    u32 kind;
    u64 start_id;
    u64 end_id;
    u32 domain_tag;
} dom_shard_ownership_scope;

typedef struct dom_shard {
    dom_shard_id shard_id;
    dom_shard_ownership_scope scope;
    u32 determinism_domain;
} dom_shard;

typedef struct dom_shard_registry {
    dom_shard* shards;
    u32 count;
    u32 capacity;
} dom_shard_registry;

void dom_shard_registry_init(dom_shard_registry* registry,
                             dom_shard* storage,
                             u32 capacity);
int dom_shard_registry_add(dom_shard_registry* registry,
                           const dom_shard* shard);
dom_shard_id dom_shard_find_owner(const dom_shard_registry* registry,
                                  u64 owner_id);

typedef struct dom_shard_task_key {
    u64 task_id;
    u64 system_id;
    u64 access_set_id;
    u32 category;
    u32 determinism_class;
    u64 primary_owner_id;
} dom_shard_task_key;

dom_shard_id dom_shard_place_task(const dom_shard_registry* registry,
                                  const dom_shard_task_key* key,
                                  dom_shard_id fallback_shard);

enum dom_shard_access_kind {
    DOM_SHARD_ACCESS_READ = 1,
    DOM_SHARD_ACCESS_WRITE = 2,
    DOM_SHARD_ACCESS_REDUCE = 3
};

int dom_shard_validate_access(const dom_shard_registry* registry,
                              dom_shard_id local_shard,
                              u64 owner_id,
                              u32 access_kind);

typedef struct dom_shard_message {
    dom_shard_id source_shard;
    dom_shard_id target_shard;
    u64 message_id;
    u64 task_id;
    dom_act_time_t arrival_tick;
    const u8* payload;
    u32 payload_size;
} dom_shard_message;

typedef struct dom_shard_message_queue {
    dom_shard_message* messages;
    u32 count;
    u32 capacity;
} dom_shard_message_queue;

void dom_shard_message_queue_init(dom_shard_message_queue* queue,
                                  dom_shard_message* storage,
                                  u32 capacity);
int dom_shard_message_queue_push(dom_shard_message_queue* queue,
                                 const dom_shard_message* message);
void dom_shard_message_queue_sort(dom_shard_message_queue* queue);
int dom_shard_message_queue_pop_ready(dom_shard_message_queue* queue,
                                      dom_act_time_t now,
                                      dom_shard_message* out_message);

typedef struct dom_shard_event_entry {
    u64 event_id;
    u64 task_id;
    dom_act_time_t tick;
} dom_shard_event_entry;

typedef struct dom_shard_log {
    dom_shard_event_entry* events;
    u32 event_count;
    u32 event_capacity;
    dom_shard_message* messages;
    u32 message_count;
    u32 message_capacity;
} dom_shard_log;

typedef struct dom_shard_replay_state {
    u64 hash;
    u32 event_count;
    u32 message_count;
} dom_shard_replay_state;

void dom_shard_log_init(dom_shard_log* log,
                        dom_shard_event_entry* event_storage,
                        u32 event_capacity,
                        dom_shard_message* message_storage,
                        u32 message_capacity);
int dom_shard_log_record_event(dom_shard_log* log,
                               const dom_shard_event_entry* entry);
int dom_shard_log_record_message(dom_shard_log* log,
                                 const dom_shard_message* message);
u64 dom_shard_log_hash(const dom_shard_log* log);
int dom_shard_replay_apply(const dom_shard_log* log,
                           dom_shard_replay_state* out_state);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_SERVER_SHARD_API_H */
