/*
FILE: game/core/dom_interest_sources.c
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium core / interest_sources
RESPONSIBILITY: Emits interest entries from explicit game-owned sources.
ALLOWED DEPENDENCIES: `game/include/**`, `engine/include/**` public headers, and C89 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; product-layer runtime code.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Ordering and expiry rules are deterministic.
*/
#include "dominium/interest_sources.h"

static dom_act_time_t dom_interest_expiry(dom_act_time_t now, dom_act_time_t ttl)
{
    if (ttl <= 0) {
        return DOM_INTEREST_PERSISTENT;
    }
    if (now > (DOM_TIME_ACT_MAX - ttl)) {
        return DOM_INTEREST_PERSISTENT;
    }
    return now + ttl;
}

static int dom_interest_emit_list(dom_interest_set* set,
                                  const dom_interest_source_list* list,
                                  dom_act_time_t now_tick,
                                  dom_interest_reason reason)
{
    u32 i;
    dom_act_time_t expiry;
    if (!set || !list) {
        return -1;
    }
    expiry = dom_interest_expiry(now_tick, list->ttl_ticks);
    for (i = 0u; i < list->count; ++i) {
        if (dom_interest_set_add(set,
                                 list->target_kind,
                                 list->ids[i],
                                 reason,
                                 list->strength,
                                 expiry) != 0) {
            return -2;
        }
    }
    return 0;
}

int dom_interest_emit_player_focus(dom_interest_set* set,
                                   const dom_interest_source_list* list,
                                   dom_act_time_t now_tick)
{
    return dom_interest_emit_list(set, list, now_tick, DOM_INTEREST_REASON_PLAYER_FOCUS);
}

int dom_interest_emit_command_intent(dom_interest_set* set,
                                     const dom_interest_source_list* list,
                                     dom_act_time_t now_tick)
{
    return dom_interest_emit_list(set, list, now_tick, DOM_INTEREST_REASON_COMMAND_INTENT);
}

int dom_interest_emit_logistics(dom_interest_set* set,
                                const dom_interest_source_list* list,
                                dom_act_time_t now_tick)
{
    return dom_interest_emit_list(set, list, now_tick, DOM_INTEREST_REASON_LOGISTICS_ROUTE);
}

int dom_interest_emit_sensor_comms(dom_interest_set* set,
                                   const dom_interest_source_list* list,
                                   dom_act_time_t now_tick)
{
    return dom_interest_emit_list(set, list, now_tick, DOM_INTEREST_REASON_SENSOR_COMMS);
}

int dom_interest_emit_hazard_conflict(dom_interest_set* set,
                                      const dom_interest_source_list* list,
                                      dom_act_time_t now_tick)
{
    return dom_interest_emit_list(set, list, now_tick, DOM_INTEREST_REASON_HAZARD_CONFLICT);
}

int dom_interest_emit_governance_scope(dom_interest_set* set,
                                       const dom_interest_source_list* list,
                                       dom_act_time_t now_tick)
{
    return dom_interest_emit_list(set, list, now_tick, DOM_INTEREST_REASON_GOVERNANCE_SCOPE);
}
