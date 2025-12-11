/* Building proto definitions (compiled blueprints) - C89. */
#ifndef D_BUILD_PROTO_H
#define D_BUILD_PROTO_H

#include "domino/core/types.h"
#include "domino/core/d_tlv.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef u32 d_building_proto_id;

/* Building proto; geometry is contained in TLV payload, not exposed here. */
typedef struct d_proto_building {
    d_building_proto_id id;
    const char         *name;

    u16                 build_model_family; /* e.g. D_MODEL_FAMILY_BUILD */
    u16                 build_model_id;     /* behavior model id within family */

    d_tlv_blob          shell_data;        /* encoded grid/geometry; opaque to core */
    d_tlv_blob          foundation_profile;
    d_tlv_blob          extra;
} d_proto_building;

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* D_BUILD_PROTO_H */
