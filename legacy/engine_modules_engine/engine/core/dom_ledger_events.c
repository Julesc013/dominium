/*
FILE: source/domino/core/dom_ledger_events.c
MODULE: Domino
RESPONSIBILITY: Ledger obligations and event-driven execution.
*/
#include "core/dom_ledger_internal.h"

#include <string.h>

int dom_ledger_obligation_find_index(const dom_ledger *ledger,
                                     dom_obligation_id_t obligation_id,
                                     u32 *out_index) {
    u32 i;
    if (!ledger || !out_index || obligation_id == 0u) {
        return DOM_LEDGER_INVALID;
    }
    for (i = 0u; i < ledger->obligation_count; ++i) {
        if (ledger->obligations[i].obligation_id == obligation_id) {
            *out_index = i;
            return DOM_LEDGER_OK;
        }
    }
    return DOM_LEDGER_NOT_FOUND;
}

static int dom_ledger_event_cb(void *user, const dom_time_event *ev) {
    dom_ledger *ledger = (dom_ledger *)user;
    dom_ledger_obligation *obl = 0;
    dom_ledger_transaction tx;
    u32 i;
    int rc;
    if (!ledger || !ev) {
        return DOM_LEDGER_INVALID;
    }
    for (i = 0u; i < ledger->obligation_count; ++i) {
        if (ledger->obligations[i].obligation_id == ev->payload_id) {
            obl = &ledger->obligations[i];
            break;
        }
    }
    if (!obl) {
        return DOM_LEDGER_NOT_FOUND;
    }
    if (obl->flags & DOM_LEDGER_OBLIGATION_EXECUTED) {
        return DOM_LEDGER_ALREADY_EXECUTED;
    }
    if (obl->flags & DOM_LEDGER_OBLIGATION_CANCELLED) {
        return DOM_LEDGER_OK;
    }
    tx.tx_id = obl->tx_id;
    tx.posting_count = obl->posting_count;
    tx.postings = obl->postings;
    rc = dom_ledger_transaction_apply(ledger, &tx, ev->trigger_time);
    if (rc != DOM_LEDGER_OK) {
        return rc;
    }
    obl->flags |= DOM_LEDGER_OBLIGATION_EXECUTED;
    obl->flags &= ~(DOM_LEDGER_OBLIGATION_ACTIVE);
    return DOM_LEDGER_OK;
}

int dom_ledger_obligation_schedule(dom_ledger *ledger,
                                   dom_obligation_id_t obligation_id,
                                   dom_act_time_t trigger_time,
                                   const dom_ledger_transaction *tx,
                                   dom_time_event_id *out_event_id) {
    dom_ledger_obligation ob;
    dom_time_event ev;
    u32 i;
    int rc;
    if (!ledger || !tx || !tx->postings || tx->posting_count == 0u) {
        return DOM_LEDGER_INVALID;
    }
    if (tx->posting_count > DOM_LEDGER_MAX_POSTINGS) {
        return DOM_LEDGER_FULL;
    }
    if (obligation_id == 0u) {
        rc = dom_ledger_next_obligation_id(ledger, &obligation_id);
        if (rc != DOM_LEDGER_OK) {
            return rc;
        }
    }
    for (i = 0u; i < ledger->obligation_count; ++i) {
        if (ledger->obligations[i].obligation_id == obligation_id) {
            return DOM_LEDGER_DUPLICATE;
        }
    }
    if (ledger->obligation_count >= DOM_LEDGER_MAX_OBLIGATIONS) {
        return DOM_LEDGER_FULL;
    }
    memset(&ob, 0, sizeof(ob));
    ob.obligation_id = obligation_id;
    ob.trigger_time = trigger_time;
    ob.tx_id = tx->tx_id;
    if (ob.tx_id == 0u) {
        rc = dom_ledger_next_tx_id(ledger, &ob.tx_id);
        if (rc != DOM_LEDGER_OK) {
            return rc;
        }
    }
    ob.posting_count = tx->posting_count;
    for (i = 0u; i < tx->posting_count; ++i) {
        ob.postings[i] = tx->postings[i];
    }
    ob.flags = DOM_LEDGER_OBLIGATION_ACTIVE;

    rc = dom_time_event_id_next(&ledger->event_id_gen, &ob.event_id);
    if (rc != DOM_TIME_OK) {
        return DOM_LEDGER_ERR;
    }
    ev.event_id = ob.event_id;
    ev.trigger_time = trigger_time;
    ev.order_key = (u64)obligation_id;
    ev.payload_id = (u64)obligation_id;
    rc = dom_time_event_schedule(&ledger->event_queue, &ev);
    if (rc != DOM_TIME_OK) {
        return DOM_LEDGER_ERR;
    }

    for (i = 0u; i < ledger->obligation_count; ++i) {
        if (ledger->obligations[i].obligation_id > obligation_id) {
            break;
        }
    }
    if (i < ledger->obligation_count) {
        memmove(&ledger->obligations[i + 1u],
                &ledger->obligations[i],
                (ledger->obligation_count - i) * sizeof(dom_ledger_obligation));
    }
    ledger->obligations[i] = ob;
    ledger->obligation_count += 1u;

    if (out_event_id) {
        *out_event_id = ob.event_id;
    }
    return DOM_LEDGER_OK;
}

int dom_ledger_obligation_cancel(dom_ledger *ledger,
                                 dom_obligation_id_t obligation_id) {
    u32 idx;
    dom_ledger_obligation *obl;
    int rc;
    if (!ledger || obligation_id == 0u) {
        return DOM_LEDGER_INVALID;
    }
    rc = dom_ledger_obligation_find_index(ledger, obligation_id, &idx);
    if (rc != DOM_LEDGER_OK) {
        return rc;
    }
    obl = &ledger->obligations[idx];
    if (obl->flags & DOM_LEDGER_OBLIGATION_EXECUTED) {
        return DOM_LEDGER_ALREADY_EXECUTED;
    }
    if (obl->flags & DOM_LEDGER_OBLIGATION_CANCELLED) {
        return DOM_LEDGER_OK;
    }
    (void)dom_time_event_cancel(&ledger->event_queue, obl->event_id);
    obl->flags |= DOM_LEDGER_OBLIGATION_CANCELLED;
    obl->flags &= ~(DOM_LEDGER_OBLIGATION_ACTIVE);
    return DOM_LEDGER_OK;
}

int dom_ledger_process_until(dom_ledger *ledger, dom_act_time_t target_act) {
    int rc;
    if (!ledger) {
        return DOM_LEDGER_INVALID;
    }
    rc = dom_time_process_until(&ledger->event_queue, target_act, dom_ledger_event_cb, ledger);
    if (rc == DOM_TIME_OK) {
        return DOM_LEDGER_OK;
    }
    return rc;
}

int dom_ledger_next_due_act(const dom_ledger *ledger, dom_act_time_t *out_act) {
    int rc;
    if (!ledger) {
        return DOM_LEDGER_INVALID;
    }
    rc = dom_time_event_next_time(&ledger->event_queue, out_act);
    if (rc == DOM_TIME_OK) {
        return DOM_LEDGER_OK;
    }
    if (rc == DOM_TIME_EMPTY) {
        return DOM_LEDGER_EMPTY;
    }
    return DOM_LEDGER_ERR;
}
