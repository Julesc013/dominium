/*
FILE: source/dominium/game/runtime/dom_ai_planner_logistics.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / game/runtime/ai_planner_logistics
RESPONSIBILITY: Deterministic logistics planner (routes/transfers) for AI.
ALLOWED DEPENDENCIES: `include/domino/**`, `source/dominium/**`, C++98 STL.
FORBIDDEN DEPENDENCIES: OS headers; non-deterministic inputs.
*/
#ifndef DOM_AI_PLANNER_LOGISTICS_H
#define DOM_AI_PLANNER_LOGISTICS_H

#include "domino/core/types.h"
#include "runtime/dom_faction_registry.h"
#include "runtime/dom_macro_economy.h"
#include "runtime/dom_station_registry.h"
#include "runtime/dom_route_graph.h"
#include "runtime/dom_transfer_scheduler.h"
#include "runtime/dom_body_registry.h"
#include "runtime/dom_system_registry.h"
#include "runtime/dom_ai_scheduler.h"

#ifdef __cplusplus
#include <vector>
#endif

#ifdef __cplusplus

struct dom_ai_planned_cmd {
    u32 schema_id;
    u16 schema_ver;
    u16 _pad0;
    u32 tick;
    std::vector<unsigned char> payload;
};

struct dom_ai_planner_logistics_result {
    std::vector<dom_ai_planned_cmd> commands;
    u32 ops_used;
    u32 reason_code;
};

int dom_ai_planner_logistics_run(const dom_faction_info *faction,
                                 const dom_macro_economy *economy,
                                 const dom_station_registry *stations,
                                 const dom_route_graph *routes,
                                 const dom_body_registry *bodies,
                                 const dom_system_registry *systems,
                                 u64 tick,
                                 u32 max_ops,
                                 dom_ai_planner_logistics_result *out_result);

#endif /* __cplusplus */

#endif /* DOM_AI_PLANNER_LOGISTICS_H */
