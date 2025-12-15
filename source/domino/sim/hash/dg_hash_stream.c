#include <string.h>

#include "sim/hash/dg_hash_stream.h"

#include "res/dg_tlv_canon.h" /* explicit LE helpers */

#define DG_HASH_FNV1A64_OFFSET 14695981039346656037ULL
#define DG_HASH_FNV1A64_PRIME  1099511628211ULL

void dg_hash_stream_init(dg_hash_stream *s) {
    if (!s) {
        return;
    }
    s->h = DG_HASH_FNV1A64_OFFSET;
}

void dg_hash_stream_update_bytes(dg_hash_stream *s, const unsigned char *data, u32 len) {
    u32 i;
    dg_hash_value h;

    if (!s) {
        return;
    }
    if (!data || len == 0u) {
        return;
    }

    h = s->h;
    for (i = 0u; i < len; ++i) {
        h ^= (dg_hash_value)data[i];
        h *= DG_HASH_FNV1A64_PRIME;
    }
    s->h = h;
}

void dg_hash_stream_update_u16_le(dg_hash_stream *s, u16 v) {
    unsigned char buf[2];
    dg_le_write_u16(buf, v);
    dg_hash_stream_update_bytes(s, buf, 2u);
}

void dg_hash_stream_update_u32_le(dg_hash_stream *s, u32 v) {
    unsigned char buf[4];
    dg_le_write_u32(buf, v);
    dg_hash_stream_update_bytes(s, buf, 4u);
}

void dg_hash_stream_update_u64_le(dg_hash_stream *s, u64 v) {
    unsigned char buf[8];
    dg_le_write_u64(buf, v);
    dg_hash_stream_update_bytes(s, buf, 8u);
}

void dg_hash_stream_update_i64_le(dg_hash_stream *s, i64 v) {
    dg_hash_stream_update_u64_le(s, (u64)v);
}

void dg_hash_stream_begin_domain(dg_hash_stream *s, dg_hash_domain_id domain_id, dg_tick tick) {
    if (!s) {
        return;
    }
    s->h = DG_HASH_FNV1A64_OFFSET;
    dg_hash_stream_update_u32_le(s, (u32)domain_id);
    dg_hash_stream_update_u64_le(s, (u64)tick);
}

dg_hash_value dg_hash_stream_finalize(const dg_hash_stream *s) {
    if (!s) {
        return 0u;
    }
    return s->h;
}

