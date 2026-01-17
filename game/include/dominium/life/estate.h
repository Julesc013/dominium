/*
FILE: include/dominium/life/estate.h
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium API / life
RESPONSIBILITY: Defines estate records, account ownership, and registries.
ALLOWED DEPENDENCIES: `game/include/**`, `engine/include/**` public headers, and C89/C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; product-layer runtime code.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Account ordering and estate insertion are deterministic.
*/
#ifndef DOMINIUM_LIFE_ESTATE_H
#define DOMINIUM_LIFE_ESTATE_H

#include "domino/core/dom_ledger.h"
#include "domino/core/dom_time_core.h"
#include "domino/core/types.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef enum life_estate_status {
    LIFE_ESTATE_OPEN = 1,
    LIFE_ESTATE_RESOLVING = 2,
    LIFE_ESTATE_CLOSED = 3
} life_estate_status;

typedef enum life_account_owner_kind {
    LIFE_ACCOUNT_OWNER_PERSON = 1,
    LIFE_ACCOUNT_OWNER_ESTATE = 2
} life_account_owner_kind;

typedef struct life_estate {
    u64 estate_id;
    u64 deceased_person_id;
    dom_act_time_t act_created;
    u32 account_offset;
    u32 account_count;
    u64 jurisdiction_id;
    u64 organization_id;
    u32 status;
    dom_act_time_t claim_end_tick;
    u32 policy_id;
    u8 has_executor_authority;
    u32 due_handle;
    dom_act_time_t next_due_tick;
} life_estate;

typedef struct life_estate_registry {
    life_estate* estates;
    u32 count;
    u32 capacity;
    u64 next_id;
    dom_account_id_t* account_storage;
    u32 account_capacity;
    u32 account_used;
} life_estate_registry;

typedef struct life_person_account_entry {
    u64 person_id;
    u32 account_offset;
    u32 account_count;
} life_person_account_entry;

typedef struct life_person_account_registry {
    life_person_account_entry* entries;
    u32 count;
    u32 capacity;
    dom_account_id_t* account_storage;
    u32 account_capacity;
    u32 account_used;
} life_person_account_registry;

typedef struct life_account_owner_entry {
    dom_account_id_t account_id;
    u32 owner_kind;
    u64 owner_id;
} life_account_owner_entry;

typedef struct life_account_owner_registry {
    life_account_owner_entry* entries;
    u32 count;
    u32 capacity;
} life_account_owner_registry;

void life_estate_registry_init(life_estate_registry* reg,
                               life_estate* estate_storage,
                               u32 estate_capacity,
                               dom_account_id_t* account_storage,
                               u32 account_capacity,
                               u64 start_id);
const life_estate* life_estate_find_by_person(const life_estate_registry* reg,
                                              u64 person_id);
life_estate* life_estate_find_by_id(life_estate_registry* reg, u64 estate_id);
const dom_account_id_t* life_estate_accounts(const life_estate_registry* reg,
                                             const life_estate* estate,
                                             u32* out_count);
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
                       u64* out_estate_id);

void life_person_account_registry_init(life_person_account_registry* reg,
                                       life_person_account_entry* entry_storage,
                                       u32 entry_capacity,
                                       dom_account_id_t* account_storage,
                                       u32 account_capacity);
int life_person_account_register(life_person_account_registry* reg,
                                 u64 person_id,
                                 const dom_account_id_t* account_ids,
                                 u32 account_count);
int life_person_account_get(const life_person_account_registry* reg,
                            u64 person_id,
                            const dom_account_id_t** out_accounts,
                            u32* out_count);

void life_account_owner_registry_init(life_account_owner_registry* reg,
                                      life_account_owner_entry* storage,
                                      u32 capacity);
int life_account_owner_set(life_account_owner_registry* reg,
                           dom_account_id_t account_id,
                           u32 owner_kind,
                           u64 owner_id);
const life_account_owner_entry* life_account_owner_get(
    const life_account_owner_registry* reg,
    dom_account_id_t account_id);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINIUM_LIFE_ESTATE_H */
