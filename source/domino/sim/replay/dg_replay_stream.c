/*
FILE: source/domino/sim/replay/dg_replay_stream.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / sim/replay/dg_replay_stream
RESPONSIBILITY: Implements `dg_replay_stream`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include <stdlib.h>
#include <string.h>

#include "sim/replay/dg_replay_stream.h"

#include "res/dg_tlv_canon.h"

static int dg_replay_cmp_u64_qsort(const void *a, const void *b) {
    u64 va = *(const u64 *)a;
    u64 vb = *(const u64 *)b;
    if (va < vb) return -1;
    if (va > vb) return 1;
    return 0;
}

static int dg_replay_cmp_remap_qsort(const void *a, const void *b) {
    const dg_replay_id_remap *ra = (const dg_replay_id_remap *)a;
    const dg_replay_id_remap *rb = (const dg_replay_id_remap *)b;
    if (ra->from_id < rb->from_id) return -1;
    if (ra->from_id > rb->from_id) return 1;
    if (ra->to_id < rb->to_id) return -1;
    if (ra->to_id > rb->to_id) return 1;
    return 0;
}

static int dg_replay_cmp_u64(u64 a, u64 b) {
    if (a < b) return -1;
    if (a > b) return 1;
    return 0;
}

static int dg_replay_cmp_u32(u32 a, u32 b) {
    if (a < b) return -1;
    if (a > b) return 1;
    return 0;
}

static int dg_replay_cmp_u16(u16 a, u16 b) {
    if (a < b) return -1;
    if (a > b) return 1;
    return 0;
}

static const unsigned char *dg_replay_stream_pkt_payload_ptr(const dg_replay_stream *rs, const dg_replay_pkt *p) {
    if (!rs || !p) return (const unsigned char *)0;
    if (p->payload_len == 0u) return (const unsigned char *)0;
    if (!rs->arena || rs->arena_capacity == 0u) return (const unsigned char *)0;
    if (p->payload_off > rs->arena_capacity) return (const unsigned char *)0;
    if (p->payload_len > (rs->arena_capacity - p->payload_off)) return (const unsigned char *)0;
    return rs->arena + p->payload_off;
}

/* Canonical ordering for input packets:
 * (tick,domain_id,chunk_id,src_entity,dst_entity,type_id,schema_id,schema_ver,flags,seq,payload_len,payload_bytes)
 * The payload bytes are TLV-canonicalized at record time.
 */
static int dg_replay_stream_pkt_cmp(const dg_replay_stream *rs, const dg_replay_pkt *a, const dg_replay_pkt *b) {
    int c;
    const unsigned char *pa;
    const unsigned char *pb;

    if (a == b) return 0;
    if (!a) return -1;
    if (!b) return 1;

    c = dg_replay_cmp_u64((u64)a->tick, (u64)b->tick);
    if (c) return c;

    c = dg_replay_cmp_u64((u64)a->hdr.domain_id, (u64)b->hdr.domain_id);
    if (c) return c;
    c = dg_replay_cmp_u64((u64)a->hdr.chunk_id, (u64)b->hdr.chunk_id);
    if (c) return c;
    c = dg_replay_cmp_u64((u64)a->hdr.src_entity, (u64)b->hdr.src_entity);
    if (c) return c;
    c = dg_replay_cmp_u64((u64)a->hdr.dst_entity, (u64)b->hdr.dst_entity);
    if (c) return c;

    c = dg_replay_cmp_u64((u64)a->hdr.type_id, (u64)b->hdr.type_id);
    if (c) return c;
    c = dg_replay_cmp_u64((u64)a->hdr.schema_id, (u64)b->hdr.schema_id);
    if (c) return c;
    c = dg_replay_cmp_u16(a->hdr.schema_ver, b->hdr.schema_ver);
    if (c) return c;
    c = dg_replay_cmp_u16(a->hdr.flags, b->hdr.flags);
    if (c) return c;
    c = dg_replay_cmp_u32(a->hdr.seq, b->hdr.seq);
    if (c) return c;
    c = dg_replay_cmp_u32(a->payload_len, b->payload_len);
    if (c) return c;

    /* Stable tie-break: compare canonical payload bytes (lexicographic). */
    if (a->payload_len == 0u) {
        return 0;
    }
    pa = dg_replay_stream_pkt_payload_ptr(rs, a);
    pb = dg_replay_stream_pkt_payload_ptr(rs, b);
    if (!pa && !pb) {
        return 0;
    }
    if (!pa) return -1;
    if (!pb) return 1;
    c = memcmp(pa, pb, (size_t)a->payload_len);
    if (c < 0) return -1;
    if (c > 0) return 1;

    /* Final tie-break: packet hash (should be equal if payload equal). */
    c = dg_replay_cmp_u64((u64)a->pkt_hash, (u64)b->pkt_hash);
    return c;
}

static u32 dg_replay_stream_pkt_upper_bound(const dg_replay_stream *rs, const dg_replay_pkt *key, u32 count) {
    u32 lo = 0u;
    u32 hi = count;
    u32 mid;
    int c;

    while (lo < hi) {
        mid = lo + ((hi - lo) / 2u);
        c = dg_replay_stream_pkt_cmp(rs, &rs->input_pkts[mid], key);
        if (c <= 0) {
            lo = mid + 1u;
        } else {
            hi = mid;
        }
    }
    return lo;
}

void dg_replay_stream_init(dg_replay_stream *rs) {
    if (!rs) {
        return;
    }
    memset(rs, 0, sizeof(*rs));
}

void dg_replay_stream_free(dg_replay_stream *rs) {
    if (!rs) {
        return;
    }
    if (rs->hash_domain_ids) free(rs->hash_domain_ids);
    if (rs->hash_domain_flags) free(rs->hash_domain_flags);
    if (rs->ticks) free(rs->ticks);
    if (rs->hash_values) free(rs->hash_values);
    if (rs->content_pack_ids) free(rs->content_pack_ids);
    if (rs->id_remaps) free(rs->id_remaps);
    if (rs->input_pkts) free(rs->input_pkts);
    if (rs->arena) free(rs->arena);
    if (rs->probes) free(rs->probes);
    dg_replay_stream_init(rs);
}

static int dg_replay_stream_alloc_zeroed(void **out_ptr, size_t bytes) {
    void *p;
    if (!out_ptr) return -1;
    if (bytes == 0u) {
        *out_ptr = (void *)0;
        return 0;
    }
    p = malloc(bytes);
    if (!p) {
        *out_ptr = (void *)0;
        return -2;
    }
    memset(p, 0, bytes);
    *out_ptr = p;
    return 0;
}

int dg_replay_stream_configure_hashes_from_registry(dg_replay_stream *rs, const dg_hash_registry *hr, u32 max_ticks) {
    u32 n;
    u32 i;
    int rc;
    size_t bytes_ids;
    size_t bytes_flags;
    size_t bytes_ticks;
    size_t bytes_hashes;

    if (!rs || !hr) {
        return -1;
    }

    dg_replay_stream_free(rs);

    n = dg_hash_registry_count(hr);
    if (n == 0u) {
        return 0;
    }
    rs->hash_domain_count = n;
    rs->hash_domain_capacity = n;

    bytes_ids = sizeof(dg_hash_domain_id) * (size_t)n;
    bytes_flags = sizeof(u32) * (size_t)n;
    bytes_ticks = sizeof(dg_tick) * (size_t)max_ticks;
    bytes_hashes = sizeof(dg_hash_value) * (size_t)max_ticks * (size_t)n;

    rc = dg_replay_stream_alloc_zeroed((void **)&rs->hash_domain_ids, bytes_ids);
    if (rc != 0) { dg_replay_stream_free(rs); return -2; }
    rc = dg_replay_stream_alloc_zeroed((void **)&rs->hash_domain_flags, bytes_flags);
    if (rc != 0) { dg_replay_stream_free(rs); return -3; }
    rc = dg_replay_stream_alloc_zeroed((void **)&rs->ticks, bytes_ticks);
    if (rc != 0) { dg_replay_stream_free(rs); return -4; }
    rc = dg_replay_stream_alloc_zeroed((void **)&rs->hash_values, bytes_hashes);
    if (rc != 0) { dg_replay_stream_free(rs); return -5; }

    rs->tick_capacity = max_ticks;
    rs->tick_count = 0u;

    for (i = 0u; i < n; ++i) {
        const dg_hash_registry_entry *e = dg_hash_registry_at(hr, i);
        if (!e) {
            dg_replay_stream_free(rs);
            return -6;
        }
        rs->hash_domain_ids[i] = e->domain_id;
        rs->hash_domain_flags[i] = e->flags;
    }

    return 0;
}

int dg_replay_stream_reserve_content_packs(dg_replay_stream *rs, u32 capacity) {
    size_t bytes;
    if (!rs) return -1;
    if (rs->content_pack_ids) free(rs->content_pack_ids);
    rs->content_pack_ids = (u64 *)0;
    rs->content_pack_count = 0u;
    rs->content_pack_capacity = 0u;
    if (capacity == 0u) return 0;
    bytes = sizeof(u64) * (size_t)capacity;
    if (dg_replay_stream_alloc_zeroed((void **)&rs->content_pack_ids, bytes) != 0) {
        rs->probe_pack_refused += 1u;
        return -2;
    }
    rs->content_pack_capacity = capacity;
    return 0;
}

int dg_replay_stream_reserve_id_remaps(dg_replay_stream *rs, u32 capacity) {
    size_t bytes;
    if (!rs) return -1;
    if (rs->id_remaps) free(rs->id_remaps);
    rs->id_remaps = (dg_replay_id_remap *)0;
    rs->id_remap_count = 0u;
    rs->id_remap_capacity = 0u;
    if (capacity == 0u) return 0;
    bytes = sizeof(dg_replay_id_remap) * (size_t)capacity;
    if (dg_replay_stream_alloc_zeroed((void **)&rs->id_remaps, bytes) != 0) {
        rs->probe_remap_refused += 1u;
        return -2;
    }
    rs->id_remap_capacity = capacity;
    return 0;
}

int dg_replay_stream_reserve_inputs(dg_replay_stream *rs, u32 max_inputs, u32 arena_bytes) {
    size_t bytes_pkts;
    size_t bytes_arena;
    if (!rs) return -1;

    if (rs->input_pkts) free(rs->input_pkts);
    if (rs->arena) free(rs->arena);
    rs->input_pkts = (dg_replay_pkt *)0;
    rs->input_count = 0u;
    rs->input_capacity = 0u;
    rs->arena = (unsigned char *)0;
    rs->arena_used = 0u;
    rs->arena_capacity = 0u;

    if (max_inputs == 0u && arena_bytes == 0u) {
        return 0;
    }

    bytes_pkts = sizeof(dg_replay_pkt) * (size_t)max_inputs;
    bytes_arena = (size_t)arena_bytes;

    if (max_inputs > 0u) {
        if (dg_replay_stream_alloc_zeroed((void **)&rs->input_pkts, bytes_pkts) != 0) {
            rs->probe_input_refused += 1u;
            return -2;
        }
        rs->input_capacity = max_inputs;
    }

    if (arena_bytes > 0u) {
        if (dg_replay_stream_alloc_zeroed((void **)&rs->arena, bytes_arena) != 0) {
            rs->probe_arena_refused += 1u;
            return -3;
        }
        rs->arena_capacity = arena_bytes;
    }

    return 0;
}

int dg_replay_stream_reserve_probes(dg_replay_stream *rs, u32 capacity) {
    size_t bytes;
    if (!rs) return -1;
    if (rs->probes) free(rs->probes);
    rs->probes = (dg_replay_probe_sample *)0;
    rs->probe_count = 0u;
    rs->probe_capacity = 0u;
    if (capacity == 0u) return 0;
    bytes = sizeof(dg_replay_probe_sample) * (size_t)capacity;
    if (dg_replay_stream_alloc_zeroed((void **)&rs->probes, bytes) != 0) {
        rs->probe_probe_refused += 1u;
        return -2;
    }
    rs->probe_capacity = capacity;
    return 0;
}

int dg_replay_stream_set_content_pack_ids(dg_replay_stream *rs, const u64 *ids, u32 count) {
    if (!rs) return -1;
    if (!ids && count != 0u) return -2;
    if (!rs->content_pack_ids || rs->content_pack_capacity < count) {
        rs->probe_pack_refused += 1u;
        return -3;
    }
    if (count > 0u) {
        memcpy(rs->content_pack_ids, ids, sizeof(u64) * (size_t)count);
        qsort(rs->content_pack_ids, (size_t)count, sizeof(u64), dg_replay_cmp_u64_qsort);
    }
    rs->content_pack_count = count;
    return 0;
}

int dg_replay_stream_set_id_remaps(dg_replay_stream *rs, const dg_replay_id_remap *pairs, u32 count) {
    if (!rs) return -1;
    if (!pairs && count != 0u) return -2;
    if (!rs->id_remaps || rs->id_remap_capacity < count) {
        rs->probe_remap_refused += 1u;
        return -3;
    }
    if (count > 0u) {
        memcpy(rs->id_remaps, pairs, sizeof(dg_replay_id_remap) * (size_t)count);
        qsort(rs->id_remaps, (size_t)count, sizeof(dg_replay_id_remap), dg_replay_cmp_remap_qsort);
    }
    rs->id_remap_count = count;
    return 0;
}

static int dg_replay_stream_hash_domain_table_matches(const dg_replay_stream *rs, const dg_hash_snapshot *snap) {
    u32 i;
    if (!rs || !snap) return 0;
    if (snap->count != rs->hash_domain_count) return 0;
    for (i = 0u; i < rs->hash_domain_count; ++i) {
        const dg_hash_snapshot_entry *e = dg_hash_snapshot_at(snap, i);
        if (!e) return 0;
        if (e->domain_id != rs->hash_domain_ids[i]) return 0;
    }
    return 1;
}

int dg_replay_stream_record_hash_snapshot(dg_replay_stream *rs, dg_tick tick, const dg_hash_snapshot *snap) {
    u32 i;
    u32 base;
    if (!rs || !snap) return -1;
    if (!rs->ticks || !rs->hash_values) return -2;
    if (rs->tick_count >= rs->tick_capacity) {
        rs->probe_tick_refused += 1u;
        return -3;
    }
    if (!dg_replay_stream_hash_domain_table_matches(rs, snap)) {
        return -4;
    }
    if (rs->tick_count > 0u) {
        dg_tick prev = rs->ticks[rs->tick_count - 1u];
        if (tick <= prev) {
            return -5;
        }
    }

    rs->ticks[rs->tick_count] = tick;
    base = rs->tick_count * rs->hash_domain_count;
    for (i = 0u; i < rs->hash_domain_count; ++i) {
        const dg_hash_snapshot_entry *e = dg_hash_snapshot_at(snap, i);
        rs->hash_values[base + i] = e ? e->value : 0u;
    }
    rs->tick_count += 1u;
    return 0;
}

static int dg_replay_arena_alloc(dg_replay_stream *rs, u32 bytes, u32 *out_off) {
    u32 off;
    if (!rs || !out_off) return -1;
    if (bytes == 0u) {
        *out_off = 0u;
        return 0;
    }
    if (!rs->arena || rs->arena_capacity == 0u) {
        rs->probe_arena_refused += 1u;
        return -2;
    }
    off = rs->arena_used;
    if (off > rs->arena_capacity || bytes > (rs->arena_capacity - off)) {
        rs->probe_arena_refused += 1u;
        return -3;
    }
    rs->arena_used = off + bytes;
    *out_off = off;
    return 0;
}

int dg_replay_stream_record_input_pkt(
    dg_replay_stream      *rs,
    dg_tick                tick,
    const dg_pkt_hdr      *hdr,
    const unsigned char   *payload,
    u32                    payload_len
) {
    dg_replay_pkt p;
    u32 off;
    u32 canon_len;
    unsigned char *dst;
    int rc;
    u32 old_arena_used;
    u32 idx;
    dg_pkt_hash ph;

    if (!rs || !hdr) return -1;
    if (!payload && payload_len != 0u) return -2;
    if (hdr->payload_len != payload_len) return -3;
    if (hdr->tick != tick) return -4;
    if (!rs->input_pkts || rs->input_capacity == 0u) {
        rs->probe_input_refused += 1u;
        return -5;
    }
    if (rs->input_count >= rs->input_capacity) {
        rs->probe_input_refused += 1u;
        return -6;
    }

    canon_len = payload_len;
    old_arena_used = rs->arena_used;
    rc = dg_replay_arena_alloc(rs, payload_len, &off);
    if (rc != 0) {
        return -7;
    }

    dst = rs->arena ? (rs->arena + off) : (unsigned char *)0;
    if (payload_len != 0u) {
        /* Canonicalize TLV payload bytes; commands are TLV by contract. */
        rc = dg_tlv_canon(payload, payload_len, dst, payload_len, &canon_len);
        if (rc != 0 || canon_len != payload_len) {
            rs->arena_used = old_arena_used;
            return -8;
        }
    }

    ph = 0u;
    rc = dg_pkt_hash_compute_canon(&ph, hdr, (const unsigned char *)dst, payload_len);
    if (rc != 0) {
        rs->arena_used = old_arena_used;
        return -9;
    }

    memset(&p, 0, sizeof(p));
    p.tick = tick;
    p.hdr = *hdr;
    p.payload_off = off;
    p.payload_len = payload_len;
    p.pkt_hash = ph;

    /* Canonical insertion (stable, independent of record order). */
    idx = dg_replay_stream_pkt_upper_bound(rs, &p, rs->input_count);
    if (idx < rs->input_count) {
        memmove(&rs->input_pkts[idx + 1u], &rs->input_pkts[idx],
                sizeof(dg_replay_pkt) * (size_t)(rs->input_count - idx));
    }
    rs->input_pkts[idx] = p;
    rs->input_count += 1u;
    return 0;
}

int dg_replay_stream_record_probe(dg_replay_stream *rs, const dg_replay_probe_sample *p) {
    if (!rs || !p) return -1;
    if (!rs->probes || rs->probe_capacity == 0u) {
        rs->probe_probe_refused += 1u;
        return -2;
    }
    if (rs->probe_count >= rs->probe_capacity) {
        rs->probe_probe_refused += 1u;
        return -3;
    }
    rs->probes[rs->probe_count++] = *p;
    return 0;
}

u32 dg_replay_stream_tick_count(const dg_replay_stream *rs) {
    return rs ? rs->tick_count : 0u;
}

u32 dg_replay_stream_hash_domain_count(const dg_replay_stream *rs) {
    return rs ? rs->hash_domain_count : 0u;
}

dg_tick dg_replay_stream_tick_at(const dg_replay_stream *rs, u32 tick_index) {
    if (!rs || !rs->ticks || tick_index >= rs->tick_count) return 0u;
    return rs->ticks[tick_index];
}

dg_hash_domain_id dg_replay_stream_hash_domain_id_at(const dg_replay_stream *rs, u32 domain_index) {
    if (!rs || !rs->hash_domain_ids || domain_index >= rs->hash_domain_count) return 0u;
    return rs->hash_domain_ids[domain_index];
}

u32 dg_replay_stream_hash_domain_flags_at(const dg_replay_stream *rs, u32 domain_index) {
    if (!rs || !rs->hash_domain_flags || domain_index >= rs->hash_domain_count) return 0u;
    return rs->hash_domain_flags[domain_index];
}

dg_hash_value dg_replay_stream_hash_value_at(const dg_replay_stream *rs, u32 tick_index, u32 domain_index) {
    u32 base;
    if (!rs || !rs->hash_values) return 0u;
    if (tick_index >= rs->tick_count) return 0u;
    if (domain_index >= rs->hash_domain_count) return 0u;
    base = tick_index * rs->hash_domain_count;
    return rs->hash_values[base + domain_index];
}

u32 dg_replay_stream_probe_hash_truncated(const dg_replay_stream *rs) {
    return rs ? rs->probe_hash_truncated : 0u;
}

u32 dg_replay_stream_probe_tick_refused(const dg_replay_stream *rs) {
    return rs ? rs->probe_tick_refused : 0u;
}

u32 dg_replay_stream_probe_input_refused(const dg_replay_stream *rs) {
    return rs ? rs->probe_input_refused : 0u;
}

u32 dg_replay_stream_probe_arena_refused(const dg_replay_stream *rs) {
    return rs ? rs->probe_arena_refused : 0u;
}
