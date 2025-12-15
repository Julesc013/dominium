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
    dg_replay_pkt *p;
    u32 off;
    u32 canon_len;
    unsigned char *dst;
    int rc;

    if (!rs || !hdr) return -1;
    if (!payload && payload_len != 0u) return -2;
    if (hdr->payload_len != payload_len) return -3;
    if (!rs->input_pkts || rs->input_capacity == 0u) {
        rs->probe_input_refused += 1u;
        return -4;
    }
    if (rs->input_count >= rs->input_capacity) {
        rs->probe_input_refused += 1u;
        return -5;
    }

    canon_len = payload_len;
    rc = dg_replay_arena_alloc(rs, payload_len, &off);
    if (rc != 0) {
        return -6;
    }

    dst = rs->arena ? (rs->arena + off) : (unsigned char *)0;
    if (payload_len != 0u) {
        /* Canonicalize TLV payload bytes; commands are TLV by contract. */
        rc = dg_tlv_canon(payload, payload_len, dst, payload_len, &canon_len);
        if (rc != 0 || canon_len != payload_len) {
            return -7;
        }
    }

    p = &rs->input_pkts[rs->input_count++];
    memset(p, 0, sizeof(*p));
    p->tick = tick;
    p->hdr = *hdr;
    p->payload_off = off;
    p->payload_len = payload_len;
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

