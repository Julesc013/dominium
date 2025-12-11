/* Structure/machine subsystem types (C89). */
#ifndef D_STRUCT_H
#define D_STRUCT_H

#include "domino/core/types.h"
#include "domino/core/fixed.h"
#include "domino/core/d_tlv.h"
#include "world/d_world.h"
#include "struct/d_struct_proto.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef u32 d_struct_instance_id;

typedef struct d_struct_instance {
    d_struct_instance_id id;
    d_structure_id       proto_id;

    q16_16 pos_x, pos_y, pos_z;
    q16_16 rot_yaw, rot_pitch, rot_roll;

    u32    chunk_id;
    u32    flags;

    /* Link to ECS entity if ECS exists; can be 0 if not yet integrated. */
    u32    entity_id;

    d_tlv_blob state;   /* machine state, process progress, etc. */
} d_struct_instance;

d_struct_instance_id d_struct_create(
    d_world       *w,
    d_structure_id proto_id,
    q16_16        x, q16_16 y, q16_16 z,
    q16_16        yaw
);

int d_struct_destroy(
    d_world             *w,
    d_struct_instance_id id
);

/* Subsystem registration hook */
void d_struct_init(void);

#ifdef __cplusplus
}
#endif

#endif /* D_STRUCT_H */
