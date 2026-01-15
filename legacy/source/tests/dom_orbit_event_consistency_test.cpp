/*
FILE: source/tests/dom_orbit_event_consistency_test.cpp
MODULE: Repository Tests
PURPOSE: Validates analytic event scheduling consistency.
*/
#include <cassert>
#include <cstdio>
#include <cstring>

extern "C" {
#include "domino/core/fixed.h"
}

#include "runtime/dom_orbit_lane.h"

int main(void) {
    dom_orbit_state orbit;
    dom_tick period_ticks = 0ull;
    dom_tick next_tick = 0ull;
    int rc;

    std::memset(&orbit, 0, sizeof(orbit));
    orbit.primary_body_id = 1ull;
    orbit.mu_m3_s2 = 1ull;
    orbit.semi_major_axis_m = d_q48_16_from_int(1);
    orbit.eccentricity = 0;
    orbit.inclination = 0;
    orbit.lon_ascending_node = 0;
    orbit.arg_periapsis = 0;
    orbit.mean_anomaly_at_epoch = 0;
    orbit.epoch_tick = 0ull;
    orbit.ups = 60u;
    orbit.soi_radius_m = 0;

    rc = dom_orbit_period_ticks(&orbit, &period_ticks);
    assert(rc == DOM_ORBIT_LANE_OK);
    assert(period_ticks > 0ull);

    rc = dom_orbit_next_event(&orbit, 0ull, DOM_ORBIT_EVENT_PERIAPSIS, &next_tick);
    assert(rc == DOM_ORBIT_LANE_OK);
    assert(next_tick == 0ull);

    rc = dom_orbit_next_event(&orbit, 1ull, DOM_ORBIT_EVENT_PERIAPSIS, &next_tick);
    assert(rc == DOM_ORBIT_LANE_OK);
    assert(next_tick == period_ticks);

    std::printf("dom_orbit_event_consistency_test: OK\n");
    return 0;
}
