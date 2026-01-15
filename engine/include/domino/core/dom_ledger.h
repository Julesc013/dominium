/*
FILE: include/domino/core/dom_ledger.h
MODULE: Domino
RESPONSIBILITY: Deterministic engine ledger core (accounts, assets, transactions, lots, obligations).
NOTES: Pure C90 header; no currencies, markets, or UI.
*/
#ifndef DOMINO_CORE_DOM_LEDGER_H
#define DOMINO_CORE_DOM_LEDGER_H

#include "domino/core/types.h"
#include "domino/core/dom_time_events.h"

#ifdef __cplusplus
extern "C" {
#endif

enum {
    DOM_LEDGER_OK = 0,
    DOM_LEDGER_ERR = -1,
    DOM_LEDGER_INVALID = -2,
    DOM_LEDGER_OVERFLOW = -3,
    DOM_LEDGER_FULL = -4,
    DOM_LEDGER_NOT_FOUND = -5,
    DOM_LEDGER_IMBALANCED = -6,
    DOM_LEDGER_INSUFFICIENT = -7,
    DOM_LEDGER_DUPLICATE = -8,
    DOM_LEDGER_ALREADY_EXECUTED = -9,
    DOM_LEDGER_EMPTY = -10
};

typedef u64 dom_asset_id_t;
typedef u64 dom_account_id_t;
typedef i64 dom_amount_t;
typedef u64 dom_lot_id_t;
typedef u64 dom_transaction_id_t;
typedef u64 dom_obligation_id_t;

enum {
    DOM_LEDGER_ACCOUNT_ALLOW_NEGATIVE = 1u << 0
};

enum {
    DOM_LEDGER_OBLIGATION_ACTIVE = 1u << 0,
    DOM_LEDGER_OBLIGATION_CANCELLED = 1u << 1,
    DOM_LEDGER_OBLIGATION_EXECUTED = 1u << 2
};

#define DOM_LEDGER_MAX_ACCOUNTS 128u
#define DOM_LEDGER_MAX_ASSETS_PER_ACCOUNT 16u
#define DOM_LEDGER_MAX_LOTS_PER_ASSET 32u
#define DOM_LEDGER_MAX_POSTINGS 32u
#define DOM_LEDGER_MAX_OBLIGATIONS 128u
#define DOM_LEDGER_MAX_EVENTS 256u

#define DOM_LEDGER_AMOUNT_MAX ((dom_amount_t)0x7fffffffffffffffLL)
#define DOM_LEDGER_AMOUNT_MIN ((dom_amount_t)(-0x7fffffffffffffffLL - 1LL))

typedef struct dom_ledger_lot {
    dom_lot_id_t lot_id;
    dom_transaction_id_t source_tx;
    u64 provenance_id;
    dom_act_time_t creation_act;
    dom_amount_t amount;
} dom_ledger_lot;

typedef struct dom_ledger_asset_slot {
    dom_asset_id_t asset_id;
    dom_amount_t balance;
    u32 lot_count;
    dom_ledger_lot lots[DOM_LEDGER_MAX_LOTS_PER_ASSET];
} dom_ledger_asset_slot;

typedef struct dom_ledger_account {
    dom_account_id_t account_id;
    u32 flags;
    u32 asset_count;
    dom_ledger_asset_slot assets[DOM_LEDGER_MAX_ASSETS_PER_ACCOUNT];
} dom_ledger_account;

typedef struct dom_ledger_posting {
    dom_account_id_t account_id;
    dom_asset_id_t asset_id;
    dom_amount_t amount;
    dom_lot_id_t lot_id;    /* optional: consume specific lot when debiting */
    u64 provenance_id;      /* used for lot creation on credits */
} dom_ledger_posting;

typedef struct dom_ledger_transaction {
    dom_transaction_id_t tx_id;
    u32 posting_count;
    const dom_ledger_posting *postings;
} dom_ledger_transaction;

typedef struct dom_ledger_obligation {
    dom_obligation_id_t obligation_id;
    dom_act_time_t trigger_time;
    dom_transaction_id_t tx_id;
    u32 posting_count;
    dom_ledger_posting postings[DOM_LEDGER_MAX_POSTINGS];
    u32 flags;
    dom_time_event_id event_id;
} dom_ledger_obligation;

typedef struct dom_ledger {
    dom_ledger_account accounts[DOM_LEDGER_MAX_ACCOUNTS];
    u32 account_count;

    dom_ledger_obligation obligations[DOM_LEDGER_MAX_OBLIGATIONS];
    u32 obligation_count;

    dom_time_event_queue event_queue;
    dom_time_event event_storage[DOM_LEDGER_MAX_EVENTS];
    dom_time_event_id_gen event_id_gen;

    dom_transaction_id_t next_tx_id;
    dom_lot_id_t next_lot_id;
    dom_obligation_id_t next_obligation_id;
} dom_ledger;

typedef struct dom_ledger_asset_summary {
    dom_asset_id_t asset_id;
    dom_amount_t balance;
    u64 provenance_hash;
} dom_ledger_asset_summary;

typedef struct dom_ledger_account_summary {
    dom_account_id_t account_id;
    u32 asset_count;
} dom_ledger_account_summary;

int dom_ledger_init(dom_ledger *ledger);

int dom_ledger_set_next_tx_id(dom_ledger *ledger, dom_transaction_id_t next_id);
int dom_ledger_set_next_lot_id(dom_ledger *ledger, dom_lot_id_t next_id);
int dom_ledger_set_next_obligation_id(dom_ledger *ledger, dom_obligation_id_t next_id);

int dom_ledger_next_tx_id(dom_ledger *ledger, dom_transaction_id_t *out_id);
int dom_ledger_next_lot_id(dom_ledger *ledger, dom_lot_id_t *out_id);
int dom_ledger_next_obligation_id(dom_ledger *ledger, dom_obligation_id_t *out_id);

int dom_ledger_account_create(dom_ledger *ledger, dom_account_id_t account_id, u32 flags);
int dom_ledger_account_copy(const dom_ledger *ledger,
                            dom_account_id_t account_id,
                            dom_ledger_account *out_account);
int dom_ledger_balance_get(const dom_ledger *ledger,
                           dom_account_id_t account_id,
                           dom_asset_id_t asset_id,
                           dom_amount_t *out_balance);

int dom_ledger_transaction_apply(dom_ledger *ledger,
                                 const dom_ledger_transaction *tx,
                                 dom_act_time_t act_time);

int dom_ledger_obligation_schedule(dom_ledger *ledger,
                                   dom_obligation_id_t obligation_id,
                                   dom_act_time_t trigger_time,
                                   const dom_ledger_transaction *tx,
                                   dom_time_event_id *out_event_id);
int dom_ledger_obligation_cancel(dom_ledger *ledger,
                                 dom_obligation_id_t obligation_id);

int dom_ledger_process_until(dom_ledger *ledger, dom_act_time_t target_act);
int dom_ledger_next_due_act(const dom_ledger *ledger, dom_act_time_t *out_act);

int dom_ledger_account_summarize(const dom_ledger *ledger,
                                 dom_account_id_t account_id,
                                 dom_ledger_account_summary *out_summary,
                                 dom_ledger_asset_summary *out_assets,
                                 u32 asset_capacity);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINO_CORE_DOM_LEDGER_H */
