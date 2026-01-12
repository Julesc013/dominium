/*
FILE: source/domino/core/dom_ledger_lots.c
MODULE: Domino
RESPONSIBILITY: Ledger lot tracking and deterministic credit/debit handling.
*/
#include "core/dom_ledger_internal.h"

#include <string.h>

static int dom_ledger_insert_lot(dom_ledger_asset_slot *slot, const dom_ledger_lot *lot) {
    u32 i;
    if (!slot || !lot) {
        return DOM_LEDGER_INVALID;
    }
    if (slot->lot_count >= DOM_LEDGER_MAX_LOTS_PER_ASSET) {
        return DOM_LEDGER_FULL;
    }
    for (i = 0u; i < slot->lot_count; ++i) {
        const dom_ledger_lot *cur = &slot->lots[i];
        if (cur->creation_act > lot->creation_act) {
            break;
        }
        if (cur->creation_act == lot->creation_act && cur->lot_id > lot->lot_id) {
            break;
        }
    }
    if (i < slot->lot_count) {
        memmove(&slot->lots[i + 1u],
                &slot->lots[i],
                (slot->lot_count - i) * sizeof(dom_ledger_lot));
    }
    slot->lots[i] = *lot;
    slot->lot_count += 1u;
    return DOM_LEDGER_OK;
}

int dom_ledger_asset_credit(dom_ledger_asset_slot *slot,
                            dom_amount_t amount,
                            dom_lot_id_t lot_id,
                            dom_transaction_id_t tx_id,
                            u64 provenance_id,
                            dom_act_time_t creation_act) {
    dom_amount_t new_balance;
    dom_ledger_lot lot;
    int rc;
    if (!slot || amount <= 0 || lot_id == 0u) {
        return DOM_LEDGER_INVALID;
    }
    rc = dom_ledger_amount_add_checked(slot->balance, amount, &new_balance);
    if (rc != DOM_LEDGER_OK) {
        return rc;
    }
    lot.lot_id = lot_id;
    lot.source_tx = tx_id;
    lot.provenance_id = provenance_id;
    lot.creation_act = creation_act;
    lot.amount = amount;
    rc = dom_ledger_insert_lot(slot, &lot);
    if (rc != DOM_LEDGER_OK) {
        return rc;
    }
    slot->balance = new_balance;
    return DOM_LEDGER_OK;
}

static int dom_ledger_consume_lot(dom_ledger_asset_slot *slot, u32 index, dom_amount_t amount) {
    dom_ledger_lot *lot;
    if (!slot || index >= slot->lot_count || amount <= 0) {
        return DOM_LEDGER_INVALID;
    }
    lot = &slot->lots[index];
    if (lot->amount < amount) {
        return DOM_LEDGER_INSUFFICIENT;
    }
    lot->amount -= amount;
    if (lot->amount == 0) {
        if (index + 1u < slot->lot_count) {
            memmove(&slot->lots[index],
                    &slot->lots[index + 1u],
                    (slot->lot_count - index - 1u) * sizeof(dom_ledger_lot));
        }
        slot->lot_count -= 1u;
    }
    return DOM_LEDGER_OK;
}

int dom_ledger_asset_debit(dom_ledger_asset_slot *slot,
                           dom_amount_t amount,
                           dom_lot_id_t lot_id,
                           int allow_negative) {
    dom_amount_t new_balance;
    dom_amount_t remaining;
    int rc;
    u32 i;
    if (!slot || amount <= 0) {
        return DOM_LEDGER_INVALID;
    }
    rc = dom_ledger_amount_add_checked(slot->balance, -amount, &new_balance);
    if (rc != DOM_LEDGER_OK) {
        return rc;
    }
    remaining = amount;
    if (lot_id != 0u) {
        for (i = 0u; i < slot->lot_count; ++i) {
            if (slot->lots[i].lot_id == lot_id) {
                if (slot->lots[i].amount < remaining) {
                    if (!allow_negative) {
                        return DOM_LEDGER_INSUFFICIENT;
                    }
                    remaining = slot->lots[i].amount;
                }
                rc = dom_ledger_consume_lot(slot, i, remaining);
                if (rc != DOM_LEDGER_OK) {
                    return rc;
                }
                remaining = amount - remaining;
                break;
            }
        }
        if (remaining > 0 && !allow_negative) {
            return DOM_LEDGER_INSUFFICIENT;
        }
        slot->balance = new_balance;
        return DOM_LEDGER_OK;
    }

    for (i = 0u; i < slot->lot_count && remaining > 0; ) {
        dom_amount_t take = slot->lots[i].amount;
        if (take > remaining) {
            take = remaining;
        }
        rc = dom_ledger_consume_lot(slot, i, take);
        if (rc != DOM_LEDGER_OK) {
            return rc;
        }
        remaining -= take;
        if (take == 0) {
            break;
        }
        if (remaining > 0 && i < slot->lot_count && slot->lots[i].amount > 0) {
            continue;
        }
    }
    if (remaining > 0 && !allow_negative) {
        return DOM_LEDGER_INSUFFICIENT;
    }
    slot->balance = new_balance;
    return DOM_LEDGER_OK;
}
