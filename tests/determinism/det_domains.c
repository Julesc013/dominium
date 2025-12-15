#include "det_common.h"

#include "sim/hash/dg_hash_registry.h"
#include "sim/replay/dg_replay.h"
#include "sim/replay/dg_replay_validate.h"

#include "res/dg_tlv_canon.h"

typedef struct det_domains_ctx {
    u64 values[9]; /* indexed by DG_HASH_DOMAIN_* (0 unused) */
} det_domains_ctx;

static void det_hash_domain_u64(dg_hash_stream *s, dg_tick tick, void *user_ctx) {
    det_domains_ctx *ctx = (det_domains_ctx *)user_ctx;
    u64 v;
    (void)tick;
    if (!ctx) {
        return;
    }
    /* Caller seeds stream with (domain_id,tick); each domain adds its own value. */
    v = ctx->values[0];
    dg_hash_stream_update_u64_le(s, v);
}

static void det_hash_domain_by_id(dg_hash_stream *s, dg_tick tick, void *user_ctx) {
    det_domains_ctx *ctx = (det_domains_ctx *)user_ctx;
    u64 v;
    u32 id;
    (void)tick;
    if (!ctx) {
        return;
    }
    /* domain_id is already encoded into the stream seed; also fold a per-domain value. */
    (void)s;
    (void)tick;
    id = 0u;
    v = 0u;
    /* This callback relies on being bound per-domain via user_ctx values table. */
    (void)id;
    (void)v;
}

static void det_hash_domain_sched(dg_hash_stream *s, dg_tick tick, void *user_ctx) {
    det_domains_ctx *ctx = (det_domains_ctx *)user_ctx;
    if (!ctx) return;
    dg_hash_stream_update_u64_le(s, ctx->values[DG_HASH_DOMAIN_SCHEDULER_STATE]);
    dg_hash_stream_update_u64_le(s, (u64)tick);
}

static void det_hash_domain_packets(dg_hash_stream *s, dg_tick tick, void *user_ctx) {
    det_domains_ctx *ctx = (det_domains_ctx *)user_ctx;
    (void)tick;
    if (!ctx) return;
    dg_hash_stream_update_u64_le(s, ctx->values[DG_HASH_DOMAIN_PACKET_STREAMS]);
}

static void det_hash_domain_deltas(dg_hash_stream *s, dg_tick tick, void *user_ctx) {
    det_domains_ctx *ctx = (det_domains_ctx *)user_ctx;
    (void)tick;
    if (!ctx) return;
    dg_hash_stream_update_u64_le(s, ctx->values[DG_HASH_DOMAIN_DELTA_COMMIT_RESULTS]);
}

static void det_hash_domain_states(dg_hash_stream *s, dg_tick tick, void *user_ctx) {
    det_domains_ctx *ctx = (det_domains_ctx *)user_ctx;
    (void)tick;
    if (!ctx) return;
    dg_hash_stream_update_u64_le(s, ctx->values[DG_HASH_DOMAIN_DOMAIN_STATES]);
}

static void det_hash_domain_graphs(dg_hash_stream *s, dg_tick tick, void *user_ctx) {
    det_domains_ctx *ctx = (det_domains_ctx *)user_ctx;
    (void)tick;
    if (!ctx) return;
    dg_hash_stream_update_u64_le(s, ctx->values[DG_HASH_DOMAIN_GRAPH_STATES]);
}

static void det_hash_domain_belief(dg_hash_stream *s, dg_tick tick, void *user_ctx) {
    det_domains_ctx *ctx = (det_domains_ctx *)user_ctx;
    (void)tick;
    if (!ctx) return;
    dg_hash_stream_update_u64_le(s, ctx->values[DG_HASH_DOMAIN_BELIEF_DB]);
}

static void det_hash_domain_comms(dg_hash_stream *s, dg_tick tick, void *user_ctx) {
    det_domains_ctx *ctx = (det_domains_ctx *)user_ctx;
    (void)tick;
    if (!ctx) return;
    dg_hash_stream_update_u64_le(s, ctx->values[DG_HASH_DOMAIN_COMMS_QUEUES]);
}

static void det_hash_domain_lod(dg_hash_stream *s, dg_tick tick, void *user_ctx) {
    det_domains_ctx *ctx = (det_domains_ctx *)user_ctx;
    (void)tick;
    if (!ctx) return;
    dg_hash_stream_update_u64_le(s, ctx->values[DG_HASH_DOMAIN_PROMO_LOD_STATE]);
}

static int det_build_registry(dg_hash_registry *hr, det_domains_ctx *ctx) {
    if (!hr || !ctx) return -1;
    dg_hash_registry_init(hr);

    DET_ASSERT(dg_hash_registry_add_domain(hr, DG_HASH_DOMAIN_SCHEDULER_STATE, 0u, det_hash_domain_sched, ctx) == 0);
    DET_ASSERT(dg_hash_registry_add_domain(hr, DG_HASH_DOMAIN_PACKET_STREAMS, DG_HASH_DOMAIN_F_BEHAVIORAL, det_hash_domain_packets, ctx) == 0);
    DET_ASSERT(dg_hash_registry_add_domain(hr, DG_HASH_DOMAIN_DELTA_COMMIT_RESULTS, DG_HASH_DOMAIN_F_BEHAVIORAL, det_hash_domain_deltas, ctx) == 0);
    DET_ASSERT(dg_hash_registry_add_domain(hr, DG_HASH_DOMAIN_DOMAIN_STATES, DG_HASH_DOMAIN_F_STRUCTURAL, det_hash_domain_states, ctx) == 0);
    DET_ASSERT(dg_hash_registry_add_domain(hr, DG_HASH_DOMAIN_GRAPH_STATES, DG_HASH_DOMAIN_F_STRUCTURAL, det_hash_domain_graphs, ctx) == 0);
    DET_ASSERT(dg_hash_registry_add_domain(hr, DG_HASH_DOMAIN_BELIEF_DB, DG_HASH_DOMAIN_F_BEHAVIORAL, det_hash_domain_belief, ctx) == 0);
    DET_ASSERT(dg_hash_registry_add_domain(hr, DG_HASH_DOMAIN_COMMS_QUEUES, DG_HASH_DOMAIN_F_BEHAVIORAL, det_hash_domain_comms, ctx) == 0);
    DET_ASSERT(dg_hash_registry_add_domain(hr, DG_HASH_DOMAIN_PROMO_LOD_STATE, 0u, det_hash_domain_lod, ctx) == 0);
    return 0;
}

static int det_record_ticks(dg_replay_stream *out, const dg_hash_registry *hr, dg_tick tick0, dg_tick tick_count) {
    dg_hash_snapshot_entry snap_store[16];
    dg_hash_snapshot snap;
    dg_replay r;
    dg_tick t;

    dg_hash_snapshot_init(&snap, snap_store, (u32)(sizeof(snap_store) / sizeof(snap_store[0])));
    dg_replay_stream_init(out);
    DET_ASSERT(dg_replay_stream_configure_hashes_from_registry(out, hr, (u32)tick_count) == 0);
    DET_ASSERT(dg_replay_stream_reserve_content_packs(out, 16u) == 0);
    DET_ASSERT(dg_replay_stream_reserve_id_remaps(out, 16u) == 0);
    DET_ASSERT(dg_replay_stream_reserve_inputs(out, 64u, 1024u) == 0);

    dg_replay_init(&r);
    dg_replay_set_stream(&r, out);

    for (t = 0u; t < tick_count; ++t) {
        dg_tick tick = tick0 + t;
        DET_ASSERT(dg_hash_registry_compute_tick(hr, tick, &snap) == 0);
        dg_replay_begin_tick(&r, tick);
        DET_ASSERT(dg_replay_record_hash_snapshot(&r, &snap) == 0);
    }

    return 0;
}

static void det_write_tlv_u32(unsigned char *buf, u32 *io_off, u32 tag, u32 v) {
    u32 off;
    if (!buf || !io_off) return;
    off = *io_off;
    dg_le_write_u32(buf + off + 0u, tag);
    dg_le_write_u32(buf + off + 4u, 4u);
    dg_le_write_u32(buf + off + 8u, v);
    *io_off = off + 12u;
}

static int det_record_two_inputs(dg_replay_stream *rs, dg_tick tick, int reverse_order, u32 v0, u32 v1) {
    dg_replay r;
    dg_pkt_hdr h0;
    dg_pkt_hdr h1;
    unsigned char p0[12];
    unsigned char p1[12];
    u32 n0 = 0u;
    u32 n1 = 0u;

    if (!rs) return -1;

    det_write_tlv_u32(p0, &n0, 1u, v0);
    det_write_tlv_u32(p1, &n1, 1u, v1);

    dg_pkt_hdr_clear(&h0);
    h0.type_id = 0xABCDEF0011223344ULL;
    h0.schema_id = 0x0000000000000001ULL;
    h0.schema_ver = 1u;
    h0.flags = DG_PKT_FLAG_NONE;
    h0.tick = tick;
    h0.src_entity = 1u;
    h0.dst_entity = 0u;
    h0.domain_id = 1u;
    h0.chunk_id = 0u;
    h0.seq = 1u;
    h0.payload_len = n0;

    dg_pkt_hdr_clear(&h1);
    h1 = h0;
    h1.seq = 2u;
    h1.payload_len = n1;

    dg_replay_init(&r);
    dg_replay_set_stream(&r, rs);
    dg_replay_begin_tick(&r, tick);

    if (!reverse_order) {
        DET_ASSERT(dg_replay_record_input_pkt(&r, &h0, p0, n0) == 0);
        DET_ASSERT(dg_replay_record_input_pkt(&r, &h1, p1, n1) == 0);
    } else {
        DET_ASSERT(dg_replay_record_input_pkt(&r, &h1, p1, n1) == 0);
        DET_ASSERT(dg_replay_record_input_pkt(&r, &h0, p0, n0) == 0);
    }
    return 0;
}

static int det_test_replay_validation_modes(void) {
    dg_hash_registry hr_expected;
    dg_hash_registry hr_actual;
    det_domains_ctx ctx_expected;
    det_domains_ctx ctx_actual;
    dg_replay_stream expected;
    dg_replay_stream actual;
    dg_replay_mismatch mm;
    int rc;

    memset(&ctx_expected, 0, sizeof(ctx_expected));
    memset(&ctx_actual, 0, sizeof(ctx_actual));

    ctx_expected.values[DG_HASH_DOMAIN_SCHEDULER_STATE] = 0x1111u;
    ctx_expected.values[DG_HASH_DOMAIN_PACKET_STREAMS] = 0x2222u;
    ctx_expected.values[DG_HASH_DOMAIN_DELTA_COMMIT_RESULTS] = 0x3333u;
    ctx_expected.values[DG_HASH_DOMAIN_DOMAIN_STATES] = 0x4444u;
    ctx_expected.values[DG_HASH_DOMAIN_GRAPH_STATES] = 0x5555u;
    ctx_expected.values[DG_HASH_DOMAIN_BELIEF_DB] = 0x6666u;
    ctx_expected.values[DG_HASH_DOMAIN_COMMS_QUEUES] = 0x7777u;
    ctx_expected.values[DG_HASH_DOMAIN_PROMO_LOD_STATE] = 0x8888u;

    ctx_actual = ctx_expected;
    ctx_actual.values[DG_HASH_DOMAIN_BELIEF_DB] = 0x6667u; /* behavioral-only divergence */

    DET_ASSERT(det_build_registry(&hr_expected, &ctx_expected) == 0);
    DET_ASSERT(det_build_registry(&hr_actual, &ctx_actual) == 0);

    DET_ASSERT(det_record_ticks(&expected, &hr_expected, 10u, 3u) == 0);
    DET_ASSERT(det_record_ticks(&actual, &hr_actual, 10u, 3u) == 0);

    dg_replay_mismatch_clear(&mm);
    rc = dg_replay_validate(DG_REPLAY_VALIDATE_STRUCTURAL, &expected, &actual, &mm);
    DET_ASSERT(rc == 0);

    dg_replay_mismatch_clear(&mm);
    rc = dg_replay_validate(DG_REPLAY_VALIDATE_BEHAVIORAL, &expected, &actual, &mm);
    DET_ASSERT(rc == 1);
    DET_ASSERT(mm.ok == D_FALSE);
    DET_ASSERT(mm.tick == 10u);
    DET_ASSERT(mm.domain_id == DG_HASH_DOMAIN_BELIEF_DB);

    dg_replay_mismatch_clear(&mm);
    rc = dg_replay_validate(DG_REPLAY_VALIDATE_STRICT, &expected, &actual, &mm);
    DET_ASSERT(rc == 1);
    DET_ASSERT(mm.ok == D_FALSE);
    DET_ASSERT(mm.tick == 10u);
    DET_ASSERT(mm.domain_id == DG_HASH_DOMAIN_BELIEF_DB);

    dg_replay_stream_free(&expected);
    dg_replay_stream_free(&actual);
    dg_hash_registry_free(&hr_expected);
    dg_hash_registry_free(&hr_actual);
    return 0;
}

static int det_test_replay_structural_metadata_mismatch(void) {
    dg_hash_registry hr;
    det_domains_ctx ctx;
    dg_replay_stream expected;
    dg_replay_stream actual;
    dg_replay_mismatch mm;
    int rc;

    memset(&ctx, 0, sizeof(ctx));
    ctx.values[DG_HASH_DOMAIN_SCHEDULER_STATE] = 0x1111u;
    ctx.values[DG_HASH_DOMAIN_PACKET_STREAMS] = 0x2222u;
    ctx.values[DG_HASH_DOMAIN_DELTA_COMMIT_RESULTS] = 0x3333u;
    ctx.values[DG_HASH_DOMAIN_DOMAIN_STATES] = 0x4444u;
    ctx.values[DG_HASH_DOMAIN_GRAPH_STATES] = 0x5555u;
    ctx.values[DG_HASH_DOMAIN_BELIEF_DB] = 0x6666u;
    ctx.values[DG_HASH_DOMAIN_COMMS_QUEUES] = 0x7777u;
    ctx.values[DG_HASH_DOMAIN_PROMO_LOD_STATE] = 0x8888u;

    DET_ASSERT(det_build_registry(&hr, &ctx) == 0);
    DET_ASSERT(det_record_ticks(&expected, &hr, 10u, 3u) == 0);
    DET_ASSERT(det_record_ticks(&actual, &hr, 10u, 3u) == 0);

    /* 1) Content pack ID mismatch (structural). */
    {
        u64 packs_a[2] = { 100u, 200u };
        u64 packs_b[2] = { 100u, 201u };
        DET_ASSERT(dg_replay_stream_set_content_pack_ids(&expected, packs_a, 2u) == 0);
        DET_ASSERT(dg_replay_stream_set_content_pack_ids(&actual, packs_b, 2u) == 0);

        dg_replay_mismatch_clear(&mm);
        rc = dg_replay_validate(DG_REPLAY_VALIDATE_STRUCTURAL, &expected, &actual, &mm);
        DET_ASSERT(rc == 1);
        DET_ASSERT(mm.ok == D_FALSE);
        DET_ASSERT(mm.tick == 0u);
        DET_ASSERT(mm.domain_id == DG_HASH_DOMAIN_DOMAIN_STATES);
        DET_ASSERT(mm.expected_hash == 200u);
        DET_ASSERT(mm.actual_hash == 201u);
    }

    /* 2) ID remap mismatch (structural). */
    {
        dg_replay_id_remap remap_a[2];
        dg_replay_id_remap remap_b[2];
        u64 packs[2] = { 100u, 200u };

        DET_ASSERT(dg_replay_stream_set_content_pack_ids(&expected, packs, 2u) == 0);
        DET_ASSERT(dg_replay_stream_set_content_pack_ids(&actual, packs, 2u) == 0);

        remap_a[0].from_id = 1u; remap_a[0].to_id = 101u;
        remap_a[1].from_id = 2u; remap_a[1].to_id = 202u;
        remap_b[0] = remap_a[0];
        remap_b[1] = remap_a[1];
        remap_b[1].to_id = 203u; /* divergence */

        DET_ASSERT(dg_replay_stream_set_id_remaps(&expected, remap_a, 2u) == 0);
        DET_ASSERT(dg_replay_stream_set_id_remaps(&actual, remap_b, 2u) == 0);

        dg_replay_mismatch_clear(&mm);
        rc = dg_replay_validate(DG_REPLAY_VALIDATE_STRUCTURAL, &expected, &actual, &mm);
        DET_ASSERT(rc == 1);
        DET_ASSERT(mm.ok == D_FALSE);
        DET_ASSERT(mm.tick == 0u);
        DET_ASSERT(mm.domain_id == DG_HASH_DOMAIN_DOMAIN_STATES);
        DET_ASSERT(mm.expected_hash == 202u);
        DET_ASSERT(mm.actual_hash == 203u);
    }

    dg_replay_stream_free(&expected);
    dg_replay_stream_free(&actual);
    dg_hash_registry_free(&hr);
    return 0;
}

static int det_test_replay_input_ordering_and_mismatch(void) {
    dg_hash_registry hr;
    det_domains_ctx ctx;
    dg_replay_stream expected;
    dg_replay_stream actual;
    dg_replay_mismatch mm;
    int rc;

    memset(&ctx, 0, sizeof(ctx));
    ctx.values[DG_HASH_DOMAIN_SCHEDULER_STATE] = 0x1111u;
    ctx.values[DG_HASH_DOMAIN_PACKET_STREAMS] = 0x2222u;
    ctx.values[DG_HASH_DOMAIN_DELTA_COMMIT_RESULTS] = 0x3333u;
    ctx.values[DG_HASH_DOMAIN_DOMAIN_STATES] = 0x4444u;
    ctx.values[DG_HASH_DOMAIN_GRAPH_STATES] = 0x5555u;
    ctx.values[DG_HASH_DOMAIN_BELIEF_DB] = 0x6666u;
    ctx.values[DG_HASH_DOMAIN_COMMS_QUEUES] = 0x7777u;
    ctx.values[DG_HASH_DOMAIN_PROMO_LOD_STATE] = 0x8888u;

    DET_ASSERT(det_build_registry(&hr, &ctx) == 0);
    DET_ASSERT(det_record_ticks(&expected, &hr, 10u, 3u) == 0);
    DET_ASSERT(det_record_ticks(&actual, &hr, 10u, 3u) == 0);

    /* Same inputs, different insertion order -> must still validate. */
    DET_ASSERT(det_record_two_inputs(&expected, 10u, 0, 7u, 9u) == 0);
    DET_ASSERT(det_record_two_inputs(&actual, 10u, 1, 7u, 9u) == 0);

    dg_replay_mismatch_clear(&mm);
    rc = dg_replay_validate(DG_REPLAY_VALIDATE_STRICT, &expected, &actual, &mm);
    DET_ASSERT(rc == 0);

    /* Input mismatch (hash domains still match) -> detected as packet stream divergence. */
    DET_ASSERT(det_record_two_inputs(&actual, 11u, 0, 7u, 999u) == 0);

    dg_replay_mismatch_clear(&mm);
    rc = dg_replay_validate(DG_REPLAY_VALIDATE_BEHAVIORAL, &expected, &actual, &mm);
    DET_ASSERT(rc == 1);
    DET_ASSERT(mm.ok == D_FALSE);
    DET_ASSERT(mm.tick == 11u);
    DET_ASSERT(mm.domain_id == DG_HASH_DOMAIN_PACKET_STREAMS);

    dg_replay_stream_free(&expected);
    dg_replay_stream_free(&actual);
    dg_hash_registry_free(&hr);
    return 0;
}

int main(void) {
    int rc;
    rc = det_test_replay_validation_modes();
    if (rc != 0) return rc;
    rc = det_test_replay_structural_metadata_mismatch();
    if (rc != 0) return rc;
    rc = det_test_replay_input_ordering_and_mismatch();
    if (rc != 0) return rc;
    return 0;
}
