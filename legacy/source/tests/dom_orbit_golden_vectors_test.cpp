/*
FILE: source/tests/dom_orbit_golden_vectors_test.cpp
MODULE: Repository Tests
PURPOSE: Verifies deterministic orbit evaluation against simple golden invariants.
*/
#include <cassert>
#include <cstring>
#include <cstdio>

extern "C" {
#include "domino/core/fixed.h"
}

#include "runtime/dom_orbit_lane.h"

int main(void) {
    dom_orbit_state orbit;
    dom_orbit_posvel posvel;
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

    rc = dom_orbit_eval_state(&orbit, 0ull, &posvel);
    assert(rc == DOM_ORBIT_LANE_OK);
    assert(posvel.pos.x == orbit.semi_major_axis_m);
    assert(posvel.pos.y == 0);
    assert(posvel.pos.z == 0);
    assert(posvel.vel.x == 0);
    assert(posvel.vel.z == 0);
    assert(posvel.vel.y != 0);

    std::printf("dom_orbit_golden_vectors_test: OK\n");
    return 0;
}
