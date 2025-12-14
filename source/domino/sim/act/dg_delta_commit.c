#include <stdlib.h>

#include "sim/act/dg_delta_commit.h"

#include "res/dg_tlv_canon.h"

static int dg_delta_record_cmp_qsort(const void *a, const void *b) {
    const dg_delta_record *ra = (const dg_delta_record *)a;
    const dg_delta_record *rb = (const dg_delta_record *)b;
    int c;

    c = dg_order_key_cmp(&ra->key, &rb->key);
    if (c) {
        return c;
    }
    if (ra->insert_index < rb->insert_index) return -1;
    if (ra->insert_index > rb->insert_index) return 1;
    return 0;
}

static u64 dg_fnv1a64_bytes(u64 h, const unsigned char *p, u32 len) {
    u32 i;
    for (i = 0u; i < len; ++i) {
        h ^= (u64)p[i];
        h *= 1099511628211ULL;
    }
    return h;
}

static u64 dg_fnv1a64_u16_le(u64 h, u16 v) {
    unsigned char buf[2];
    dg_le_write_u16(buf, v);
    return dg_fnv1a64_bytes(h, buf, 2u);
}

static u64 dg_fnv1a64_u32_le(u64 h, u32 v) {
    unsigned char buf[4];
    dg_le_write_u32(buf, v);
    return dg_fnv1a64_bytes(h, buf, 4u);
}

static u64 dg_fnv1a64_u64_le(u64 h, u64 v) {
    unsigned char buf[8];
    dg_le_write_u64(buf, v);
    return dg_fnv1a64_bytes(h, buf, 8u);
}

static u64 dg_delta_key_checksum(u64 h, const dg_order_key *k) {
    if (!k) {
        return h;
    }
    h = dg_fnv1a64_u16_le(h, k->phase);
    h = dg_fnv1a64_u64_le(h, k->domain_id);
    h = dg_fnv1a64_u64_le(h, k->chunk_id);
    h = dg_fnv1a64_u64_le(h, k->entity_id);
    h = dg_fnv1a64_u64_le(h, k->component_id);
    h = dg_fnv1a64_u64_le(h, k->type_id);
    h = dg_fnv1a64_u32_le(h, k->seq);
    return h;
}

int dg_delta_commit_apply(
    void                   *world,
    const dg_delta_registry *registry,
    dg_delta_buffer        *buffer,
    dg_delta_commit_stats  *out_stats
) {
    dg_delta_commit_stats st;
    u32 i;

    if (!registry || !buffer) {
        return -1;
    }

    st.deltas_applied = 0u;
    st.deltas_rejected = 0u;
    st.ordering_checksum = 14695981039346656037ULL;

    if (buffer->count > 1u && buffer->records) {
        qsort(buffer->records, (size_t)buffer->count, sizeof(dg_delta_record), dg_delta_record_cmp_qsort);
    }

    for (i = 0u; i < buffer->count; ++i) {
        dg_pkt_delta pkt;
        const dg_delta_record *r = &buffer->records[i];
        const dg_delta_registry_entry *e = dg_delta_registry_find(registry, r->hdr.type_id);

        pkt.hdr = r->hdr;
        pkt.payload = r->payload;
        pkt.payload_len = r->payload_len;

        if (!e || !e->vtbl.apply) {
            st.deltas_rejected += 1u;
            continue;
        }

        st.ordering_checksum = dg_delta_key_checksum(st.ordering_checksum, &r->key);
        e->vtbl.apply(world, &pkt);
        st.deltas_applied += 1u;
    }

    if (out_stats) {
        *out_stats = st;
    }
    return 0;
}

