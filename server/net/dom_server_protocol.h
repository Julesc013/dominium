/*
FILE: server/net/dom_server_protocol.h
MODULE: Dominium
LAYER / SUBSYSTEM: Server / net
RESPONSIBILITY: Deterministic authoritative protocol surfaces for MMO-1.
DETERMINISM: All enums and payload shapes are stable and replayable.
*/
#ifndef DOMINIUM_SERVER_NET_DOM_SERVER_PROTOCOL_H
#define DOMINIUM_SERVER_NET_DOM_SERVER_PROTOCOL_H

#include "domino/core/types.h"
#include "domino/core/dom_time_core.h"

#include "dominium/rules/scale/scale_collapse_expand.h"

#include "server/shard/shard_api.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef enum dom_server_intent_kind {
    DOM_SERVER_INTENT_OBSERVE = 1,
    DOM_SERVER_INTENT_COLLAPSE = 2,
    DOM_SERVER_INTENT_EXPAND = 3,
    DOM_SERVER_INTENT_MACRO_ADVANCE = 4,
    DOM_SERVER_INTENT_TRANSFER_OWNERSHIP = 5
} dom_server_intent_kind;

typedef enum dom_server_event_kind {
    DOM_SERVER_EVENT_INTENT_ACCEPT = 1,
    DOM_SERVER_EVENT_INTENT_REFUSE = 2,
    DOM_SERVER_EVENT_INTENT_DEFER = 3,
    DOM_SERVER_EVENT_COLLAPSE = 4,
    DOM_SERVER_EVENT_EXPAND = 5,
    DOM_SERVER_EVENT_OWNERSHIP_TRANSFER = 6,
    DOM_SERVER_EVENT_MESSAGE_APPLY = 7,
    DOM_SERVER_EVENT_JOIN = 8,
    DOM_SERVER_EVENT_RESYNC = 9,
    DOM_SERVER_EVENT_BUDGET_SNAPSHOT = 10
} dom_server_event_kind;

typedef enum dom_server_refusal_code {
    DOM_SERVER_REFUSE_NONE = 0,
    DOM_SERVER_REFUSE_INVALID_INTENT = 1,
    DOM_SERVER_REFUSE_LAW_FORBIDDEN = 2,
    DOM_SERVER_REFUSE_CAPABILITY_MISSING = 3,
    DOM_SERVER_REFUSE_DOMAIN_FORBIDDEN = 4,
    DOM_SERVER_REFUSE_INTEGRITY_VIOLATION = 5,
    DOM_SERVER_REFUSE_RATE_LIMIT = 6,
    DOM_SERVER_REFUSE_BUDGET_EXCEEDED = 7,
    DOM_SERVER_REFUSE_ACTIVE_DOMAIN_LIMIT = 701,
    DOM_SERVER_REFUSE_REFINEMENT_BUDGET = 702,
    DOM_SERVER_REFUSE_MACRO_EVENT_BUDGET = 703,
    DOM_SERVER_REFUSE_AGENT_PLANNING_BUDGET = 704,
    DOM_SERVER_REFUSE_SNAPSHOT_BUDGET = 705,
    DOM_SERVER_REFUSE_COLLAPSE_BUDGET = 706,
    DOM_SERVER_REFUSE_DEFER_QUEUE_LIMIT = 707
} dom_server_refusal_code;

typedef struct dom_server_budget_state {
    dom_act_time_t tick;
    u32 intents_limit;
    u32 intents_used;
    u32 bytes_limit;
    u32 bytes_used;
} dom_server_budget_state;

typedef struct dom_server_intent {
    u64 intent_id;
    u64 client_id;
    dom_shard_id target_shard_id;
    u64 domain_id;
    u64 capsule_id;
    dom_act_time_t intent_tick;
    dom_act_time_t client_tick_ref;
    u64 idempotency_key;
    u32 intent_kind; /* dom_server_intent_kind */
    u32 intent_cost_units;
    u32 detail_code;
    u32 payload_u32;
    u32 payload_bytes;
} dom_server_intent;

typedef struct dom_server_snapshot_fragment {
    dom_shard_id shard_id;
    u64 domain_id;
    u32 domain_kind;
    dom_act_time_t tick;
    dom_fidelity_tier tier;
    u64 domain_hash;
    u64 capsule_id;
} dom_server_snapshot_fragment;

typedef struct dom_server_join_bundle {
    u64 client_id;
    dom_shard_id assigned_shard_id;
    dom_act_time_t tick;
    u64 world_hash;
    u64 capability_hash;
    dom_server_snapshot_fragment snapshot;
    u32 inspect_only;
    u32 event_tail_index;
    u32 message_tail_index;
} dom_server_join_bundle;

typedef struct dom_server_resync_bundle {
    u64 client_id;
    dom_shard_id shard_id;
    dom_act_time_t tick;
    u64 world_hash;
    dom_server_snapshot_fragment snapshot;
    u32 event_tail_index;
    u32 message_tail_index;
    u32 refusal_code;
} dom_server_resync_bundle;

typedef struct dom_server_event {
    u64 event_id;
    dom_act_time_t tick;
    dom_shard_id shard_id;
    u64 client_id;
    u64 domain_id;
    u64 capsule_id;
    u64 causal_id;
    u32 event_kind; /* dom_server_event_kind */
    u32 intent_kind; /* dom_server_intent_kind */
    u32 refusal_code; /* dom_server_refusal_code */
    u32 defer_code; /* dom_scale_defer_code */
    u32 budget_kind; /* dom_scale_budget_kind */
    u32 budget_limit;
    u32 budget_used;
    u32 budget_cost;
    u32 detail_code;
    u32 payload_u32;
    dom_server_budget_state client_budget;
    dom_scale_budget_snapshot scale_budget;
} dom_server_event;

const char* dom_server_refusal_to_string(u32 refusal_code);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_SERVER_NET_DOM_SERVER_PROTOCOL_H */
