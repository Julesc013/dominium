/*
FILE: source/domino/vehicle/d_vehicle_validate.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / vehicle/d_vehicle_validate
RESPONSIBILITY: Implements `d_vehicle_validate`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include <stdio.h>

#include "content/d_content.h"
#include "content/d_content_extra.h"
#include "core/d_tlv_kv.h"
#include "vehicle/d_vehicle.h"

static int dveh_validate_volume_record(const d_tlv_blob *rec) {
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
    return 0;
}

static int dveh_validate_edge_record(const d_tlv_blob *rec, u16 vol_count) {
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

static int dveh_validate_proto(const d_proto_vehicle *proto) {
    u32 offset;
    u32 tag;
    d_tlv_blob payload;
    int rc;
    u16 vol_count = 0u;

    if (!proto) {
        return -1;
    }
    if (!proto->params.ptr || proto->params.len == 0u) {
        return 0;
    }

    offset = 0u;
    while ((rc = d_tlv_kv_next(&proto->params, &offset, &tag, &payload)) == 0) {
        if (tag == D_TLV_ENV_VOLUME) {
            if (dveh_validate_volume_record(&payload) != 0) {
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
    while ((rc = d_tlv_kv_next(&proto->params, &offset, &tag, &payload)) == 0) {
        if (tag == D_TLV_ENV_EDGE) {
            if (dveh_validate_edge_record(&payload, vol_count) != 0) {
                return -1;
            }
        }
    }
    if (rc < 0) {
        return -1;
    }

    return 0;
}

int d_vehicle_validate(const d_world *w) {
    u32 count;
    u32 i;
    (void)w;

    count = d_content_vehicle_count();
    for (i = 0u; i < count; ++i) {
        const d_proto_vehicle *p = d_content_get_vehicle_by_index(i);
        if (p && dveh_validate_proto(p) != 0) {
            fprintf(stderr, "vehicle validate: invalid volume params in proto %u\n", (unsigned)p->id);
            return -1;
        }
    }
    return 0;
}
