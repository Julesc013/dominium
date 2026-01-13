/*
TEST: dom_market_settlement_conservation_test
PURPOSE: Market settlement conserves balances via ledger transactions.
*/
#include "runtime/dom_market_registry.h"

#include <string.h>

extern "C" {
#include "domino/core/dom_ledger.h"
}

static int seed_balances(dom_ledger *ledger,
                         dom_account_id_t buyer,
                         dom_account_id_t seller,
                         dom_account_id_t mint,
                         dom_asset_id_t base,
                         dom_asset_id_t quote) {
    dom_ledger_posting postings[4];
    dom_ledger_transaction tx;
    dom_transaction_id_t tx_id = 0ull;

    if (dom_ledger_next_tx_id(ledger, &tx_id) != DOM_LEDGER_OK) {
        return 1;
    }
    postings[0].account_id = buyer;
    postings[0].asset_id = quote;
    postings[0].amount = 1000;
    postings[0].lot_id = 0ull;
    postings[0].provenance_id = 0ull;

    postings[1].account_id = mint;
    postings[1].asset_id = quote;
    postings[1].amount = -1000;
    postings[1].lot_id = 0ull;
    postings[1].provenance_id = 0ull;

    postings[2].account_id = seller;
    postings[2].asset_id = base;
    postings[2].amount = 50;
    postings[2].lot_id = 0ull;
    postings[2].provenance_id = 0ull;

    postings[3].account_id = mint;
    postings[3].asset_id = base;
    postings[3].amount = -50;
    postings[3].lot_id = 0ull;
    postings[3].provenance_id = 0ull;

    tx.tx_id = tx_id;
    tx.posting_count = 4u;
    tx.postings = postings;
    return dom_ledger_transaction_apply(ledger, &tx, 0);
}

int main(void) {
    dom_market_registry *reg = dom_market_registry_create();
    dom_ledger ledger;
    dom_market_trade trade;
    dom_account_id_t buyer = 1ull;
    dom_account_id_t seller = 2ull;
    dom_account_id_t mint = 99ull;
    dom_asset_id_t base = 10ull;
    dom_asset_id_t quote = 20ull;
    dom_amount_t bal = 0;
    int rc;

    if (!reg) {
        return 1;
    }
    if (dom_ledger_init(&ledger) != DOM_LEDGER_OK) {
        dom_market_registry_destroy(reg);
        return 2;
    }
    if (dom_ledger_account_create(&ledger, buyer, 0u) != DOM_LEDGER_OK ||
        dom_ledger_account_create(&ledger, seller, 0u) != DOM_LEDGER_OK ||
        dom_ledger_account_create(&ledger, mint, DOM_LEDGER_ACCOUNT_ALLOW_NEGATIVE) != DOM_LEDGER_OK) {
        dom_market_registry_destroy(reg);
        return 3;
    }
    if (seed_balances(&ledger, buyer, seller, mint, base, quote) != DOM_LEDGER_OK) {
        dom_market_registry_destroy(reg);
        return 4;
    }

    memset(&trade, 0, sizeof(trade));
    trade.trade_id = 1ull;
    trade.buy_order_id = 100ull;
    trade.sell_order_id = 200ull;
    trade.buy_account_id = buyer;
    trade.sell_account_id = seller;
    trade.base_asset_id = base;
    trade.quote_asset_id = quote;
    trade.quantity_base = 10;
    trade.quantity_quote = 100;
    trade.execution_tick = 5;
    trade.settlement_tick = 5;

    rc = dom_market_registry_settle_trades(reg, &ledger, &trade, 1u, 5);
    if (rc != DOM_MARKET_OK) {
        dom_market_registry_destroy(reg);
        return 5;
    }

    if (dom_ledger_balance_get(&ledger, buyer, quote, &bal) != DOM_LEDGER_OK || bal != 900) {
        dom_market_registry_destroy(reg);
        return 6;
    }
    if (dom_ledger_balance_get(&ledger, buyer, base, &bal) != DOM_LEDGER_OK || bal != 10) {
        dom_market_registry_destroy(reg);
        return 7;
    }
    if (dom_ledger_balance_get(&ledger, seller, base, &bal) != DOM_LEDGER_OK || bal != 40) {
        dom_market_registry_destroy(reg);
        return 8;
    }
    if (dom_ledger_balance_get(&ledger, seller, quote, &bal) != DOM_LEDGER_OK || bal != 100) {
        dom_market_registry_destroy(reg);
        return 9;
    }

    dom_market_registry_destroy(reg);
    return 0;
}
