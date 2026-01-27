/*
FILE: server/shard/dom_shard_lifecycle.h
MODULE: Dominium
LAYER / SUBSYSTEM: Server / shard
RESPONSIBILITY: Deterministic shard lifecycle state machine and logging.
*/
#ifndef DOMINIUM_SERVER_SHARD_DOM_SHARD_LIFECYCLE_H
#define DOMINIUM_SERVER_SHARD_DOM_SHARD_LIFECYCLE_H

#include "domino/core/types.h"
#include "domino/core/dom_time_core.h"

#include "shard_api.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef enum dom_shard_lifecycle_state {
    DOM_SHARD_LIFECYCLE_INITIALIZING = 1,
    DOM_SHARD_LIFECYCLE_ACTIVE = 2,
    DOM_SHARD_LIFECYCLE_DRAINING = 3,
    DOM_SHARD_LIFECYCLE_FROZEN = 4,
    DOM_SHARD_LIFECYCLE_OFFLINE = 5
} dom_shard_lifecycle_state;

typedef struct dom_shard_lifecycle_entry {
    dom_shard_id shard_id;
    dom_act_time_t tick;
    u32 from_state; /* dom_shard_lifecycle_state */
    u32 to_state;   /* dom_shard_lifecycle_state */
    u32 reason_code;
} dom_shard_lifecycle_entry;

typedef struct dom_shard_lifecycle_log {
    dom_shard_lifecycle_entry* entries;
    u32 count;
    u32 capacity;
    u32 overflow;
} dom_shard_lifecycle_log;

void dom_shard_lifecycle_log_init(dom_shard_lifecycle_log* log,
                                  dom_shard_lifecycle_entry* storage,
                                  u32 capacity);
void dom_shard_lifecycle_log_clear(dom_shard_lifecycle_log* log);

int dom_shard_lifecycle_transition_allowed(u32 from_state, u32 to_state);
int dom_shard_lifecycle_log_transition(dom_shard_lifecycle_log* log,
                                       dom_shard_id shard_id,
                                       dom_act_time_t tick,
                                       u32 from_state,
                                       u32 to_state,
                                       u32 reason_code);

const char* dom_shard_lifecycle_state_name(u32 state);
u64 dom_shard_lifecycle_log_hash(const dom_shard_lifecycle_log* log);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_SERVER_SHARD_DOM_SHARD_LIFECYCLE_H */

