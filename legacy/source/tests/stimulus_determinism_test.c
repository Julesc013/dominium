/*
FILE: source/tests/stimulus_determinism_test.c
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
#include <stdio.h>

#include "sim/bus/dg_event_bus.h"
#include "sim/bus/dg_message_bus.h"
#include "sim/bus/dg_field.h"
#include "res/dg_tlv_canon.h"

#define TEST_ASSERT(cond) do { if (!(cond)) return __LINE__; } while (0)

typedef struct test_log_entry {
    u64 src_entity;
    u32 seq;
    u32 sub_id;
} test_log_entry;

typedef struct test_log {
    test_log_entry entries[128];
    u32            count;
} test_log;

typedef struct test_cb_ctx {
    test_log *log;
    u32       sub_id;
} test_cb_ctx;

static void test_log_init(test_log *log) {
    if (!log) return;
    memset(log, 0, sizeof(*log));
}

static void test_event_cb(const dg_pkt_event *ev, void *user_ctx) {
    test_cb_ctx *ctx;
    if (!ev || !user_ctx) return;
    ctx = (test_cb_ctx *)user_ctx;
    if (!ctx->log) return;
    if (ctx->log->count >= (u32)(sizeof(ctx->log->entries) / sizeof(ctx->log->entries[0]))) return;
    ctx->log->entries[ctx->log->count].src_entity = ev->hdr.src_entity;
    ctx->log->entries[ctx->log->count].seq = ev->hdr.seq;
    ctx->log->entries[ctx->log->count].sub_id = ctx->sub_id;
    ctx->log->count += 1u;
}

static void test_message_cb(const dg_pkt_message *msg, void *user_ctx) {
    test_cb_ctx *ctx;
    if (!msg || !user_ctx) return;
    ctx = (test_cb_ctx *)user_ctx;
    if (!ctx->log) return;
    if (ctx->log->count >= (u32)(sizeof(ctx->log->entries) / sizeof(ctx->log->entries[0]))) return;
    ctx->log->entries[ctx->log->count].src_entity = msg->hdr.src_entity;
    ctx->log->entries[ctx->log->count].seq = msg->hdr.seq;
    ctx->log->entries[ctx->log->count].sub_id = ctx->sub_id;
    ctx->log->count += 1u;
}

static int test_logs_equal(const test_log *a, const test_log *b) {
    if (!a || !b) return 0;
    if (a->count != b->count) return 0;
    if (a->count == 0u) return 1;
    return memcmp(a->entries, b->entries, sizeof(test_log_entry) * (size_t)a->count) == 0;
}

static int run_event_scenario(int variant, test_log *out_log) {
    const dg_type_id EVT_TYPE = 0x1001ULL;
    dg_event_bus bus;
    dg_budget budget;
    test_cb_ctx c1, c2, c3;
    dg_pkt_event e1, e2, e3;
    dg_tick tick = 1u;
    u32 delivered;

    if (!out_log) return -1;
    test_log_init(out_log);

    dg_event_bus_init(&bus);
    dg_budget_init(&budget);

    /* Unlimited global budget (events use domain_id/chunk_id = 0). */
    dg_budget_set_limits(&budget, DG_BUDGET_UNLIMITED, DG_BUDGET_UNLIMITED, DG_BUDGET_UNLIMITED);
    dg_budget_begin_tick(&budget, tick);

    memset(&c1, 0, sizeof(c1));
    memset(&c2, 0, sizeof(c2));
    memset(&c3, 0, sizeof(c3));
    c1.log = out_log; c1.sub_id = 1u;
    c2.log = out_log; c2.sub_id = 2u;
    c3.log = out_log; c3.sub_id = 3u;

    /* Priorities: subscriber 2 first, then 1, then 3 (tie on priority). */
    TEST_ASSERT(dg_event_bus_subscribe(&bus, EVT_TYPE, test_event_cb, 10u, &c1) == 0);
    TEST_ASSERT(dg_event_bus_subscribe(&bus, EVT_TYPE, test_event_cb, 5u,  &c2) == 0);
    TEST_ASSERT(dg_event_bus_subscribe(&bus, EVT_TYPE, test_event_cb, 10u, &c3) == 0);

    memset(&e1, 0, sizeof(e1));
    memset(&e2, 0, sizeof(e2));
    memset(&e3, 0, sizeof(e3));

    /* Events: same tick/type/dst, different src/seq. */
    e1.hdr.type_id = EVT_TYPE; e1.hdr.tick = tick; e1.hdr.src_entity = 2u; e1.hdr.dst_entity = 0u; e1.hdr.seq = 2u;
    e2.hdr.type_id = EVT_TYPE; e2.hdr.tick = tick; e2.hdr.src_entity = 1u; e2.hdr.dst_entity = 0u; e2.hdr.seq = 1u;
    e3.hdr.type_id = EVT_TYPE; e3.hdr.tick = tick; e3.hdr.src_entity = 1u; e3.hdr.dst_entity = 0u; e3.hdr.seq = 2u;
    e1.payload = (const unsigned char *)0; e1.payload_len = 0u;
    e2.payload = (const unsigned char *)0; e2.payload_len = 0u;
    e3.payload = (const unsigned char *)0; e3.payload_len = 0u;

    if (variant == 0) {
        TEST_ASSERT(dg_event_bus_publish(&bus, &e1) == 0);
        TEST_ASSERT(dg_event_bus_publish(&bus, &e2) == 0);
        TEST_ASSERT(dg_event_bus_publish(&bus, &e3) == 0);
    } else {
        TEST_ASSERT(dg_event_bus_publish(&bus, &e3) == 0);
        TEST_ASSERT(dg_event_bus_publish(&bus, &e1) == 0);
        TEST_ASSERT(dg_event_bus_publish(&bus, &e2) == 0);
    }

    delivered = dg_event_bus_deliver(&bus, &budget, tick);
    TEST_ASSERT(delivered == 9u);
    TEST_ASSERT(out_log->count == 9u);

    dg_event_bus_free(&bus);
    dg_budget_free(&budget);
    return 0;
}

static int test_event_determinism(void) {
    test_log a, b;
    int rc;
    rc = run_event_scenario(0, &a);
    TEST_ASSERT(rc == 0);
    rc = run_event_scenario(1, &b);
    TEST_ASSERT(rc == 0);
    TEST_ASSERT(test_logs_equal(&a, &b));
    return 0;
}

static int run_message_scenario(int variant, test_log *out_log) {
    const dg_entity_id DST = 42u;
    const dg_type_id MSG_TYPE = 0x2001ULL;
    dg_message_bus bus;
    dg_budget budget;
    test_cb_ctx c1, c2;
    dg_pkt_message m1, m2, m3;
    dg_tick tick = 1u;
    u32 delivered;

    if (!out_log) return -1;
    test_log_init(out_log);

    dg_message_bus_init(&bus);
    dg_budget_init(&budget);

    dg_budget_set_limits(&budget, DG_BUDGET_UNLIMITED, DG_BUDGET_UNLIMITED, DG_BUDGET_UNLIMITED);
    dg_budget_begin_tick(&budget, tick);

    memset(&c1, 0, sizeof(c1));
    memset(&c2, 0, sizeof(c2));
    c1.log = out_log; c1.sub_id = 10u;
    c2.log = out_log; c2.sub_id = 11u;

    TEST_ASSERT(dg_message_bus_subscribe(&bus, DST, MSG_TYPE, test_message_cb, 0u, &c1) == 0);
    TEST_ASSERT(dg_message_bus_subscribe(&bus, DST, MSG_TYPE, test_message_cb, 0u, &c2) == 0);

    memset(&m1, 0, sizeof(m1));
    memset(&m2, 0, sizeof(m2));
    memset(&m3, 0, sizeof(m3));

    m1.hdr.type_id = MSG_TYPE; m1.hdr.tick = tick; m1.hdr.dst_entity = DST; m1.hdr.src_entity = 2u; m1.hdr.seq = 1u;
    m2.hdr.type_id = MSG_TYPE; m2.hdr.tick = tick; m2.hdr.dst_entity = DST; m2.hdr.src_entity = 1u; m2.hdr.seq = 2u;
    m3.hdr.type_id = MSG_TYPE; m3.hdr.tick = tick; m3.hdr.dst_entity = DST; m3.hdr.src_entity = 1u; m3.hdr.seq = 1u;
    m1.payload = (const unsigned char *)0; m1.payload_len = 0u;
    m2.payload = (const unsigned char *)0; m2.payload_len = 0u;
    m3.payload = (const unsigned char *)0; m3.payload_len = 0u;

    if (variant == 0) {
        TEST_ASSERT(dg_message_bus_send(&bus, &m1) == 0);
        TEST_ASSERT(dg_message_bus_send(&bus, &m2) == 0);
        TEST_ASSERT(dg_message_bus_send(&bus, &m3) == 0);
    } else {
        TEST_ASSERT(dg_message_bus_send(&bus, &m3) == 0);
        TEST_ASSERT(dg_message_bus_send(&bus, &m1) == 0);
        TEST_ASSERT(dg_message_bus_send(&bus, &m2) == 0);
    }

    delivered = dg_message_bus_deliver(&bus, &budget, tick);
    TEST_ASSERT(delivered == 6u);
    TEST_ASSERT(out_log->count == 6u);

    dg_message_bus_free(&bus);
    dg_budget_free(&budget);
    return 0;
}

static int test_message_determinism(void) {
    test_log a, b;
    int rc;
    rc = run_message_scenario(0, &a);
    TEST_ASSERT(rc == 0);
    rc = run_message_scenario(1, &b);
    TEST_ASSERT(rc == 0);
    TEST_ASSERT(test_logs_equal(&a, &b));
    return 0;
}

static void build_field_set_cell_tlv(
    unsigned char *out,
    u32            out_cap,
    u32           *out_len,
    u16            x,
    u16            y,
    u16            z,
    q16_16         v
) {
    unsigned char payload[6 + 4];
    u32 tlv_len;

    if (!out_len) return;
    *out_len = 0u;
    if (!out || out_cap < (u32)(8 + sizeof(payload))) return;

    dg_le_write_u16(payload + 0u, x);
    dg_le_write_u16(payload + 2u, y);
    dg_le_write_u16(payload + 4u, z);
    dg_le_write_u32(payload + 6u, (u32)(i32)v);

    dg_le_write_u32(out + 0u, DG_FIELD_TLV_SET_CELL);
    dg_le_write_u32(out + 4u, (u32)sizeof(payload));
    memcpy(out + 8u, payload, sizeof(payload));

    tlv_len = 8u + (u32)sizeof(payload);
    *out_len = tlv_len;
}

static int run_field_scenario(int variant, q16_16 *out_sample) {
    const dg_type_id FIELD_TYPE = 0x3001ULL;
    const dg_domain_id DOMAIN = 1u;
    const dg_chunk_id CHUNK = 2u;
    dg_field field;
    dg_budget budget;
    dg_field_type_desc td;
    dg_pkt_field_update u1, u2;
    unsigned char tlv1[32];
    unsigned char tlv2[32];
    u32 tlv1_len, tlv2_len;
    dg_field_pos pos;
    q16_16 sample[DG_FIELD_MAX_DIM];
    int rc;

    if (!out_sample) return -1;
    *out_sample = 0;

    dg_field_init(&field);
    dg_budget_init(&budget);
    TEST_ASSERT(dg_budget_reserve(&budget, 16u, 16u) == 0);
    dg_budget_set_limits(&budget, DG_BUDGET_UNLIMITED, DG_BUDGET_UNLIMITED, DG_BUDGET_UNLIMITED);
    dg_budget_begin_tick(&budget, 1u);

    memset(&td, 0, sizeof(td));
    td.field_type_id = FIELD_TYPE;
    td.dim = 1u;
    td.res = 4u;
    TEST_ASSERT(dg_field_register_type(&field, &td) == 0);

    memset(&u1, 0, sizeof(u1));
    memset(&u2, 0, sizeof(u2));
    u1.hdr.type_id = FIELD_TYPE; u1.hdr.tick = 1u; u1.hdr.domain_id = DOMAIN; u1.hdr.chunk_id = CHUNK; u1.hdr.seq = 2u;
    u2.hdr.type_id = FIELD_TYPE; u2.hdr.tick = 1u; u2.hdr.domain_id = DOMAIN; u2.hdr.chunk_id = CHUNK; u2.hdr.seq = 1u;

    build_field_set_cell_tlv(tlv1, (u32)sizeof(tlv1), &tlv1_len, 1u, 1u, 1u, (q16_16)(100 << Q16_16_FRAC_BITS));
    build_field_set_cell_tlv(tlv2, (u32)sizeof(tlv2), &tlv2_len, 1u, 1u, 1u, (q16_16)(200 << Q16_16_FRAC_BITS));
    u1.payload = tlv1; u1.payload_len = tlv1_len; u1.hdr.payload_len = tlv1_len;
    u2.payload = tlv2; u2.payload_len = tlv2_len; u2.hdr.payload_len = tlv2_len;

    if (variant == 0) {
        TEST_ASSERT(dg_field_publish_update(&field, &u1) == 0);
        TEST_ASSERT(dg_field_publish_update(&field, &u2) == 0);
    } else {
        TEST_ASSERT(dg_field_publish_update(&field, &u2) == 0);
        TEST_ASSERT(dg_field_publish_update(&field, &u1) == 0);
    }

    (void)dg_field_apply_updates(&field, &budget, 1u);

    memset(&pos, 0, sizeof(pos));
    pos.chunk_id = CHUNK;
    pos.x = (q16_16)(1 << Q16_16_FRAC_BITS);
    pos.y = (q16_16)(1 << Q16_16_FRAC_BITS);
    pos.z = (q16_16)(1 << Q16_16_FRAC_BITS);

    rc = dg_field_sample(&field, &budget, DOMAIN, &pos, FIELD_TYPE, sample, DG_FIELD_MAX_DIM);
    TEST_ASSERT(rc == 0);
    *out_sample = sample[0];

    dg_field_free(&field);
    dg_budget_free(&budget);
    return 0;
}

static int test_field_determinism(void) {
    q16_16 a, b;
    q16_16 expected;
    int rc;
    rc = run_field_scenario(0, &a);
    TEST_ASSERT(rc == 0);
    rc = run_field_scenario(1, &b);
    TEST_ASSERT(rc == 0);
    TEST_ASSERT(a == b);
    /* Sorted by seq: u2(seq=1) applies first, then u1(seq=2) => final 100. */
    expected = (q16_16)(100 << Q16_16_FRAC_BITS);
    if (a != expected) {
        printf("field_determinism: expected=%ld got=%ld\n", (long)expected, (long)a);
        return __LINE__;
    }
    return 0;
}

int main(void) {
    int rc;

    rc = test_event_determinism();
    if (rc != 0) return rc;
    rc = test_message_determinism();
    if (rc != 0) return rc;
    rc = test_field_determinism();
    if (rc != 0) return rc;

    return 0;
}
