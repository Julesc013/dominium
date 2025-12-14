/* Vehicle subsystem types (C89). */
#ifndef D_VEHICLE_H
#define D_VEHICLE_H

#include "domino/core/types.h"
#include "domino/core/fixed.h"
#include "domino/core/d_tlv.h"
#include "core/d_org.h"
#include "world/d_world.h"
#include "vehicle/d_vehicle_proto.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef u32 d_vehicle_instance_id;

typedef struct d_vehicle_instance {
    d_vehicle_instance_id id;
    d_vehicle_proto_id    proto_id;
    d_org_id              owner_org;

    q16_16 pos_x, pos_y, pos_z;
    q16_16 vel_x, vel_y, vel_z;
    q16_16 rot_yaw, rot_pitch, rot_roll;

    u32    chunk_id;
    u32    flags;

    /* Link to ECS or physics proxy; for now store entity id. */
    u32    entity_id;

    d_tlv_blob state;   /* fuel state, cargo contents, etc. */
} d_vehicle_instance;

d_vehicle_instance_id d_vehicle_create(
    d_world             *w,
    d_vehicle_proto_id   proto_id,
    q16_16              x, q16_16 y, q16_16 z
);

int d_vehicle_destroy(
    d_world               *w,
    d_vehicle_instance_id  id
);

/* Subsystem registration hook */
void d_vehicle_init(void);
int d_vehicle_validate(const d_world *w);

#ifdef __cplusplus
}
#endif

#endif /* D_VEHICLE_H */
