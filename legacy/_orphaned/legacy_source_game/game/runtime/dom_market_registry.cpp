/*
FILE: source/dominium/game/runtime/dom_market_registry.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / game/runtime/market_registry
RESPONSIBILITY: Deterministic market registry and provider dispatch.
*/
#include "runtime/dom_market_registry.h"

#include <algorithm>
#include <vector>

extern "C" {
#include "domino/core/spacetime.h"
}

#include "runtime/dom_market_provider_impl.h"

namespace {

struct MarketEntry {
    dom_market_spec spec;
    std::string id;
    dom_market_provider_vtbl vtbl;
    void *state;
};

static int compute_hash_id(const char *bytes, u32 len, u64 *out_id) {
    u64 hash = 0ull;
    if (!bytes || len == 0u || !out_id) {
        return DOM_MARKET_INVALID_ARGUMENT;
    }
    if (dom_id_hash64(bytes, len, &hash) != DOM_SPACETIME_OK) {
        return DOM_MARKET_ERR;
    }
    if (hash == 0ull) {
        return DOM_MARKET_ERR;
    }
    *out_id = hash;
    return DOM_MARKET_OK;
}

static bool entry_less(const MarketEntry &a, const MarketEntry &b) {
    if (a.spec.id_hash != b.spec.id_hash) {
        return a.spec.id_hash < b.spec.id_hash;
    }
    return a.id < b.id;
}

static int create_provider(u32 kind, dom_market_provider_vtbl *out_vtbl, void **out_state) {
    if (!out_vtbl || !out_state) {
        return DOM_MARKET_INVALID_ARGUMENT;
    }
    *out_state = 0;
    switch (kind) {
    case DOM_MARKET_PROVIDER_BARTER:
        return dom_market_provider_create_barter(out_vtbl, out_state);
    case DOM_MARKET_PROVIDER_FIXED_PRICE:
        return dom_market_provider_create_fixed_price(out_vtbl, out_state);
    case DOM_MARKET_PROVIDER_AUCTION:
        return dom_market_provider_create_auction(out_vtbl, out_state);
    case DOM_MARKET_PROVIDER_ORDERBOOK:
        return dom_market_provider_create_orderbook(out_vtbl, out_state);
    case DOM_MARKET_PROVIDER_CLEARINGHOUSE:
        return dom_market_provider_create_clearinghouse(out_vtbl, out_state);
    default:
        break;
    }
    return DOM_MARKET_NOT_IMPLEMENTED;
}

static MarketEntry *find_entry(std::vector<MarketEntry> &list, dom_market_id id_hash) {
    size_t i;
    for (i = 0u; i < list.size(); ++i) {
        if (list[i].spec.id_hash == id_hash) {
            return &list[i];
        }
    }
    return 0;
}

static const MarketEntry *find_entry_const(const std::vector<MarketEntry> &list, dom_market_id id_hash) {
    size_t i;
    for (i = 0u; i < list.size(); ++i) {
        if (list[i].spec.id_hash == id_hash) {
            return &list[i];
        }
    }
    return 0;
}

} // namespace

struct dom_market_registry {
    std::vector<MarketEntry> markets;
    std::string last_error;
};

dom_market_registry *dom_market_registry_create(void) {
    return new dom_market_registry();
}

void dom_market_registry_destroy(dom_market_registry *registry) {
    size_t i;
    if (!registry) {
        return;
    }
    for (i = 0u; i < registry->markets.size(); ++i) {
        MarketEntry &entry = registry->markets[i];
        if (entry.vtbl.destroy && entry.state) {
            entry.vtbl.destroy(entry.state);
        }
        entry.state = 0;
    }
    delete registry;
}

int dom_market_registry_register(dom_market_registry *registry,
                                 const dom_market_spec *spec) {
    dom_market_spec tmp;
    MarketEntry entry;
    void *state = 0;
    dom_market_provider_vtbl vtbl;
    int rc;

    if (!registry || !spec) {
        return DOM_MARKET_INVALID_ARGUMENT;
    }
    tmp = *spec;
    if (tmp.id && tmp.id_len > 0u) {
        rc = compute_hash_id(tmp.id, tmp.id_len, &tmp.id_hash);
        if (rc != DOM_MARKET_OK) {
            return rc;
        }
    }
    if (tmp.id_hash == 0ull) {
        return DOM_MARKET_INVALID_ARGUMENT;
    }
    if (find_entry(registry->markets, tmp.id_hash)) {
        return DOM_MARKET_DUPLICATE_ID;
    }
    if (tmp.provider_kind == DOM_MARKET_PROVIDER_FIXED_PRICE && tmp.fixed_price <= 0) {
        return DOM_MARKET_INVALID_ARGUMENT;
    }
    if (tmp.provider_kind != DOM_MARKET_PROVIDER_BARTER && tmp.price_scale == 0u) {
        return DOM_MARKET_INVALID_ARGUMENT;
    }
    if (tmp.max_matches_per_clear == 0u) {
        tmp.max_matches_per_clear = 32u;
    }

    rc = create_provider(tmp.provider_kind, &vtbl, &state);
    if (rc != DOM_MARKET_OK) {
        return rc;
    }
    if (vtbl.init && vtbl.init(state, &tmp) != DOM_MARKET_OK) {
        if (vtbl.destroy && state) {
            vtbl.destroy(state);
        }
        return DOM_MARKET_ERR;
    }

    entry.spec = tmp;
    entry.id.assign(tmp.id ? tmp.id : "", tmp.id ? tmp.id_len : 0u);
    entry.vtbl = vtbl;
    entry.state = state;

    registry->markets.push_back(entry);
    std::sort(registry->markets.begin(), registry->markets.end(), entry_less);
    return DOM_MARKET_OK;
}

int dom_market_registry_get(const dom_market_registry *registry,
                            dom_market_id id_hash,
                            dom_market_spec *out_spec) {
    const MarketEntry *entry;
    if (!registry || !out_spec) {
        return DOM_MARKET_INVALID_ARGUMENT;
    }
    entry = find_entry_const(registry->markets, id_hash);
    if (!entry) {
        return DOM_MARKET_NOT_FOUND;
    }
    *out_spec = entry->spec;
    out_spec->id = entry->id.empty() ? 0 : entry->id.c_str();
    out_spec->id_len = (u32)entry->id.size();
    return DOM_MARKET_OK;
}

int dom_market_registry_submit_order(dom_market_registry *registry,
                                     dom_market_id market_id,
                                     const dom_market_order *order,
                                     dom_market_order_ack *out_ack) {
    MarketEntry *entry;
    if (out_ack) {
        out_ack->status = 0u;
        out_ack->order_id = 0ull;
        out_ack->next_due_tick = 0;
    }
    if (!registry || !order) {
        return DOM_MARKET_INVALID_ARGUMENT;
    }
    entry = find_entry(registry->markets, market_id);
    if (!entry || !entry->vtbl.submit_order) {
        registry->last_error = "market_not_found";
        return DOM_MARKET_NOT_FOUND;
    }
    return entry->vtbl.submit_order(entry->state, order, out_ack);
}

int dom_market_registry_cancel_order(dom_market_registry *registry,
                                     dom_market_id market_id,
                                     dom_market_order_id order_id) {
    MarketEntry *entry;
    if (!registry) {
        return DOM_MARKET_INVALID_ARGUMENT;
    }
    entry = find_entry(registry->markets, market_id);
    if (!entry || !entry->vtbl.cancel_order) {
        registry->last_error = "market_not_found";
        return DOM_MARKET_NOT_FOUND;
    }
    return entry->vtbl.cancel_order(entry->state, order_id);
}

int dom_market_registry_clear(dom_market_registry *registry,
                              dom_market_id market_id,
                              dom_act_time_t now,
                              dom_market_clear_result *out_result) {
    MarketEntry *entry;
    if (out_result) {
        out_result->trades = 0;
        out_result->trade_count = 0u;
        out_result->quotes = 0;
        out_result->quote_count = 0u;
        out_result->next_due_tick = 0;
    }
    if (!registry || !out_result) {
        return DOM_MARKET_INVALID_ARGUMENT;
    }
    entry = find_entry(registry->markets, market_id);
    if (!entry || !entry->vtbl.clear) {
        registry->last_error = "market_not_found";
        return DOM_MARKET_NOT_FOUND;
    }
    return entry->vtbl.clear(entry->state, now, out_result);
}

int dom_market_registry_next_due_tick(dom_market_registry *registry,
                                      dom_market_id market_id,
                                      dom_act_time_t *out_tick) {
    MarketEntry *entry;
    if (!registry || !out_tick) {
        return DOM_MARKET_INVALID_ARGUMENT;
    }
    entry = find_entry(registry->markets, market_id);
    if (!entry || !entry->vtbl.next_due_tick) {
        registry->last_error = "market_not_found";
        return DOM_MARKET_NOT_FOUND;
    }
    return entry->vtbl.next_due_tick(entry->state, out_tick);
}

int dom_market_registry_next_global_due(dom_market_registry *registry,
                                        dom_act_time_t *out_tick) {
    size_t i;
    dom_act_time_t best = 0;
    int have = 0;
    if (!registry || !out_tick) {
        return DOM_MARKET_INVALID_ARGUMENT;
    }
    for (i = 0u; i < registry->markets.size(); ++i) {
        dom_act_time_t due = 0;
        if (registry->markets[i].vtbl.next_due_tick &&
            registry->markets[i].vtbl.next_due_tick(registry->markets[i].state, &due) == DOM_MARKET_OK &&
            due > 0) {
            if (!have || due < best) {
                best = due;
                have = 1;
            }
        }
    }
    if (!have) {
        *out_tick = 0;
        return DOM_MARKET_NOT_FOUND;
    }
    *out_tick = best;
    return DOM_MARKET_OK;
}

int dom_market_registry_settle_trades(dom_market_registry *registry,
                                      dom_ledger *ledger,
                                      const dom_market_trade *trades,
                                      u32 trade_count,
                                      dom_act_time_t act_time) {
    u32 i;
    if (!registry || !ledger || (!trades && trade_count > 0u)) {
        return DOM_MARKET_INVALID_ARGUMENT;
    }
    for (i = 0u; i < trade_count; ++i) {
        const dom_market_trade *tr = &trades[i];
        dom_ledger_posting postings[4];
        dom_ledger_transaction tx;
        dom_transaction_id_t tx_id = 0ull;

        if (tr->quantity_base <= 0 || tr->quantity_quote <= 0) {
            return DOM_MARKET_ERR;
        }
        if (dom_ledger_next_tx_id(ledger, &tx_id) != DOM_LEDGER_OK) {
            return DOM_MARKET_ERR;
        }
        postings[0].account_id = tr->buy_account_id;
        postings[0].asset_id = tr->quote_asset_id;
        postings[0].amount = -(dom_amount_t)tr->quantity_quote;
        postings[0].lot_id = 0ull;
        postings[0].provenance_id = 0ull;

        postings[1].account_id = tr->sell_account_id;
        postings[1].asset_id = tr->quote_asset_id;
        postings[1].amount = (dom_amount_t)tr->quantity_quote;
        postings[1].lot_id = 0ull;
        postings[1].provenance_id = 0ull;

        postings[2].account_id = tr->sell_account_id;
        postings[2].asset_id = tr->base_asset_id;
        postings[2].amount = -(dom_amount_t)tr->quantity_base;
        postings[2].lot_id = 0ull;
        postings[2].provenance_id = 0ull;

        postings[3].account_id = tr->buy_account_id;
        postings[3].asset_id = tr->base_asset_id;
        postings[3].amount = (dom_amount_t)tr->quantity_base;
        postings[3].lot_id = 0ull;
        postings[3].provenance_id = 0ull;

        tx.tx_id = tx_id;
        tx.posting_count = 4u;
        tx.postings = postings;

        if (dom_ledger_transaction_apply(ledger, &tx, act_time) != DOM_LEDGER_OK) {
            return DOM_MARKET_INSUFFICIENT;
        }
    }
    (void)registry;
    return DOM_MARKET_OK;
}

const char *dom_market_registry_last_error(const dom_market_registry *registry) {
    if (!registry) {
        return "";
    }
    return registry->last_error.c_str();
}
