/*
FILE: source/dominium/game/runtime/dom_ai_planner_events.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / game/runtime/ai_planner_events
RESPONSIBILITY: Deterministic macro-event planner for AI factions.
ALLOWED DEPENDENCIES: `include/domino/**`, `source/dominium/**`, C++98 STL.
FORBIDDEN DEPENDENCIES: OS headers; non-deterministic inputs.
*/
#ifndef DOM_AI_PLANNER_EVENTS_H
#define DOM_AI_PLANNER_EVENTS_H

#include "domino/core/types.h"
#include "runtime/dom_faction_registry.h"
#include "runtime/dom_macro_economy.h"
#include "runtime/dom_macro_events.h"
#include "runtime/dom_system_registry.h"
#include "runtime/dom_ai_scheduler.h"

#ifdef __cplusplus
#include <vector>
#endif

#ifdef __cplusplus

struct dom_ai_planned_event {
    dom_macro_event_desc desc;
    std::vector<dom_macro_event_effect> effects;
};

struct dom_ai_planner_events_result {
    std::vector<dom_ai_planned_event> events;
    u32 ops_used;
    u32 reason_code;
};

int dom_ai_planner_events_run(const dom_faction_info *faction,
                              const dom_macro_economy *economy,
                              const dom_macro_events *events,
                              const dom_system_registry *systems,
                              u64 tick,
                              u32 max_ops,
                              dom_ai_planner_events_result *out_result);

#endif /* __cplusplus */

#endif /* DOM_AI_PLANNER_EVENTS_H */
