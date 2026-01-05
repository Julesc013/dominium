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

#include "domino/core/spacetime.h"
#include "domino/dorbit.h"

#ifdef __cplusplus
extern "C" {
#endif

enum {
    DOM_ORBIT_LANE_OK = 0,
    DOM_ORBIT_LANE_ERR = -1,
    DOM_ORBIT_LANE_INVALID_ARGUMENT = -2,
    DOM_ORBIT_LANE_NOT_IMPLEMENTED = -3
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

typedef struct dom_orbit_posvel {
    SpacePos pos;
    SpacePos vel;
} dom_orbit_posvel;

typedef struct dom_orbit_state {
    OrbitComponent elements;
    dom_tick epoch_tick;
} dom_orbit_state;

int dom_orbit_eval_state(const dom_orbit_state *orbit,
                         dom_tick tick,
                         dom_orbit_posvel *out_posvel);

int dom_orbit_next_event(const dom_orbit_state *orbit,
                         dom_tick tick,
                         dom_orbit_event_kind kind,
                         dom_tick *out_tick);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOM_ORBIT_LANE_H */
