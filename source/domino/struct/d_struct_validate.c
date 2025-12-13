#include <stdio.h>
#include <string.h>

#include "content/d_content.h"
#include "content/d_content_extra.h"
#include "core/d_tlv_kv.h"
#include "struct/d_struct.h"

static int dstruct_validate_volume_record(const d_tlv_blob *rec, q16_16 *out_min, q16_16 *out_max) {
    u32 offset;
    u32 tag;
    d_tlv_blob payload;
    int rc;
    q16_16 min_x = 0, min_y = 0, min_z = 0;
    q16_16 max_x = 0, max_y = 0, max_z = 0;

    if (!rec) {
        return -1;
    }

    offset = 0u;
    while ((rc = d_tlv_kv_next(rec, &offset, &tag, &payload)) == 0) {
        switch (tag) {
        case D_TLV_ENV_VOLUME_MIN_X: (void)d_tlv_kv_read_q16_16(&payload, &min_x); break;
        case D_TLV_ENV_VOLUME_MIN_Y: (void)d_tlv_kv_read_q16_16(&payload, &min_y); break;
        case D_TLV_ENV_VOLUME_MIN_Z: (void)d_tlv_kv_read_q16_16(&payload, &min_z); break;
        case D_TLV_ENV_VOLUME_MAX_X: (void)d_tlv_kv_read_q16_16(&payload, &max_x); break;
        case D_TLV_ENV_VOLUME_MAX_Y: (void)d_tlv_kv_read_q16_16(&payload, &max_y); break;
        case D_TLV_ENV_VOLUME_MAX_Z: (void)d_tlv_kv_read_q16_16(&payload, &max_z); break;
        default: break;
        }
    }

    if (max_x < min_x || max_y < min_y || max_z < min_z) {
        return -1;
    }
    if (out_min) {
        out_min[0] = min_x; out_min[1] = min_y; out_min[2] = min_z;
    }
    if (out_max) {
        out_max[0] = max_x; out_max[1] = max_y; out_max[2] = max_z;
    }
    return 0;
}

static int dstruct_validate_edge_record(const d_tlv_blob *rec, u16 vol_count) {
    u32 offset;
    u32 tag;
    d_tlv_blob payload;
    int rc;
    u16 a = 0u;
    u16 b = 0u;
    q16_16 gas_k = (q16_16)0;
    q16_16 heat_k = (q16_16)0;

    if (!rec) {
        return -1;
    }

    offset = 0u;
    while ((rc = d_tlv_kv_next(rec, &offset, &tag, &payload)) == 0) {
        switch (tag) {
        case D_TLV_ENV_EDGE_A: (void)d_tlv_kv_read_u16(&payload, &a); break;
        case D_TLV_ENV_EDGE_B: (void)d_tlv_kv_read_u16(&payload, &b); break;
        case D_TLV_ENV_EDGE_GAS_K: (void)d_tlv_kv_read_q16_16(&payload, &gas_k); break;
        case D_TLV_ENV_EDGE_HEAT_K: (void)d_tlv_kv_read_q16_16(&payload, &heat_k); break;
        default: break;
        }
    }

    if (a == 0u || a > vol_count) {
        return -1;
    }
    if (b > vol_count) {
        return -1;
    }
    if (b != 0u && b == a) {
        return -1;
    }
    if (gas_k < 0 || gas_k > d_q16_16_from_int(1)) {
        return -1;
    }
    if (heat_k < 0 || heat_k > d_q16_16_from_int(1)) {
        return -1;
    }
    return 0;
}

static int dstruct_validate_proto(const d_proto_structure *proto) {
    u32 offset;
    u32 tag;
    d_tlv_blob payload;
    int rc;
    u16 vol_count = 0u;

    if (!proto) {
        return -1;
    }

    if (!proto->layout.ptr || proto->layout.len == 0u) {
        return 0;
    }

    offset = 0u;
    while ((rc = d_tlv_kv_next(&proto->layout, &offset, &tag, &payload)) == 0) {
        if (tag == D_TLV_ENV_VOLUME) {
            if (dstruct_validate_volume_record(&payload, (q16_16 *)0, (q16_16 *)0) != 0) {
                return -1;
            }
            if (vol_count < 0xFFFFu) {
                vol_count += 1u;
            }
        }
    }
    if (rc < 0) {
        return -1;
    }

    if (vol_count == 0u) {
        return 0;
    }

    offset = 0u;
    while ((rc = d_tlv_kv_next(&proto->layout, &offset, &tag, &payload)) == 0) {
        if (tag == D_TLV_ENV_EDGE) {
            if (dstruct_validate_edge_record(&payload, vol_count) != 0) {
                return -1;
            }
        }
    }
    if (rc < 0) {
        return -1;
    }

    return 0;
}

int d_struct_validate(const d_world *w) {
    u32 count;
    u32 i;
    (void)w;

    count = d_content_structure_count();
    for (i = 0u; i < count; ++i) {
        const d_proto_structure *p = d_content_get_structure_by_index(i);
        if (p && dstruct_validate_proto(p) != 0) {
            fprintf(stderr, "struct validate: invalid volume layout in proto %u\n", (unsigned)p->id);
            return -1;
        }
    }

    return 0;
}
