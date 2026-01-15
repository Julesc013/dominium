/*
FILE: source/domino/core/dom_ledger_core.c
MODULE: Domino
RESPONSIBILITY: Ledger core init and ID generation.
*/
#include "core/dom_ledger_internal.h"

#include <string.h>

int dom_ledger_amount_add_checked(dom_amount_t a, dom_amount_t b, dom_amount_t *out_val) {
    if (!out_val) {
        return DOM_LEDGER_INVALID;
    }
    if (b > 0) {
        if (a > (DOM_LEDGER_AMOUNT_MAX - b)) {
            return DOM_LEDGER_OVERFLOW;
        }
    } else if (b < 0) {
        if (a < (DOM_LEDGER_AMOUNT_MIN - b)) {
            return DOM_LEDGER_OVERFLOW;
        }
    }
    *out_val = (dom_amount_t)(a + b);
    return DOM_LEDGER_OK;
}

int dom_ledger_init(dom_ledger *ledger) {
    int rc;
    if (!ledger) {
        return DOM_LEDGER_INVALID;
    }
    memset(ledger, 0, sizeof(*ledger));
    rc = dom_time_event_queue_init(&ledger->event_queue,
                                   ledger->event_storage,
                                   DOM_LEDGER_MAX_EVENTS);
    if (rc != DOM_TIME_OK) {
        return DOM_LEDGER_ERR;
    }
    (void)dom_time_event_id_init(&ledger->event_id_gen, 1u);
    ledger->next_tx_id = 1u;
    ledger->next_lot_id = 1u;
    ledger->next_obligation_id = 1u;
    return DOM_LEDGER_OK;
}

int dom_ledger_set_next_tx_id(dom_ledger *ledger, dom_transaction_id_t next_id) {
    if (!ledger || next_id == 0u) {
        return DOM_LEDGER_INVALID;
    }
    ledger->next_tx_id = next_id;
    return DOM_LEDGER_OK;
}

int dom_ledger_set_next_lot_id(dom_ledger *ledger, dom_lot_id_t next_id) {
    if (!ledger || next_id == 0u) {
        return DOM_LEDGER_INVALID;
    }
    ledger->next_lot_id = next_id;
    return DOM_LEDGER_OK;
}

int dom_ledger_set_next_obligation_id(dom_ledger *ledger, dom_obligation_id_t next_id) {
    if (!ledger || next_id == 0u) {
        return DOM_LEDGER_INVALID;
    }
    ledger->next_obligation_id = next_id;
    return DOM_LEDGER_OK;
}

int dom_ledger_next_tx_id(dom_ledger *ledger, dom_transaction_id_t *out_id) {
    if (!ledger || !out_id) {
        return DOM_LEDGER_INVALID;
    }
    if (ledger->next_tx_id == 0u) {
        return DOM_LEDGER_OVERFLOW;
    }
    *out_id = ledger->next_tx_id;
    ledger->next_tx_id += 1u;
    if (ledger->next_tx_id == 0u) {
        return DOM_LEDGER_OVERFLOW;
    }
    return DOM_LEDGER_OK;
}

int dom_ledger_next_lot_id(dom_ledger *ledger, dom_lot_id_t *out_id) {
    if (!ledger || !out_id) {
        return DOM_LEDGER_INVALID;
    }
    if (ledger->next_lot_id == 0u) {
        return DOM_LEDGER_OVERFLOW;
    }
    *out_id = ledger->next_lot_id;
    ledger->next_lot_id += 1u;
    if (ledger->next_lot_id == 0u) {
        return DOM_LEDGER_OVERFLOW;
    }
    return DOM_LEDGER_OK;
}

int dom_ledger_next_obligation_id(dom_ledger *ledger, dom_obligation_id_t *out_id) {
    if (!ledger || !out_id) {
        return DOM_LEDGER_INVALID;
    }
    if (ledger->next_obligation_id == 0u) {
        return DOM_LEDGER_OVERFLOW;
    }
    *out_id = ledger->next_obligation_id;
    ledger->next_obligation_id += 1u;
    if (ledger->next_obligation_id == 0u) {
        return DOM_LEDGER_OVERFLOW;
    }
    return DOM_LEDGER_OK;
}
