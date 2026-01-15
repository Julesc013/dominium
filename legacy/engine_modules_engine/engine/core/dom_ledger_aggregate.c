/*
FILE: source/domino/core/dom_ledger_aggregate.c
MODULE: Domino
RESPONSIBILITY: Ledger aggregation helpers for balances and provenance summaries.
*/
#include "core/dom_ledger_internal.h"
#include "core/dg_det_hash.h"

static u64 dom_ledger_lot_hash(u64 seed, const dom_ledger_lot *lot) {
    u64 h = seed;
    if (!lot) {
        return h;
    }
    h ^= lot->lot_id;
    h ^= lot->provenance_id;
    h ^= lot->source_tx;
    h ^= (u64)lot->amount;
    return dg_det_hash_u64(h);
}

int dom_ledger_account_summarize(const dom_ledger *ledger,
                                 dom_account_id_t account_id,
                                 dom_ledger_account_summary *out_summary,
                                 dom_ledger_asset_summary *out_assets,
                                 u32 asset_capacity) {
    const dom_ledger_account *acc;
    u32 i;
    if (!ledger || !out_summary || !out_assets) {
        return DOM_LEDGER_INVALID;
    }
    acc = dom_ledger_account_find_const(ledger, account_id);
    if (!acc) {
        return DOM_LEDGER_NOT_FOUND;
    }
    if (asset_capacity < acc->asset_count) {
        return DOM_LEDGER_FULL;
    }
    out_summary->account_id = acc->account_id;
    out_summary->asset_count = acc->asset_count;
    for (i = 0u; i < acc->asset_count; ++i) {
        const dom_ledger_asset_slot *slot = &acc->assets[i];
        u32 j;
        u64 hash = 0u;
        out_assets[i].asset_id = slot->asset_id;
        out_assets[i].balance = slot->balance;
        for (j = 0u; j < slot->lot_count; ++j) {
            hash = dom_ledger_lot_hash(hash, &slot->lots[j]);
        }
        out_assets[i].provenance_hash = hash;
    }
    return DOM_LEDGER_OK;
}
