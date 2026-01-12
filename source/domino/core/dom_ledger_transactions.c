/*
FILE: source/domino/core/dom_ledger_transactions.c
MODULE: Domino
RESPONSIBILITY: Deterministic transaction validation and application.
*/
#include "core/dom_ledger_internal.h"

#include <string.h>

typedef struct dom_ledger_asset_sum {
    dom_asset_id_t asset_id;
    dom_amount_t sum;
} dom_ledger_asset_sum;

typedef struct dom_ledger_pair_sum {
    dom_account_id_t account_id;
    dom_asset_id_t asset_id;
    dom_amount_t delta;
} dom_ledger_pair_sum;

static int dom_ledger_add_asset_sum(dom_ledger_asset_sum *items,
                                    u32 *count,
                                    dom_asset_id_t asset_id,
                                    dom_amount_t amount) {
    u32 i;
    if (!items || !count) {
        return DOM_LEDGER_INVALID;
    }
    for (i = 0u; i < *count; ++i) {
        if (items[i].asset_id == asset_id) {
            return dom_ledger_amount_add_checked(items[i].sum, amount, &items[i].sum);
        }
    }
    if (*count >= DOM_LEDGER_MAX_POSTINGS) {
        return DOM_LEDGER_FULL;
    }
    items[*count].asset_id = asset_id;
    items[*count].sum = amount;
    *count += 1u;
    return DOM_LEDGER_OK;
}

static int dom_ledger_add_pair_sum(dom_ledger_pair_sum *items,
                                   u32 *count,
                                   dom_account_id_t account_id,
                                   dom_asset_id_t asset_id,
                                   dom_amount_t amount) {
    u32 i;
    if (!items || !count) {
        return DOM_LEDGER_INVALID;
    }
    for (i = 0u; i < *count; ++i) {
        if (items[i].account_id == account_id && items[i].asset_id == asset_id) {
            return dom_ledger_amount_add_checked(items[i].delta, amount, &items[i].delta);
        }
    }
    if (*count >= DOM_LEDGER_MAX_POSTINGS) {
        return DOM_LEDGER_FULL;
    }
    items[*count].account_id = account_id;
    items[*count].asset_id = asset_id;
    items[*count].delta = amount;
    *count += 1u;
    return DOM_LEDGER_OK;
}

int dom_ledger_transaction_apply(dom_ledger *ledger,
                                 const dom_ledger_transaction *tx,
                                 dom_act_time_t act_time) {
    dom_ledger_asset_sum asset_sums[DOM_LEDGER_MAX_POSTINGS];
    dom_ledger_pair_sum pair_sums[DOM_LEDGER_MAX_POSTINGS];
    u32 asset_count = 0u;
    u32 pair_count = 0u;
    u32 i;
    int rc;

    if (!ledger || !tx || !tx->postings || tx->posting_count == 0u) {
        return DOM_LEDGER_INVALID;
    }
    if (tx->posting_count > DOM_LEDGER_MAX_POSTINGS) {
        return DOM_LEDGER_FULL;
    }
    memset(asset_sums, 0, sizeof(asset_sums));
    memset(pair_sums, 0, sizeof(pair_sums));

    for (i = 0u; i < tx->posting_count; ++i) {
        const dom_ledger_posting *p = &tx->postings[i];
        if (p->account_id == 0u || p->asset_id == 0u) {
            return DOM_LEDGER_INVALID;
        }
        if (p->amount == 0) {
            continue;
        }
        rc = dom_ledger_add_asset_sum(asset_sums, &asset_count, p->asset_id, p->amount);
        if (rc != DOM_LEDGER_OK) {
            return rc;
        }
        rc = dom_ledger_add_pair_sum(pair_sums, &pair_count, p->account_id, p->asset_id, p->amount);
        if (rc != DOM_LEDGER_OK) {
            return rc;
        }
    }
    for (i = 0u; i < asset_count; ++i) {
        if (asset_sums[i].sum != 0) {
            return DOM_LEDGER_IMBALANCED;
        }
    }

    for (i = 0u; i < pair_count; ++i) {
        dom_ledger_account *account = dom_ledger_account_find(ledger, pair_sums[i].account_id);
        const dom_ledger_asset_slot *slot = 0;
        dom_amount_t balance = 0;
        dom_amount_t new_balance;
        if (!account) {
            return DOM_LEDGER_NOT_FOUND;
        }
        slot = dom_ledger_asset_find_const(account, pair_sums[i].asset_id);
        if (slot) {
            balance = slot->balance;
        }
        rc = dom_ledger_amount_add_checked(balance, pair_sums[i].delta, &new_balance);
        if (rc != DOM_LEDGER_OK) {
            return rc;
        }
        if (new_balance < 0 && !(account->flags & DOM_LEDGER_ACCOUNT_ALLOW_NEGATIVE)) {
            return DOM_LEDGER_INSUFFICIENT;
        }
    }

    for (i = 0u; i < tx->posting_count; ++i) {
        const dom_ledger_posting *p = &tx->postings[i];
        dom_ledger_account *account;
        dom_ledger_asset_slot *slot;
        int created = 0;
        dom_lot_id_t lot_id;
        int allow_negative;
        if (p->amount == 0) {
            continue;
        }
        account = dom_ledger_account_find(ledger, p->account_id);
        if (!account) {
            return DOM_LEDGER_NOT_FOUND;
        }
        slot = dom_ledger_asset_get_or_create(account, p->asset_id, &created);
        if (!slot) {
            return DOM_LEDGER_FULL;
        }
        allow_negative = (account->flags & DOM_LEDGER_ACCOUNT_ALLOW_NEGATIVE) ? 1 : 0;
        if (p->amount < 0) {
            rc = dom_ledger_asset_debit(slot, (dom_amount_t)(-p->amount), p->lot_id, allow_negative);
            if (rc != DOM_LEDGER_OK) {
                return rc;
            }
        } else {
            if (p->lot_id != 0u) {
                lot_id = p->lot_id;
            } else {
                rc = dom_ledger_next_lot_id(ledger, &lot_id);
                if (rc != DOM_LEDGER_OK) {
                    return rc;
                }
            }
            rc = dom_ledger_asset_credit(slot, p->amount, lot_id, tx->tx_id, p->provenance_id, act_time);
            if (rc != DOM_LEDGER_OK) {
                return rc;
            }
        }
    }

    return DOM_LEDGER_OK;
}
