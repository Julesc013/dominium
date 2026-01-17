/*
FILE: include/dominium/interest_sources.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / interest_sources
RESPONSIBILITY: Defines interest source producers (game-owned).
ALLOWED DEPENDENCIES: `game/include/**`, `engine/include/**` public headers, and C89 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; product-layer runtime code.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Deterministic ordering and bounded output required.
*/
#ifndef DOMINIUM_INTEREST_SOURCES_H
#define DOMINIUM_INTEREST_SOURCES_H

#include "dominium/interest_set.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct dom_interest_source_list {
    const u64* ids;
    u32        count;
    u32        target_kind;
    u32        strength;
    dom_act_time_t ttl_ticks; /* 0 => persistent */
} dom_interest_source_list;

int dom_interest_emit_player_focus(dom_interest_set* set,
                                   const dom_interest_source_list* list,
                                   dom_act_time_t now_tick);

int dom_interest_emit_command_intent(dom_interest_set* set,
                                     const dom_interest_source_list* list,
                                     dom_act_time_t now_tick);

int dom_interest_emit_logistics(dom_interest_set* set,
                                const dom_interest_source_list* list,
                                dom_act_time_t now_tick);

int dom_interest_emit_sensor_comms(dom_interest_set* set,
                                   const dom_interest_source_list* list,
                                   dom_act_time_t now_tick);

int dom_interest_emit_hazard_conflict(dom_interest_set* set,
                                      const dom_interest_source_list* list,
                                      dom_act_time_t now_tick);

int dom_interest_emit_governance_scope(dom_interest_set* set,
                                       const dom_interest_source_list* list,
                                       dom_act_time_t now_tick);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_INTEREST_SOURCES_H */
