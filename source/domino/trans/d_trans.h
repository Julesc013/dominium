/* Transport subsystem types (C89). */
#ifndef D_TRANS_H
#define D_TRANS_H

#include "domino/core/types.h"
#include "domino/core/d_tlv.h"
#include "domino/core/fixed.h"
#include "world/d_world.h"
#include "trans/d_trans_proto.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef u32 d_spline_instance_id;

typedef struct d_spline_knot {
    q16_16 x, y, z;
    q16_16 handle_in_x, handle_in_y, handle_in_z;
    q16_16 handle_out_x, handle_out_y, handle_out_z;
} d_spline_knot;

typedef struct d_spline_instance {
    d_spline_instance_id id;
    d_spline_profile_id  profile_id;

    u32                  chunk_id_start;
    u32                  chunk_id_end;

    u16                  knot_count;
    d_spline_knot       *knots;

    d_tlv_blob           state; /* transport-specific state; e.g. items/fluid packets (for now leave empty) */
} d_spline_instance;

/* Create a spline instance */
d_spline_instance_id d_trans_create_spline(
    d_world              *w,
    d_spline_profile_id   profile_id,
    const d_spline_knot  *knots,
    u16                   knot_count
);

int d_trans_destroy_spline(
    d_world               *w,
    d_spline_instance_id   id
);

/* Subsystem registration hook */
void d_trans_init(void);

#ifdef __cplusplus
}
#endif

#endif /* D_TRANS_H */
