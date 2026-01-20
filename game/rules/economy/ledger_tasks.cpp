/*
FILE: game/rules/economy/ledger_tasks.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Game / economy rules
RESPONSIBILITY: Implements ledger task helpers for Work IR tasks.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
DETERMINISM: Ledger ordering and updates are deterministic.
*/
#include "dominium/rules/economy/ledger_tasks.h"

#include <string.h>

extern "C" {

void dom_ledger_state_init(dom_ledger_state* state,
                           dom_ledger_account* storage,
                           u32 capacity)
{
    if (!state) {
        return;
    }
    state->accounts = storage;
    state->account_count = 0u;
    state->account_capacity = capacity;
    if (storage && capacity > 0u) {
        memset(storage, 0, sizeof(dom_ledger_account) * (size_t)capacity);
    }
}

static int dom_ledger_account_cmp(const dom_ledger_account* a, const dom_ledger_account* b)
{
    if (!a || !b) {
        return a ? 1 : (b ? -1 : 0);
    }
    if (a->account_id < b->account_id) return -1;
    if (a->account_id > b->account_id) return 1;
    return 0;
}

dom_ledger_account* dom_ledger_account_find(dom_ledger_state* state, u64 account_id)
{
    u32 i;
    if (!state || !state->accounts) {
        return 0;
    }
    for (i = 0u; i < state->account_count; ++i) {
        if (state->accounts[i].account_id == account_id) {
            return &state->accounts[i];
        }
        if (state->accounts[i].account_id > account_id) {
            break;
        }
    }
    return 0;
}

dom_ledger_account* dom_ledger_account_ensure(dom_ledger_state* state, u64 account_id)
{
    u32 idx;
    u32 i;
    dom_ledger_account key;
    if (!state || !state->accounts) {
        return 0;
    }
    for (i = 0u; i < state->account_count; ++i) {
        if (state->accounts[i].account_id == account_id) {
            return &state->accounts[i];
        }
        if (state->accounts[i].account_id > account_id) {
            break;
        }
    }
    if (state->account_count >= state->account_capacity) {
        return 0;
    }
    idx = i;
    for (i = state->account_count; i > idx; --i) {
        state->accounts[i] = state->accounts[i - 1u];
    }
    key.account_id = account_id;
    key.balance = 0;
    state->accounts[idx] = key;
    state->account_count += 1u;
    return &state->accounts[idx];
}

void dom_economy_audit_init(dom_economy_audit_log* log,
                            dom_economy_audit_entry* storage,
                            u32 capacity,
                            u64 start_id)
{
    if (!log) {
        return;
    }
    log->entries = storage;
    log->count = 0u;
    log->capacity = capacity;
    log->next_event_id = start_id;
    if (storage && capacity > 0u) {
        memset(storage, 0, sizeof(dom_economy_audit_entry) * (size_t)capacity);
    }
}

int dom_economy_audit_record(dom_economy_audit_log* log,
                             u32 kind,
                             u64 primary_id,
                             i64 amount)
{
    dom_economy_audit_entry* entry;
    if (!log || !log->entries) {
        return -1;
    }
    if (log->count >= log->capacity) {
        return -2;
    }
    entry = &log->entries[log->count++];
    entry->event_id = log->next_event_id++;
    entry->kind = kind;
    entry->primary_id = primary_id;
    entry->amount = amount;
    return 0;
}

void dom_economy_runtime_reset(dom_economy_runtime_state* state)
{
    if (!state) {
        return;
    }
    state->transfer_cursor = 0u;
    state->contract_cursor = 0u;
    state->production_cursor = 0u;
    state->consumption_cursor = 0u;
    state->maintenance_cursor = 0u;
}

static u32 dom_ledger_apply_transfer(dom_ledger_state* ledger,
                                     u64 from_id,
                                     u64 to_id,
                                     i64 amount)
{
    dom_ledger_account* from;
    dom_ledger_account* to;
    if (!ledger) {
        return 0u;
    }
    from = dom_ledger_account_ensure(ledger, from_id);
    to = dom_ledger_account_ensure(ledger, to_id);
    if (!from || !to) {
        return 0u;
    }
    from->balance -= amount;
    to->balance += amount;
    return 1u;
}

u32 dom_ledger_apply_transfer_slice(dom_ledger_state* ledger,
                                    const dom_ledger_transfer* transfers,
                                    u32 transfer_count,
                                    u32 start_index,
                                    u32 max_count,
                                    dom_economy_audit_log* audit)
{
    u32 i;
    u32 processed = 0u;
    if (!ledger || !transfers || max_count == 0u) {
        return 0u;
    }
    if (start_index >= transfer_count) {
        return 0u;
    }
    for (i = 0u; i < max_count && (start_index + i) < transfer_count; ++i) {
        const dom_ledger_transfer* t = &transfers[start_index + i];
        if (dom_ledger_apply_transfer(ledger, t->from_id, t->to_id, t->amount) == 0u) {
            continue;
        }
        if (audit) {
            (void)dom_economy_audit_record(audit, DOM_ECON_AUDIT_TRANSFER, t->transfer_id, t->amount);
        }
        processed += 1u;
    }
    return processed;
}

u32 dom_ledger_apply_contract_slice(dom_ledger_state* ledger,
                                    const dom_contract_settlement* contracts,
                                    u32 contract_count,
                                    u32 start_index,
                                    u32 max_count,
                                    dom_economy_audit_log* audit)
{
    u32 i;
    u32 processed = 0u;
    if (!ledger || !contracts || max_count == 0u) {
        return 0u;
    }
    if (start_index >= contract_count) {
        return 0u;
    }
    for (i = 0u; i < max_count && (start_index + i) < contract_count; ++i) {
        const dom_contract_settlement* c = &contracts[start_index + i];
        if (dom_ledger_apply_transfer(ledger, c->payer_id, c->payee_id, c->amount) == 0u) {
            continue;
        }
        if (audit) {
            (void)dom_economy_audit_record(audit, DOM_ECON_AUDIT_CONTRACT, c->contract_id, c->amount);
        }
        processed += 1u;
    }
    return processed;
}

u32 dom_ledger_apply_production_slice(dom_ledger_state* ledger,
                                      const dom_production_step* steps,
                                      u32 step_count,
                                      u32 start_index,
                                      u32 max_count,
                                      dom_economy_audit_log* audit)
{
    u32 i;
    u32 processed = 0u;
    if (!ledger || !steps || max_count == 0u) {
        return 0u;
    }
    if (start_index >= step_count) {
        return 0u;
    }
    for (i = 0u; i < max_count && (start_index + i) < step_count; ++i) {
        const dom_production_step* step = &steps[start_index + i];
        dom_ledger_account* acct = dom_ledger_account_ensure(ledger, step->producer_id);
        if (!acct) {
            continue;
        }
        acct->balance += step->amount;
        if (audit) {
            (void)dom_economy_audit_record(audit, DOM_ECON_AUDIT_PRODUCTION, step->producer_id, step->amount);
        }
        processed += 1u;
    }
    return processed;
}

u32 dom_ledger_apply_consumption_slice(dom_ledger_state* ledger,
                                       const dom_consumption_step* steps,
                                       u32 step_count,
                                       u32 start_index,
                                       u32 max_count,
                                       dom_economy_audit_log* audit)
{
    u32 i;
    u32 processed = 0u;
    if (!ledger || !steps || max_count == 0u) {
        return 0u;
    }
    if (start_index >= step_count) {
        return 0u;
    }
    for (i = 0u; i < max_count && (start_index + i) < step_count; ++i) {
        const dom_consumption_step* step = &steps[start_index + i];
        dom_ledger_account* acct = dom_ledger_account_ensure(ledger, step->consumer_id);
        if (!acct) {
            continue;
        }
        acct->balance -= step->amount;
        if (audit) {
            (void)dom_economy_audit_record(audit, DOM_ECON_AUDIT_CONSUMPTION, step->consumer_id, step->amount);
        }
        processed += 1u;
    }
    return processed;
}

u32 dom_ledger_apply_maintenance_slice(dom_ledger_state* ledger,
                                       const dom_maintenance_step* steps,
                                       u32 step_count,
                                       u32 start_index,
                                       u32 max_count,
                                       dom_economy_audit_log* audit)
{
    u32 i;
    u32 processed = 0u;
    if (!ledger || !steps || max_count == 0u) {
        return 0u;
    }
    if (start_index >= step_count) {
        return 0u;
    }
    for (i = 0u; i < max_count && (start_index + i) < step_count; ++i) {
        const dom_maintenance_step* step = &steps[start_index + i];
        dom_ledger_account* acct = dom_ledger_account_ensure(ledger, step->owner_id);
        if (!acct) {
            continue;
        }
        acct->balance -= step->upkeep;
        if (audit) {
            (void)dom_economy_audit_record(audit, DOM_ECON_AUDIT_MAINTENANCE, step->asset_id, step->upkeep);
        }
        processed += 1u;
    }
    return processed;
}

} /* extern "C" */
