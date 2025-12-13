/* Building subsystem types (C89). */
#ifndef D_BUILD_H
#define D_BUILD_H

#include "domino/core/types.h"
#include "domino/core/fixed.h"
#include "domino/core/d_tlv.h"
#include "world/d_world.h"
#include "build/d_build_proto.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef u32 d_building_instance_id;

typedef struct d_building_instance {
    d_building_instance_id id;
    d_building_proto_id    proto_id;

    q16_16  pos_x, pos_y, pos_z;
    q16_16  rot_yaw, rot_pitch, rot_roll;

    u32     chunk_id;  /* owning chunk; or derive from pos */
    u32     flags;     /* ACTIVE, UNDER_CONSTRUCTION, etc. */

    d_tlv_blob state;  /* future per-building state (e.g. custom zones) */
} d_building_instance;

/* Create/destroy building instances in a world. */
d_building_instance_id d_build_create(
    d_world             *w,
    d_building_proto_id  proto_id,
    q16_16               x, q16_16 y, q16_16 z,
    q16_16               yaw
);

int d_build_destroy(
    d_world              *w,
    d_building_instance_id id
);

/* Subsystem registration hook */
void d_build_init(void);
int d_build_validate(const d_world *w);

#ifdef __cplusplus
}
#endif

#endif /* D_BUILD_H */
