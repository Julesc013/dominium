/* Generic movers running along spline instances (C89). */
#ifndef D_TRANS_MOVER_H
#define D_TRANS_MOVER_H

#include "domino/core/types.h"
#include "domino/core/fixed.h"
#include "world/d_world.h"
#include "trans/d_trans_spline.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef u32 d_mover_id;

typedef enum d_mover_kind_e {
    D_MOVER_KIND_NONE = 0,
    D_MOVER_KIND_ITEM,
    D_MOVER_KIND_CONTAINER,
    D_MOVER_KIND_VEHICLE,
    D_MOVER_KIND_FLUID_PACKET
} d_mover_kind;

typedef struct d_mover_s {
    d_mover_id     id;
    d_mover_kind   kind;
    d_spline_id    spline_id;
    q16_16         param;       /* position along spline [0,1] */
    q16_16         speed_param; /* param units per tick */
    q16_16         size_param;  /* normalized size/spacing */

    /* Payload representation is abstracted; summary only. */
    u32            payload_id;     /* item/vehicle/fluid/container prototype id */
    u32            payload_count;  /* item count or volume units */
} d_mover;

d_mover_id d_trans_mover_create(d_world *w, const d_mover *init);
int        d_trans_mover_destroy(d_world *w, d_mover_id id);

int d_trans_mover_get(const d_world *w, d_mover_id id, d_mover *out);
int d_trans_mover_update(d_world *w, const d_mover *m);

/* Iteration helpers for UI/debug. */
u32 d_trans_mover_count(const d_world *w);
int d_trans_mover_get_by_index(const d_world *w, u32 index, d_mover *out);

/* Called from d_trans_tick to advance movers and handle transitions. */
void d_trans_mover_tick(d_world *w, u32 ticks);

#ifdef __cplusplus
}
#endif

#endif /* D_TRANS_MOVER_H */

