/* Vehicle/module prototype definitions (C89). */
#ifndef D_VEHICLE_PROTO_H
#define D_VEHICLE_PROTO_H

#include "domino/core/types.h"
#include "domino/core/d_tlv.h"
#include "domino/core/fixed.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef u32 d_vehicle_proto_id;
typedef u32 d_module_proto_id;

typedef struct d_proto_module {
    d_module_proto_id id;
    const char       *name;

    u32               module_kind;  /* ENGINE, WHEELSET, HULL, TURRET, GUN, ARMOR_PLATE, etc. */

    d_tlv_blob        params;       /* engine curves, armor ratings, etc. */
    d_tlv_blob        extra;
} d_proto_module;

#define DVEH_MAX_MODULES  32

typedef struct d_proto_vehicle {
    d_vehicle_proto_id id;
    const char        *name;

    u32                source_blueprint_id;  /* d_blueprint_id or 0 if built-in */

    q16_16             total_mass;
    q16_16             inertia_xx, inertia_yy, inertia_zz;
    q16_16             drag_coeff;

    q16_16             max_engine_power;
    q16_16             max_speed;
    q16_16             tractive_effort;
    u16                traction_mode;        /* WHEELED, TRACKED, RAIL, AIR, etc. */

    u16                module_count;
    struct {
        d_module_proto_id module_id;
        d_tlv_blob        module_state_defaults;
    } modules[DVEH_MAX_MODULES];

    d_tlv_blob         cargo_layout;
    d_tlv_blob         fuel_layout;

    d_tlv_blob         extra;
} d_proto_vehicle;

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* D_VEHICLE_PROTO_H */
