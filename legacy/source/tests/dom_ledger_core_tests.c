/*
FILE: source/tests/dom_ledger_core_tests.c
MODULE: Domino Tests
PURPOSE: Validate deterministic ledger core invariants.
*/
#include <stdio.h>
#include <string.h>

#include "domino/core/dom_ledger.h"

static int fail(const char *msg) {
    fprintf(stderr, "FAIL: %s\n", msg ? msg : "(null)");
    return 1;
}

static int test_double_entry_conservation(void) {
    static dom_ledger ledger;
    dom_ledger_posting postings[2];
    dom_ledger_posting fund_postings[2];
    dom_ledger_transaction fund_tx;
    dom_ledger_transaction tx;
    dom_amount_t bal = 0;
    int rc;

    printf("test_double_entry_conservation\n");
    fflush(stdout);
    rc = dom_ledger_init(&ledger);
    if (rc != DOM_LEDGER_OK) {
        return fail("ledger_init");
    }
    (void)dom_ledger_account_create(&ledger, 1u, 0u);
    (void)dom_ledger_account_create(&ledger, 2u, 0u);
    (void)dom_ledger_account_create(&ledger, 99u, DOM_LEDGER_ACCOUNT_ALLOW_NEGATIVE);

    fund_postings[0].account_id = 99u;
    fund_postings[0].asset_id = 10u;
    fund_postings[0].amount = -100;
    fund_postings[0].lot_id = 0u;
    fund_postings[0].provenance_id = 0u;
    fund_postings[1].account_id = 1u;
    fund_postings[1].asset_id = 10u;
    fund_postings[1].amount = 100;
    fund_postings[1].lot_id = 0u;
    fund_postings[1].provenance_id = 1u;
    fund_tx.tx_id = 1u;
    fund_tx.posting_count = 2u;
    fund_tx.postings = fund_postings;
    rc = dom_ledger_transaction_apply(&ledger, &fund_tx, 4);
    if (rc != DOM_LEDGER_OK) {
        return fail("funding failed");
    }

    postings[0].account_id = 1u;
    postings[0].asset_id = 10u;
    postings[0].amount = -100;
    postings[0].lot_id = 0u;
    postings[0].provenance_id = 1u;

    postings[1].account_id = 2u;
    postings[1].asset_id = 10u;
    postings[1].amount = 100;
    postings[1].lot_id = 0u;
    postings[1].provenance_id = 1u;

    tx.tx_id = 2u;
    tx.posting_count = 2u;
    tx.postings = postings;
    rc = dom_ledger_transaction_apply(&ledger, &tx, 5);
    if (rc != DOM_LEDGER_OK) {
        return fail("double entry apply failed");
    }
    rc = dom_ledger_balance_get(&ledger, 2u, 10u, &bal);
    if (rc != DOM_LEDGER_OK || bal != 100) {
        return fail("balance mismatch");
    }

    postings[1].amount = 50;
    rc = dom_ledger_transaction_apply(&ledger, &tx, 6);
    if (rc != DOM_LEDGER_IMBALANCED) {
        return fail("imbalanced transaction not refused");
    }
    return 0;
}

static int test_lot_tracking(void) {
    static dom_ledger ledger;
    dom_ledger_posting postings[2];
    dom_ledger_transaction tx;
    dom_ledger_account acc;
    int rc;

    printf("test_lot_tracking\n");
    fflush(stdout);
    rc = dom_ledger_init(&ledger);
    if (rc != DOM_LEDGER_OK) {
        return fail("ledger_init");
    }
    (void)dom_ledger_account_create(&ledger, 3u, 0u);
    (void)dom_ledger_account_create(&ledger, 99u, DOM_LEDGER_ACCOUNT_ALLOW_NEGATIVE);

    postings[0].account_id = 99u;
    postings[0].asset_id = 20u;
    postings[0].amount = -250;
    postings[0].lot_id = 0u;
    postings[0].provenance_id = 0u;

    postings[1].account_id = 3u;
    postings[1].asset_id = 20u;
    postings[1].amount = 250;
    postings[1].lot_id = 0u;
    postings[1].provenance_id = 99u;

    tx.tx_id = 2u;
    tx.posting_count = 2u;
    tx.postings = postings;
    rc = dom_ledger_transaction_apply(&ledger, &tx, 7);
    if (rc != DOM_LEDGER_OK) {
        return fail("credit failed");
    }
    rc = dom_ledger_account_copy(&ledger, 3u, &acc);
    if (rc != DOM_LEDGER_OK) {
        return fail("account copy failed");
    }
    if (acc.asset_count != 1u || acc.assets[0].lot_count != 1u) {
        return fail("lot count mismatch");
    }
    if (acc.assets[0].lots[0].provenance_id != 99u) {
        return fail("provenance mismatch");
    }
    if (acc.assets[0].lots[0].source_tx != 2u) {
        return fail("source_tx mismatch");
    }
    return 0;
}

static int test_obligation_trigger_and_order(void) {
    static dom_ledger ledger;
    dom_ledger_posting postings_a[2];
    dom_ledger_posting postings_b[2];
    dom_ledger_posting fund_postings[2];
    dom_ledger_transaction tx_a;
    dom_ledger_transaction tx_b;
    dom_ledger_transaction fund_tx;
    dom_ledger_account acc;
    int rc;

    printf("test_obligation_trigger_and_order\n");
    fflush(stdout);
    rc = dom_ledger_init(&ledger);
    if (rc != DOM_LEDGER_OK) {
        return fail("ledger_init");
    }
    (void)dom_ledger_account_create(&ledger, 10u, 0u);
    (void)dom_ledger_account_create(&ledger, 11u, 0u);
    (void)dom_ledger_account_create(&ledger, 99u, DOM_LEDGER_ACCOUNT_ALLOW_NEGATIVE);

    fund_postings[0].account_id = 99u;
    fund_postings[0].asset_id = 30u;
    fund_postings[0].amount = -100;
    fund_postings[0].lot_id = 0u;
    fund_postings[0].provenance_id = 0u;
    fund_postings[1].account_id = 10u;
    fund_postings[1].asset_id = 30u;
    fund_postings[1].amount = 100;
    fund_postings[1].lot_id = 0u;
    fund_postings[1].provenance_id = 0u;
    fund_tx.tx_id = 10u;
    fund_tx.posting_count = 2u;
    fund_tx.postings = fund_postings;
    rc = dom_ledger_transaction_apply(&ledger, &fund_tx, 1);
    if (rc != DOM_LEDGER_OK) {
        return fail("funding obligation test");
    }

    postings_a[0].account_id = 10u;
    postings_a[0].asset_id = 30u;
    postings_a[0].amount = -40;
    postings_a[0].lot_id = 0u;
    postings_a[0].provenance_id = 0u;
    postings_a[1].account_id = 11u;
    postings_a[1].asset_id = 30u;
    postings_a[1].amount = 40;
    postings_a[1].lot_id = 0u;
    postings_a[1].provenance_id = 1u;

    postings_b[0] = postings_a[0];
    postings_b[1] = postings_a[1];

    tx_a.tx_id = 0u;
    tx_a.posting_count = 2u;
    tx_a.postings = postings_a;
    tx_b.tx_id = 0u;
    tx_b.posting_count = 2u;
    tx_b.postings = postings_b;

    rc = dom_ledger_obligation_schedule(&ledger, 1u, 10, &tx_a, 0);
    if (rc != DOM_LEDGER_OK) {
        return fail("schedule obligation a");
    }
    rc = dom_ledger_obligation_schedule(&ledger, 2u, 10, &tx_b, 0);
    if (rc != DOM_LEDGER_OK) {
        return fail("schedule obligation b");
    }

    rc = dom_ledger_process_until(&ledger, 9);
    if (rc != DOM_LEDGER_OK) {
        return fail("process_until pre");
    }
    rc = dom_ledger_process_until(&ledger, 10);
    if (rc != DOM_LEDGER_OK) {
        return fail("process_until trigger");
    }
    rc = dom_ledger_account_copy(&ledger, 11u, &acc);
    if (rc != DOM_LEDGER_OK) {
        return fail("account copy");
    }
    if (acc.asset_count != 1u || acc.assets[0].lot_count != 2u) {
        return fail("expected two lots");
    }
    if (acc.assets[0].lots[0].lot_id >= acc.assets[0].lots[1].lot_id) {
        return fail("obligation order not deterministic");
    }
    return 0;
}

static int test_batch_vs_step(void) {
    static dom_ledger ledger_a;
    static dom_ledger ledger_b;
    dom_ledger_posting postings[2];
    dom_ledger_posting fund_postings[2];
    dom_ledger_transaction tx;
    dom_ledger_transaction fund_tx;
    dom_ledger_asset_summary assets_a[4];
    dom_ledger_asset_summary assets_b[4];
    dom_ledger_account_summary sum_a;
    dom_ledger_account_summary sum_b;
    int rc;

    printf("test_batch_vs_step\n");
    fflush(stdout);
    rc = dom_ledger_init(&ledger_a);
    if (rc != DOM_LEDGER_OK) {
        return fail("ledger_init a");
    }
    rc = dom_ledger_init(&ledger_b);
    if (rc != DOM_LEDGER_OK) {
        return fail("ledger_init b");
    }
    (void)dom_ledger_account_create(&ledger_a, 21u, 0u);
    (void)dom_ledger_account_create(&ledger_a, 22u, 0u);
    (void)dom_ledger_account_create(&ledger_a, 99u, DOM_LEDGER_ACCOUNT_ALLOW_NEGATIVE);
    (void)dom_ledger_account_create(&ledger_b, 21u, 0u);
    (void)dom_ledger_account_create(&ledger_b, 22u, 0u);
    (void)dom_ledger_account_create(&ledger_b, 99u, DOM_LEDGER_ACCOUNT_ALLOW_NEGATIVE);

    fund_postings[0].account_id = 99u;
    fund_postings[0].asset_id = 50u;
    fund_postings[0].amount = -40;
    fund_postings[0].lot_id = 0u;
    fund_postings[0].provenance_id = 0u;
    fund_postings[1].account_id = 21u;
    fund_postings[1].asset_id = 50u;
    fund_postings[1].amount = 40;
    fund_postings[1].lot_id = 0u;
    fund_postings[1].provenance_id = 2u;
    fund_tx.tx_id = 20u;
    fund_tx.posting_count = 2u;
    fund_tx.postings = fund_postings;
    rc = dom_ledger_transaction_apply(&ledger_a, &fund_tx, 2);
    if (rc != DOM_LEDGER_OK) {
        return fail("funding a");
    }
    rc = dom_ledger_transaction_apply(&ledger_b, &fund_tx, 2);
    if (rc != DOM_LEDGER_OK) {
        return fail("funding b");
    }

    postings[0].account_id = 21u;
    postings[0].asset_id = 50u;
    postings[0].amount = -10;
    postings[0].lot_id = 0u;
    postings[0].provenance_id = 0u;
    postings[1].account_id = 22u;
    postings[1].asset_id = 50u;
    postings[1].amount = 10;
    postings[1].lot_id = 0u;
    postings[1].provenance_id = 2u;
    tx.tx_id = 0u;
    tx.posting_count = 2u;
    tx.postings = postings;

    rc = dom_ledger_obligation_schedule(&ledger_a, 3u, 5, &tx, 0);
    if (rc != DOM_LEDGER_OK) {
        return fail("schedule a1");
    }
    rc = dom_ledger_obligation_schedule(&ledger_a, 4u, 9, &tx, 0);
    if (rc != DOM_LEDGER_OK) {
        return fail("schedule a2");
    }
    rc = dom_ledger_obligation_schedule(&ledger_b, 3u, 5, &tx, 0);
    if (rc != DOM_LEDGER_OK) {
        return fail("schedule b1");
    }
    rc = dom_ledger_obligation_schedule(&ledger_b, 4u, 9, &tx, 0);
    if (rc != DOM_LEDGER_OK) {
        return fail("schedule b2");
    }

    rc = dom_ledger_process_until(&ledger_a, 5);
    if (rc != DOM_LEDGER_OK) {
        return fail("batch step a");
    }
    rc = dom_ledger_process_until(&ledger_a, 9);
    if (rc != DOM_LEDGER_OK) {
        return fail("batch step a2");
    }
    rc = dom_ledger_process_until(&ledger_b, 9);
    if (rc != DOM_LEDGER_OK) {
        return fail("batch step b");
    }

    rc = dom_ledger_account_summarize(&ledger_a, 22u, &sum_a, assets_a, 4u);
    if (rc != DOM_LEDGER_OK) {
        return fail("summary a");
    }
    rc = dom_ledger_account_summarize(&ledger_b, 22u, &sum_b, assets_b, 4u);
    if (rc != DOM_LEDGER_OK) {
        return fail("summary b");
    }
    if (sum_a.asset_count != sum_b.asset_count ||
        assets_a[0].balance != assets_b[0].balance ||
        assets_a[0].provenance_hash != assets_b[0].provenance_hash) {
        return fail("batch vs step mismatch");
    }
    return 0;
}

int main(void) {
    int rc;
    printf("dom_ledger_core_tests start\n");
    fflush(stdout);
    rc = test_double_entry_conservation();
    if (rc != 0) return rc;
    rc = test_lot_tracking();
    if (rc != 0) return rc;
    rc = test_obligation_trigger_and_order();
    if (rc != 0) return rc;
    rc = test_batch_vs_step();
    if (rc != 0) return rc;
    printf("dom_ledger_core_tests passed\n");
    return 0;
}
