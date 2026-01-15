/*
FILE: source/dominium/game/runtime/dom_lane_scheduler.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / game/runtime/lane_scheduler
RESPONSIBILITY: Implements lane scheduling for orbital/local/docked transitions.
*/
#include "runtime/dom_lane_scheduler.h"

#include <algorithm>
#include <vector>
#include <cstring>
#include <climits>

#include "runtime/dom_body_registry.h"
#include "runtime/dom_game_runtime.h"
#include "runtime/dom_media_provider.h"
#include "runtime/dom_atmos_provider.h"
#include "runtime/dom_weather_provider.h"

extern "C" {
#include "domino/core/spacetime.h"
#include "domino/core/dom_deterministic_math.h"
}

namespace {

struct DomLaneVessel {
    u64 id;
    dom_lane_state state;
    dom_orbit_state orbit;
    SpacePos local_pos;
    SpacePos local_vel;
    dom_vehicle_aero_props aero_props;
    dom_vehicle_aero_state aero_state;
    int has_orbit;
    int has_aero_props;
    int landed;
    dom_body_id landed_body_id;
    dom_topo_latlong_q16 landed_latlong;
    q48_16 landed_altitude_m;
    dom_posseg_q16 landed_pos;
};

struct DomLanePending {
    u64 vessel_id;
    dom_lane_type target;
};

static bool lane_transition_allowed(dom_lane_type from, dom_lane_type to) {
    if (from == to) {
        return true;
    }
    if (from == DOM_LANE_ORBITAL) {
        return to == DOM_LANE_LOCAL_KINEMATIC || to == DOM_LANE_APPROACH;
    }
    if (from == DOM_LANE_APPROACH) {
        return to == DOM_LANE_ORBITAL || to == DOM_LANE_LOCAL_KINEMATIC;
    }
    if (from == DOM_LANE_LOCAL_KINEMATIC) {
        return to == DOM_LANE_ORBITAL || to == DOM_LANE_DOCKED_LANDED;
    }
    if (from == DOM_LANE_DOCKED_LANDED) {
        return to == DOM_LANE_LOCAL_KINEMATIC;
    }
    return false;
}

static bool vessel_id_less(const DomLaneVessel &a, const DomLaneVessel &b) {
    return a.id < b.id;
}

static bool pending_less(const DomLanePending &a, const DomLanePending &b) {
    if (a.vessel_id != b.vessel_id) {
        return a.vessel_id < b.vessel_id;
    }
    return (u32)a.target < (u32)b.target;
}

static q48_16 default_enter_radius(void) {
    return d_q48_16_from_int(1000);
}

static q48_16 default_exit_radius(void) {
    return d_q48_16_from_int(1200);
}

static u32 default_max_warp(void) {
    return 8u;
}

static u32 atmos_max_warp(void) {
    return 4u;
}

static dom_body_id default_body_id(void) {
    dom_body_id id = 0ull;
    (void)dom_id_hash64("earth", 5u, &id);
    return id;
}

static u64 abs_i64_u64(i64 v) {
    return v < 0 ? (u64)(-v) : (u64)v;
}

static u64 square_u64_clamp(u64 v) {
    if (v != 0u && v > (UINT64_MAX / v)) {
        return UINT64_MAX;
    }
    return v * v;
}

static u64 add_u64_clamp(u64 a, u64 b) {
    u64 sum = a + b;
    if (sum < a) {
        return UINT64_MAX;
    }
    return sum;
}

static u64 spacepos_length_u64(const SpacePos *pos) {
    u64 x2;
    u64 y2;
    u64 z2;
    u64 sum;
    if (!pos) {
        return 0u;
    }
    x2 = square_u64_clamp(abs_i64_u64(d_q48_16_to_int(pos->x)));
    y2 = square_u64_clamp(abs_i64_u64(d_q48_16_to_int(pos->y)));
    z2 = square_u64_clamp(abs_i64_u64(d_q48_16_to_int(pos->z)));
    sum = add_u64_clamp(x2, y2);
    sum = add_u64_clamp(sum, z2);
    return dom_sqrt_u64(sum);
}

static bool compute_altitude_from_pos(const dom_body_registry *bodies,
                                      dom_body_id body_id,
                                      const SpacePos *pos,
                                      q48_16 *out_altitude) {
    dom_body_info info;
    q48_16 radius;
    if (!bodies || !pos || !out_altitude || body_id == 0ull) {
        return false;
    }
    if (dom_body_registry_get(bodies, body_id, &info) != DOM_BODY_REGISTRY_OK) {
        return false;
    }
    radius = info.radius_m;
    *out_altitude = d_q48_16_sub(d_q48_16_from_int((i64)spacepos_length_u64(pos)), radius);
    return true;
}

static bool compute_orbital_altitude(const DomLaneVessel &v,
                                     const dom_body_registry *bodies,
                                     dom_tick tick,
                                     q48_16 *out_altitude) {
    dom_orbit_posvel posvel;
    dom_body_info info;
    if (!out_altitude || !v.has_orbit) {
        return false;
    }
    if (dom_orbit_eval_state(&v.orbit, tick, &posvel) != DOM_ORBIT_LANE_OK) {
        if (!bodies) {
            return false;
        }
        if (dom_body_registry_get(bodies, v.orbit.primary_body_id, &info) != DOM_BODY_REGISTRY_OK) {
            return false;
        }
        *out_altitude = d_q48_16_sub(v.orbit.semi_major_axis_m, info.radius_m);
        return true;
    }
    return compute_altitude_from_pos(bodies, v.orbit.primary_body_id, &posvel.pos, out_altitude);
}

static void update_orbit_environment(DomLaneVessel *v,
                                     const dom_body_registry *bodies,
                                     const dom_media_registry *media) {
    dom_body_info info;
    dom_media_binding binding;
    q48_16 top_alt = 0;
    if (!v || !v->has_orbit) {
        return;
    }
    v->orbit.body_radius_m = 0;
    v->orbit.atmosphere_top_alt_m = 0;
    if (bodies &&
        dom_body_registry_get(bodies, v->orbit.primary_body_id, &info) == DOM_BODY_REGISTRY_OK) {
        v->orbit.body_radius_m = info.radius_m;
    }
    if (media &&
        dom_media_registry_get_binding(media,
                                       v->orbit.primary_body_id,
                                       DOM_MEDIA_KIND_ATMOSPHERE,
                                       &binding) == DOM_MEDIA_OK) {
        if (dom_atmos_profile_top_altitude(&binding, &top_alt) == DOM_ATMOS_OK) {
            v->orbit.atmosphere_top_alt_m = top_alt;
        }
    }
}

static void zero_media_sample(dom_media_sample *sample) {
    if (!sample) {
        return;
    }
    std::memset(sample, 0, sizeof(*sample));
}

static void apply_weather_mods(dom_media_sample *sample,
                               const dom_weather_mods *mods) {
    if (!sample || !mods) {
        return;
    }
    sample->density_q16 = d_q16_16_add(sample->density_q16, mods->density_delta_q16);
    if (sample->density_q16 < 0) {
        sample->density_q16 = 0;
    }
    sample->pressure_q16 = d_q16_16_add(sample->pressure_q16, mods->pressure_delta_q16);
    if (sample->pressure_q16 < 0) {
        sample->pressure_q16 = 0;
    }
    sample->temperature_q16 = d_q16_16_add(sample->temperature_q16, mods->temperature_delta_q16);
    if (sample->temperature_q16 < 0) {
        sample->temperature_q16 = 0;
    }
    if (mods->has_wind || sample->has_wind) {
        sample->wind_body_q16.v[0] =
            d_q16_16_add(sample->wind_body_q16.v[0], mods->wind_delta_q16.v[0]);
        sample->wind_body_q16.v[1] =
            d_q16_16_add(sample->wind_body_q16.v[1], mods->wind_delta_q16.v[1]);
        sample->wind_body_q16.v[2] =
            d_q16_16_add(sample->wind_body_q16.v[2], mods->wind_delta_q16.v[2]);
        sample->has_wind = 1u;
    }
}

} // namespace

struct dom_lane_scheduler {
    std::vector<DomLaneVessel> vessels;
    std::vector<DomLanePending> pending;
    dom_activation_bubble bubble;
    int bubble_active;
    u64 active_vessel_id;
    u32 max_warp_factor;
    dom_body_id bubble_body_id;
    dom_topo_latlong_q16 bubble_center;
    int bubble_has_center;
};

dom_lane_scheduler *dom_lane_scheduler_create(void) {
    dom_lane_scheduler *sched = new dom_lane_scheduler();
    if (!sched) {
        return 0;
    }
    (void)dom_lane_scheduler_init(sched);
    return sched;
}

void dom_lane_scheduler_destroy(dom_lane_scheduler *sched) {
    if (!sched) {
        return;
    }
    delete sched;
}

int dom_lane_scheduler_init(dom_lane_scheduler *sched) {
    if (!sched) {
        return DOM_LANE_INVALID_ARGUMENT;
    }
    sched->vessels.clear();
    sched->pending.clear();
    std::memset(&sched->bubble, 0, sizeof(sched->bubble));
    sched->bubble_active = 0;
    sched->active_vessel_id = 0ull;
    sched->max_warp_factor = default_max_warp();
    sched->bubble_body_id = 0ull;
    sched->bubble_center.lat_turns = 0;
    sched->bubble_center.lon_turns = 0;
    sched->bubble_has_center = 0;
    return DOM_LANE_OK;
}

int dom_lane_scheduler_register_vessel(dom_lane_scheduler *sched,
                                       const dom_lane_vessel_desc *desc) {
    size_t i;
    DomLaneVessel entry;
    if (!sched || !desc || desc->vessel_id == 0ull) {
        return DOM_LANE_INVALID_ARGUMENT;
    }
    if (desc->has_aero_props) {
        if (dom_vehicle_aero_props_validate(&desc->aero_props) != DOM_VEHICLE_AERO_OK) {
            return DOM_LANE_INVALID_ARGUMENT;
        }
    }
    for (i = 0u; i < sched->vessels.size(); ++i) {
        if (sched->vessels[i].id == desc->vessel_id) {
            sched->vessels[i].orbit = desc->orbit;
            sched->vessels[i].local_pos = desc->local_pos;
            sched->vessels[i].local_vel = desc->local_vel;
            sched->vessels[i].state.lane_type = desc->lane_type;
            sched->vessels[i].has_orbit = 1;
            sched->vessels[i].has_aero_props = desc->has_aero_props ? 1 : 0;
            sched->vessels[i].aero_props = desc->aero_props;
            dom_vehicle_aero_state_reset(&sched->vessels[i].aero_state);
            return DOM_LANE_OK;
        }
    }
    std::memset(&entry, 0, sizeof(entry));
    entry.id = desc->vessel_id;
    entry.state.lane_type = desc->lane_type;
    entry.state.since_tick = 0ull;
    entry.state.active_bubble_id = 0u;
    entry.orbit = desc->orbit;
    entry.local_pos = desc->local_pos;
    entry.local_vel = desc->local_vel;
    entry.aero_props = desc->aero_props;
    dom_vehicle_aero_state_reset(&entry.aero_state);
    entry.has_orbit = 1;
    entry.has_aero_props = desc->has_aero_props ? 1 : 0;
    entry.landed = 0;
    entry.landed_body_id = 0ull;
    entry.landed_latlong.lat_turns = 0;
    entry.landed_latlong.lon_turns = 0;
    entry.landed_altitude_m = 0;
    std::memset(&entry.landed_pos, 0, sizeof(entry.landed_pos));
    {
        std::vector<DomLaneVessel>::iterator it =
            std::lower_bound(sched->vessels.begin(),
                             sched->vessels.end(),
                             entry,
                             vessel_id_less);
        sched->vessels.insert(it, entry);
    }
    return DOM_LANE_OK;
}

int dom_lane_scheduler_request_transition(dom_lane_scheduler *sched,
                                          u64 vessel_id,
                                          dom_lane_type target_lane) {
    DomLanePending req;
    if (!sched || vessel_id == 0ull) {
        return DOM_LANE_INVALID_ARGUMENT;
    }
    req.vessel_id = vessel_id;
    req.target = target_lane;
    sched->pending.push_back(req);
    return DOM_LANE_OK;
}

int dom_lane_scheduler_get_state(const dom_lane_scheduler *sched,
                                 u64 vessel_id,
                                 dom_lane_state *out_state) {
    size_t i;
    if (!sched || !out_state || vessel_id == 0ull) {
        return DOM_LANE_INVALID_ARGUMENT;
    }
    for (i = 0u; i < sched->vessels.size(); ++i) {
        if (sched->vessels[i].id == vessel_id) {
            *out_state = sched->vessels[i].state;
            return DOM_LANE_OK;
        }
    }
    return DOM_LANE_NOT_FOUND;
}

int dom_lane_scheduler_set_active_vessel(dom_lane_scheduler *sched,
                                         u64 vessel_id) {
    if (!sched) {
        return DOM_LANE_INVALID_ARGUMENT;
    }
    sched->active_vessel_id = vessel_id;
    return DOM_LANE_OK;
}

int dom_lane_scheduler_update(dom_lane_scheduler *sched,
                              const struct dom_game_runtime *rt,
                              dom_tick tick) {
    size_t i;
    const dom_body_registry *bodies = 0;
    const dom_media_registry *media = 0;
    const dom_weather_registry *weather = 0;
    int result = DOM_LANE_OK;
    if (!sched) {
        return DOM_LANE_INVALID_ARGUMENT;
    }
    if (rt) {
        bodies = static_cast<const dom_body_registry *>(dom_game_runtime_body_registry(rt));
        media = static_cast<const dom_media_registry *>(dom_game_runtime_media_registry(rt));
        weather = static_cast<const dom_weather_registry *>(dom_game_runtime_weather_registry(rt));
    }
    sched->max_warp_factor = default_max_warp();

    for (i = 0u; i < sched->vessels.size(); ++i) {
        DomLaneVessel &vessel = sched->vessels[i];
        update_orbit_environment(&vessel, bodies, media);
        if (vessel.state.lane_type == DOM_LANE_ORBITAL && vessel.has_orbit) {
            dom_tick event_tick = 0u;
            if (dom_orbit_next_event(&vessel.orbit,
                                     tick,
                                     DOM_ORBIT_EVENT_ATMOS_ENTER,
                                     &event_tick) == DOM_ORBIT_LANE_OK) {
                if (event_tick == tick) {
                    DomLanePending req;
                    req.vessel_id = vessel.id;
                    req.target = DOM_LANE_LOCAL_KINEMATIC;
                    sched->pending.push_back(req);
                }
            }
        }
    }

    if (!sched->bubble_active && sched->active_vessel_id != 0ull) {
        for (i = 0u; i < sched->vessels.size(); ++i) {
            if (sched->vessels[i].id == sched->active_vessel_id) {
                if (sched->vessels[i].state.lane_type == DOM_LANE_DOCKED_LANDED ||
                    sched->vessels[i].state.lane_type == DOM_LANE_LOCAL_KINEMATIC) {
                    sched->bubble_active = 1;
                    sched->bubble.id = 1u;
                    sched->bubble.center_vessel_id = sched->active_vessel_id;
                    sched->bubble.enter_radius_m = default_enter_radius();
                    sched->bubble.exit_radius_m = default_exit_radius();
                    sched->bubble.radius_m = sched->bubble.exit_radius_m;
                    sched->bubble_body_id = sched->vessels[i].landed_body_id;
                    if (sched->bubble_body_id == 0ull) {
                        sched->bubble_body_id = sched->vessels[i].orbit.primary_body_id;
                    }
                    if (sched->bubble_body_id == 0ull) {
                        sched->bubble_body_id = default_body_id();
                    }
                    sched->bubble_center = sched->vessels[i].landed_latlong;
                    sched->bubble_has_center = 1;
                    break;
                }
                q48_16 altitude = 0;
                if (compute_orbital_altitude(sched->vessels[i], bodies, tick, &altitude)) {
                    if (altitude <= default_enter_radius()) {
                        sched->bubble_active = 1;
                        sched->bubble.id = 1u;
                        sched->bubble.center_vessel_id = sched->active_vessel_id;
                        sched->bubble.enter_radius_m = default_enter_radius();
                        sched->bubble.exit_radius_m = default_exit_radius();
                        sched->bubble.radius_m = sched->bubble.exit_radius_m;
                        sched->bubble_body_id = sched->vessels[i].orbit.primary_body_id;
                        if (sched->bubble_body_id == 0ull) {
                            sched->bubble_body_id = default_body_id();
                        }
                        sched->bubble_center.lat_turns = 0;
                        sched->bubble_center.lon_turns = 0;
                        sched->bubble_has_center = 1;
                    }
                }
                break;
            }
        }
    }

    if (sched->bubble_active) {
        for (i = 0u; i < sched->vessels.size(); ++i) {
            if (sched->vessels[i].id == sched->bubble.center_vessel_id) {
                if (sched->vessels[i].state.lane_type == DOM_LANE_LOCAL_KINEMATIC ||
                    sched->vessels[i].state.lane_type == DOM_LANE_DOCKED_LANDED) {
                    break;
                }
                q48_16 altitude = 0;
                if (compute_orbital_altitude(sched->vessels[i], bodies, tick, &altitude)) {
                    if (altitude > sched->bubble.exit_radius_m) {
                        sched->bubble_active = 0;
                        sched->bubble.id = 0u;
                        sched->bubble.center_vessel_id = 0ull;
                        sched->bubble_body_id = 0ull;
                        sched->bubble_has_center = 0;
                        sched->bubble_center.lat_turns = 0;
                        sched->bubble_center.lon_turns = 0;
                    }
                }
                break;
            }
        }
    }

    if (!sched->pending.empty()) {
        std::sort(sched->pending.begin(), sched->pending.end(), pending_less);
        for (i = 0u; i < sched->pending.size(); ++i) {
            const DomLanePending &req = sched->pending[i];
            size_t v;
            for (v = 0u; v < sched->vessels.size(); ++v) {
                if (sched->vessels[v].id == req.vessel_id) {
                    dom_lane_type from = sched->vessels[v].state.lane_type;
                    if (!lane_transition_allowed(from, req.target)) {
                        result = DOM_LANE_TRANSITION_REFUSED;
                        break;
                    }
                    if (req.target == DOM_LANE_LOCAL_KINEMATIC) {
                        if (sched->vessels[v].has_orbit) {
                            dom_orbit_posvel posvel;
                            if (dom_orbit_eval_state(&sched->vessels[v].orbit,
                                                     tick,
                                                     &posvel) == DOM_ORBIT_LANE_OK) {
                                sched->vessels[v].local_pos = posvel.pos;
                                sched->vessels[v].local_vel = posvel.vel;
                            }
                        }
                        dom_vehicle_aero_state_reset(&sched->vessels[v].aero_state);
                        if (!sched->bubble_active) {
                            sched->bubble_active = 1;
                            sched->bubble.id = 1u;
                            sched->bubble.center_vessel_id = req.vessel_id;
                            sched->bubble.enter_radius_m = default_enter_radius();
                            sched->bubble.exit_radius_m = default_exit_radius();
                            sched->bubble.radius_m = sched->bubble.exit_radius_m;
                            sched->bubble_body_id = sched->vessels[v].orbit.primary_body_id;
                            if (sched->bubble_body_id == 0ull) {
                                sched->bubble_body_id = default_body_id();
                            }
                            sched->bubble_center.lat_turns = 0;
                            sched->bubble_center.lon_turns = 0;
                            sched->bubble_has_center = 1;
                        } else if (sched->bubble.center_vessel_id != req.vessel_id) {
                            result = DOM_LANE_BUBBLE_LIMIT;
                            break;
                        }
                        sched->vessels[v].state.active_bubble_id = sched->bubble.id;
                    }
                    sched->vessels[v].state.lane_type = req.target;
                    sched->vessels[v].state.since_tick = tick;
                    if (req.target != DOM_LANE_LOCAL_KINEMATIC) {
                        sched->vessels[v].state.active_bubble_id = 0u;
                    }
                    break;
                }
            }
        }
        sched->pending.clear();
    }

    for (i = 0u; i < sched->vessels.size(); ++i) {
        DomLaneVessel &vessel = sched->vessels[i];
        if (vessel.state.lane_type != DOM_LANE_LOCAL_KINEMATIC || vessel.landed) {
            continue;
        }
        dom_body_id body_id = vessel.orbit.primary_body_id;
        q48_16 altitude = 0;
        if (body_id == 0ull) {
            body_id = default_body_id();
        }
        if (!compute_altitude_from_pos(bodies, body_id, &vessel.local_pos, &altitude)) {
            altitude = 0;
        }
        dom_media_sample sample;
        zero_media_sample(&sample);
        if (media) {
            int rc = dom_media_sample_query(media,
                                            body_id,
                                            DOM_MEDIA_KIND_ATMOSPHERE,
                                            0,
                                            altitude,
                                            tick,
                                            &sample);
            if (rc != DOM_MEDIA_OK) {
                zero_media_sample(&sample);
            }
        }
        if (weather) {
            dom_weather_mods mods;
            std::memset(&mods, 0, sizeof(mods));
            if (dom_weather_sample_modifiers(weather,
                                             body_id,
                                             0,
                                             altitude,
                                             tick,
                                             &mods) == DOM_WEATHER_OK) {
                apply_weather_mods(&sample, &mods);
            }
        }
        if (sample.density_q16 > 0 && sched->max_warp_factor > atmos_max_warp()) {
            sched->max_warp_factor = atmos_max_warp();
        }
        if (vessel.has_aero_props && sample.density_q16 > 0) {
            (void)dom_vehicle_aero_apply(&vessel.aero_props,
                                         &sample,
                                         &vessel.local_vel,
                                         &vessel.aero_state);
        }
        vessel.local_pos.x = d_q48_16_add(vessel.local_pos.x, vessel.local_vel.x);
        vessel.local_pos.y = d_q48_16_add(vessel.local_pos.y, vessel.local_vel.y);
        vessel.local_pos.z = d_q48_16_add(vessel.local_pos.z, vessel.local_vel.z);
        if (vessel.orbit.atmosphere_top_alt_m > 0 &&
            altitude > vessel.orbit.atmosphere_top_alt_m) {
            (void)dom_lane_scheduler_request_transition(sched,
                                                        vessel.id,
                                                        DOM_LANE_ORBITAL);
        }
    }
    return result;
}

u32 dom_lane_scheduler_max_warp(const dom_lane_scheduler *sched) {
    if (!sched || sched->max_warp_factor == 0u) {
        return 1u;
    }
    return sched->max_warp_factor;
}

int dom_lane_scheduler_get_bubble(const dom_lane_scheduler *sched,
                                  dom_activation_bubble *out_bubble,
                                  int *out_active,
                                  dom_body_id *out_body_id,
                                  dom_topo_latlong_q16 *out_center) {
    if (!sched) {
        return DOM_LANE_INVALID_ARGUMENT;
    }
    if (out_bubble) {
        *out_bubble = sched->bubble;
    }
    if (out_active) {
        *out_active = sched->bubble_active;
    }
    if (out_body_id) {
        *out_body_id = sched->bubble_body_id;
    }
    if (out_center) {
        *out_center = sched->bubble_center;
    }
    return DOM_LANE_OK;
}

int dom_lane_scheduler_landing_attach(dom_lane_scheduler *sched,
                                      const dom_body_registry *bodies,
                                      u64 vessel_id,
                                      dom_body_id body_id,
                                      const dom_topo_latlong_q16 *latlong,
                                      q48_16 altitude_m) {
    size_t i;
    dom_topology_binding binding;
    dom_posseg_q16 pos;
    int rc;

    if (!sched || !bodies || vessel_id == 0ull || !latlong) {
        return DOM_LANE_INVALID_ARGUMENT;
    }
    for (i = 0u; i < sched->vessels.size(); ++i) {
        if (sched->vessels[i].id == vessel_id) {
            rc = dom_surface_topology_select(bodies, body_id, 0u, &binding);
            if (rc != DOM_TOPOLOGY_OK) {
                return DOM_LANE_ERR;
            }
            rc = dom_surface_topology_pos_from_latlong(&binding, latlong, altitude_m, &pos);
            if (rc != DOM_TOPOLOGY_OK) {
                return DOM_LANE_ERR;
            }
            sched->vessels[i].landed = 1;
            sched->vessels[i].landed_body_id = body_id;
            sched->vessels[i].landed_latlong = *latlong;
            sched->vessels[i].landed_altitude_m = altitude_m;
            sched->vessels[i].landed_pos = pos;
            sched->vessels[i].state.lane_type = DOM_LANE_DOCKED_LANDED;
            sched->vessels[i].state.active_bubble_id = sched->bubble.id;
            return DOM_LANE_OK;
        }
    }
    return DOM_LANE_NOT_FOUND;
}

int dom_lane_scheduler_landing_detach(dom_lane_scheduler *sched,
                                      u64 vessel_id,
                                      dom_lane_type next_lane) {
    size_t i;
    if (!sched || vessel_id == 0ull) {
        return DOM_LANE_INVALID_ARGUMENT;
    }
    for (i = 0u; i < sched->vessels.size(); ++i) {
        if (sched->vessels[i].id == vessel_id) {
            sched->vessels[i].landed = 0;
            if (!lane_transition_allowed(DOM_LANE_DOCKED_LANDED, next_lane)) {
                return DOM_LANE_TRANSITION_REFUSED;
            }
            sched->vessels[i].state.lane_type = next_lane;
            sched->vessels[i].state.active_bubble_id = 0u;
            return DOM_LANE_OK;
        }
    }
    return DOM_LANE_NOT_FOUND;
}

int dom_lane_scheduler_get_landing(const dom_lane_scheduler *sched,
                                   u64 vessel_id,
                                   dom_body_id *out_body_id,
                                   dom_topo_latlong_q16 *out_latlong,
                                   q48_16 *out_altitude_m,
                                   dom_posseg_q16 *out_pos) {
    size_t i;
    if (!sched || vessel_id == 0ull) {
        return DOM_LANE_INVALID_ARGUMENT;
    }
    for (i = 0u; i < sched->vessels.size(); ++i) {
        if (sched->vessels[i].id == vessel_id) {
            if (!sched->vessels[i].landed) {
                return DOM_LANE_NOT_FOUND;
            }
            if (out_body_id) {
                *out_body_id = sched->vessels[i].landed_body_id;
            }
            if (out_latlong) {
                *out_latlong = sched->vessels[i].landed_latlong;
            }
            if (out_altitude_m) {
                *out_altitude_m = sched->vessels[i].landed_altitude_m;
            }
            if (out_pos) {
                *out_pos = sched->vessels[i].landed_pos;
            }
            return DOM_LANE_OK;
        }
    }
    return DOM_LANE_NOT_FOUND;
}

int dom_lane_scheduler_get_local_state(const dom_lane_scheduler *sched,
                                       u64 vessel_id,
                                       SpacePos *out_pos,
                                       SpacePos *out_vel,
                                       dom_lane_type *out_lane) {
    size_t i;
    if (!sched || vessel_id == 0ull) {
        return DOM_LANE_INVALID_ARGUMENT;
    }
    for (i = 0u; i < sched->vessels.size(); ++i) {
        if (sched->vessels[i].id == vessel_id) {
            if (out_pos) {
                *out_pos = sched->vessels[i].local_pos;
            }
            if (out_vel) {
                *out_vel = sched->vessels[i].local_vel;
            }
            if (out_lane) {
                *out_lane = sched->vessels[i].state.lane_type;
            }
            return DOM_LANE_OK;
        }
    }
    return DOM_LANE_NOT_FOUND;
}

int dom_lane_scheduler_get_aero_state(const dom_lane_scheduler *sched,
                                      u64 vessel_id,
                                      dom_vehicle_aero_state *out_state) {
    size_t i;
    if (!sched || vessel_id == 0ull || !out_state) {
        return DOM_LANE_INVALID_ARGUMENT;
    }
    for (i = 0u; i < sched->vessels.size(); ++i) {
        if (sched->vessels[i].id == vessel_id) {
            if (!sched->vessels[i].has_aero_props) {
                std::memset(out_state, 0, sizeof(*out_state));
                return DOM_LANE_NOT_IMPLEMENTED;
            }
            *out_state = sched->vessels[i].aero_state;
            return DOM_LANE_OK;
        }
    }
    return DOM_LANE_NOT_FOUND;
}

int dom_lane_scheduler_list_aero(const dom_lane_scheduler *sched,
                                 dom_lane_vessel_aero *out_list,
                                 u32 capacity,
                                 u32 *out_count) {
    size_t i;
    u32 count;
    if (!sched || !out_count) {
        return DOM_LANE_INVALID_ARGUMENT;
    }
    count = (u32)sched->vessels.size();
    *out_count = count;
    if (!out_list || capacity == 0u) {
        return DOM_LANE_OK;
    }
    if (capacity < count) {
        return DOM_LANE_ERR;
    }
    for (i = 0u; i < sched->vessels.size(); ++i) {
        const DomLaneVessel &v = sched->vessels[i];
        out_list[i].vessel_id = v.id;
        out_list[i].has_aero_props = v.has_aero_props ? 1u : 0u;
        out_list[i].aero_props = v.aero_props;
        out_list[i].aero_state = v.aero_state;
    }
    return DOM_LANE_OK;
}

int dom_lane_scheduler_set_aero_props(dom_lane_scheduler *sched,
                                      u64 vessel_id,
                                      const dom_vehicle_aero_props *props) {
    size_t i;
    if (!sched || vessel_id == 0ull || !props) {
        return DOM_LANE_INVALID_ARGUMENT;
    }
    if (dom_vehicle_aero_props_validate(props) != DOM_VEHICLE_AERO_OK) {
        return DOM_LANE_INVALID_ARGUMENT;
    }
    for (i = 0u; i < sched->vessels.size(); ++i) {
        if (sched->vessels[i].id == vessel_id) {
            sched->vessels[i].aero_props = *props;
            sched->vessels[i].has_aero_props = 1;
            return DOM_LANE_OK;
        }
    }
    return DOM_LANE_NOT_FOUND;
}

int dom_lane_scheduler_set_aero_state(dom_lane_scheduler *sched,
                                      u64 vessel_id,
                                      const dom_vehicle_aero_state *state) {
    size_t i;
    if (!sched || vessel_id == 0ull || !state) {
        return DOM_LANE_INVALID_ARGUMENT;
    }
    for (i = 0u; i < sched->vessels.size(); ++i) {
        if (sched->vessels[i].id == vessel_id) {
            if (!sched->vessels[i].has_aero_props) {
                return DOM_LANE_NOT_IMPLEMENTED;
            }
            sched->vessels[i].aero_state = *state;
            return DOM_LANE_OK;
        }
    }
    return DOM_LANE_NOT_FOUND;
}
