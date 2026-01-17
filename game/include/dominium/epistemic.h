/*
FILE: include/dominium/epistemic.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / epistemic
RESPONSIBILITY: Defines the Epistemic Interface Layer (EIL) snapshot contract.
ALLOWED DEPENDENCIES: `game/include/**`, `engine/include/**` public headers, and C89 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; product-layer runtime code.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Snapshot ordering and queries are deterministic.
*/
#ifndef DOMINIUM_EPISTEMIC_H
#define DOMINIUM_EPISTEMIC_H

#include "domino/core/types.h"
#include "domino/core/dom_time_core.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef enum dom_epistemic_state {
    DOM_EPI_UNKNOWN = 0,
    DOM_EPI_KNOWN = 1
} dom_epistemic_state;

typedef enum dom_capability_kind {
    DOM_CAP_TIME_READOUT = 1,
    DOM_CAP_CALENDAR_VIEW = 2,
    DOM_CAP_MAP_VIEW = 3,
    DOM_CAP_POSITION_ESTIMATE = 4,
    DOM_CAP_HEALTH_STATUS = 5,
    DOM_CAP_INVENTORY_SUMMARY = 6,
    DOM_CAP_ECONOMIC_ACCOUNT = 7,
    DOM_CAP_MARKET_QUOTES = 8,
    DOM_CAP_COMMUNICATIONS = 9,
    DOM_CAP_COMMAND_STATUS = 10,
    DOM_CAP_ENVIRONMENTAL_STATUS = 11,
    DOM_CAP_LEGAL_STATUS = 12
} dom_capability_kind;

typedef struct dom_capability_entry {
    u32               capability_id;
    u32               subject_kind;
    u64               subject_id;
    dom_epistemic_state state;
    u32               uncertainty_q16;
    u32               latency_ticks;
    dom_act_time_t    observed_tick;
    dom_act_time_t    expires_tick;
    u32               source_mask;
} dom_capability_entry;

typedef struct dom_capability_snapshot {
    dom_capability_entry* entries;
    u32                   count;
    u32                   capacity;
    dom_act_time_t         snapshot_tick;
} dom_capability_snapshot;

typedef struct dom_epistemic_view {
    dom_epistemic_state state;
    u32               uncertainty_q16;
    dom_act_time_t    observed_tick;
    u32               latency_ticks;
    int               is_stale;
    int               is_uncertain;
} dom_epistemic_view;

#define DOM_EPISTEMIC_EXPIRES_NEVER DOM_TIME_ACT_MAX

void dom_capability_snapshot_init(dom_capability_snapshot* snap,
                                  dom_capability_entry* storage,
                                  u32 capacity);

void dom_capability_snapshot_clear(dom_capability_snapshot* snap);

int dom_capability_snapshot_add(dom_capability_snapshot* snap,
                                const dom_capability_entry* entry);

void dom_capability_snapshot_finalize(dom_capability_snapshot* snap);

const dom_capability_entry* dom_capability_snapshot_find(
    const dom_capability_snapshot* snap,
    u32 capability_id,
    u32 subject_kind,
    u64 subject_id
);

dom_epistemic_view dom_epistemic_query(
    const dom_capability_snapshot* snap,
    u32 capability_id,
    u32 subject_kind,
    u64 subject_id,
    dom_act_time_t now_tick
);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_EPISTEMIC_H */
