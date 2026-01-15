/*
FILE: source/dominium/game/runtime/dom_vehicle_aero.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / game/runtime/vehicle_aero
RESPONSIBILITY: Deterministic aero properties/state and drag/heating update helpers.
ALLOWED DEPENDENCIES: `include/domino/**`, `source/dominium/**`.
FORBIDDEN DEPENDENCIES: OS headers; floating-point math.
*/
#ifndef DOM_VEHICLE_AERO_H
#define DOM_VEHICLE_AERO_H

#include "domino/core/fixed.h"
#include "domino/dorbit.h"
#include "runtime/dom_media_provider.h"

#ifdef __cplusplus
extern "C" {
#endif

enum {
    DOM_VEHICLE_AERO_OK = 0,
    DOM_VEHICLE_AERO_ERR = -1,
    DOM_VEHICLE_AERO_INVALID_ARGUMENT = -2,
    DOM_VEHICLE_AERO_INVALID_DATA = -3
};

typedef struct dom_vehicle_aero_props {
    q16_16 mass_kg_q16;
    q16_16 drag_area_cda_q16;
    q16_16 heat_coeff_q16;
    q16_16 max_heat_q16;
    u32 has_max_heat;
} dom_vehicle_aero_props;

typedef struct dom_vehicle_aero_state {
    q16_16 heat_accum_q16;
    q16_16 last_heating_rate_q16;
    q16_16 last_drag_accel_q16;
} dom_vehicle_aero_state;

int dom_vehicle_aero_props_validate(const dom_vehicle_aero_props *props);
void dom_vehicle_aero_state_reset(dom_vehicle_aero_state *state);

int dom_vehicle_aero_apply(const dom_vehicle_aero_props *props,
                           const dom_media_sample *sample,
                           SpacePos *inout_vel,
                           dom_vehicle_aero_state *state);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOM_VEHICLE_AERO_H */
