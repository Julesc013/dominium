/*
FILE: source/tests/dom_cosmo_transit_determinism_test.cpp
MODULE: Repository
PURPOSE: Validates deterministic logical transit scheduling under different tick pacing.
*/
#include <cassert>
#include <cstdio>

#include "runtime/dom_cosmo_transit.h"

static void run_stepwise(u64 start_tick, u64 duration_ticks) {
    dom_cosmo_transit_state state;
    int arrived = 0;
    u64 tick;

    dom_cosmo_transit_reset(&state);
    assert(dom_cosmo_transit_begin(&state, 1ull, 2ull, 3ull, start_tick, duration_ticks)
           == DOM_COSMO_TRANSIT_OK);

    for (tick = start_tick; tick < start_tick + duration_ticks; ++tick) {
        arrived = 0;
        assert(dom_cosmo_transit_tick(&state, tick, &arrived) == DOM_COSMO_TRANSIT_OK);
        assert(arrived == 0);
    }

    arrived = 0;
    assert(dom_cosmo_transit_tick(&state, start_tick + duration_ticks, &arrived)
           == DOM_COSMO_TRANSIT_OK);
    assert(arrived == 1);
    assert(dom_cosmo_transit_is_active(&state) == 0);
}

static void run_batched(u64 start_tick, u64 duration_ticks) {
    dom_cosmo_transit_state state;
    int arrived = 0;
    const u64 end_tick = start_tick + duration_ticks;

    dom_cosmo_transit_reset(&state);
    assert(dom_cosmo_transit_begin(&state, 1ull, 2ull, 3ull, start_tick, duration_ticks)
           == DOM_COSMO_TRANSIT_OK);

    arrived = 0;
    assert(dom_cosmo_transit_tick(&state, start_tick + 5u, &arrived) == DOM_COSMO_TRANSIT_OK);
    assert(arrived == 0);

    arrived = 0;
    assert(dom_cosmo_transit_tick(&state, start_tick + duration_ticks - 1u, &arrived)
           == DOM_COSMO_TRANSIT_OK);
    assert(arrived == 0);

    arrived = 0;
    assert(dom_cosmo_transit_tick(&state, end_tick + 10u, &arrived)
           == DOM_COSMO_TRANSIT_OK);
    assert(arrived == 1);
    assert(state.end_tick == end_tick);
    assert(dom_cosmo_transit_is_active(&state) == 0);
}

int main(void) {
    run_stepwise(100u, 50u);
    run_batched(100u, 50u);

    std::printf("dom_cosmo_transit_determinism_test: OK\n");
    return 0;
}
