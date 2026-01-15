/*
FILE: source/dominium/game/runtime/dom_tax_rules.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / game/runtime/tax_rules
RESPONSIBILITY: Deterministic tax rule registry and obligation scheduling.
*/
#include "runtime/dom_tax_rules.h"

#include <algorithm>
#include <vector>

extern "C" {
#include "domino/core/spacetime.h"
}

#include "dominium/econ_schema.h"

namespace {

struct TaxEntry {
    dom_tax_rule_desc desc;
    std::string id;
};

static bool entry_less(const TaxEntry &a, const TaxEntry &b) {
    if (a.desc.jurisdiction_id != b.desc.jurisdiction_id) {
        return a.desc.jurisdiction_id < b.desc.jurisdiction_id;
    }
    if (a.desc.id_hash != b.desc.id_hash) {
        return a.desc.id_hash < b.desc.id_hash;
    }
    return a.id < b.id;
}

static int compute_hash_id(const char *bytes, u32 len, dom_tax_rule_id *out_id) {
    u64 hash = 0ull;
    if (!bytes || len == 0u || !out_id) {
        return DOM_TAX_INVALID_ARGUMENT;
    }
    if (dom_id_hash64(bytes, len, &hash) != DOM_SPACETIME_OK) {
        return DOM_TAX_ERR;
    }
    if (hash == 0ull) {
        return DOM_TAX_ERR;
    }
    *out_id = hash;
    return DOM_TAX_OK;
}

static TaxEntry *find_entry(std::vector<TaxEntry> &list, dom_tax_rule_id id_hash) {
    size_t i;
    for (i = 0u; i < list.size(); ++i) {
        if (list[i].desc.id_hash == id_hash) {
            return &list[i];
        }
    }
    return 0;
}

static const TaxEntry *find_entry_const(const std::vector<TaxEntry> &list, dom_tax_rule_id id_hash) {
    size_t i;
    for (i = 0u; i < list.size(); ++i) {
        if (list[i].desc.id_hash == id_hash) {
            return &list[i];
        }
    }
    return 0;
}

static int compute_rate_amount(dom_amount_t base_amount,
                               u32 rate_bps,
                               u32 rounding_mode,
                               dom_amount_t *out_amount) {
    const dom_amount_t denom = 10000;
    dom_amount_t numer;
    dom_amount_t amount;
    if (!out_amount) {
        return DOM_TAX_INVALID_ARGUMENT;
    }
    *out_amount = 0;
    if (base_amount <= 0 || rate_bps == 0u) {
        return DOM_TAX_OK;
    }
    if (rate_bps > 10000u) {
        return DOM_TAX_INVALID_ARGUMENT;
    }
    if (base_amount > DOM_LEDGER_AMOUNT_MAX / (dom_amount_t)rate_bps) {
        return DOM_TAX_OVERFLOW;
    }
    numer = base_amount * (dom_amount_t)rate_bps;
    amount = numer / denom;
    if (rounding_mode == ECON_MONEY_ROUND_CEIL && (numer % denom) != 0) {
        amount += 1;
    } else if (rounding_mode == ECON_MONEY_ROUND_FLOOR) {
        /* amount already floored for positive values */
    }
    *out_amount = amount;
    return DOM_TAX_OK;
}

} // namespace

struct dom_tax_registry {
    std::vector<TaxEntry> entries;
};

dom_tax_registry *dom_tax_registry_create(void) {
    return new dom_tax_registry();
}

void dom_tax_registry_destroy(dom_tax_registry *registry) {
    if (!registry) {
        return;
    }
    delete registry;
}

int dom_tax_registry_register(dom_tax_registry *registry,
                              const dom_tax_rule_desc *desc) {
    TaxEntry entry;
    dom_tax_rule_desc tmp;
    int rc;
    if (!registry || !desc) {
        return DOM_TAX_INVALID_ARGUMENT;
    }
    tmp = *desc;
    if (tmp.id && tmp.id_len > 0u) {
        rc = compute_hash_id(tmp.id, tmp.id_len, &tmp.id_hash);
        if (rc != DOM_TAX_OK) {
            return rc;
        }
    }
    if (tmp.id_hash == 0ull) {
        return DOM_TAX_INVALID_ARGUMENT;
    }
    if (find_entry(registry->entries, tmp.id_hash)) {
        return DOM_TAX_DUPLICATE_ID;
    }
    entry.desc = tmp;
    entry.id.assign(tmp.id ? tmp.id : "", tmp.id ? tmp.id_len : 0u);
    registry->entries.push_back(entry);
    std::sort(registry->entries.begin(), registry->entries.end(), entry_less);
    return DOM_TAX_OK;
}

int dom_tax_registry_get(const dom_tax_registry *registry,
                         dom_tax_rule_id id_hash,
                         dom_tax_rule_desc *out_desc) {
    const TaxEntry *entry;
    if (!registry || !out_desc) {
        return DOM_TAX_INVALID_ARGUMENT;
    }
    entry = find_entry_const(registry->entries, id_hash);
    if (!entry) {
        return DOM_TAX_NOT_FOUND;
    }
    *out_desc = entry->desc;
    out_desc->id = entry->id.empty() ? 0 : entry->id.c_str();
    out_desc->id_len = (u32)entry->id.size();
    return DOM_TAX_OK;
}

int dom_tax_registry_collect(const dom_tax_registry *registry,
                             dom_jurisdiction_id jurisdiction_id,
                             const dom_tax_rule_desc **out_rules,
                             u32 *out_rule_count) {
    size_t i;
    size_t start = 0u;
    size_t count = 0u;
    if (!registry || !out_rules || !out_rule_count) {
        return DOM_TAX_INVALID_ARGUMENT;
    }
    *out_rules = 0;
    *out_rule_count = 0u;
    for (i = 0u; i < registry->entries.size(); ++i) {
        if (registry->entries[i].desc.jurisdiction_id == jurisdiction_id) {
            start = i;
            break;
        }
    }
    if (i == registry->entries.size()) {
        return DOM_TAX_NOT_FOUND;
    }
    for (i = start; i < registry->entries.size(); ++i) {
        if (registry->entries[i].desc.jurisdiction_id != jurisdiction_id) {
            break;
        }
        count++;
    }
    *out_rules = &registry->entries[start].desc;
    *out_rule_count = (u32)count;
    return DOM_TAX_OK;
}

int dom_tax_compute_amount(dom_amount_t base_amount,
                           u32 rate_bps,
                           u32 rounding_mode,
                           dom_amount_t *out_amount) {
    return compute_rate_amount(base_amount, rate_bps, rounding_mode, out_amount);
}

int dom_tax_schedule_sales(dom_ledger *ledger,
                           const dom_tax_rule_desc *rule,
                           dom_account_id_t taxpayer_account,
                           dom_amount_t taxable_amount,
                           dom_act_time_t act_time,
                           dom_obligation_id_t *out_obligation_id) {
    dom_ledger_posting postings[2];
    dom_ledger_transaction tx;
    dom_transaction_id_t tx_id = 0ull;
    dom_obligation_id_t obligation_id = 0ull;
    dom_amount_t tax_amount = 0;
    int rc;

    if (!ledger || !rule) {
        return DOM_TAX_INVALID_ARGUMENT;
    }
    if (rule->revenue_account_id == 0ull || rule->asset_id == 0ull) {
        return DOM_TAX_INVALID_ARGUMENT;
    }
    rc = compute_rate_amount(taxable_amount, rule->rate_bps,
                             rule->rounding_mode, &tax_amount);
    if (rc != DOM_TAX_OK) {
        return rc;
    }
    if (tax_amount <= 0) {
        if (out_obligation_id) {
            *out_obligation_id = 0ull;
        }
        return DOM_TAX_OK;
    }
    if (dom_ledger_next_tx_id(ledger, &tx_id) != DOM_LEDGER_OK) {
        return DOM_TAX_LEDGER_ERROR;
    }
    if (dom_ledger_next_obligation_id(ledger, &obligation_id) != DOM_LEDGER_OK) {
        return DOM_TAX_LEDGER_ERROR;
    }
    postings[0].account_id = taxpayer_account;
    postings[0].asset_id = rule->asset_id;
    postings[0].amount = -(dom_amount_t)tax_amount;
    postings[0].lot_id = 0ull;
    postings[0].provenance_id = 0ull;

    postings[1].account_id = rule->revenue_account_id;
    postings[1].asset_id = rule->asset_id;
    postings[1].amount = (dom_amount_t)tax_amount;
    postings[1].lot_id = 0ull;
    postings[1].provenance_id = 0ull;

    tx.tx_id = tx_id;
    tx.posting_count = 2u;
    tx.postings = postings;

    if (dom_ledger_obligation_schedule(ledger, obligation_id, act_time, &tx, 0) != DOM_LEDGER_OK) {
        return DOM_TAX_LEDGER_ERROR;
    }
    if (out_obligation_id) {
        *out_obligation_id = obligation_id;
    }
    return DOM_TAX_OK;
}

int dom_tax_schedule_periodic(dom_ledger *ledger,
                              const dom_tax_rule_desc *rule,
                              dom_account_id_t taxpayer_account,
                              dom_amount_t taxable_amount,
                              dom_act_time_t start_act,
                              dom_obligation_id_t *out_obligation_id,
                              dom_act_time_t *out_next_due) {
    dom_act_time_t next_due;
    if (!rule) {
        return DOM_TAX_INVALID_ARGUMENT;
    }
    if (rule->schedule_kind != DOM_TAX_SCHEDULE_PHYSICAL) {
        return DOM_TAX_NOT_IMPLEMENTED;
    }
    if (rule->period_ticks <= 0) {
        return DOM_TAX_INVALID_ARGUMENT;
    }
    next_due = start_act + rule->period_ticks;
    if (out_next_due) {
        *out_next_due = next_due;
    }
    return dom_tax_schedule_sales(ledger, rule, taxpayer_account,
                                  taxable_amount, start_act, out_obligation_id);
}
