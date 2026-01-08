/*
FILE: source/dominium/game/runtime/dom_lane_scheduler.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / game/runtime/lane_scheduler
RESPONSIBILITY: Lane scheduler for orbital/local/docked transitions and bubble gating.
ALLOWED DEPENDENCIES: `include/domino/**`, `source/dominium/**`, C++98 STL.
FORBIDDEN DEPENDENCIES: OS headers; floating-point math.
*/
#ifndef DOM_LANE_SCHEDULER_H
#define DOM_LANE_SCHEDULER_H

#include "domino/core/fixed.h"
#include "domino/core/spacetime.h"
#include "runtime/dom_orbit_lane.h"
#include "runtime/dom_surface_topology.h"

#ifdef __cplusplus
extern "C" {
#endif

struct dom_game_runtime;

enum {
    DOM_LANE_OK = 0,
    DOM_LANE_ERR = -1,
    DOM_LANE_INVALID_ARGUMENT = -2,
    DOM_LANE_NOT_FOUND = -3,
    DOM_LANE_TRANSITION_REFUSED = -4,
    DOM_LANE_BUBBLE_LIMIT = -5,
    DOM_LANE_NOT_IMPLEMENTED = -6
};

typedef enum dom_lane_type {
    DOM_LANE_ORBITAL = 0,
    DOM_LANE_APPROACH = 1,
    DOM_LANE_LOCAL_KINEMATIC = 2,
    DOM_LANE_DOCKED_LANDED = 3
} dom_lane_type;

typedef struct dom_lane_state {
    dom_lane_type lane_type;
    dom_tick since_tick;
    u32 active_bubble_id;
} dom_lane_state;

typedef struct dom_activation_bubble {
    u32 id;
    u64 center_vessel_id;
    q48_16 radius_m;
    q48_16 enter_radius_m;
    q48_16 exit_radius_m;
} dom_activation_bubble;

typedef struct dom_lane_vessel_desc {
    u64 vessel_id;
    dom_orbit_state orbit;
    SpacePos local_pos;
    SpacePos local_vel;
    dom_lane_type lane_type;
} dom_lane_vessel_desc;

typedef struct dom_lane_scheduler dom_lane_scheduler;

dom_lane_scheduler *dom_lane_scheduler_create(void);
void dom_lane_scheduler_destroy(dom_lane_scheduler *sched);
int dom_lane_scheduler_init(dom_lane_scheduler *sched);

int dom_lane_scheduler_register_vessel(dom_lane_scheduler *sched,
                                       const dom_lane_vessel_desc *desc);
int dom_lane_scheduler_request_transition(dom_lane_scheduler *sched,
                                          u64 vessel_id,
                                          dom_lane_type target_lane);
int dom_lane_scheduler_get_state(const dom_lane_scheduler *sched,
                                 u64 vessel_id,
                                 dom_lane_state *out_state);
int dom_lane_scheduler_set_active_vessel(dom_lane_scheduler *sched,
                                         u64 vessel_id);
int dom_lane_scheduler_update(dom_lane_scheduler *sched,
                              const struct dom_game_runtime *rt,
                              dom_tick tick);
u32 dom_lane_scheduler_max_warp(const dom_lane_scheduler *sched);

int dom_lane_scheduler_get_bubble(const dom_lane_scheduler *sched,
                                  dom_activation_bubble *out_bubble,
                                  int *out_active,
                                  dom_body_id *out_body_id,
                                  dom_topo_latlong_q16 *out_center);

int dom_lane_scheduler_landing_attach(dom_lane_scheduler *sched,
                                      const dom_body_registry *bodies,
                                      u64 vessel_id,
                                      dom_body_id body_id,
                                      const dom_topo_latlong_q16 *latlong,
                                      q48_16 altitude_m);
int dom_lane_scheduler_landing_detach(dom_lane_scheduler *sched,
                                      u64 vessel_id,
                                      dom_lane_type next_lane);
int dom_lane_scheduler_get_landing(const dom_lane_scheduler *sched,
                                   u64 vessel_id,
                                   dom_body_id *out_body_id,
                                   dom_topo_latlong_q16 *out_latlong,
                                   q48_16 *out_altitude_m,
                                   dom_posseg_q16 *out_pos);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOM_LANE_SCHEDULER_H */
