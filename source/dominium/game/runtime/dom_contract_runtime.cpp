/*
FILE: source/dominium/game/runtime/dom_contract_runtime.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium impl / game/runtime/contract_runtime
RESPONSIBILITY: Deterministic contract runtime scheduling via engine ledger.
*/
#include "runtime/dom_contract_runtime.h"

#include <algorithm>
#include <vector>

extern "C" {
#include "domino/core/spacetime.h"
}

namespace {

struct RoleBinding {
    dom_contract_role_id role_hash;
    dom_account_id_t account_id;
};

static int compute_hash_id(const char *bytes, u32 len, u64 *out_id) {
    u64 hash = 0ull;
    if (!bytes || len == 0u || !out_id) {
        return DOM_CONTRACT_RUNTIME_INVALID_ARGUMENT;
    }
    if (dom_id_hash64(bytes, len, &hash) != DOM_SPACETIME_OK) {
        return DOM_CONTRACT_RUNTIME_ERR;
    }
    if (hash == 0ull) {
        return DOM_CONTRACT_RUNTIME_ERR;
    }
    *out_id = hash;
    return DOM_CONTRACT_RUNTIME_OK;
}

static bool binding_less(const RoleBinding &a, const RoleBinding &b) {
    return a.role_hash < b.role_hash;
}

static bool obligation_less(const dom_contract_obligation &a,
                            const dom_contract_obligation &b) {
    if (a.offset_ticks != b.offset_ticks) {
        return a.offset_ticks < b.offset_ticks;
    }
    if (a.role_from_hash != b.role_from_hash) {
        return a.role_from_hash < b.role_from_hash;
    }
    if (a.role_to_hash != b.role_to_hash) {
        return a.role_to_hash < b.role_to_hash;
    }
    if (a.asset_id_hash != b.asset_id_hash) {
        return a.asset_id_hash < b.asset_id_hash;
    }
    return a.amount < b.amount;
}

static bool lookup_binding(const std::vector<RoleBinding> &bindings,
                           dom_contract_role_id role,
                           dom_account_id_t &out_account) {
    size_t i;
    for (i = 0u; i < bindings.size(); ++i) {
        if (bindings[i].role_hash == role) {
            out_account = bindings[i].account_id;
            return true;
        }
    }
    return false;
}

} // namespace

int dom_contract_runtime_schedule(dom_ledger *ledger,
                                  const dom_contract_template_registry *templates,
                                  const dom_contract_instance_desc *desc,
                                  dom_contract_schedule_result *out_result) {
    dom_contract_template_id template_hash = 0ull;
    dom_contract_template_info tmpl_info;
    std::vector<RoleBinding> bindings;
    std::vector<dom_contract_obligation> obligations;
    std::vector<dom_obligation_id_t> scheduled;
    size_t i;
    u64 tmp_hash = 0ull;

    if (out_result) {
        out_result->obligation_count = 0u;
        out_result->first_obligation_id = 0ull;
    }
    if (!ledger || !templates || !desc) {
        return DOM_CONTRACT_RUNTIME_INVALID_ARGUMENT;
    }

    if (desc->template_id && desc->template_id_len > 0u) {
        int rc = compute_hash_id(desc->template_id, desc->template_id_len, &template_hash);
        if (rc != DOM_CONTRACT_RUNTIME_OK) {
            return rc;
        }
        if (desc->template_id_hash != 0ull && desc->template_id_hash != template_hash) {
            return DOM_CONTRACT_RUNTIME_ERR;
        }
    } else {
        template_hash = desc->template_id_hash;
    }
    if (template_hash == 0ull) {
        return DOM_CONTRACT_RUNTIME_INVALID_ARGUMENT;
    }
    if (dom_contract_template_registry_get(templates, template_hash, &tmpl_info) != DOM_CONTRACT_TEMPLATE_OK) {
        return DOM_CONTRACT_RUNTIME_TEMPLATE_NOT_FOUND;
    }
    if (!tmpl_info.obligations || tmpl_info.obligation_count == 0u) {
        return DOM_CONTRACT_RUNTIME_ERR;
    }

    if (desc->role_bindings && desc->role_binding_count > 0u) {
        bindings.reserve(desc->role_binding_count);
        for (i = 0u; i < desc->role_binding_count; ++i) {
            const dom_contract_role_binding_desc &rb = desc->role_bindings[i];
            dom_contract_role_id role_hash = 0ull;
            if (rb.role_id && rb.role_id_len > 0u) {
                int rc = compute_hash_id(rb.role_id, rb.role_id_len, &tmp_hash);
                if (rc != DOM_CONTRACT_RUNTIME_OK) {
                    return rc;
                }
                if (rb.role_id_hash != 0ull && rb.role_id_hash != tmp_hash) {
                    return DOM_CONTRACT_RUNTIME_ERR;
                }
                role_hash = tmp_hash;
            } else {
                role_hash = rb.role_id_hash;
            }
            if (role_hash == 0ull || rb.account_id == 0ull) {
                return DOM_CONTRACT_RUNTIME_INVALID_ARGUMENT;
            }
            {
                RoleBinding binding;
                binding.role_hash = role_hash;
                binding.account_id = rb.account_id;
                bindings.push_back(binding);
            }
        }
        std::sort(bindings.begin(), bindings.end(), binding_less);
        for (i = 1u; i < bindings.size(); ++i) {
            if (bindings[i].role_hash == bindings[i - 1u].role_hash) {
                return DOM_CONTRACT_RUNTIME_ROLE_DUPLICATE;
            }
        }
    }

    obligations.assign(tmpl_info.obligations, tmpl_info.obligations + tmpl_info.obligation_count);
    std::sort(obligations.begin(), obligations.end(), obligation_less);

    for (i = 0u; i < obligations.size(); ++i) {
        const dom_contract_obligation &obl = obligations[i];
        dom_account_id_t from_account = 0ull;
        dom_account_id_t to_account = 0ull;
        dom_amount_t amount = obl.amount;
        dom_act_time_t trigger_time = desc->start_act;
        dom_ledger_posting postings[2];
        dom_ledger_transaction tx;
        dom_transaction_id_t tx_id = 0ull;
        dom_obligation_id_t obligation_id = 0ull;
        dom_time_event_id event_id = 0ull;
        dom_amount_t debit_amount = 0;

        if (!lookup_binding(bindings, obl.role_from_hash, from_account) ||
            !lookup_binding(bindings, obl.role_to_hash, to_account)) {
            return DOM_CONTRACT_RUNTIME_ROLE_MISSING;
        }
        if (amount == 0) {
            return DOM_CONTRACT_RUNTIME_ERR;
        }
        if (amount < 0) {
            amount = -amount;
            {
                dom_account_id_t tmp = from_account;
                from_account = to_account;
                to_account = tmp;
            }
        }
        if (obl.offset_ticks > (u64)DOM_TIME_ACT_MAX) {
            return DOM_CONTRACT_RUNTIME_OVERFLOW;
        }
        if (obl.offset_ticks > 0ull) {
            dom_act_time_t offset = (dom_act_time_t)obl.offset_ticks;
            if (trigger_time > DOM_TIME_ACT_MAX - offset) {
                return DOM_CONTRACT_RUNTIME_OVERFLOW;
            }
            trigger_time += offset;
        }

        if (dom_ledger_next_tx_id(ledger, &tx_id) != DOM_LEDGER_OK) {
            return DOM_CONTRACT_RUNTIME_LEDGER_ERROR;
        }
        if (dom_ledger_next_obligation_id(ledger, &obligation_id) != DOM_LEDGER_OK) {
            return DOM_CONTRACT_RUNTIME_LEDGER_ERROR;
        }

        debit_amount = -amount;
        postings[0].account_id = from_account;
        postings[0].asset_id = obl.asset_id_hash;
        postings[0].amount = debit_amount;
        postings[0].lot_id = 0ull;
        postings[0].provenance_id = 0ull;

        postings[1].account_id = to_account;
        postings[1].asset_id = obl.asset_id_hash;
        postings[1].amount = amount;
        postings[1].lot_id = 0ull;
        postings[1].provenance_id = 0ull;

        tx.tx_id = tx_id;
        tx.posting_count = 2u;
        tx.postings = postings;

        if (dom_ledger_obligation_schedule(ledger, obligation_id, trigger_time, &tx, &event_id) != DOM_LEDGER_OK) {
            size_t j;
            for (j = 0u; j < scheduled.size(); ++j) {
                dom_ledger_obligation_cancel(ledger, scheduled[j]);
            }
            return DOM_CONTRACT_RUNTIME_LEDGER_ERROR;
        }

        if (scheduled.empty() && out_result) {
            out_result->first_obligation_id = obligation_id;
        }
        scheduled.push_back(obligation_id);
    }

    if (out_result) {
        out_result->obligation_count = (u32)scheduled.size();
    }
    return DOM_CONTRACT_RUNTIME_OK;
}
