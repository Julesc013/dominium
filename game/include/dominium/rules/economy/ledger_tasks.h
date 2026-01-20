/*
FILE: include/dominium/rules/economy/ledger_tasks.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / economy
RESPONSIBILITY: Ledger task helpers for Work IR execution.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C89/C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Ledger ordering and updates are deterministic.
*/
#ifndef DOMINIUM_RULES_ECONOMY_LEDGER_TASKS_H
#define DOMINIUM_RULES_ECONOMY_LEDGER_TASKS_H

#include "domino/core/types.h"
#include "domino/core/dom_time_core.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct dom_ledger_account {
    u64 account_id;
    i64 balance;
} dom_ledger_account;

typedef struct dom_ledger_state {
    dom_ledger_account* accounts;
    u32 account_count;
    u32 account_capacity;
} dom_ledger_state;

void dom_ledger_state_init(dom_ledger_state* state,
                           dom_ledger_account* storage,
                           u32 capacity);
dom_ledger_account* dom_ledger_account_find(dom_ledger_state* state, u64 account_id);
dom_ledger_account* dom_ledger_account_ensure(dom_ledger_state* state, u64 account_id);

typedef struct dom_ledger_transfer {
    u64 transfer_id;
    u64 from_id;
    u64 to_id;
    i64 amount;
} dom_ledger_transfer;

typedef struct dom_contract_settlement {
    u64 contract_id;
    u64 payer_id;
    u64 payee_id;
    i64 amount;
} dom_contract_settlement;

typedef struct dom_production_step {
    u64 producer_id;
    i64 amount;
} dom_production_step;

typedef struct dom_consumption_step {
    u64 consumer_id;
    i64 amount;
} dom_consumption_step;

typedef struct dom_maintenance_step {
    u64 asset_id;
    u64 owner_id;
    i64 upkeep;
} dom_maintenance_step;

typedef enum dom_economy_audit_kind {
    DOM_ECON_AUDIT_TRANSFER = 1,
    DOM_ECON_AUDIT_CONTRACT = 2,
    DOM_ECON_AUDIT_PRODUCTION = 3,
    DOM_ECON_AUDIT_CONSUMPTION = 4,
    DOM_ECON_AUDIT_MAINTENANCE = 5
} dom_economy_audit_kind;

typedef struct dom_economy_audit_entry {
    u64 event_id;
    u32 kind;
    u64 primary_id;
    i64 amount;
} dom_economy_audit_entry;

typedef struct dom_economy_audit_log {
    dom_economy_audit_entry* entries;
    u32 count;
    u32 capacity;
    u64 next_event_id;
} dom_economy_audit_log;

void dom_economy_audit_init(dom_economy_audit_log* log,
                            dom_economy_audit_entry* storage,
                            u32 capacity,
                            u64 start_id);
int dom_economy_audit_record(dom_economy_audit_log* log,
                             u32 kind,
                             u64 primary_id,
                             i64 amount);

typedef struct dom_economy_runtime_state {
    u32 transfer_cursor;
    u32 contract_cursor;
    u32 production_cursor;
    u32 consumption_cursor;
    u32 maintenance_cursor;
} dom_economy_runtime_state;

void dom_economy_runtime_reset(dom_economy_runtime_state* state);

u32 dom_ledger_apply_transfer_slice(dom_ledger_state* ledger,
                                    const dom_ledger_transfer* transfers,
                                    u32 transfer_count,
                                    u32 start_index,
                                    u32 max_count,
                                    dom_economy_audit_log* audit);

u32 dom_ledger_apply_contract_slice(dom_ledger_state* ledger,
                                    const dom_contract_settlement* contracts,
                                    u32 contract_count,
                                    u32 start_index,
                                    u32 max_count,
                                    dom_economy_audit_log* audit);

u32 dom_ledger_apply_production_slice(dom_ledger_state* ledger,
                                      const dom_production_step* steps,
                                      u32 step_count,
                                      u32 start_index,
                                      u32 max_count,
                                      dom_economy_audit_log* audit);

u32 dom_ledger_apply_consumption_slice(dom_ledger_state* ledger,
                                       const dom_consumption_step* steps,
                                       u32 step_count,
                                       u32 start_index,
                                       u32 max_count,
                                       dom_economy_audit_log* audit);

u32 dom_ledger_apply_maintenance_slice(dom_ledger_state* ledger,
                                       const dom_maintenance_step* steps,
                                       u32 step_count,
                                       u32 start_index,
                                       u32 max_count,
                                       dom_economy_audit_log* audit);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_RULES_ECONOMY_LEDGER_TASKS_H */
