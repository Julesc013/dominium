/*
FILE: source/dominium/game/runtime/dom_cosmo_transit.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / game/runtime/dom_cosmo_transit
RESPONSIBILITY: Implements logical cosmos travel transit state machine.
*/
#include "runtime/dom_cosmo_transit.h"

void dom_cosmo_transit_reset(dom_cosmo_transit_state *state) {
    if (!state) {
        return;
    }
    state->src_entity_id = 0ull;
    state->dst_entity_id = 0ull;
    state->travel_edge_id = 0ull;
    state->start_tick = 0ull;
    state->end_tick = 0ull;
    state->active = 0;
}

int dom_cosmo_transit_begin(dom_cosmo_transit_state *state,
                            u64 src_entity_id,
                            u64 dst_entity_id,
                            u64 travel_edge_id,
                            u64 start_tick,
                            u64 duration_ticks) {
    u64 end_tick;
    if (!state) {
        return DOM_COSMO_TRANSIT_INVALID_ARGUMENT;
    }
    if (src_entity_id == 0ull || dst_entity_id == 0ull || src_entity_id == dst_entity_id) {
        return DOM_COSMO_TRANSIT_INVALID_ARGUMENT;
    }
    if (travel_edge_id == 0ull || duration_ticks == 0ull) {
        return DOM_COSMO_TRANSIT_INVALID_ARGUMENT;
    }
    if (start_tick > (0xffffffffffffffffull - duration_ticks)) {
        return DOM_COSMO_TRANSIT_INVALID_ARGUMENT;
    }
    end_tick = start_tick + duration_ticks;
    state->src_entity_id = src_entity_id;
    state->dst_entity_id = dst_entity_id;
    state->travel_edge_id = travel_edge_id;
    state->start_tick = start_tick;
    state->end_tick = end_tick;
    state->active = 1;
    return DOM_COSMO_TRANSIT_OK;
}

int dom_cosmo_transit_tick(dom_cosmo_transit_state *state,
                           u64 current_tick,
                           int *out_arrived) {
    if (out_arrived) {
        *out_arrived = 0;
    }
    if (!state) {
        return DOM_COSMO_TRANSIT_INVALID_ARGUMENT;
    }
    if (!state->active) {
        return DOM_COSMO_TRANSIT_NOT_ACTIVE;
    }
    if (current_tick >= state->end_tick) {
        state->active = 0;
        if (out_arrived) {
            *out_arrived = 1;
        }
        return DOM_COSMO_TRANSIT_OK;
    }
    return DOM_COSMO_TRANSIT_OK;
}

int dom_cosmo_transit_is_active(const dom_cosmo_transit_state *state) {
    if (!state) {
        return 0;
    }
    return state->active ? 1 : 0;
}
