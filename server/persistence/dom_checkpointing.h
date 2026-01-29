/*
FILE: server/persistence/dom_checkpointing.h
MODULE: Dominium
LAYER / SUBSYSTEM: Server / persistence
RESPONSIBILITY: Deterministic MMO checkpoint capture and recovery helpers.
*/
#ifndef DOMINIUM_SERVER_PERSISTENCE_DOM_CHECKPOINTING_H
#define DOMINIUM_SERVER_PERSISTENCE_DOM_CHECKPOINTING_H

#include "domino/core/types.h"
#include "domino/core/dom_time_core.h"
#include "domino/sim/sim.h"

#include "persistence/dom_checkpoint_policy.h"
#include "net/dom_server_protocol.h"
#include "net/dom_server_types.h"
#include "shard/dom_cross_shard_log.h"
#include "shard/dom_shard_lifecycle.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct dom_server_runtime dom_server_runtime;

typedef struct dom_checkpoint_manifest {
    u32 schema_version;
    u64 checkpoint_id;
    dom_act_time_t tick;
    u32 trigger_reason; /* dom_checkpoint_trigger_reason */
    u64 worlddef_hash;
    u64 capability_lock_hash;
    u64 runtime_hash;
    u64 lifecycle_hash;
    u64 message_sequence;
    u64 message_applied;
    u64 macro_events_executed;
    u32 event_count;
    u32 event_overflow;
    u32 shard_count;
} dom_checkpoint_manifest;

typedef struct dom_shard_checkpoint {
    dom_shard_id shard_id;
    dom_act_time_t tick;
    u32 lifecycle_state;
    u32 version_id;
    u64 capability_mask;
    u64 baseline_hash;
    u64 world_checksum;
    u32 domain_count;
    dom_scale_domain_slot domains[DOM_SERVER_MAX_DOMAINS_PER_SHARD];
    dom_scale_resource_entry resource_entries[8];
    dom_scale_network_node network_nodes[8];
    dom_scale_network_edge network_edges[8];
    dom_scale_agent_entry agent_entries[16];
    u64 domain_hashes[DOM_SERVER_MAX_DOMAINS_PER_SHARD];
    u64 capsule_ids[DOM_SERVER_MAX_DOMAINS_PER_SHARD];
    dom_scale_budget_state budget_state;
    dom_scale_budget_snapshot budget_snapshot;
    u64 scale_event_hash;
    u32 scale_event_count;
    u32 scale_event_overflow;
    dom_scale_event scale_events[256];
    u64 shard_hash;
} dom_shard_checkpoint;

typedef struct dom_checkpoint_deferred_intent {
    dom_server_intent intent;
    u32 refusal_code;
} dom_checkpoint_deferred_intent;

typedef struct dom_checkpoint_record {
    dom_checkpoint_manifest manifest;
    dom_shard_checkpoint shards[DOM_SERVER_MAX_SHARDS];

    u32 lifecycle_count;
    u32 lifecycle_overflow;
    dom_shard_lifecycle_entry lifecycle_entries[256];

    u32 intent_count;
    u32 intent_overflow;
    dom_server_intent intents[DOM_SERVER_MAX_INTENTS];

    u32 deferred_count;
    u32 deferred_overflow;
    dom_checkpoint_deferred_intent deferred[DOM_SERVER_MAX_DEFERRED];

    u32 event_count;
    u32 event_overflow;
    dom_server_event events[DOM_SERVER_MAX_EVENTS];

    u32 owner_count;
    dom_server_domain_owner owners[DOM_SERVER_MAX_DOMAIN_OWNERS];

    u32 message_count;
    dom_cross_shard_message messages[DOM_SERVER_MAX_MESSAGES];
    u32 idempotency_count;
    dom_cross_shard_idempotency_entry idempotency[DOM_SERVER_MAX_IDEMPOTENCY];

    d_world* world_clones[DOM_SERVER_MAX_SHARDS];
} dom_checkpoint_record;

typedef struct dom_checkpoint_store {
    dom_checkpoint_record* records;
    u32 capacity;
    u32 count;
    u32 head;
    u32 overflow;
} dom_checkpoint_store;

void dom_checkpoint_store_init(dom_checkpoint_store* store,
                               dom_checkpoint_record* storage,
                               u32 capacity);
const dom_checkpoint_record* dom_checkpoint_store_last(const dom_checkpoint_store* store);
int dom_checkpoint_store_record(dom_checkpoint_store* store,
                                dom_checkpoint_record* record);
u64 dom_checkpoint_store_hash(const dom_checkpoint_store* store);

int dom_checkpoint_capture(dom_checkpoint_record* out_record,
                           const dom_server_runtime* runtime,
                           u32 trigger_reason);

int dom_checkpoint_recover(dom_server_runtime* runtime,
                           const dom_checkpoint_record* record,
                           u32* out_refusal_code);

void dom_checkpoint_record_dispose(dom_checkpoint_record* record);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_SERVER_PERSISTENCE_DOM_CHECKPOINTING_H */
