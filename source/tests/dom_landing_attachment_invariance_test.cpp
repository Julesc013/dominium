/*
FILE: source/tests/dom_landing_attachment_invariance_test.cpp
MODULE: Repository
PURPOSE: Ensures landing attach/detach round-trips deterministically.
*/
#include <cassert>
#include <cstdio>
#include <cstring>

#include "runtime/dom_body_registry.h"
#include "runtime/dom_game_runtime.h"
#include "runtime/dom_lane_scheduler.h"
#include "runtime/dom_media_provider.h"
#include "runtime/dom_orbit_lane.h"
#include "runtime/dom_weather_provider.h"
#include "runtime/dom_vehicle_aero.h"
#include "runtime/dom_atmos_provider.h"

extern "C" {
#include "domino/core/fixed.h"
#include "domino/core/spacetime.h"
}

extern "C" {
int dom_orbit_eval_state(const dom_orbit_state *orbit,
                         dom_tick tick,
                         dom_orbit_posvel *out_posvel) {
    (void)orbit;
    (void)tick;
    if (out_posvel) {
        std::memset(out_posvel, 0, sizeof(*out_posvel));
    }
    return DOM_ORBIT_LANE_NOT_IMPLEMENTED;
}

int dom_orbit_next_event(const dom_orbit_state *orbit,
                         dom_tick tick,
                         dom_orbit_event_kind kind,
                         dom_tick *out_tick) {
    (void)orbit;
    (void)kind;
    if (out_tick) {
        *out_tick = tick;
    }
    return DOM_ORBIT_LANE_NOT_IMPLEMENTED;
}

int dom_media_registry_get_binding(const dom_media_registry *registry,
                                   dom_body_id body_id,
                                   u32 kind,
                                   dom_media_binding *out_binding) {
    (void)registry;
    (void)body_id;
    (void)kind;
    if (out_binding) {
        std::memset(out_binding, 0, sizeof(*out_binding));
    }
    return DOM_MEDIA_NOT_FOUND;
}

int dom_media_sample_query(const dom_media_registry *registry,
                           dom_body_id body_id,
                           u32 kind,
                           const dom_posseg_q16 *pos_body_fixed,
                           q48_16 altitude_m,
                           dom_tick tick,
                           dom_media_sample *out_sample) {
    (void)registry;
    (void)body_id;
    (void)kind;
    (void)pos_body_fixed;
    (void)altitude_m;
    (void)tick;
    if (out_sample) {
        std::memset(out_sample, 0, sizeof(*out_sample));
    }
    return DOM_MEDIA_NOT_FOUND;
}

int dom_vehicle_aero_props_validate(const dom_vehicle_aero_props *props) {
    return props ? DOM_VEHICLE_AERO_OK : DOM_VEHICLE_AERO_INVALID_ARGUMENT;
}

void dom_vehicle_aero_state_reset(dom_vehicle_aero_state *state) {
    if (state) {
        std::memset(state, 0, sizeof(*state));
    }
}

int dom_vehicle_aero_apply(const dom_vehicle_aero_props *props,
                           const dom_media_sample *sample,
                           SpacePos *inout_vel,
                           dom_vehicle_aero_state *state) {
    (void)props;
    (void)sample;
    (void)inout_vel;
    if (state) {
        state->last_heating_rate_q16 = 0;
        state->last_drag_accel_q16 = 0;
    }
    return DOM_VEHICLE_AERO_OK;
}

const void *dom_game_runtime_body_registry(const dom_game_runtime *rt) {
    (void)rt;
    return 0;
}

const void *dom_game_runtime_media_registry(const dom_game_runtime *rt) {
    (void)rt;
    return 0;
}

const void *dom_game_runtime_weather_registry(const dom_game_runtime *rt) {
    (void)rt;
    return 0;
}

int dom_atmos_profile_top_altitude(const dom_media_binding *binding,
                                   q48_16 *out_top_altitude_m) {
    (void)binding;
    if (out_top_altitude_m) {
        *out_top_altitude_m = 0;
    }
    return DOM_ATMOS_OK;
}

int dom_weather_sample_modifiers(const dom_weather_registry *registry,
                                 dom_body_id body_id,
                                 const dom_posseg_q16 *pos_body_fixed,
                                 q48_16 altitude_m,
                                 dom_tick tick,
                                 dom_weather_mods *out_mods) {
    (void)registry;
    (void)body_id;
    (void)pos_body_fixed;
    (void)altitude_m;
    (void)tick;
    if (out_mods) {
        std::memset(out_mods, 0, sizeof(*out_mods));
    }
    return DOM_WEATHER_NOT_FOUND;
}
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
