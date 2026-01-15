/*
FILE: source/tests/dom_orbit_warp_invariance_test.cpp
MODULE: Repository Tests
PURPOSE: Ensures orbit evaluation is invariant to stepped vs direct tick sampling.
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
    dom_orbit_posvel direct;
    dom_orbit_posvel stepped;
    dom_orbit_posvel tmp;
    const dom_tick target_tick = 120ull;
    dom_tick t;
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

    rc = dom_orbit_eval_state(&orbit, target_tick, &direct);
    assert(rc == DOM_ORBIT_LANE_OK);

    std::memset(&stepped, 0, sizeof(stepped));
    for (t = 0ull; t <= target_tick; ++t) {
        rc = dom_orbit_eval_state(&orbit, t, &tmp);
        assert(rc == DOM_ORBIT_LANE_OK);
        stepped = tmp;
    }

    assert(stepped.pos.x == direct.pos.x);
    assert(stepped.pos.y == direct.pos.y);
    assert(stepped.pos.z == direct.pos.z);
    assert(stepped.vel.x == direct.vel.x);
    assert(stepped.vel.y == direct.vel.y);
    assert(stepped.vel.z == direct.vel.z);

    std::printf("dom_orbit_warp_invariance_test: OK\n");
    return 0;
}
