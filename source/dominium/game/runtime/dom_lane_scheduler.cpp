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

#include "runtime/dom_body_registry.h"
#include "runtime/dom_game_runtime.h"

extern "C" {
#include "domino/core/spacetime.h"
}

namespace {

struct DomLaneVessel {
    u64 id;
    dom_lane_state state;
    dom_orbit_state orbit;
    SpacePos local_pos;
    SpacePos local_vel;
    int has_orbit;
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

static dom_body_id default_body_id(void) {
    dom_body_id id = 0ull;
    (void)dom_id_hash64("earth", 5u, &id);
    return id;
}

static bool compute_orbital_altitude(const DomLaneVessel &v,
                                     const dom_body_registry *bodies,
                                     q48_16 *out_altitude) {
    dom_body_info info;
    q48_16 radius = 0;
    if (!out_altitude || !v.has_orbit || !bodies) {
        return false;
    }
    if (dom_body_registry_get(bodies, v.orbit.primary_body_id, &info) != DOM_BODY_REGISTRY_OK) {
        return false;
    }
    radius = info.radius_m;
    *out_altitude = d_q48_16_sub(v.orbit.semi_major_axis_m, radius);
    return true;
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
    sched->max_warp_factor = 8u;
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
    for (i = 0u; i < sched->vessels.size(); ++i) {
        if (sched->vessels[i].id == desc->vessel_id) {
            sched->vessels[i].orbit = desc->orbit;
            sched->vessels[i].local_pos = desc->local_pos;
            sched->vessels[i].local_vel = desc->local_vel;
            sched->vessels[i].state.lane_type = desc->lane_type;
            sched->vessels[i].has_orbit = 1;
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
    entry.has_orbit = 1;
    entry.landed = 0;
    entry.landed_body_id = 0ull;
    entry.landed_latlong.lat_turns = 0;
    entry.landed_latlong.lon_turns = 0;
    entry.landed_altitude_m = 0;
    std::memset(&entry.landed_pos, 0, sizeof(entry.landed_pos));
    sched->vessels.push_back(entry);
    std::sort(sched->vessels.begin(), sched->vessels.end(), vessel_id_less);
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
    int result = DOM_LANE_OK;
    if (!sched) {
        return DOM_LANE_INVALID_ARGUMENT;
    }
    if (rt) {
        bodies = static_cast<const dom_body_registry *>(dom_game_runtime_body_registry(rt));
    }

    if (!sched->bubble_active && sched->active_vessel_id != 0ull) {
        for (i = 0u; i < sched->vessels.size(); ++i) {
            if (sched->vessels[i].id == sched->active_vessel_id) {
                if (sched->vessels[i].state.lane_type == DOM_LANE_DOCKED_LANDED) {
                    sched->bubble_active = 1;
                    sched->bubble.id = 1u;
                    sched->bubble.center_vessel_id = sched->active_vessel_id;
                    sched->bubble.enter_radius_m = default_enter_radius();
                    sched->bubble.exit_radius_m = default_exit_radius();
                    sched->bubble.radius_m = sched->bubble.exit_radius_m;
                    sched->bubble_body_id = sched->vessels[i].landed_body_id;
                    if (sched->bubble_body_id == 0ull) {
                        sched->bubble_body_id = default_body_id();
                    }
                    sched->bubble_center = sched->vessels[i].landed_latlong;
                    sched->bubble_has_center = 1;
                    break;
                }
                q48_16 altitude = 0;
                if (compute_orbital_altitude(sched->vessels[i], bodies, &altitude)) {
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
                q48_16 altitude = 0;
                if (compute_orbital_altitude(sched->vessels[i], bodies, &altitude)) {
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
    return result;
}

u32 dom_lane_scheduler_max_warp(const dom_lane_scheduler *sched) {
    if (!sched) {
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
