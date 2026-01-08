/*
FILE: source/dominium/game/runtime/dom_orbit_lane.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / game/runtime/orbit_lane
RESPONSIBILITY: Orbit lane scaffolding and analytic event API (stubbed).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/dominium/**`, C++98 STL.
FORBIDDEN DEPENDENCIES: OS headers; floating-point math.
*/
#ifndef DOM_ORBIT_LANE_H
#define DOM_ORBIT_LANE_H

#include "domino/core/fixed.h"
#include "domino/core/spacetime.h"
#include "domino/dorbit.h"

#ifdef __cplusplus
extern "C" {
#endif

enum {
    DOM_ORBIT_LANE_OK = 0,
    DOM_ORBIT_LANE_ERR = -1,
    DOM_ORBIT_LANE_INVALID_ARGUMENT = -2,
    DOM_ORBIT_LANE_NOT_IMPLEMENTED = -3,
    DOM_ORBIT_LANE_INVALID_STATE = -4
};

typedef enum dom_orbit_mode {
    DOM_ORBIT_MODE_ORBITAL = 0,
    DOM_ORBIT_MODE_LOCAL_PHYS = 1,
    DOM_ORBIT_MODE_DOCKED = 2,
    DOM_ORBIT_MODE_LANDED = 3
} dom_orbit_mode;

typedef enum dom_orbit_event_kind {
    DOM_ORBIT_EVENT_PERIAPSIS = 0,
    DOM_ORBIT_EVENT_APOAPSIS = 1,
    DOM_ORBIT_EVENT_SOI_ENTER = 2,
    DOM_ORBIT_EVENT_SOI_EXIT = 3,
    DOM_ORBIT_EVENT_ASC_NODE = 4,
    DOM_ORBIT_EVENT_DESC_NODE = 5
} dom_orbit_event_kind;

typedef u32 dom_orbit_event_mask;

#define DOM_ORBIT_EVENT_MASK(kind) ((dom_orbit_event_mask)(1u << (kind)))

typedef struct dom_orbit_posvel {
    SpacePos pos;
    SpacePos vel;
} dom_orbit_posvel;

typedef struct dom_orbit_state {
    u64 primary_body_id;
    u64 mu_m3_s2;
    q48_16 semi_major_axis_m;
    q16_16 eccentricity;
    Turn inclination;
    Turn lon_ascending_node;
    Turn arg_periapsis;
    Turn mean_anomaly_at_epoch;
    dom_tick epoch_tick;
    u32 ups;
    q48_16 soi_radius_m;
} dom_orbit_state;

typedef struct dom_orbit_maneuver {
    dom_tick trigger_tick;
    SpacePos delta_v;
    u64 frame_id;
} dom_orbit_maneuver;

int dom_orbit_state_validate(const dom_orbit_state *orbit);
int dom_orbit_elements_normalize(dom_orbit_state *orbit);
int dom_orbit_period_ticks(const dom_orbit_state *orbit, dom_tick *out_period_ticks);

int dom_orbit_eval_state(const dom_orbit_state *orbit,
                         dom_tick tick,
                         dom_orbit_posvel *out_posvel);

int dom_orbit_apply_maneuver(dom_orbit_state *orbit,
                             const dom_orbit_maneuver *maneuver);

int dom_orbit_next_event(const dom_orbit_state *orbit,
                         dom_tick tick,
                         dom_orbit_event_kind kind,
                         dom_tick *out_tick);

int dom_orbit_next_any_event(const dom_orbit_state *orbit,
                             dom_tick tick,
                             dom_orbit_event_mask mask,
                             dom_orbit_event_kind *out_kind,
                             dom_tick *out_tick);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOM_ORBIT_LANE_H */
