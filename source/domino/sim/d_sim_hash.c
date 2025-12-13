#include <stdlib.h>
#include <string.h>

#include "sim/d_sim_hash.h"
#include "world/d_serialize.h"

#define FNV1A64_OFFSET 14695981039346656037ULL
#define FNV1A64_PRIME  1099511628211ULL

static u64 d_sim_hash_bytes(u64 h, const void *data, u32 len) {
    const unsigned char *p = (const unsigned char *)data;
    u32 i;
    if (!p || len == 0u) {
        return h;
    }
    for (i = 0u; i < len; ++i) {
        h ^= (u64)p[i];
        h *= FNV1A64_PRIME;
    }
    return h;
}

static u64 d_sim_hash_u32(u64 h, u32 v) {
    return d_sim_hash_bytes(h, &v, (u32)sizeof(u32));
}

static u64 d_sim_hash_u64(u64 h, u64 v) {
    return d_sim_hash_bytes(h, &v, (u32)sizeof(u64));
}

static int d_sim_hash_chunk_cmp(const void *a, const void *b) {
    const d_chunk *ca = *(const d_chunk * const *)a;
    const d_chunk *cb = *(const d_chunk * const *)b;
    if (!ca && !cb) return 0;
    if (!ca) return -1;
    if (!cb) return 1;
    if (ca->cx < cb->cx) return -1;
    if (ca->cx > cb->cx) return 1;
    if (ca->cy < cb->cy) return -1;
    if (ca->cy > cb->cy) return 1;
    return 0;
}

d_world_hash d_sim_hash_chunk(const d_chunk *chunk) {
    u64 h = FNV1A64_OFFSET;
    if (!chunk) {
        return 0u;
    }
    h = d_sim_hash_u32(h, (u32)chunk->chunk_id);
    h = d_sim_hash_u32(h, (u32)chunk->cx);
    h = d_sim_hash_u32(h, (u32)chunk->cy);
    h = d_sim_hash_u32(h, (u32)chunk->flags);
    return h;
}

static u64 d_sim_hash_chunk_payload(d_world *w, d_chunk *chunk) {
    d_tlv_blob blob;
    u64 h;

    blob.ptr = (unsigned char *)0;
    blob.len = 0u;

    h = d_sim_hash_chunk((const d_chunk *)chunk);

    if (!w || !chunk) {
        return h;
    }
    if (d_serialize_save_chunk_all(w, chunk, &blob) == 0) {
        h = d_sim_hash_u32(h, blob.len);
        h = d_sim_hash_bytes(h, blob.ptr, blob.len);
    }
    if (blob.ptr) {
        free(blob.ptr);
    }
    return h;
}

d_world_hash d_sim_hash_world(const d_world *w) {
    d_tlv_blob inst_blob;
    d_chunk **chunk_list = (d_chunk **)0;
    u32 chunk_count = 0u;
    u32 i;
    u64 h = FNV1A64_OFFSET;

    if (!w) {
        return 0u;
    }

    /* World metadata */
    h = d_sim_hash_u64(h, w->meta.seed);
    h = d_sim_hash_u32(h, w->meta.world_size_m);
    h = d_sim_hash_u32(h, (u32)w->meta.vertical_min);
    h = d_sim_hash_u32(h, (u32)w->meta.vertical_max);
    h = d_sim_hash_u32(h, w->meta.core_version);
    h = d_sim_hash_u32(h, w->meta.suite_version);
    h = d_sim_hash_u32(h, w->meta.compat_profile_id);
    h = d_sim_hash_u32(h, w->tick_count);

    /* Instance-level serialized payload */
    inst_blob.ptr = (unsigned char *)0;
    inst_blob.len = 0u;
    if (d_serialize_save_instance_all((d_world *)w, &inst_blob) == 0) {
        h = d_sim_hash_u32(h, inst_blob.len);
        h = d_sim_hash_bytes(h, inst_blob.ptr, inst_blob.len);
    }
    if (inst_blob.ptr) {
        free(inst_blob.ptr);
    }

    /* Chunk list sorted by coordinates for deterministic ordering. */
    if (w->chunk_count > 0u && w->chunks) {
        chunk_list = (d_chunk **)malloc(sizeof(d_chunk *) * w->chunk_count);
        if (chunk_list) {
            chunk_count = w->chunk_count;
            for (i = 0u; i < chunk_count; ++i) {
                chunk_list[i] = &w->chunks[i];
            }
            qsort(chunk_list, chunk_count, sizeof(d_chunk *), d_sim_hash_chunk_cmp);
            for (i = 0u; i < chunk_count; ++i) {
                u64 ch = d_sim_hash_chunk_payload((d_world *)w, chunk_list[i]);
                h = d_sim_hash_u64(h, ch);
            }
            free(chunk_list);
        }
    }

    return h;
}
