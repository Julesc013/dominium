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
