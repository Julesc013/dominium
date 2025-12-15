/* Deterministic replay stream (C89).
 *
 * In-memory only: no file IO; all storage is caller-reserved/bounded.
 *
 * The replay stream records:
 * - canonical per-tick hash snapshots (all registered hash domains)
 * - input command packets (header + canonical TLV payload bytes)
 * - content pack ID tables (stable IDs)
 * - deterministic ID remap tables
 * - optional probe samples (bounded; IDs only)
 */
#ifndef DG_REPLAY_STREAM_H
#define DG_REPLAY_STREAM_H

#include "domino/core/types.h"

#include "sim/pkt/dg_pkt_common.h"
#include "sim/pkt/pkt_hash.h"
#include "sim/hash/dg_hash.h"
#include "sim/hash/dg_hash_registry.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct dg_replay_id_remap {
    u64 from_id;
    u64 to_id;
} dg_replay_id_remap;

typedef struct dg_replay_probe_sample {
    dg_tick tick;
    u64     probe_id;
    u64     a;
    u64     b;
} dg_replay_probe_sample;

typedef struct dg_replay_pkt {
    dg_tick   tick;
    dg_pkt_hdr hdr;
    u32       payload_off; /* into arena */
    u32       payload_len;
    dg_pkt_hash pkt_hash; /* hdr + canonical TLV payload */
} dg_replay_pkt;

typedef struct dg_replay_stream {
    /* Hash domains table (canonical). */
    dg_hash_domain_id *hash_domain_ids;   /* owned */
    u32               *hash_domain_flags; /* owned (DG_HASH_DOMAIN_F_*) */
    u32                hash_domain_count;
    u32                hash_domain_capacity;

    /* Per-tick hash snapshots: row-major [tick_index][domain_index]. */
    dg_tick      *ticks;        /* owned */
    dg_hash_value *hash_values; /* owned */
    u32           tick_count;
    u32           tick_capacity;

    /* Content pack IDs (stable, sorted). */
    u64 *content_pack_ids; /* owned */
    u32  content_pack_count;
    u32  content_pack_capacity;

    /* Deterministic ID remap table (sorted by from_id,to_id). */
    dg_replay_id_remap *id_remaps; /* owned */
    u32                 id_remap_count;
    u32                 id_remap_capacity;

    /* Input packets (canonical TLV payload in arena), stored in canonical order. */
    dg_replay_pkt  *input_pkts; /* owned */
    u32             input_count;
    u32             input_capacity;

    unsigned char  *arena; /* owned */
    u32             arena_used;
    u32             arena_capacity;

    /* Optional probe samples. */
    dg_replay_probe_sample *probes; /* owned */
    u32                    probe_count;
    u32                    probe_capacity;

    /* Refusal probes (never silent drops). */
    u32 probe_hash_truncated;
    u32 probe_tick_refused;
    u32 probe_pack_refused;
    u32 probe_remap_refused;
    u32 probe_input_refused;
    u32 probe_arena_refused;
    u32 probe_probe_refused;
} dg_replay_stream;

void dg_replay_stream_init(dg_replay_stream *rs);
void dg_replay_stream_free(dg_replay_stream *rs);

/* Configure hash domains from a registry and reserve per-tick snapshot storage. */
int dg_replay_stream_configure_hashes_from_registry(dg_replay_stream *rs, const dg_hash_registry *hr, u32 max_ticks);

/* Configure auxiliary tables (bounded). */
int dg_replay_stream_reserve_content_packs(dg_replay_stream *rs, u32 capacity);
int dg_replay_stream_reserve_id_remaps(dg_replay_stream *rs, u32 capacity);
int dg_replay_stream_reserve_inputs(dg_replay_stream *rs, u32 max_inputs, u32 arena_bytes);
int dg_replay_stream_reserve_probes(dg_replay_stream *rs, u32 capacity);

/* Set content pack IDs (copied and sorted). */
int dg_replay_stream_set_content_pack_ids(dg_replay_stream *rs, const u64 *ids, u32 count);

/* Set ID remaps (copied and sorted). */
int dg_replay_stream_set_id_remaps(dg_replay_stream *rs, const dg_replay_id_remap *pairs, u32 count);

/* Record a per-tick hash snapshot (must match configured domains). */
int dg_replay_stream_record_hash_snapshot(dg_replay_stream *rs, dg_tick tick, const dg_hash_snapshot *snap);

/* Record an input packet (payload will be TLV-canonicalized into the arena).
 * The packet is inserted into the stream in canonical order, independent of
 * record call order.
 */
int dg_replay_stream_record_input_pkt(
    dg_replay_stream      *rs,
    dg_tick                tick,
    const dg_pkt_hdr      *hdr,
    const unsigned char   *payload,
    u32                    payload_len
);

int dg_replay_stream_record_probe(dg_replay_stream *rs, const dg_replay_probe_sample *p);

u32 dg_replay_stream_tick_count(const dg_replay_stream *rs);
u32 dg_replay_stream_hash_domain_count(const dg_replay_stream *rs);
dg_tick dg_replay_stream_tick_at(const dg_replay_stream *rs, u32 tick_index);
dg_hash_domain_id dg_replay_stream_hash_domain_id_at(const dg_replay_stream *rs, u32 domain_index);
u32 dg_replay_stream_hash_domain_flags_at(const dg_replay_stream *rs, u32 domain_index);
dg_hash_value dg_replay_stream_hash_value_at(const dg_replay_stream *rs, u32 tick_index, u32 domain_index);

/* Refusal probes. */
u32 dg_replay_stream_probe_hash_truncated(const dg_replay_stream *rs);
u32 dg_replay_stream_probe_tick_refused(const dg_replay_stream *rs);
u32 dg_replay_stream_probe_input_refused(const dg_replay_stream *rs);
u32 dg_replay_stream_probe_arena_refused(const dg_replay_stream *rs);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DG_REPLAY_STREAM_H */
