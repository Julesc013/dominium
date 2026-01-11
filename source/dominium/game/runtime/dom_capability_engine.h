/*
FILE: source/dominium/game/runtime/dom_capability_engine.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / game/runtime/capability_engine
RESPONSIBILITY: Derives capability snapshots from belief and time-knowledge inputs.
ALLOWED DEPENDENCIES: `include/domino/**`, `source/dominium/**`, C++98 STL.
FORBIDDEN DEPENDENCIES: OS headers; locale/timezone libraries.
*/
#ifndef DOM_CAPABILITY_ENGINE_H
#define DOM_CAPABILITY_ENGINE_H

#include "domino/core/spacetime.h"
#include "domino/core/types.h"
#include "runtime/dom_belief_store.h"
#include "runtime/dom_time_knowledge.h"

#ifdef __cplusplus
extern "C" {
#endif

enum {
    DOM_CAPABILITY_ENGINE_OK = 0,
    DOM_CAPABILITY_ENGINE_ERR = -1,
    DOM_CAPABILITY_ENGINE_INVALID_ARGUMENT = -2
};

enum dom_capability_flags {
    DOM_CAPABILITY_FLAG_UNKNOWN = 1u << 0,
    DOM_CAPABILITY_FLAG_STALE = 1u << 1,
    DOM_CAPABILITY_FLAG_DEGRADED = 1u << 2,
    DOM_CAPABILITY_FLAG_CONFLICT = 1u << 3
};

typedef struct dom_capability {
    dom_capability_id capability_id;
    dom_capability_subject subject;
    u32 resolution_tier;
    i64 value_min;
    i64 value_max;
    dom_tick observed_tick;
    dom_tick delivery_tick;
    dom_tick expiry_tick;
    u64 latency_ticks;
    u64 staleness_ticks;
    u64 source_provenance;
    u32 flags;
} dom_capability;

typedef struct dom_capability_snapshot {
    dom_tick tick;
    u32 capability_count;
    const dom_capability *capabilities;
} dom_capability_snapshot;

typedef struct dom_capability_filters {
    i32 latency_scale_q16;
    i32 uncertainty_scale_q16;
    u32 staleness_grace_ticks;
} dom_capability_filters;

typedef struct dom_capability_engine dom_capability_engine;

dom_capability_engine *dom_capability_engine_create(void);
void dom_capability_engine_destroy(dom_capability_engine *engine);
int dom_capability_engine_init(dom_capability_engine *engine);

const dom_capability_snapshot *dom_capability_engine_build_snapshot(
    dom_capability_engine *engine,
    dom_time_actor_id actor_id,
    const dom_belief_store *belief_store,
    const dom_time_knowledge *time_knowledge,
    dom_tick tick,
    dom_ups ups,
    const dom_time_clock_env *clock_env,
    const dom_capability_filters *filters);

int dom_capability_snapshot_list(const dom_capability_snapshot *snapshot,
                                 dom_capability *out_caps,
                                 u32 max_caps,
                                 u32 *out_count);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOM_CAPABILITY_ENGINE_H */
