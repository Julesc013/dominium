/*
FILE: game/core/life/estate.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Game / life
RESPONSIBILITY: Implements estate registries, account ownership, and person-account mapping.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Account ordering and registry insertion are deterministic.
*/
#include "dominium/life/estate.h"

#include <string.h>

static void life_sort_accounts(dom_account_id_t* accounts, u32 count)
{
    u32 i;
    if (!accounts || count < 2u) {
        return;
    }
    for (i = 1u; i < count; ++i) {
        dom_account_id_t key = accounts[i];
        u32 j = i;
        while (j > 0u && accounts[j - 1u] > key) {
            accounts[j] = accounts[j - 1u];
            --j;
        }
        accounts[j] = key;
    }
}

void life_estate_registry_init(life_estate_registry* reg,
                               life_estate* estate_storage,
                               u32 estate_capacity,
                               dom_account_id_t* account_storage,
                               u32 account_capacity,
                               u64 start_id)
{
    if (!reg) {
        return;
    }
    reg->estates = estate_storage;
    reg->count = 0u;
    reg->capacity = estate_capacity;
    reg->next_id = start_id ? start_id : 1u;
    reg->account_storage = account_storage;
    reg->account_capacity = account_capacity;
    reg->account_used = 0u;
    if (estate_storage && estate_capacity > 0u) {
        memset(estate_storage, 0, sizeof(life_estate) * (size_t)estate_capacity);
    }
    if (account_storage && account_capacity > 0u) {
        memset(account_storage, 0, sizeof(dom_account_id_t) * (size_t)account_capacity);
    }
}

const life_estate* life_estate_find_by_person(const life_estate_registry* reg,
                                              u64 person_id)
{
    u32 i;
    if (!reg || !reg->estates) {
        return 0;
    }
    for (i = 0u; i < reg->count; ++i) {
        if (reg->estates[i].deceased_person_id == person_id) {
            return &reg->estates[i];
        }
    }
    return 0;
}

life_estate* life_estate_find_by_id(life_estate_registry* reg, u64 estate_id)
{
    u32 i;
    if (!reg || !reg->estates) {
        return 0;
    }
    for (i = 0u; i < reg->count; ++i) {
        if (reg->estates[i].estate_id == estate_id) {
            return &reg->estates[i];
        }
    }
    return 0;
}

const dom_account_id_t* life_estate_accounts(const life_estate_registry* reg,
                                             const life_estate* estate,
                                             u32* out_count)
{
    if (out_count) {
        *out_count = 0u;
    }
    if (!reg || !estate || !reg->account_storage) {
        return 0;
    }
    if (estate->account_offset + estate->account_count > reg->account_used) {
        return 0;
    }
    if (out_count) {
        *out_count = estate->account_count;
    }
    return &reg->account_storage[estate->account_offset];
}

static int life_ledger_account_exists(const dom_ledger* ledger, dom_account_id_t account_id)
{
    dom_ledger_account tmp;
    if (!ledger || account_id == 0u) {
        return 0;
    }
    if (dom_ledger_account_copy(ledger, account_id, &tmp) != DOM_LEDGER_OK) {
        return 0;
    }
    return 1;
}

int life_estate_create(life_estate_registry* reg,
                       const dom_ledger* ledger,
                       life_account_owner_registry* owners,
                       u64 deceased_person_id,
                       const dom_account_id_t* account_ids,
                       u32 account_count,
                       dom_act_time_t act_created,
                       u64 jurisdiction_id,
                       u64 organization_id,
                       u32 policy_id,
                       u64* out_estate_id)
{
    life_estate* estate;
    dom_account_id_t* dst;
    u32 i;

    if (!reg || !reg->estates || !reg->account_storage || !ledger) {
        return -1;
    }
    if (!account_ids || account_count == 0u) {
        return -2;
    }
    if (reg->count >= reg->capacity) {
        return -3;
    }
    if (reg->account_used + account_count > reg->account_capacity) {
        return -4;
    }

    for (i = 0u; i < account_count; ++i) {
        if (!life_ledger_account_exists(ledger, account_ids[i])) {
            return -5;
        }
    }

    dst = &reg->account_storage[reg->account_used];
    for (i = 0u; i < account_count; ++i) {
        dst[i] = account_ids[i];
    }
    life_sort_accounts(dst, account_count);

    estate = &reg->estates[reg->count++];
    memset(estate, 0, sizeof(*estate));
    estate->estate_id = reg->next_id++;
    estate->deceased_person_id = deceased_person_id;
    estate->act_created = act_created;
    estate->account_offset = reg->account_used;
    estate->account_count = account_count;
    estate->jurisdiction_id = jurisdiction_id;
    estate->organization_id = organization_id;
    estate->status = LIFE_ESTATE_OPEN;
    estate->policy_id = policy_id;
    estate->has_executor_authority = 0u;
    estate->due_handle = 0u;
    estate->next_due_tick = DOM_TIME_ACT_MAX;

    reg->account_used += account_count;

    if (owners) {
        for (i = 0u; i < account_count; ++i) {
            if (life_account_owner_set(owners, dst[i], LIFE_ACCOUNT_OWNER_ESTATE, estate->estate_id) != 0) {
                return -6;
            }
        }
    }

    if (out_estate_id) {
        *out_estate_id = estate->estate_id;
    }
    return 0;
}

void life_person_account_registry_init(life_person_account_registry* reg,
                                       life_person_account_entry* entry_storage,
                                       u32 entry_capacity,
                                       dom_account_id_t* account_storage,
                                       u32 account_capacity)
{
    if (!reg) {
        return;
    }
    reg->entries = entry_storage;
    reg->count = 0u;
    reg->capacity = entry_capacity;
    reg->account_storage = account_storage;
    reg->account_capacity = account_capacity;
    reg->account_used = 0u;
    if (entry_storage && entry_capacity > 0u) {
        memset(entry_storage, 0, sizeof(life_person_account_entry) * (size_t)entry_capacity);
    }
    if (account_storage && account_capacity > 0u) {
        memset(account_storage, 0, sizeof(dom_account_id_t) * (size_t)account_capacity);
    }
}

int life_person_account_register(life_person_account_registry* reg,
                                 u64 person_id,
                                 const dom_account_id_t* account_ids,
                                 u32 account_count)
{
    life_person_account_entry* entry;
    dom_account_id_t* dst;
    u32 i;

    if (!reg || !reg->entries || !reg->account_storage) {
        return -1;
    }
    if (!account_ids || account_count == 0u) {
        return -2;
    }
    if (reg->count >= reg->capacity) {
        return -3;
    }
    if (reg->account_used + account_count > reg->account_capacity) {
        return -4;
    }
    for (i = 0u; i < reg->count; ++i) {
        if (reg->entries[i].person_id == person_id) {
            return -5;
        }
    }

    dst = &reg->account_storage[reg->account_used];
    for (i = 0u; i < account_count; ++i) {
        dst[i] = account_ids[i];
    }
    life_sort_accounts(dst, account_count);

    entry = &reg->entries[reg->count++];
    entry->person_id = person_id;
    entry->account_offset = reg->account_used;
    entry->account_count = account_count;
    reg->account_used += account_count;
    return 0;
}

int life_person_account_get(const life_person_account_registry* reg,
                            u64 person_id,
                            const dom_account_id_t** out_accounts,
                            u32* out_count)
{
    u32 i;
    if (out_accounts) {
        *out_accounts = 0;
    }
    if (out_count) {
        *out_count = 0u;
    }
    if (!reg || !reg->entries || !reg->account_storage) {
        return 0;
    }
    for (i = 0u; i < reg->count; ++i) {
        if (reg->entries[i].person_id == person_id) {
            if (out_accounts) {
                *out_accounts = &reg->account_storage[reg->entries[i].account_offset];
            }
            if (out_count) {
                *out_count = reg->entries[i].account_count;
            }
            return 1;
        }
    }
    return 0;
}

void life_account_owner_registry_init(life_account_owner_registry* reg,
                                      life_account_owner_entry* storage,
                                      u32 capacity)
{
    if (!reg) {
        return;
    }
    reg->entries = storage;
    reg->count = 0u;
    reg->capacity = capacity;
    if (storage && capacity > 0u) {
        memset(storage, 0, sizeof(life_account_owner_entry) * (size_t)capacity);
    }
}

static u32 life_owner_find_index(const life_account_owner_registry* reg,
                                 dom_account_id_t account_id,
                                 int* out_found)
{
    u32 i;
    if (out_found) {
        *out_found = 0;
    }
    if (!reg || !reg->entries) {
        return 0u;
    }
    for (i = 0u; i < reg->count; ++i) {
        if (reg->entries[i].account_id == account_id) {
            if (out_found) {
                *out_found = 1;
            }
            return i;
        }
        if (reg->entries[i].account_id > account_id) {
            break;
        }
    }
    return i;
}

int life_account_owner_set(life_account_owner_registry* reg,
                           dom_account_id_t account_id,
                           u32 owner_kind,
                           u64 owner_id)
{
    int found = 0;
    u32 idx;
    u32 i;

    if (!reg || !reg->entries || account_id == 0u) {
        return -1;
    }
    idx = life_owner_find_index(reg, account_id, &found);
    if (found) {
        reg->entries[idx].owner_kind = owner_kind;
        reg->entries[idx].owner_id = owner_id;
        return 0;
    }
    if (reg->count >= reg->capacity) {
        return -2;
    }
    for (i = reg->count; i > idx; --i) {
        reg->entries[i] = reg->entries[i - 1u];
    }
    reg->entries[idx].account_id = account_id;
    reg->entries[idx].owner_kind = owner_kind;
    reg->entries[idx].owner_id = owner_id;
    reg->count += 1u;
    return 0;
}

const life_account_owner_entry* life_account_owner_get(
    const life_account_owner_registry* reg,
    dom_account_id_t account_id)
{
    int found = 0;
    u32 idx;
    if (!reg || !reg->entries) {
        return 0;
    }
    idx = life_owner_find_index(reg, account_id, &found);
    if (!found) {
        return 0;
    }
    return &reg->entries[idx];
}
