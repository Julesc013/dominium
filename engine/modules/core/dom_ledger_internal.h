/*
FILE: source/domino/core/dom_ledger_internal.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / core/dom_ledger
RESPONSIBILITY: Internal helpers for ledger core implementation.
*/
#ifndef DOM_LEDGER_INTERNAL_H
#define DOM_LEDGER_INTERNAL_H

#include "domino/core/dom_ledger.h"

#ifdef __cplusplus
extern "C" {
#endif

int dom_ledger_amount_add_checked(dom_amount_t a, dom_amount_t b, dom_amount_t *out_val);

dom_ledger_account *dom_ledger_account_find(dom_ledger *ledger, dom_account_id_t account_id);
const dom_ledger_account *dom_ledger_account_find_const(const dom_ledger *ledger, dom_account_id_t account_id);

dom_ledger_asset_slot *dom_ledger_asset_find(dom_ledger_account *account, dom_asset_id_t asset_id);
const dom_ledger_asset_slot *dom_ledger_asset_find_const(const dom_ledger_account *account, dom_asset_id_t asset_id);
dom_ledger_asset_slot *dom_ledger_asset_get_or_create(dom_ledger_account *account, dom_asset_id_t asset_id, int *out_created);

int dom_ledger_asset_credit(dom_ledger_asset_slot *slot,
                            dom_amount_t amount,
                            dom_lot_id_t lot_id,
                            dom_transaction_id_t tx_id,
                            u64 provenance_id,
                            dom_act_time_t creation_act);
int dom_ledger_asset_debit(dom_ledger_asset_slot *slot,
                           dom_amount_t amount,
                           dom_lot_id_t lot_id,
                           int allow_negative);

int dom_ledger_obligation_find_index(const dom_ledger *ledger, dom_obligation_id_t obligation_id, u32 *out_index);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOM_LEDGER_INTERNAL_H */
