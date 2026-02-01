/*
FILE: source/domino/world/d_litho_validate.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / world/d_litho_validate
RESPONSIBILITY: Implements `d_litho_validate`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/specs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/specs/SPEC_*.md` without cross-layer coupling.
*/
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "core/d_serialize_tags.h"
#include "core/d_tlv_kv.h"
#include "world/d_litho.h"
#include "world/d_serialize.h"

static int dlitho_validate_chunk_payload(const d_tlv_blob *payload) {
    const unsigned char *ptr;
    u32 remaining;
    u32 col_count;
    u32 i;

    if (!payload || payload->len == 0u) {
        return 0;
    }
    if (!payload->ptr || payload->len < 4u) {
        return -1;
    }

    ptr = payload->ptr;
    remaining = payload->len;

    memcpy(&col_count, ptr, sizeof(u32));
    ptr += 4u;
    remaining -= 4u;

    if (col_count != (D_LITHO_GRID_RES * D_LITHO_GRID_RES)) {
        return -1;
    }

    for (i = 0u; i < col_count; ++i) {
        u16 lc;
        u32 l;
        u32 need;
        if (remaining < sizeof(u16)) {
            return -1;
        }
        memcpy(&lc, ptr, sizeof(u16));
        ptr += sizeof(u16);
        remaining -= sizeof(u16);

        if (lc > D_LITHO_MAX_LAYERS) {
            return -1;
        }

        need = (u32)D_LITHO_MAX_LAYERS * ((u32)sizeof(d_material_id) + (u32)sizeof(q16_16));
        if (remaining < need) {
            return -1;
        }
        for (l = 0u; l < D_LITHO_MAX_LAYERS; ++l) {
            d_material_id mid;
            q16_16 th;
            memcpy(&mid, ptr, sizeof(d_material_id));
            ptr += sizeof(d_material_id);
            memcpy(&th, ptr, sizeof(q16_16));
            ptr += sizeof(q16_16);
            remaining -= sizeof(d_material_id) + sizeof(q16_16);

            (void)mid;
            if (l < (u32)lc && th < 0) {
                return -1;
            }
        }
    }

    return 0;
}

static int dlitho_validate_world_chunks(const d_world *w) {
    u32 i;
    if (!w) {
        return -1;
    }
    for (i = 0u; i < w->chunk_count; ++i) {
        d_tlv_blob blob;
        u32 offset;
        u32 tag;
        d_tlv_blob payload;
        int rc;

        blob.ptr = (unsigned char *)0;
        blob.len = 0u;
        if (d_serialize_save_chunk_all((d_world *)w, (d_chunk *)&w->chunks[i], &blob) != 0) {
            if (blob.ptr) free(blob.ptr);
            return -1;
        }
        if (!blob.ptr || blob.len == 0u) {
            if (blob.ptr) free(blob.ptr);
            continue;
        }

        offset = 0u;
        while ((rc = d_tlv_kv_next(&blob, &offset, &tag, &payload)) == 0) {
            if (tag == TAG_SUBSYS_DLITHO) {
                if (dlitho_validate_chunk_payload(&payload) != 0) {
                    free(blob.ptr);
                    return -1;
                }
                break;
            }
        }
        if (rc < 0) {
            free(blob.ptr);
            return -1;
        }
        free(blob.ptr);
    }
    return 0;
}

int d_litho_validate(const d_world *w) {
    if (!w) {
        return -1;
    }
    if (dlitho_validate_world_chunks(w) != 0) {
        fprintf(stderr, "litho validate: invalid chunk payload\n");
        return -1;
    }
    return 0;
}
