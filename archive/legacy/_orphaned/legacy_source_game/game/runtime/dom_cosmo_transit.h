/*
FILE: source/dominium/game/runtime/dom_cosmo_transit.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / game/runtime/dom_cosmo_transit
RESPONSIBILITY: Defines logical cosmos travel transit state machine.
ALLOWED DEPENDENCIES: `include/dominium/**`, `source/dominium/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: OS-specific headers; floating-point math.
*/
#ifndef DOM_COSMO_TRANSIT_H
#define DOM_COSMO_TRANSIT_H

#include "domino/core/types.h"

#ifdef __cplusplus
extern "C" {
#endif

enum {
    DOM_COSMO_TRANSIT_OK = 0,
    DOM_COSMO_TRANSIT_ERR = -1,
    DOM_COSMO_TRANSIT_INVALID_ARGUMENT = -2,
    DOM_COSMO_TRANSIT_NOT_ACTIVE = 1
};

typedef struct dom_cosmo_transit_state {
    u64 src_entity_id;
    u64 dst_entity_id;
    u64 travel_edge_id;
    u64 start_tick;
    u64 end_tick;
    int active;
} dom_cosmo_transit_state;

void dom_cosmo_transit_reset(dom_cosmo_transit_state *state);
int dom_cosmo_transit_begin(dom_cosmo_transit_state *state,
                            u64 src_entity_id,
                            u64 dst_entity_id,
                            u64 travel_edge_id,
                            u64 start_tick,
                            u64 duration_ticks);
int dom_cosmo_transit_tick(dom_cosmo_transit_state *state,
                           u64 current_tick,
                           int *out_arrived);
int dom_cosmo_transit_is_active(const dom_cosmo_transit_state *state);
u64 dom_cosmo_transit_arrival_tick(const dom_cosmo_transit_state *state);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOM_COSMO_TRANSIT_H */
