#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "core/d_model.h"
#include "core/d_serialize_tags.h"
#include "core/d_tlv_kv.h"
#include "hydro/d_hydro.h"
#include "world/d_serialize.h"

static int dhydro_validate_models(void) {
    if (!d_model_get(D_MODEL_FAMILY_HYDRO, (d_model_id)D_HYDRO_MODEL_SURFACE_WATER)) {
        fprintf(stderr, "hydro validate: missing hydro model %u\n", (unsigned)D_HYDRO_MODEL_SURFACE_WATER);
        return -1;
    }
    return 0;
}

static int dhydro_validate_chunk_payload(const d_tlv_blob *payload) {
    const unsigned char *ptr;
    u32 remaining;
    u32 cell_count;
    u32 i;

    if (!payload || payload->len == 0u) {
        return 0;
    }
    if (!payload->ptr || payload->len < 4u) {
        return -1;
    }
    ptr = payload->ptr;
    remaining = payload->len;
    memcpy(&cell_count, ptr, sizeof(u32));
    ptr += 4u;
    remaining -= 4u;

    if (cell_count != 256u) {
        return -1;
    }
    if (remaining < cell_count * (sizeof(q16_16) * 5u)) {
        return -1;
    }

    for (i = 0u; i < cell_count; ++i) {
        q16_16 surface_h;
        q16_16 depth;
        q16_16 vx;
        q16_16 vy;
        q16_16 flags;
        memcpy(&surface_h, ptr, sizeof(q16_16)); ptr += sizeof(q16_16);
        memcpy(&depth, ptr, sizeof(q16_16)); ptr += sizeof(q16_16);
        memcpy(&vx, ptr, sizeof(q16_16)); ptr += sizeof(q16_16);
        memcpy(&vy, ptr, sizeof(q16_16)); ptr += sizeof(q16_16);
        memcpy(&flags, ptr, sizeof(q16_16)); ptr += sizeof(q16_16);
        (void)surface_h;
        (void)vx;
        (void)vy;
        (void)flags;
        if (depth < 0) {
            return -1;
        }
    }

    return 0;
}

static int dhydro_validate_world_chunks(const d_world *w) {
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
        int found = 0;

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
            if (tag == TAG_SUBSYS_DHYDRO) {
                found = 1;
                if (dhydro_validate_chunk_payload(&payload) != 0) {
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
        (void)found;
        free(blob.ptr);
    }
    return 0;
}

int d_hydro_validate(const d_world *w) {
    if (!w) {
        return -1;
    }
    if (dhydro_validate_models() != 0) {
        return -1;
    }
    if (dhydro_validate_world_chunks(w) != 0) {
        return -1;
    }
    return 0;
}
