/*
FILE: source/domino/struct/d_struct_blueprint.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / struct/d_struct_blueprint
RESPONSIBILITY: Implements `d_struct_blueprint`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include "struct/d_struct_blueprint.h"

#include <string.h>
#include "content/d_content_extra.h"
#include "struct/d_struct.h"
#include "struct/d_struct_instance.h"

static int d_struct_bp_next(const d_tlv_blob *blob, u32 *offset, u32 *tag, d_tlv_blob *payload) {
    u32 remaining;
    u32 len;
    if (!blob || !offset || !tag || !payload) {
        return -1;
    }
    if (*offset >= blob->len) {
        return 1;
    }
    remaining = blob->len - *offset;
    if (remaining < 8u) {
        return -1;
    }
    memcpy(tag, blob->ptr + *offset, sizeof(u32));
    memcpy(&len, blob->ptr + *offset + 4u, sizeof(u32));
    *offset += 8u;
    if (len > blob->len - *offset) {
        return -1;
    }
    payload->ptr = blob->ptr + *offset;
    payload->len = len;
    *offset += len;
    return 0;
}

int d_struct_spawn_blueprint(
    d_world                 *w,
    const d_proto_blueprint *bp,
    q16_16                   x,
    q16_16                   y,
    q16_16                   z
) {
    u32 offset = 0u;
    u32 tag;
    d_tlv_blob payload;
    d_structure_proto_id proto_id = 0u;

    if (!w || !bp) {
        return -1;
    }
    while (1) {
        int rc = d_struct_bp_next(&bp->contents, &offset, &tag, &payload);
        if (rc == 1) {
            break;
        }
        if (rc != 0) {
            return -1;
        }
        if (tag == D_TLV_BLUEPRINT_STRUCTURE_PROTO) {
            if (payload.len >= sizeof(d_structure_proto_id) && payload.ptr) {
                memcpy(&proto_id, payload.ptr, sizeof(d_structure_proto_id));
                break;
            }
        }
    }
    if (proto_id == 0u) {
        return -1;
    }

    {
        d_struct_instance inst;
        memset(&inst, 0, sizeof(inst));
        inst.proto_id = proto_id;
        inst.pos_x = x;
        inst.pos_y = y;
        inst.pos_z = z;
        inst.rot_yaw = d_q16_16_from_int(0);
        inst.rot_pitch = d_q16_16_from_int(0);
        inst.rot_roll = d_q16_16_from_int(0);
        return (int)d_struct_spawn(w, &inst);
    }
}
