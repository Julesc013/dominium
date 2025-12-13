#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "core/d_model.h"
#include "env/d_env.h"
#include "env/d_env_field.h"
#include "env/d_env_volume.h"

static int denv_id_in_list(const d_env_volume_id *ids, u32 count, d_env_volume_id id) {
    u32 i;
    if (!ids || count == 0u) {
        return 0;
    }
    for (i = 0u; i < count; ++i) {
        if (ids[i] == id) {
            return 1;
        }
    }
    return 0;
}

static int denv_validate_models(void) {
    if (!d_model_get(D_MODEL_FAMILY_ENV, (d_model_id)D_ENV_MODEL_ATMOSPHERE_DEFAULT)) {
        fprintf(stderr, "env validate: missing env model %u\n", (unsigned)D_ENV_MODEL_ATMOSPHERE_DEFAULT);
        return -1;
    }
    return 0;
}

static int denv_validate_samples(const d_world *w) {
    u32 i;
    if (!w) {
        return -1;
    }
    for (i = 0u; i < w->chunk_count; ++i) {
        const d_chunk *chunk = &w->chunks[i];
        d_env_sample samples[16];
        u16 count;
        u16 s;
        q32_32 x = ((q32_32)chunk->cx) << Q32_32_FRAC_BITS;
        q32_32 y = ((q32_32)chunk->cy) << Q32_32_FRAC_BITS;
        q32_32 z = 0;
        count = d_env_sample_exterior_at(w, x, y, z, samples, 16u);
        if (count == 0u) {
            fprintf(stderr, "env validate: no samples for chunk (%d,%d)\n", (int)chunk->cx, (int)chunk->cy);
            return -1;
        }
        for (s = 0u; s < count; ++s) {
            if (!d_model_get(D_MODEL_FAMILY_ENV, (d_model_id)samples[s].model_id)) {
                fprintf(stderr, "env validate: unregistered env model %u\n", (unsigned)samples[s].model_id);
                return -1;
            }
        }
    }
    return 0;
}

static int denv_validate_volume_graph(d_world *w) {
    d_tlv_blob blob;
    const unsigned char *ptr;
    u32 remaining;
    u32 vol_count;
    u32 edge_count;
    d_env_volume_id ids[1024];
    u32 i;

    if (!w) {
        return -1;
    }

    blob.ptr = (unsigned char *)0;
    blob.len = 0u;
    if (d_env_volume_save_instance(w, &blob) != 0) {
        return -1;
    }

    if (blob.len == 0u) {
        if (blob.ptr) {
            free(blob.ptr);
        }
        return 0;
    }
    if (!blob.ptr || blob.len < 8u) {
        if (blob.ptr) {
            free(blob.ptr);
        }
        return -1;
    }

    ptr = blob.ptr;
    remaining = blob.len;
    memcpy(&vol_count, ptr, sizeof(u32));
    ptr += 4u;
    memcpy(&edge_count, ptr, sizeof(u32));
    ptr += 4u;
    remaining -= 8u;

    if (vol_count > 1024u) {
        free(blob.ptr);
        return -1;
    }
    memset(ids, 0, sizeof(ids));

    for (i = 0u; i < vol_count; ++i) {
        d_env_volume_id id;
        q32_32 min_x, min_y, min_z;
        q32_32 max_x, max_y, max_z;
        u32 need = sizeof(d_env_volume_id) + (sizeof(q32_32) * 6u) + (sizeof(u32) * 2u) + (sizeof(q16_16) * 6u);
        if (remaining < need) {
            free(blob.ptr);
            return -1;
        }
        memcpy(&id, ptr, sizeof(d_env_volume_id));
        ptr += sizeof(d_env_volume_id);
        memcpy(&min_x, ptr, sizeof(q32_32)); ptr += sizeof(q32_32);
        memcpy(&min_y, ptr, sizeof(q32_32)); ptr += sizeof(q32_32);
        memcpy(&min_z, ptr, sizeof(q32_32)); ptr += sizeof(q32_32);
        memcpy(&max_x, ptr, sizeof(q32_32)); ptr += sizeof(q32_32);
        memcpy(&max_y, ptr, sizeof(q32_32)); ptr += sizeof(q32_32);
        memcpy(&max_z, ptr, sizeof(q32_32)); ptr += sizeof(q32_32);
        ptr += sizeof(u32) * 2u; /* owner ids */
        ptr += sizeof(q16_16) * 6u; /* fields */
        remaining -= need;

        if (id == 0u) {
            free(blob.ptr);
            return -1;
        }
        if (denv_id_in_list(ids, vol_count, id)) {
            free(blob.ptr);
            return -1;
        }
        if (max_x < min_x || max_y < min_y || max_z < min_z) {
            free(blob.ptr);
            return -1;
        }
        ids[i] = id;
    }

    for (i = 0u; i < edge_count; ++i) {
        d_env_volume_id a;
        d_env_volume_id b;
        q16_16 gas_k;
        q16_16 heat_k;
        u32 need = (sizeof(d_env_volume_id) * 2u) + (sizeof(q16_16) * 2u);
        if (remaining < need) {
            free(blob.ptr);
            return -1;
        }
        memcpy(&a, ptr, sizeof(d_env_volume_id)); ptr += sizeof(d_env_volume_id);
        memcpy(&b, ptr, sizeof(d_env_volume_id)); ptr += sizeof(d_env_volume_id);
        memcpy(&gas_k, ptr, sizeof(q16_16)); ptr += sizeof(q16_16);
        memcpy(&heat_k, ptr, sizeof(q16_16)); ptr += sizeof(q16_16);
        remaining -= need;

        if (a == b) {
            free(blob.ptr);
            return -1;
        }
        if (a == 0u && b == 0u) {
            free(blob.ptr);
            return -1;
        }
        if (a != 0u && !denv_id_in_list(ids, vol_count, a)) {
            free(blob.ptr);
            return -1;
        }
        if (b != 0u && !denv_id_in_list(ids, vol_count, b)) {
            free(blob.ptr);
            return -1;
        }
        if (gas_k < 0 || gas_k > d_q16_16_from_int(1)) {
            free(blob.ptr);
            return -1;
        }
        if (heat_k < 0 || heat_k > d_q16_16_from_int(1)) {
            free(blob.ptr);
            return -1;
        }
    }

    free(blob.ptr);
    return 0;
}

int d_env_validate(const d_world *w) {
    if (!w) {
        return -1;
    }
    if (denv_validate_models() != 0) {
        return -1;
    }
    if (denv_validate_samples(w) != 0) {
        return -1;
    }
    if (denv_validate_volume_graph((d_world *)w) != 0) {
        return -1;
    }
    return 0;
}
