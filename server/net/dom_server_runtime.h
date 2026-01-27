/*
FILE: server/net/dom_server_runtime.h
MODULE: Dominium
LAYER / SUBSYSTEM: Server / net
RESPONSIBILITY: Deterministic authoritative MMO-1 runtime surfaces.
DETERMINISM: All ordering, admission, and hashing are stable.
*/
#ifndef DOMINIUM_SERVER_NET_DOM_SERVER_RUNTIME_H
#define DOMINIUM_SERVER_NET_DOM_SERVER_RUNTIME_H

#include "domino/core/types.h"
#include "domino/core/dom_time_core.h"
#include "domino/sim/sim.h"

#include "dominium/rules/scale/scale_collapse_expand.h"

#include "server/net/dom_server_types.h"
#include "server/net/dom_server_protocol.h"
#include "server/persistence/dom_checkpoint_policy.h"
#include "server/persistence/dom_checkpointing.h"
#include "server/shard/dom_cross_shard_log.h"
#include "server/shard/dom_global_id.h"
#include "server/shard/dom_shard_lifecycle.h"
#include "server/shard/shard_api.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct dom_server_client_policy {
    u32 intents_per_tick;
    u32 bytes_per_tick;
    u32 inspect_only;
    u32 capability_mask;
} dom_server_client_policy;

typedef struct dom_server_runtime_config {
    dom_act_time_t start_tick;
    u32 shard_count;
    u32 worker_count;
    u64 worlddef_hash;
    u64 capability_lock_hash;
    dom_scale_budget_policy scale_budget_policy;
    dom_scale_macro_policy macro_policy;
    dom_checkpoint_policy checkpoint_policy;
    u32 shard_version_id;
    u64 shard_capability_mask;
    u64 shard_baseline_hash;
    dom_server_client_policy default_client_policy;
    u32 deferred_limit;
} dom_server_runtime_config;

typedef struct dom_server_client {
    u64 client_id;
    dom_shard_id shard_id;
    dom_server_client_policy policy;
    dom_server_budget_state budget_state;
    u64 idempotency_keys[DOM_SERVER_MAX_CLIENT_IDEMPOTENCY];
    u32 idempotency_count;
} dom_server_client;

typedef struct dom_server_deferred_intent {
    dom_server_intent intent;
    u32 refusal_code;
} dom_server_deferred_intent;

typedef struct dom_server_shard {
    dom_shard_id shard_id;
    d_world* world;
    dom_scale_context scale_ctx;
    dom_scale_domain_slot domain_storage[DOM_SERVER_MAX_DOMAINS_PER_SHARD];
    dom_interest_state interest_storage[DOM_SERVER_MAX_DOMAINS_PER_SHARD];
    dom_scale_event_log scale_event_log;
    dom_scale_event scale_events[256];
    dom_scale_macro_policy macro_policy;
    dom_global_id_gen id_gen;
    u32 lifecycle_state;
    u32 version_id;
    u64 capability_mask;
    u64 baseline_hash;

    dom_scale_resource_entry resource_entries[8];
    dom_scale_network_node network_nodes[8];
    dom_scale_network_edge network_edges[8];
    dom_scale_agent_entry agent_entries[16];
} dom_server_shard;

typedef struct dom_server_runtime {
    dom_server_runtime_config config;
    dom_act_time_t now_tick;
    dom_act_time_t next_checkpoint_tick;
    u64 macro_events_executed;
    u64 last_macro_stride;
    u32 checkpoints_taken;

    dom_server_shard shards[DOM_SERVER_MAX_SHARDS];
    u32 shard_count;

    dom_server_client clients[DOM_SERVER_MAX_CLIENTS];
    u32 client_count;

    dom_shard_lifecycle_log lifecycle_log;
    dom_shard_lifecycle_entry lifecycle_entries[256];

    dom_checkpoint_store checkpoint_store;
    dom_checkpoint_record checkpoint_records[DOM_CHECKPOINT_MAX_RECORDS];

    dom_server_intent intents[DOM_SERVER_MAX_INTENTS];
    u32 intent_count;
    u32 intent_overflow;

    dom_server_deferred_intent deferred[DOM_SERVER_MAX_DEFERRED];
    u32 deferred_count;
    u32 deferred_overflow;

    dom_server_domain_owner owners[DOM_SERVER_MAX_DOMAIN_OWNERS];
    u32 owner_count;

    dom_server_event events[DOM_SERVER_MAX_EVENTS];
    u32 event_count;
    u32 event_overflow;

    dom_cross_shard_log message_log;
    dom_cross_shard_message message_storage[DOM_SERVER_MAX_MESSAGES];
    dom_cross_shard_idempotency_entry message_idempotency[DOM_SERVER_MAX_IDEMPOTENCY];
    u64 message_sequence;
    u64 message_applied;
} dom_server_runtime;

void dom_server_runtime_config_default(dom_server_runtime_config* config);
int dom_server_runtime_init(dom_server_runtime* runtime,
                            const dom_server_runtime_config* config);

int dom_server_runtime_add_client(dom_server_runtime* runtime,
                                  u64 client_id,
                                  dom_shard_id shard_id,
                                  const dom_server_client_policy* policy);

int dom_server_runtime_submit_intent(dom_server_runtime* runtime,
                                     const dom_server_intent* intent,
                                     u32 payload_bytes);

int dom_server_runtime_tick(dom_server_runtime* runtime, dom_act_time_t tick);

int dom_server_runtime_join(dom_server_runtime* runtime,
                            u64 client_id,
                            dom_server_join_bundle* out_bundle);

int dom_server_runtime_resync(dom_server_runtime* runtime,
                              u64 client_id,
                              dom_shard_id shard_id,
                              u32 allow_partial,
                              dom_server_resync_bundle* out_bundle);

u64 dom_server_runtime_hash(const dom_server_runtime* runtime);

u32 dom_server_runtime_event_count(const dom_server_runtime* runtime);
int dom_server_runtime_event_get(const dom_server_runtime* runtime,
                                 u32 index,
                                 dom_server_event* out_event);

int dom_server_runtime_set_scale_budget(dom_server_runtime* runtime,
                                        dom_shard_id shard_id,
                                        const dom_scale_budget_policy* policy);

int dom_server_runtime_set_client_policy(dom_server_runtime* runtime,
                                         u64 client_id,
                                         const dom_server_client_policy* policy);

int dom_server_runtime_budget_snapshot(dom_server_runtime* runtime,
                                       u64 client_id,
                                       dom_server_budget_state* out_state);

int dom_server_runtime_scale_snapshot(dom_server_runtime* runtime,
                                      dom_shard_id shard_id,
                                      dom_scale_budget_snapshot* out_snapshot);

int dom_server_runtime_checkpoint(dom_server_runtime* runtime,
                                  u32 trigger_reason);
int dom_server_runtime_recover_last(dom_server_runtime* runtime,
                                    u32* out_refusal_code);
const dom_checkpoint_record* dom_server_runtime_last_checkpoint(const dom_server_runtime* runtime);
u64 dom_server_runtime_checkpoint_hash(const dom_server_runtime* runtime);

int dom_server_runtime_set_shard_state(dom_server_runtime* runtime,
                                       dom_shard_id shard_id,
                                       u32 to_state,
                                       u32 reason_code);
int dom_server_runtime_set_shard_version(dom_server_runtime* runtime,
                                         dom_shard_id shard_id,
                                         u32 version_id,
                                         u64 capability_mask,
                                         u64 baseline_hash);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_SERVER_NET_DOM_SERVER_RUNTIME_H */
