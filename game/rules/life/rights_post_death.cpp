/*
FILE: game/core/life/rights_post_death.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Game / life
RESPONSIBILITY: Implements post-death rights registry.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Ordering and IDs are deterministic.
*/
#include "dominium/life/rights_post_death.h"

#include <string.h>

void life_post_death_rights_registry_init(life_post_death_rights_registry* reg,
                                          life_post_death_rights* storage,
                                          u32 capacity,
                                          u64 start_id)
{
    if (!reg) {
        return;
    }
    reg->rights = storage;
    reg->count = 0u;
    reg->capacity = capacity;
    reg->next_id = start_id ? start_id : 1u;
    if (storage && capacity > 0u) {
        memset(storage, 0, sizeof(life_post_death_rights) * (size_t)capacity);
    }
}

life_post_death_rights* life_post_death_rights_find(life_post_death_rights_registry* reg,
                                                    u64 rights_id)
{
    u32 i;
    if (!reg || !reg->rights) {
        return 0;
    }
    for (i = 0u; i < reg->count; ++i) {
        if (reg->rights[i].rights_id == rights_id) {
            return &reg->rights[i];
        }
    }
    return 0;
}

int life_post_death_rights_create(life_post_death_rights_registry* reg,
                                  u64 estate_id,
                                  u64 jurisdiction_id,
                                  u8 has_contract,
                                  u8 allow_finder,
                                  u8 jurisdiction_allows,
                                  u8 estate_locked,
                                  u64* out_rights_id)
{
    life_post_death_rights* entry;
    if (!reg || !reg->rights) {
        return -1;
    }
    if (reg->count >= reg->capacity) {
        return -2;
    }
    entry = &reg->rights[reg->count++];
    memset(entry, 0, sizeof(*entry));
    entry->rights_id = reg->next_id++;
    entry->estate_id = estate_id;
    entry->jurisdiction_id = jurisdiction_id;
    entry->has_contract = has_contract;
    entry->allow_finder = allow_finder;
    entry->jurisdiction_allows = jurisdiction_allows;
    entry->estate_locked = estate_locked;
    if (out_rights_id) {
        *out_rights_id = entry->rights_id;
    }
    return 0;
}
