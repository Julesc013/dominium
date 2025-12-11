/* Transport spline profile prototypes (C89). */
#ifndef D_TRANS_PROTO_H
#define D_TRANS_PROTO_H

#include "domino/core/types.h"
#include "domino/core/d_tlv.h"
#include "domino/core/fixed.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef u32 d_spline_profile_id;

typedef struct d_proto_spline_profile {
    d_spline_profile_id id;
    const char         *name;

    u16                 kind;            /* BELT, RAIL, ROAD, PIPE, CABLE, CHUTE, etc. */
    q16_16              gauge;           /* width or bore */
    q16_16              default_speed;
    q16_16              capacity_per_m;

    u32                 media_mask;      /* ITEMS, BULK, FLUIDS, PEOPLE, POWER, etc. */

    d_tlv_blob          build_rules;     /* cut/fill/bridge/tunnel logic */
    d_tlv_blob          extra;
} d_proto_spline_profile;

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* D_TRANS_PROTO_H */
