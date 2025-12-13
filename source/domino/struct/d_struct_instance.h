/* Structure instance state helpers (C89). */
#ifndef D_STRUCT_INSTANCE_H
#define D_STRUCT_INSTANCE_H

#include "domino/core/types.h"
#include "domino/core/fixed.h"
#include "domino/core/d_tlv.h"
#include "content/d_content.h"
#include "world/d_world.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef u32 d_struct_instance_id;

typedef struct d_struct_inventory_s {
    u32 item_id;
    u32 count;
} d_struct_inventory;

typedef struct d_struct_instance {
    d_struct_instance_id id;
    d_structure_proto_id proto_id;

    q16_16 pos_x, pos_y, pos_z;
    q16_16 rot_yaw, rot_pitch, rot_roll;

    u32    chunk_id;
    u32    flags;

    u32    entity_id;

    d_struct_inventory inventory;

    d_tlv_blob state;   /* machine state, process progress, etc. */
} d_struct_instance;

void d_struct_inventory_clear(d_struct_inventory *inv);
int  d_struct_inventory_add(d_struct_inventory *inv, u32 item_id, u32 count);

#ifdef __cplusplus
}
#endif

#endif /* D_STRUCT_INSTANCE_H */
