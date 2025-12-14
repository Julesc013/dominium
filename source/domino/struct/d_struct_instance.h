/* Structure instance state helpers (C89). */
#ifndef D_STRUCT_INSTANCE_H
#define D_STRUCT_INSTANCE_H

#include "domino/core/types.h"
#include "domino/core/fixed.h"
#include "domino/core/d_tlv.h"
#include "core/d_container_state.h"
#include "core/d_org.h"
#include "content/d_content.h"
#include "world/d_world.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef u32 d_struct_instance_id;

typedef struct d_machine_runtime_s {
    d_process_id active_process_id;
    q16_16       progress;    /* 0..process.base_duration */
    u16          state_flags; /* MACHINE_IDLE, MACHINE_ACTIVE, MACHINE_BLOCKED, etc. */
} d_machine_runtime;

enum {
    D_MACHINE_FLAG_IDLE    = 1u << 0,
    D_MACHINE_FLAG_ACTIVE  = 1u << 1,
    D_MACHINE_FLAG_BLOCKED = 1u << 2,
    D_MACHINE_FLAG_POLICY_BLOCKED = 1u << 3
};

typedef struct d_struct_instance {
    d_struct_instance_id id;
    d_structure_proto_id proto_id;
    d_org_id             owner_org;

    q16_16 pos_x, pos_y, pos_z;
    q16_16 rot_yaw, rot_pitch, rot_roll;

    u32    chunk_id;
    u32    flags;

    u32    entity_id;

    d_container_state inv_in;
    d_container_state inv_out;

    d_machine_runtime machine;

    d_tlv_blob state;   /* machine state, process progress, etc. */
} d_struct_instance;

#ifdef __cplusplus
}
#endif

#endif /* D_STRUCT_INSTANCE_H */
