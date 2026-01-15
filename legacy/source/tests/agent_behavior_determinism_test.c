/*
FILE: source/tests/agent_behavior_determinism_test.c
MODULE: Repository
LAYER / SUBSYSTEM: source/tests
RESPONSIBILITY: Owns documentation for this translation unit.
ALLOWED DEPENDENCIES: Project-local headers; C89/C++98 standard headers.
FORBIDDEN DEPENDENCIES: N/A.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A.
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include <string.h>

#include "res/dg_tlv_canon.h"

#include "sim/sched/dg_budget.h"
#include "sim/sched/dg_phase.h"

#include "sim/sense/dg_sensor_registry.h"
#include "agent/mind/dg_mind_registry.h"
#include "agent/act/dg_intent_dispatch.h"

#include "sim/act/dg_delta_registry.h"
#include "sim/act/dg_delta_commit.h"

#define TEST_ASSERT(cond) do { if (!(cond)) return __LINE__; } while (0)

typedef struct test_world_state {
    u32 a;
    u32 b;
} test_world_state;

static int hdr_equal(const dg_pkt_hdr *a, const dg_pkt_hdr *b) {
    if (!a || !b) return 0;
    if (a->type_id != b->type_id) return 0;
    if (a->schema_id != b->schema_id) return 0;
    if (a->schema_ver != b->schema_ver) return 0;
    if (a->flags != b->flags) return 0;
    if (a->tick != b->tick) return 0;
    if (a->src_entity != b->src_entity) return 0;
    if (a->dst_entity != b->dst_entity) return 0;
    if (a->domain_id != b->domain_id) return 0;
    if (a->chunk_id != b->chunk_id) return 0;
    if (a->seq != b->seq) return 0;
    if (a->payload_len != b->payload_len) return 0;
    return 1;
}

static int obs_buffers_equal(const dg_observation_buffer *a, const dg_observation_buffer *b) {
    u32 i;
    if (!a || !b) return 0;
    if (a->tick != b->tick) return 0;
    if (a->agent_id != b->agent_id) return 0;
    if (dg_observation_buffer_count(a) != dg_observation_buffer_count(b)) return 0;
    for (i = 0u; i < dg_observation_buffer_count(a); ++i) {
        const dg_observation_record *ra = dg_observation_buffer_at(a, i);
        const dg_observation_record *rb = dg_observation_buffer_at(b, i);
        if (!ra || !rb) return 0;
        if (!hdr_equal(&ra->hdr, &rb->hdr)) return 0;
        if (ra->payload_len != rb->payload_len) return 0;
        if (ra->payload_len != 0u) {
            if (!ra->payload || !rb->payload) return 0;
            if (memcmp(ra->payload, rb->payload, (size_t)ra->payload_len) != 0) return 0;
        }
    }
    return 1;
}

static int intent_buffers_equal(const dg_intent_buffer *a, const dg_intent_buffer *b) {
    u32 i;
    if (!a || !b) return 0;
    if (a->tick != b->tick) return 0;
    if (dg_intent_buffer_count(a) != dg_intent_buffer_count(b)) return 0;
    for (i = 0u; i < dg_intent_buffer_count(a); ++i) {
        const dg_intent_record *ra = dg_intent_buffer_at(a, i);
        const dg_intent_record *rb = dg_intent_buffer_at(b, i);
        if (!ra || !rb) return 0;
        if (!hdr_equal(&ra->hdr, &rb->hdr)) return 0;
        if (ra->payload_len != rb->payload_len) return 0;
        if (ra->payload_len != 0u) {
            if (!ra->payload || !rb->payload) return 0;
            if (memcmp(ra->payload, rb->payload, (size_t)ra->payload_len) != 0) return 0;
        }
    }
    return 1;
}

static int delta_buffers_equal(const dg_delta_buffer *a, const dg_delta_buffer *b) {
    u32 i;
    if (!a || !b) return 0;
    if (a->tick != b->tick) return 0;
    if (dg_delta_buffer_count(a) != dg_delta_buffer_count(b)) return 0;
    for (i = 0u; i < dg_delta_buffer_count(a); ++i) {
        const dg_delta_record *ra = dg_delta_buffer_at(a, i);
        const dg_delta_record *rb = dg_delta_buffer_at(b, i);
        if (!ra || !rb) return 0;
        if (dg_order_key_cmp(&ra->key, &rb->key) != 0) return 0;
        if (!hdr_equal(&ra->hdr, &rb->hdr)) return 0;
        if (ra->payload_len != rb->payload_len) return 0;
        if (ra->payload_len != 0u) {
            if (!ra->payload || !rb->payload) return 0;
            if (memcmp(ra->payload, rb->payload, (size_t)ra->payload_len) != 0) return 0;
        }
    }
    return 1;
}

static void build_u32_tlv(unsigned char *out, u32 out_cap, u32 tag, u32 v, u32 *out_len) {
    if (out_len) *out_len = 0u;
    if (!out || !out_len) return;
    if (out_cap < 12u) return;
    dg_le_write_u32(out + 0u, tag);
    dg_le_write_u32(out + 4u, 4u);
    dg_le_write_u32(out + 8u, v);
    *out_len = 12u;
}

static int test_sensor_a_sample(
    dg_agent_id agent_id,
    const void *observer_ctx,
    dg_tick tick,
    u32 *io_seq,
    dg_observation_buffer *out_obs
) {
    const test_world_state *w;
    dg_pkt_observation obs;
    unsigned char payload[12];
    u32 payload_len;

    (void)io_seq;
    if (!observer_ctx || !out_obs) return -1;
    w = (const test_world_state *)observer_ctx;

    memset(&obs, 0, sizeof(obs));
    obs.hdr.type_id = 0x5101ULL;
    obs.hdr.tick = tick;
    obs.hdr.src_entity = 1001u;
    obs.hdr.dst_entity = agent_id;
    obs.hdr.seq = 0u;

    build_u32_tlv(payload, (u32)sizeof(payload), 1u, w->a, &payload_len);
    obs.hdr.payload_len = payload_len;
    obs.payload = payload;
    obs.payload_len = payload_len;

    return dg_observation_buffer_push(out_obs, &obs);
}

static int test_sensor_b_sample(
    dg_agent_id agent_id,
    const void *observer_ctx,
    dg_tick tick,
    u32 *io_seq,
    dg_observation_buffer *out_obs
) {
    const test_world_state *w;
    dg_pkt_observation obs;
    unsigned char payload[12];
    u32 payload_len;

    (void)io_seq;
    if (!observer_ctx || !out_obs) return -1;
    w = (const test_world_state *)observer_ctx;

    memset(&obs, 0, sizeof(obs));
    obs.hdr.type_id = 0x5102ULL;
    obs.hdr.tick = tick;
    obs.hdr.src_entity = 1002u;
    obs.hdr.dst_entity = agent_id;
    obs.hdr.seq = 0u;

    build_u32_tlv(payload, (u32)sizeof(payload), 2u, w->b, &payload_len);
    obs.hdr.payload_len = payload_len;
    obs.payload = payload;
    obs.payload_len = payload_len;

    return dg_observation_buffer_push(out_obs, &obs);
}

static int run_sensor_scenario(int variant, dg_observation_buffer *out_obs) {
    dg_sensor_registry reg;
    dg_sensor_desc sa, sb;
    dg_budget budget;
    dg_tick tick = 1u;
    dg_agent_id agent_id = 42u;
    test_world_state w;
    int rc;

    if (!out_obs) return -1;

    memset(&w, 0, sizeof(w));
    w.a = 123u;
    w.b = 456u;

    dg_sensor_registry_init(&reg);
    dg_budget_init(&budget);
    dg_budget_set_limits(&budget, DG_BUDGET_UNLIMITED, DG_BUDGET_UNLIMITED, DG_BUDGET_UNLIMITED);
    dg_budget_begin_tick(&budget, tick);

    memset(&sa, 0, sizeof(sa));
    memset(&sb, 0, sizeof(sb));
    sa.sensor_id = 0x5101ULL;
    sa.vtbl.sample = test_sensor_a_sample;
    sa.stride = 0u;
    sb.sensor_id = 0x5102ULL;
    sb.vtbl.sample = test_sensor_b_sample;
    sb.stride = 0u;

    if (variant == 0) {
        TEST_ASSERT(dg_sensor_registry_add(&reg, &sa) == 0);
        TEST_ASSERT(dg_sensor_registry_add(&reg, &sb) == 0);
    } else {
        TEST_ASSERT(dg_sensor_registry_add(&reg, &sb) == 0);
        TEST_ASSERT(dg_sensor_registry_add(&reg, &sa) == 0);
    }

    rc = dg_sensor_registry_sample_agent(&reg, tick, agent_id, &w, &budget, (const dg_budget_scope *)0, (dg_work_queue *)0, out_obs, (u32 *)0);
    TEST_ASSERT(rc == 0);
    dg_observation_buffer_canonize(out_obs);

    dg_sensor_registry_free(&reg);
    dg_budget_free(&budget);
    return 0;
}

static int test_sensor_determinism(void) {
    dg_observation_buffer a, b;

    dg_observation_buffer_init(&a);
    dg_observation_buffer_init(&b);
    TEST_ASSERT(dg_observation_buffer_reserve(&a, 16u, 256u) == 0);
    TEST_ASSERT(dg_observation_buffer_reserve(&b, 16u, 256u) == 0);
    dg_observation_buffer_begin_tick(&a, 1u, 42u);
    dg_observation_buffer_begin_tick(&b, 1u, 42u);

    TEST_ASSERT(run_sensor_scenario(0, &a) == 0);
    TEST_ASSERT(run_sensor_scenario(1, &b) == 0);
    TEST_ASSERT(obs_buffers_equal(&a, &b));

    dg_observation_buffer_free(&a);
    dg_observation_buffer_free(&b);
    return 0;
}

static int test_mind_step(
    dg_agent_id agent_id,
    const dg_observation_buffer *observations,
    void *internal_state,
    dg_tick tick,
    u32 budget_units,
    u32 *io_seq,
    dg_intent_emit_fn emit,
    void *emit_ctx
) {
    dg_pkt_intent intent;
    unsigned char payload[12];
    u32 payload_len;
    u32 count;

    (void)internal_state;
    (void)budget_units;
    (void)io_seq;
    if (!emit) return -1;

    count = observations ? dg_observation_buffer_count(observations) : 0u;

    memset(&intent, 0, sizeof(intent));
    intent.hdr.type_id = 0x6101ULL;
    intent.hdr.tick = tick;
    intent.hdr.src_entity = agent_id;
    intent.hdr.seq = 0u;

    build_u32_tlv(payload, (u32)sizeof(payload), 10u, count, &payload_len);
    intent.hdr.payload_len = payload_len;
    intent.payload = payload;
    intent.payload_len = payload_len;

    return emit(&intent, emit_ctx);
}

static int run_mind_scenario(int variant, dg_intent_buffer *out_intents) {
    dg_observation_buffer obs;
    dg_mind_registry minds;
    dg_mind_desc mind;
    dg_budget budget;
    dg_tick tick = 1u;
    dg_agent_id agent_id = 42u;
    int rc;

    if (!out_intents) return -1;

    dg_observation_buffer_init(&obs);
    TEST_ASSERT(dg_observation_buffer_reserve(&obs, 16u, 256u) == 0);
    dg_observation_buffer_begin_tick(&obs, tick, agent_id);
    TEST_ASSERT(run_sensor_scenario(variant, &obs) == 0);

    dg_mind_registry_init(&minds);
    memset(&mind, 0, sizeof(mind));
    mind.mind_id = 0x7101ULL;
    mind.vtbl.step = test_mind_step;
    mind.stride = 0u;
    TEST_ASSERT(dg_mind_registry_add(&minds, &mind) == 0);

    dg_budget_init(&budget);
    dg_budget_set_limits(&budget, DG_BUDGET_UNLIMITED, DG_BUDGET_UNLIMITED, DG_BUDGET_UNLIMITED);
    dg_budget_begin_tick(&budget, tick);

    rc = dg_mind_registry_step_agent(&minds, mind.mind_id, tick, agent_id, &obs, (void *)0, &budget, (const dg_budget_scope *)0, (dg_work_queue *)0, out_intents, (u32 *)0);
    TEST_ASSERT(rc == 0);
    dg_intent_buffer_canonize(out_intents);

    dg_budget_free(&budget);
    dg_mind_registry_free(&minds);
    dg_observation_buffer_free(&obs);
    return 0;
}

static int test_mind_determinism(void) {
    dg_intent_buffer a, b;

    dg_intent_buffer_init(&a);
    dg_intent_buffer_init(&b);
    TEST_ASSERT(dg_intent_buffer_reserve(&a, 16u, 256u) == 0);
    TEST_ASSERT(dg_intent_buffer_reserve(&b, 16u, 256u) == 0);
    dg_intent_buffer_begin_tick(&a, 1u);
    dg_intent_buffer_begin_tick(&b, 1u);

    TEST_ASSERT(run_mind_scenario(0, &a) == 0);
    TEST_ASSERT(run_mind_scenario(1, &b) == 0);
    TEST_ASSERT(intent_buffers_equal(&a, &b));

    dg_intent_buffer_free(&a);
    dg_intent_buffer_free(&b);
    return 0;
}

static void fill_intent(dg_pkt_intent *out, dg_tick tick, dg_agent_id agent_id, dg_type_id type_id, u32 seq) {
    if (!out) return;
    memset(out, 0, sizeof(*out));
    out->hdr.tick = tick;
    out->hdr.src_entity = agent_id;
    out->hdr.type_id = type_id;
    out->hdr.seq = seq;
    out->hdr.payload_len = 0u;
    out->payload = (const unsigned char *)0;
    out->payload_len = 0u;
}

static int test_intent_ordering(void) {
    dg_intent_buffer a, b;
    dg_pkt_intent intents[4];

    dg_intent_buffer_init(&a);
    dg_intent_buffer_init(&b);
    TEST_ASSERT(dg_intent_buffer_reserve(&a, 16u, 64u) == 0);
    TEST_ASSERT(dg_intent_buffer_reserve(&b, 16u, 64u) == 0);
    dg_intent_buffer_begin_tick(&a, 1u);
    dg_intent_buffer_begin_tick(&b, 1u);

    fill_intent(&intents[0], 1u, 2u, 0x8002ULL, 1u);
    fill_intent(&intents[1], 1u, 1u, 0x8001ULL, 2u);
    fill_intent(&intents[2], 1u, 1u, 0x8001ULL, 1u);
    fill_intent(&intents[3], 1u, 1u, 0x8000ULL, 5u);

    /* Variant A insertion order. */
    TEST_ASSERT(dg_intent_buffer_push(&a, &intents[0]) == 0);
    TEST_ASSERT(dg_intent_buffer_push(&a, &intents[1]) == 0);
    TEST_ASSERT(dg_intent_buffer_push(&a, &intents[2]) == 0);
    TEST_ASSERT(dg_intent_buffer_push(&a, &intents[3]) == 0);

    /* Variant B insertion order (reversed/shuffled). */
    TEST_ASSERT(dg_intent_buffer_push(&b, &intents[3]) == 0);
    TEST_ASSERT(dg_intent_buffer_push(&b, &intents[2]) == 0);
    TEST_ASSERT(dg_intent_buffer_push(&b, &intents[0]) == 0);
    TEST_ASSERT(dg_intent_buffer_push(&b, &intents[1]) == 0);

    dg_intent_buffer_canonize(&a);
    dg_intent_buffer_canonize(&b);
    TEST_ASSERT(intent_buffers_equal(&a, &b));

    /* Spot-check canonical order: agent=1 first; type_id ascending; then seq. */
    TEST_ASSERT(dg_intent_buffer_count(&a) == 4u);
    TEST_ASSERT(dg_intent_buffer_at(&a, 0u)->hdr.src_entity == 1u);
    TEST_ASSERT(dg_intent_buffer_at(&a, 0u)->hdr.type_id == 0x8000ULL);
    TEST_ASSERT(dg_intent_buffer_at(&a, 1u)->hdr.type_id == 0x8001ULL);
    TEST_ASSERT(dg_intent_buffer_at(&a, 1u)->hdr.seq == 1u);
    TEST_ASSERT(dg_intent_buffer_at(&a, 2u)->hdr.type_id == 0x8001ULL);
    TEST_ASSERT(dg_intent_buffer_at(&a, 2u)->hdr.seq == 2u);
    TEST_ASSERT(dg_intent_buffer_at(&a, 3u)->hdr.src_entity == 2u);

    dg_intent_buffer_free(&a);
    dg_intent_buffer_free(&b);
    return 0;
}

static d_bool test_action_validate(dg_agent_id agent_id, const dg_pkt_intent *intent, const void *world_state, u32 *out_reason) {
    (void)agent_id;
    (void)intent;
    (void)world_state;
    if (out_reason) *out_reason = 0u;
    return D_TRUE;
}

static int test_action_apply(
    dg_agent_id agent_id,
    const dg_pkt_intent *intent,
    const void *world_state,
    dg_action_emit_delta_fn emit_delta,
    void *emit_ctx
) {
    const test_world_state *w;
    dg_pkt_delta d;
    unsigned char payload[12];
    u32 payload_len;
    u32 v;

    if (!intent || !emit_delta) return -1;
    w = (const test_world_state *)world_state;
    v = (u32)agent_id + (intent->hdr.seq * 10u) + (w ? w->a : 0u);

    memset(&d, 0, sizeof(d));
    d.hdr.type_id = 0xD001ULL;
    d.hdr.tick = intent->hdr.tick;
    d.hdr.src_entity = agent_id;
    d.hdr.seq = 0u;

    build_u32_tlv(payload, (u32)sizeof(payload), 100u, v, &payload_len);
    d.hdr.payload_len = payload_len;
    d.payload = payload;
    d.payload_len = payload_len;

    return emit_delta(&d, emit_ctx);
}

static void test_delta_apply(void *world, const dg_pkt_delta *delta) {
    (void)world;
    (void)delta;
}

static int run_action_dispatch_scenario(int variant, dg_delta_buffer *out_deltas) {
    test_world_state w;
    dg_intent_buffer intents;
    dg_pkt_intent i1, i2;
    dg_action_registry actions;
    dg_action_vtbl av;
    dg_delta_registry deltas;
    dg_delta_handler_vtbl dv;
    dg_delta_commit_stats stats;

    memset(&w, 0, sizeof(w));
    w.a = 7u;

    dg_intent_buffer_init(&intents);
    TEST_ASSERT(dg_intent_buffer_reserve(&intents, 16u, 256u) == 0);
    dg_intent_buffer_begin_tick(&intents, 1u);

    fill_intent(&i1, 1u, 2u, 0x9001ULL, 2u);
    fill_intent(&i2, 1u, 1u, 0x9001ULL, 1u);

    if (variant == 0) {
        TEST_ASSERT(dg_intent_buffer_push(&intents, &i1) == 0);
        TEST_ASSERT(dg_intent_buffer_push(&intents, &i2) == 0);
    } else {
        TEST_ASSERT(dg_intent_buffer_push(&intents, &i2) == 0);
        TEST_ASSERT(dg_intent_buffer_push(&intents, &i1) == 0);
    }
    dg_intent_buffer_canonize(&intents);

    dg_action_registry_init(&actions);
    memset(&av, 0, sizeof(av));
    av.validate = test_action_validate;
    av.apply = test_action_apply;
    TEST_ASSERT(dg_action_registry_add(&actions, 0x9001ULL, &av, "test_action") == 0);

    TEST_ASSERT(dg_intent_dispatch_to_deltas(&intents, &actions, &w, out_deltas, (u16)DG_PH_ACTION) == 0);

    /* Sort deltas via commit pipeline and validate deterministic ordering. */
    dg_delta_registry_init(&deltas);
    memset(&dv, 0, sizeof(dv));
    dv.apply = test_delta_apply;
    TEST_ASSERT(dg_delta_registry_add(&deltas, 0xD001ULL, &dv, "test_delta") == 0);
    TEST_ASSERT(dg_delta_commit_apply((void *)0, &deltas, out_deltas, &stats) == 0);
    TEST_ASSERT(stats.deltas_applied == dg_delta_buffer_count(out_deltas));

    dg_delta_registry_free(&deltas);
    dg_action_registry_free(&actions);
    dg_intent_buffer_free(&intents);
    return 0;
}

static int test_action_dispatch_determinism(void) {
    dg_delta_buffer a, b;

    dg_delta_buffer_init(&a);
    dg_delta_buffer_init(&b);
    TEST_ASSERT(dg_delta_buffer_reserve(&a, 32u, 512u) == 0);
    TEST_ASSERT(dg_delta_buffer_reserve(&b, 32u, 512u) == 0);
    dg_delta_buffer_begin_tick(&a, 1u);
    dg_delta_buffer_begin_tick(&b, 1u);

    TEST_ASSERT(run_action_dispatch_scenario(0, &a) == 0);
    TEST_ASSERT(run_action_dispatch_scenario(1, &b) == 0);
    TEST_ASSERT(delta_buffers_equal(&a, &b));

    dg_delta_buffer_free(&a);
    dg_delta_buffer_free(&b);
    return 0;
}

int main(void) {
    int rc;

    rc = test_sensor_determinism();
    if (rc != 0) return rc;
    rc = test_mind_determinism();
    if (rc != 0) return rc;
    rc = test_intent_ordering();
    if (rc != 0) return rc;
    rc = test_action_dispatch_determinism();
    if (rc != 0) return rc;

    return 0;
}

