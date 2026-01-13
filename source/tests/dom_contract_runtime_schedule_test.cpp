/*
TEST: dom_contract_runtime_schedule_test
PURPOSE: Deterministic contract scheduling + obligation execution.
*/
#include "runtime/dom_contract_runtime.h"

#include <string.h>

extern "C" {
#include "domino/core/spacetime.h"
}

static int run_once(dom_amount_t *out_payer, dom_amount_t *out_payee) {
    dom_ledger ledger;
    dom_contract_template_registry *templates = 0;
    dom_contract_obligation_desc obligation;
    dom_contract_template_desc template_desc;
    dom_contract_role_binding_desc bindings[2];
    dom_contract_instance_desc instance;
    dom_contract_schedule_result result;
    dom_ledger_posting postings[2];
    dom_ledger_transaction tx;
    dom_transaction_id_t tx_id = 0ull;
    dom_amount_t payer_balance = 0;
    dom_amount_t payee_balance = 0;
    u64 asset_hash = 0ull;
    u64 template_hash = 0ull;
    u64 role_from_hash = 0ull;
    u64 role_to_hash = 0ull;

    if (dom_ledger_init(&ledger) != DOM_LEDGER_OK) {
        return 1;
    }

    if (dom_ledger_account_create(&ledger, 1ull, DOM_LEDGER_ACCOUNT_ALLOW_NEGATIVE) != DOM_LEDGER_OK) {
        return 2;
    }
    if (dom_ledger_account_create(&ledger, 2ull, 0u) != DOM_LEDGER_OK) {
        return 3;
    }
    if (dom_ledger_account_create(&ledger, 3ull, 0u) != DOM_LEDGER_OK) {
        return 4;
    }

    if (dom_id_hash64("asset_credit", 12u, &asset_hash) != DOM_SPACETIME_OK) {
        return 5;
    }
    if (dom_id_hash64("rent", 4u, &template_hash) != DOM_SPACETIME_OK) {
        return 6;
    }
    if (dom_id_hash64("payer", 5u, &role_from_hash) != DOM_SPACETIME_OK) {
        return 7;
    }
    if (dom_id_hash64("payee", 5u, &role_to_hash) != DOM_SPACETIME_OK) {
        return 8;
    }

    if (dom_ledger_next_tx_id(&ledger, &tx_id) != DOM_LEDGER_OK) {
        return 9;
    }
    postings[0].account_id = 1ull;
    postings[0].asset_id = asset_hash;
    postings[0].amount = -200;
    postings[0].lot_id = 0ull;
    postings[0].provenance_id = 0ull;
    postings[1].account_id = 2ull;
    postings[1].asset_id = asset_hash;
    postings[1].amount = 200;
    postings[1].lot_id = 0ull;
    postings[1].provenance_id = 0ull;
    tx.tx_id = tx_id;
    tx.posting_count = 2u;
    tx.postings = postings;
    if (dom_ledger_transaction_apply(&ledger, &tx, 0) != DOM_LEDGER_OK) {
        return 10;
    }

    templates = dom_contract_template_registry_create();
    if (!templates) {
        return 11;
    }
    obligation.role_from_id = "payer";
    obligation.role_from_id_len = 5u;
    obligation.role_from_hash = role_from_hash;
    obligation.role_to_id = "payee";
    obligation.role_to_id_len = 5u;
    obligation.role_to_hash = role_to_hash;
    obligation.asset_id = "asset_credit";
    obligation.asset_id_len = 12u;
    obligation.asset_id_hash = asset_hash;
    obligation.amount = 100;
    obligation.offset_ticks = 10ull;

    template_desc.id = "rent";
    template_desc.id_len = 4u;
    template_desc.id_hash = template_hash;
    template_desc.obligations = &obligation;
    template_desc.obligation_count = 1u;

    if (dom_contract_template_registry_register(templates, &template_desc) != DOM_CONTRACT_TEMPLATE_OK) {
        dom_contract_template_registry_destroy(templates);
        return 12;
    }

    bindings[0].role_id = "payer";
    bindings[0].role_id_len = 5u;
    bindings[0].role_id_hash = role_from_hash;
    bindings[0].account_id = 2ull;
    bindings[1].role_id = "payee";
    bindings[1].role_id_len = 5u;
    bindings[1].role_id_hash = role_to_hash;
    bindings[1].account_id = 3ull;

    instance.template_id = "rent";
    instance.template_id_len = 4u;
    instance.template_id_hash = template_hash;
    instance.role_bindings = bindings;
    instance.role_binding_count = 2u;
    instance.start_act = 100;

    if (dom_contract_runtime_schedule(&ledger, templates, &instance, &result) != DOM_CONTRACT_RUNTIME_OK) {
        dom_contract_template_registry_destroy(templates);
        return 13;
    }
    if (result.obligation_count != 1u) {
        dom_contract_template_registry_destroy(templates);
        return 14;
    }

    if (dom_ledger_process_until(&ledger, 110) != DOM_LEDGER_OK) {
        dom_contract_template_registry_destroy(templates);
        return 15;
    }
    if (dom_ledger_balance_get(&ledger, 2ull, asset_hash, &payer_balance) != DOM_LEDGER_OK) {
        dom_contract_template_registry_destroy(templates);
        return 16;
    }
    if (dom_ledger_balance_get(&ledger, 3ull, asset_hash, &payee_balance) != DOM_LEDGER_OK) {
        dom_contract_template_registry_destroy(templates);
        return 17;
    }

    dom_contract_template_registry_destroy(templates);
    if (out_payer) {
        *out_payer = payer_balance;
    }
    if (out_payee) {
        *out_payee = payee_balance;
    }
    return 0;
}

int main(void) {
    dom_amount_t payer_a = 0;
    dom_amount_t payee_a = 0;
    dom_amount_t payer_b = 0;
    dom_amount_t payee_b = 0;
    int rc;

    rc = run_once(&payer_a, &payee_a);
    if (rc != 0) {
        return rc;
    }
    rc = run_once(&payer_b, &payee_b);
    if (rc != 0) {
        return rc;
    }
    if (payer_a != payer_b || payee_a != payee_b) {
        return 100;
    }
    if (payer_a != 100 || payee_a != 100) {
        return 101;
    }
    return 0;
}
