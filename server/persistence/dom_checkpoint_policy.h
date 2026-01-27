/*
FILE: server/persistence/dom_checkpoint_policy.h
MODULE: Dominium
LAYER / SUBSYSTEM: Server / persistence
RESPONSIBILITY: Checkpoint policy and trigger definitions shared across ops surfaces.
*/
#ifndef DOMINIUM_SERVER_PERSISTENCE_DOM_CHECKPOINT_POLICY_H
#define DOMINIUM_SERVER_PERSISTENCE_DOM_CHECKPOINT_POLICY_H

#include "domino/core/types.h"
#include "domino/core/dom_time_core.h"

#ifdef __cplusplus
extern "C" {
#endif

#define DOM_CHECKPOINT_SCHEMA_VERSION 1u
#define DOM_CHECKPOINT_MAX_RECORDS 32u

typedef enum dom_checkpoint_trigger_reason {
    DOM_CHECKPOINT_TRIGGER_POLICY_TICK = 1,
    DOM_CHECKPOINT_TRIGGER_POLICY_MACRO = 2,
    DOM_CHECKPOINT_TRIGGER_BEFORE_TRANSFER = 3,
    DOM_CHECKPOINT_TRIGGER_MANUAL = 4,
    DOM_CHECKPOINT_TRIGGER_RECOVERY = 5
} dom_checkpoint_trigger_reason;

typedef struct dom_checkpoint_policy {
    u32 interval_ticks;
    u32 macro_event_stride;
    u32 checkpoint_before_transfer;
    u32 max_records;
} dom_checkpoint_policy;

void dom_checkpoint_policy_default(dom_checkpoint_policy* policy);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_SERVER_PERSISTENCE_DOM_CHECKPOINT_POLICY_H */

