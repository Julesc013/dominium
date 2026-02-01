/*
FILE: source/domino/vehicle/d_vehicle_model.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / vehicle/d_vehicle_model
RESPONSIBILITY: Defines internal contract for `d_vehicle_model`; shared within its subsystem; does NOT define a public API (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/specs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (internal header).
EXTENSION POINTS: Extend via public headers and relevant `docs/specs/SPEC_*.md` without cross-layer coupling.
*/
/* Vehicle model vtable (C89). */
#ifndef D_VEHICLE_MODEL_H
#define D_VEHICLE_MODEL_H

#include "domino/core/types.h"
#include "world/d_world.h"
#include "vehicle/d_vehicle.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct dveh_model_vtable {
    u16 model_id; /* within D_MODEL_FAMILY_VEH */

    void (*tick_vehicle)(
        d_world            *w,
        d_vehicle_instance *veh,
        u32                 ticks
    );
} dveh_model_vtable;

int dveh_register_model(const dveh_model_vtable *vt);

#ifdef __cplusplus
}
#endif

#endif /* D_VEHICLE_MODEL_H */
