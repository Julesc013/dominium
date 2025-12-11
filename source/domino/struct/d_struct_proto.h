/* Structure/machine prototype definitions (C89). */
#ifndef D_STRUCT_PROTO_H
#define D_STRUCT_PROTO_H

#include "domino/core/types.h"
#include "domino/core/d_tlv.h"
#include "domino/core/fixed.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef u32 d_structure_id;

#define DSTRUCT_MAX_PORTS    16
#define DSTRUCT_MAX_PROCS    16

typedef struct d_struct_port {
    u32   port_id;
    u16   kind;         /* ITEM, FLUID, ELECTRIC, MECHANICAL, PERSON, ENV_PORTAL, etc. */
    u16   dir_flags;    /* IN, OUT, BIDIR */
    q16_16 local_x, local_y, local_z;
    q16_16 local_nx, local_ny, local_nz;
    u32   media_mask;   /* ITEM_TYPES, FLUID_TYPES, etc. */
} d_struct_port;

typedef struct d_proto_structure {
    d_structure_id id;
    const char    *name;

    q16_16        footprint_x;
    q16_16        footprint_y;
    q16_16        height;

    u32           tags;     /* MACHINE, SUPPORT, FOUNDATION, etc. */

    d_struct_port ports[DSTRUCT_MAX_PORTS];
    u16           port_count;

    u32           allowed_process_ids[DSTRUCT_MAX_PROCS];
    u16           allowed_process_count;

    d_tlv_blob    extra;    /* for UI, models, etc. */
} d_proto_structure;

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* D_STRUCT_PROTO_H */
