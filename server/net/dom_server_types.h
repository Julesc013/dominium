/*
FILE: server/net/dom_server_types.h
MODULE: Dominium
LAYER / SUBSYSTEM: Server / net
RESPONSIBILITY: Shared deterministic server sizing constants and small structs.
*/
#ifndef DOMINIUM_SERVER_NET_DOM_SERVER_TYPES_H
#define DOMINIUM_SERVER_NET_DOM_SERVER_TYPES_H

#include "domino/core/types.h"
#include "domino/core/dom_time_core.h"

#include "shard/shard_api.h"

#ifdef __cplusplus
extern "C" {
#endif

#define DOM_SERVER_MAX_SHARDS 4u
#define DOM_SERVER_MAX_CLIENTS 16u
#define DOM_SERVER_MAX_DOMAINS_PER_SHARD 3u
#define DOM_SERVER_MAX_EVENTS 4096u
#define DOM_SERVER_MAX_INTENTS 1024u
#define DOM_SERVER_MAX_DEFERRED 256u
#define DOM_SERVER_MAX_DOMAIN_OWNERS 64u
#define DOM_SERVER_MAX_MESSAGES 2048u
#define DOM_SERVER_MAX_IDEMPOTENCY 2048u
#define DOM_SERVER_MAX_CLIENT_IDEMPOTENCY 256u

typedef struct dom_server_domain_owner {
    u64 domain_id;
    dom_shard_id owner_shard_id;
} dom_server_domain_owner;

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_SERVER_NET_DOM_SERVER_TYPES_H */
