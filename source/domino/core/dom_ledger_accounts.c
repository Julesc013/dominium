/*
FILE: source/domino/core/dom_ledger_accounts.c
MODULE: Domino
RESPONSIBILITY: Ledger account storage and balance queries.
*/
#include "core/dom_ledger_internal.h"

#include <string.h>

dom_ledger_account *dom_ledger_account_find(dom_ledger *ledger, dom_account_id_t account_id) {
    u32 i;
    if (!ledger || account_id == 0u) {
        return (dom_ledger_account *)0;
    }
    for (i = 0u; i < ledger->account_count; ++i) {
        if (ledger->accounts[i].account_id == account_id) {
            return &ledger->accounts[i];
        }
    }
    return (dom_ledger_account *)0;
}

const dom_ledger_account *dom_ledger_account_find_const(const dom_ledger *ledger,
                                                        dom_account_id_t account_id) {
    u32 i;
    if (!ledger || account_id == 0u) {
        return (const dom_ledger_account *)0;
    }
    for (i = 0u; i < ledger->account_count; ++i) {
        if (ledger->accounts[i].account_id == account_id) {
            return &ledger->accounts[i];
        }
    }
    return (const dom_ledger_account *)0;
}

dom_ledger_asset_slot *dom_ledger_asset_find(dom_ledger_account *account, dom_asset_id_t asset_id) {
    u32 i;
    if (!account || asset_id == 0u) {
        return (dom_ledger_asset_slot *)0;
    }
    for (i = 0u; i < account->asset_count; ++i) {
        if (account->assets[i].asset_id == asset_id) {
            return &account->assets[i];
        }
    }
    return (dom_ledger_asset_slot *)0;
}

const dom_ledger_asset_slot *dom_ledger_asset_find_const(const dom_ledger_account *account,
                                                         dom_asset_id_t asset_id) {
    u32 i;
    if (!account || asset_id == 0u) {
        return (const dom_ledger_asset_slot *)0;
    }
    for (i = 0u; i < account->asset_count; ++i) {
        if (account->assets[i].asset_id == asset_id) {
            return &account->assets[i];
        }
    }
    return (const dom_ledger_asset_slot *)0;
}

dom_ledger_asset_slot *dom_ledger_asset_get_or_create(dom_ledger_account *account,
                                                      dom_asset_id_t asset_id,
                                                      int *out_created) {
    u32 i;
    if (out_created) {
        *out_created = 0;
    }
    if (!account || asset_id == 0u) {
        return (dom_ledger_asset_slot *)0;
    }
    for (i = 0u; i < account->asset_count; ++i) {
        if (account->assets[i].asset_id == asset_id) {
            return &account->assets[i];
        }
        if (account->assets[i].asset_id > asset_id) {
            break;
        }
    }
    if (account->asset_count >= DOM_LEDGER_MAX_ASSETS_PER_ACCOUNT) {
        return (dom_ledger_asset_slot *)0;
    }
    if (i < account->asset_count) {
        memmove(&account->assets[i + 1u],
                &account->assets[i],
                (account->asset_count - i) * sizeof(dom_ledger_asset_slot));
    }
    memset(&account->assets[i], 0, sizeof(dom_ledger_asset_slot));
    account->assets[i].asset_id = asset_id;
    account->asset_count += 1u;
    if (out_created) {
        *out_created = 1;
    }
    return &account->assets[i];
}

int dom_ledger_account_create(dom_ledger *ledger, dom_account_id_t account_id, u32 flags) {
    u32 i;
    if (!ledger || account_id == 0u) {
        return DOM_LEDGER_INVALID;
    }
    if (ledger->account_count >= DOM_LEDGER_MAX_ACCOUNTS) {
        return DOM_LEDGER_FULL;
    }
    if (dom_ledger_account_find(ledger, account_id)) {
        return DOM_LEDGER_DUPLICATE;
    }
    for (i = 0u; i < ledger->account_count; ++i) {
        if (ledger->accounts[i].account_id > account_id) {
            break;
        }
    }
    if (i < ledger->account_count) {
        memmove(&ledger->accounts[i + 1u],
                &ledger->accounts[i],
                (ledger->account_count - i) * sizeof(dom_ledger_account));
    }
    memset(&ledger->accounts[i], 0, sizeof(dom_ledger_account));
    ledger->accounts[i].account_id = account_id;
    ledger->accounts[i].flags = flags;
    ledger->account_count += 1u;
    return DOM_LEDGER_OK;
}

int dom_ledger_account_copy(const dom_ledger *ledger,
                            dom_account_id_t account_id,
                            dom_ledger_account *out_account) {
    const dom_ledger_account *acc;
    if (!ledger || !out_account) {
        return DOM_LEDGER_INVALID;
    }
    acc = dom_ledger_account_find_const(ledger, account_id);
    if (!acc) {
        return DOM_LEDGER_NOT_FOUND;
    }
    *out_account = *acc;
    return DOM_LEDGER_OK;
}

int dom_ledger_balance_get(const dom_ledger *ledger,
                           dom_account_id_t account_id,
                           dom_asset_id_t asset_id,
                           dom_amount_t *out_balance) {
    const dom_ledger_account *acc;
    const dom_ledger_asset_slot *slot;
    if (!ledger || !out_balance) {
        return DOM_LEDGER_INVALID;
    }
    acc = dom_ledger_account_find_const(ledger, account_id);
    if (!acc) {
        return DOM_LEDGER_NOT_FOUND;
    }
    slot = dom_ledger_asset_find_const(acc, asset_id);
    if (!slot) {
        *out_balance = 0;
        return DOM_LEDGER_OK;
    }
    *out_balance = slot->balance;
    return DOM_LEDGER_OK;
}
