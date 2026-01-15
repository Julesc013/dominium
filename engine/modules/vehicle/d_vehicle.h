/*
FILE: source/domino/vehicle/d_vehicle.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / vehicle/d_vehicle
RESPONSIBILITY: Defines internal contract for `d_vehicle`; shared within its subsystem; does NOT define a public API (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (internal header).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
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
