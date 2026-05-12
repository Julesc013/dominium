/*
FILE: source/dominium/game/runtime/dom_macro_events.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / game/runtime/macro_events
RESPONSIBILITY: Deterministic macro event scheduler for system/galaxy scopes.
ALLOWED DEPENDENCIES: `include/domino/**`, `source/dominium/**`, C++98 STL.
FORBIDDEN DEPENDENCIES: OS headers; non-deterministic inputs.
*/
#ifndef DOM_MACRO_EVENTS_H
#define DOM_MACRO_EVENTS_H

#include "domino/core/types.h"
#include "runtime/dom_macro_economy.h"

#ifdef __cplusplus
extern "C" {
#endif

enum {
    DOM_MACRO_EVENTS_OK = 0,
    DOM_MACRO_EVENTS_ERR = -1,
    DOM_MACRO_EVENTS_INVALID_ARGUMENT = -2,
    DOM_MACRO_EVENTS_DUPLICATE_ID = -3,
    DOM_MACRO_EVENTS_NOT_FOUND = -4,
    DOM_MACRO_EVENTS_INVALID_DATA = -5,
    DOM_MACRO_EVENTS_OVERFLOW = -6,
    DOM_MACRO_EVENTS_TOO_EARLY = -7
};

typedef struct dom_macro_event_effect {
    dom_resource_id resource_id;
    i64 production_delta;
    i64 demand_delta;
    u32 flags_set;
    u32 flags_clear;
} dom_macro_event_effect;

typedef struct dom_macro_event_desc {
    u64 event_id;
    u32 scope_kind;
    u64 scope_id;
    u64 trigger_tick;
    u32 effect_count;
    const dom_macro_event_effect *effects;
} dom_macro_event_desc;

typedef struct dom_macro_event_info {
    u64 event_id;
    u32 scope_kind;
    u64 scope_id;
    u64 trigger_tick;
    u32 effect_count;
} dom_macro_event_info;

typedef void (*dom_macro_event_iter_fn)(const dom_macro_event_info *info, void *user);

typedef struct dom_macro_events dom_macro_events;

dom_macro_events *dom_macro_events_create(void);
void dom_macro_events_destroy(dom_macro_events *events);
int dom_macro_events_init(dom_macro_events *events);

int dom_macro_events_schedule(dom_macro_events *events,
                              const dom_macro_event_desc *desc);
int dom_macro_events_iterate(const dom_macro_events *events,
                             dom_macro_event_iter_fn fn,
                             void *user);
int dom_macro_events_list(const dom_macro_events *events,
                          dom_macro_event_info *out_infos,
                          u32 max_infos,
                          u32 *out_count);
int dom_macro_events_list_effects(const dom_macro_events *events,
                                  u64 event_id,
                                  dom_macro_event_effect *out_effects,
                                  u32 max_effects,
                                  u32 *out_count);
u32 dom_macro_events_count(const dom_macro_events *events);

int dom_macro_events_update(dom_macro_events *events,
                            dom_macro_economy *economy,
                            u64 current_tick);
int dom_macro_events_seek(dom_macro_events *events, u64 tick);

u64 dom_macro_events_last_tick(const dom_macro_events *events);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOM_MACRO_EVENTS_H */
