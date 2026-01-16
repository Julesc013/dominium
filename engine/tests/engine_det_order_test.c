/*
Deterministic ordering permutation tests.
*/
#include <string.h>

#include "domino/core/dom_time_events.h"
#include "domino/core/dom_ledger.h"
#include "domino/core/det_order.h"
#include "domino/core/fixed.h"

#include "sim/lod/dg_interest.h"

#define TEST_CHECK(cond) do { if (!(cond)) return 1; } while (0)

static int run_event_queue_order(const dom_time_event *events,
                                 const u32 *order,
                                 u32 count,
                                 u64 *out_ids) {
    dom_time_event_queue q;
    dom_time_event storage[8];
    dom_time_event ev;
    u32 i;
    int rc;

    rc = dom_time_event_queue_init(&q, storage, 8u);
    TEST_CHECK(rc == DOM_TIME_OK);

    for (i = 0u; i < count; ++i) {
        ev = events[order[i]];
        rc = dom_time_event_schedule(&q, &ev);
        TEST_CHECK(rc == DOM_TIME_OK);
    }

    for (i = 0u; i < count; ++i) {
        rc = dom_time_event_pop(&q, &ev);
        TEST_CHECK(rc == DOM_TIME_OK);
        out_ids[i] = ev.event_id;
    }
    return 0;
}

static int test_event_queue_ordering(void) {
    const dom_time_event events[5] = {
        { 7u,  10u, 1u, 0u },
        { 10u, 5u,  2u, 0u },
        { 6u,  10u, 0u, 0u },
        { 9u,  5u,  1u, 0u },
        { 8u,  10u, 1u, 0u }
    };
    const u32 order_a[5] = { 0u, 1u, 2u, 3u, 4u };
    const u32 order_b[5] = { 4u, 2u, 0u, 3u, 1u };
    const u64 expected[5] = { 9u, 10u, 6u, 7u, 8u };
    u64 ids_a[5];
    u64 ids_b[5];
    u32 i;

    TEST_CHECK(run_event_queue_order(events, order_a, 5u, ids_a) == 0);
    TEST_CHECK(run_event_queue_order(events, order_b, 5u, ids_b) == 0);

    for (i = 0u; i < 5u; ++i) {
        TEST_CHECK(ids_a[i] == expected[i]);
        TEST_CHECK(ids_b[i] == expected[i]);
    }
    return 0;
}

static int run_ledger_order(const dom_obligation_id_t *order,
                            u32 count,
                            u64 *out_ids) {
    dom_ledger ledger;
    dom_ledger_posting postings[2];
    dom_ledger_transaction tx;
    dom_time_event ev;
    u32 i;
    int rc;

    rc = dom_ledger_init(&ledger);
    TEST_CHECK(rc == DOM_LEDGER_OK);
    rc = dom_ledger_account_create(&ledger, 1u, 0u);
    TEST_CHECK(rc == DOM_LEDGER_OK);
    rc = dom_ledger_account_create(&ledger, 2u, 0u);
    TEST_CHECK(rc == DOM_LEDGER_OK);

    postings[0].account_id = 1u;
    postings[0].asset_id = 1u;
    postings[0].amount = -10;
    postings[0].lot_id = 0u;
    postings[0].provenance_id = 0u;

    postings[1].account_id = 2u;
    postings[1].asset_id = 1u;
    postings[1].amount = 10;
    postings[1].lot_id = 0u;
    postings[1].provenance_id = 0u;

    for (i = 0u; i < count; ++i) {
        tx.tx_id = (dom_transaction_id_t)order[i];
        tx.posting_count = 2u;
        tx.postings = postings;
        rc = dom_ledger_obligation_schedule(&ledger, order[i], 100u, &tx, 0);
        TEST_CHECK(rc == DOM_LEDGER_OK);
    }

    for (i = 0u; i < count; ++i) {
        rc = dom_time_event_pop(&ledger.event_queue, &ev);
        TEST_CHECK(rc == DOM_TIME_OK);
        out_ids[i] = ev.payload_id;
    }
    return 0;
}

static int test_ledger_obligation_ordering(void) {
    const dom_obligation_id_t order_a[2] = { 20u, 10u };
    const dom_obligation_id_t order_b[2] = { 10u, 20u };
    const u64 expected[2] = { 10u, 20u };
    u64 ids_a[2];
    u64 ids_b[2];

    TEST_CHECK(run_ledger_order(order_a, 2u, ids_a) == 0);
    TEST_CHECK(run_ledger_order(order_b, 2u, ids_b) == 0);
    TEST_CHECK(ids_a[0] == expected[0] && ids_a[1] == expected[1]);
    TEST_CHECK(ids_b[0] == expected[0] && ids_b[1] == expected[1]);
    return 0;
}

typedef struct interest_fixture {
    const dg_interest_volume *vols;
    u32 count;
} interest_fixture;

static void interest_source(dg_tick tick, dg_interest_list *out_list, void *user_ctx) {
    interest_fixture *fix = (interest_fixture *)user_ctx;
    u32 i;
    (void)tick;
    if (!fix || !out_list) {
        return;
    }
    for (i = 0u; i < fix->count; ++i) {
        (void)dg_interest_list_push(out_list, &fix->vols[i]);
    }
}

static int interest_volume_equal(const dg_interest_volume *a, const dg_interest_volume *b) {
    if (a == b) return 1;
    if (!a || !b) return 0;
    return a->type == b->type &&
           a->shape == b->shape &&
           a->domain_id == b->domain_id &&
           a->src_entity == b->src_entity &&
           a->center.x == b->center.x &&
           a->center.y == b->center.y &&
           a->center.z == b->center.z &&
           a->radius == b->radius &&
           a->half_extents.x == b->half_extents.x &&
           a->half_extents.y == b->half_extents.y &&
           a->half_extents.z == b->half_extents.z &&
           a->weight == b->weight;
}

static int run_interest_order(const dg_interest_volume *vols,
                              u32 count,
                              dg_interest_volume *out_sorted) {
    dg_interest_ctx ctx;
    dg_interest_list list;
    interest_fixture fix;
    u32 i;
    int rc;

    fix.vols = vols;
    fix.count = count;

    dg_interest_init(&ctx);
    rc = dg_interest_reserve(&ctx, 1u);
    TEST_CHECK(rc == 0);
    rc = dg_interest_register_source(&ctx, interest_source, 0u, &fix);
    TEST_CHECK(rc == 0);

    dg_interest_list_init(&list);
    rc = dg_interest_list_reserve(&list, 8u);
    TEST_CHECK(rc == 0);

    rc = dg_interest_collect(&ctx, 0u, &list);
    TEST_CHECK(rc == 0);
    TEST_CHECK(list.count == count);

    for (i = 0u; i < count; ++i) {
        out_sorted[i] = list.volumes[i];
    }

    dg_interest_list_free(&list);
    dg_interest_free(&ctx);
    return 0;
}

static int test_interest_ordering(void) {
    const dg_interest_volume vols_a[3] = {
        { DG_IV_PLAYER, DG_IV_SHAPE_SPHERE, 1u, 10u,
          { d_q16_16_from_int(1), d_q16_16_from_int(2), d_q16_16_from_int(3) },
          d_q16_16_from_int(4),
          { 0, 0, 0 },
          d_q16_16_from_int(1) },
        { DG_IV_ACTIVITY, DG_IV_SHAPE_AABB, 2u, 20u,
          { d_q16_16_from_int(5), d_q16_16_from_int(6), d_q16_16_from_int(7) },
          0,
          { d_q16_16_from_int(2), d_q16_16_from_int(2), d_q16_16_from_int(2) },
          d_q16_16_from_int(2) },
        { DG_IV_HAZARD, DG_IV_SHAPE_SPHERE, 1u, 5u,
          { d_q16_16_from_int(8), d_q16_16_from_int(9), d_q16_16_from_int(10) },
          d_q16_16_from_int(3),
          { 0, 0, 0 },
          d_q16_16_from_int(3) }
    };
    const dg_interest_volume vols_b[3] = {
        vols_a[2],
        vols_a[0],
        vols_a[1]
    };
    dg_interest_volume out_a[3];
    dg_interest_volume out_b[3];
    u32 i;

    TEST_CHECK(run_interest_order(vols_a, 3u, out_a) == 0);
    TEST_CHECK(run_interest_order(vols_b, 3u, out_b) == 0);

    for (i = 0u; i < 3u; ++i) {
        TEST_CHECK(interest_volume_equal(&out_a[i], &out_b[i]));
    }
    return 0;
}

static int test_det_heap_ordering(void) {
    dom_det_heap heap;
    dom_det_order_item storage[6];
    dom_det_order_item items[4];
    dom_det_order_item out;
    u64 expected[4] = { 3u, 1u, 2u, 4u };
    u64 got[4];
    u32 i;

    items[0].primary = 2u; items[0].secondary = 5u; items[0].payload = 1u;
    items[1].primary = 1u; items[1].secondary = 9u; items[1].payload = 3u;
    items[2].primary = 2u; items[2].secondary = 5u; items[2].payload = 2u;
    items[3].primary = 3u; items[3].secondary = 0u; items[3].payload = 4u;

    TEST_CHECK(dom_det_heap_init(&heap, storage, 6u) == DOM_DET_OK);
    for (i = 0u; i < 4u; ++i) {
        TEST_CHECK(dom_det_heap_push(&heap, &items[i]) == DOM_DET_OK);
    }
    for (i = 0u; i < 4u; ++i) {
        TEST_CHECK(dom_det_heap_pop(&heap, &out) == DOM_DET_OK);
        got[i] = out.payload;
    }
    for (i = 0u; i < 4u; ++i) {
        TEST_CHECK(got[i] == expected[i]);
    }
    return 0;
}

int main(void) {
    if (test_event_queue_ordering() != 0) return 1;
    if (test_ledger_obligation_ordering() != 0) return 1;
    if (test_interest_ordering() != 0) return 1;
    if (test_det_heap_ordering() != 0) return 1;
    return 0;
}
