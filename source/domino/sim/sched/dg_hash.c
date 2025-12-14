#include <string.h>

#include "sim/sched/dg_hash.h"

static u64 dg_hash64_update_bytes(u64 h, const unsigned char *data, u32 len) {
    u32 i;
    if (!data || len == 0u) {
        return h;
    }
    for (i = 0u; i < len; ++i) {
        h ^= (u64)data[i];
        h *= 1099511628211ULL;
    }
    return h;
}

static u64 dg_hash64_update_u16_le(u64 h, u16 v) {
    unsigned char buf[2];
    /* local little-endian write to avoid extra dependencies */
    buf[0] = (unsigned char)(v & 0xFFu);
    buf[1] = (unsigned char)((v >> 8) & 0xFFu);
    return dg_hash64_update_bytes(h, buf, 2u);
}

static u64 dg_hash64_update_u64_le(u64 h, u64 v) {
    unsigned char buf[8];
    buf[0] = (unsigned char)(v & 0xFFu);
    buf[1] = (unsigned char)((v >> 8) & 0xFFu);
    buf[2] = (unsigned char)((v >> 16) & 0xFFu);
    buf[3] = (unsigned char)((v >> 24) & 0xFFu);
    buf[4] = (unsigned char)((v >> 32) & 0xFFu);
    buf[5] = (unsigned char)((v >> 40) & 0xFFu);
    buf[6] = (unsigned char)((v >> 48) & 0xFFu);
    buf[7] = (unsigned char)((v >> 56) & 0xFFu);
    return dg_hash64_update_bytes(h, buf, 8u);
}

void dg_hash_init(dg_hash_ctx *hc) {
    if (!hc) {
        return;
    }
    memset(hc, 0, sizeof(*hc));
    hc->deltas_hash = 14695981039346656037ULL;
}

void dg_hash_begin_tick(dg_hash_ctx *hc, dg_tick tick) {
    u32 i;
    if (!hc) {
        return;
    }
    hc->tick = tick;
    for (i = 0u; i < (u32)DG_PH_COUNT; ++i) {
        hc->phase_begin_count[i] = 0u;
        hc->phase_end_count[i] = 0u;
    }
    hc->deltas_committed = 0u;
    hc->deltas_hash = 14695981039346656037ULL;
}

void dg_hash_phase_begin(dg_hash_ctx *hc, dg_phase phase) {
    if (!hc) {
        return;
    }
    if (phase < 0 || phase >= DG_PH_COUNT) {
        return;
    }
    hc->phase_begin_count[(u32)phase] += 1u;
}

void dg_hash_phase_end(dg_hash_ctx *hc, dg_phase phase) {
    if (!hc) {
        return;
    }
    if (phase < 0 || phase >= DG_PH_COUNT) {
        return;
    }
    hc->phase_end_count[(u32)phase] += 1u;
}

void dg_hash_record_committed_delta(dg_hash_ctx *hc, const dg_order_key *key, const dg_pkt_delta *delta) {
    dg_pkt_hash ph;
    u64 h;
    if (!hc || !key || !delta) {
        return;
    }
    if (dg_pkt_hash_compute(&ph, &delta->hdr, delta->payload, delta->payload_len) != 0) {
        return;
    }

    h = (u64)hc->deltas_hash;
    h = dg_hash64_update_u16_le(h, key->phase);
    h = dg_hash64_update_u64_le(h, key->component_id);
    h = dg_hash64_update_u64_le(h, (u64)ph);
    hc->deltas_hash = (dg_pkt_hash)h;
    hc->deltas_committed += 1u;
}

