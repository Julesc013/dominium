/*
FILE: source/tests/dom_landing_attachment_invariance_test.cpp
MODULE: Repository
PURPOSE: Ensures landing attach/detach round-trips deterministically.
*/
#include <cassert>
#include <cstdio>
#include <cstring>

#include "runtime/dom_body_registry.h"
#include "runtime/dom_lane_scheduler.h"

extern "C" {
#include "domino/core/fixed.h"
#include "domino/core/spacetime.h"
}

int main(void) {
    dom_body_registry *bodies = dom_body_registry_create();
    dom_lane_scheduler *sched = dom_lane_scheduler_create();
    dom_lane_vessel_desc desc;
    dom_body_id earth_id = 0ull;
    dom_body_info earth_info;
    dom_topo_latlong_q16 latlong;
    q48_16 altitude;
    dom_body_id out_body = 0ull;
    dom_topo_latlong_q16 out_latlong;
    q48_16 out_altitude = 0;
    dom_posseg_q16 pos_first;
    dom_posseg_q16 pos_second;
    dom_lane_state state;
    int rc;

    assert(bodies != 0);
    assert(sched != 0);
    rc = dom_body_registry_add_baseline(bodies);
    assert(rc == DOM_BODY_REGISTRY_OK);

    rc = dom_id_hash64("earth", 5u, &earth_id);
    assert(rc == DOM_SPACETIME_OK);
    rc = dom_body_registry_get(bodies, earth_id, &earth_info);
    assert(rc == DOM_BODY_REGISTRY_OK);

    std::memset(&desc, 0, sizeof(desc));
    desc.vessel_id = 1ull;
    desc.lane_type = DOM_LANE_LOCAL_KINEMATIC;
    desc.orbit.primary_body_id = earth_id;
    desc.orbit.semi_major_axis_m = d_q48_16_add(earth_info.radius_m, d_q48_16_from_int(1000));
    desc.orbit.ups = 60u;
    rc = dom_lane_scheduler_register_vessel(sched, &desc);
    assert(rc == DOM_LANE_OK);

    latlong.lat_turns = (q16_16)0x2000;
    latlong.lon_turns = (q16_16)0x0100;
    altitude = d_q48_16_from_int(50);

    rc = dom_lane_scheduler_landing_attach(sched, bodies, desc.vessel_id, earth_id, &latlong, altitude);
    assert(rc == DOM_LANE_OK);
    rc = dom_lane_scheduler_get_state(sched, desc.vessel_id, &state);
    assert(rc == DOM_LANE_OK);
    assert(state.lane_type == DOM_LANE_DOCKED_LANDED);

    rc = dom_lane_scheduler_get_landing(sched,
                                        desc.vessel_id,
                                        &out_body,
                                        &out_latlong,
                                        &out_altitude,
                                        &pos_first);
    assert(rc == DOM_LANE_OK);
    assert(out_body == earth_id);
    assert(out_latlong.lat_turns == latlong.lat_turns);
    assert(out_latlong.lon_turns == latlong.lon_turns);
    assert(out_altitude == altitude);

    rc = dom_lane_scheduler_landing_detach(sched, desc.vessel_id, DOM_LANE_LOCAL_KINEMATIC);
    assert(rc == DOM_LANE_OK);
    rc = dom_lane_scheduler_get_landing(sched, desc.vessel_id, 0, 0, 0, 0);
    assert(rc == DOM_LANE_NOT_FOUND);

    rc = dom_lane_scheduler_landing_attach(sched, bodies, desc.vessel_id, earth_id, &latlong, altitude);
    assert(rc == DOM_LANE_OK);
    rc = dom_lane_scheduler_get_landing(sched, desc.vessel_id, 0, 0, 0, &pos_second);
    assert(rc == DOM_LANE_OK);

    assert(pos_first.seg[0] == pos_second.seg[0]);
    assert(pos_first.seg[1] == pos_second.seg[1]);
    assert(pos_first.seg[2] == pos_second.seg[2]);
    assert(pos_first.loc[0] == pos_second.loc[0]);
    assert(pos_first.loc[1] == pos_second.loc[1]);
    assert(pos_first.loc[2] == pos_second.loc[2]);

    dom_lane_scheduler_destroy(sched);
    dom_body_registry_destroy(bodies);

    std::printf("dom_landing_attachment_invariance_test: OK\n");
    return 0;
}
