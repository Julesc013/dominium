/*
FILE: game/core/life/remains.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Game / life
RESPONSIBILITY: Implements remains registries and aggregate collapse/refine.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Ordering and IDs are deterministic.
*/
#include "dominium/life/remains.h"

#include <string.h>

static u64 life_hash_mix(u64 h, u64 v)
{
    const u64 prime = 1099511628211ULL;
    h ^= v;
    h *= prime;
    return h;
}

void life_remains_registry_init(life_remains_registry* reg,
                                life_remains* storage,
                                u32 capacity,
                                u64 start_id)
{
    if (!reg) {
        return;
    }
    reg->remains = storage;
    reg->count = 0u;
    reg->capacity = capacity;
    reg->next_id = start_id ? start_id : 1u;
    reg->notice_cb = 0;
    reg->notice_user = 0;
    if (storage && capacity > 0u) {
        memset(storage, 0, sizeof(life_remains) * (size_t)capacity);
    }
}

void life_remains_registry_set_notice(life_remains_registry* reg,
                                      void (*notice_cb)(void*, const life_remains*),
                                      void* notice_user)
{
    if (!reg) {
        return;
    }
    reg->notice_cb = notice_cb;
    reg->notice_user = notice_user;
}

life_remains* life_remains_find(life_remains_registry* reg, u64 remains_id)
{
    u32 i;
    if (!reg || !reg->remains) {
        return 0;
    }
    for (i = 0u; i < reg->count; ++i) {
        if (reg->remains[i].remains_id == remains_id) {
            return &reg->remains[i];
        }
    }
    return 0;
}

int life_remains_create(life_remains_registry* reg,
                        u64 person_id,
                        u64 body_id,
                        u64 location_ref,
                        dom_act_time_t created_act,
                        u64 ownership_rights_ref,
                        u64 provenance_ref,
                        dom_account_id_t inventory_account_id,
                        u64* out_remains_id)
{
    life_remains* entry;
    if (!reg || !reg->remains) {
        return -1;
    }
    if (reg->count >= reg->capacity) {
        return -2;
    }
    entry = &reg->remains[reg->count++];
    memset(entry, 0, sizeof(*entry));
    entry->remains_id = reg->next_id++;
    entry->person_id = person_id;
    entry->body_id = body_id;
    entry->location_ref = location_ref;
    entry->created_act = created_act;
    entry->state = LIFE_REMAINS_FRESH;
    entry->ownership_rights_ref = ownership_rights_ref;
    entry->next_due_tick = DOM_TIME_ACT_MAX;
    entry->provenance_ref = provenance_ref;
    entry->inventory_account_id = inventory_account_id;
    entry->active_claim_id = 0u;
    if (out_remains_id) {
        *out_remains_id = entry->remains_id;
    }
    if (reg->notice_cb) {
        reg->notice_cb(reg->notice_user, entry);
    }
    return 0;
}

int life_remains_set_next_due(life_remains_registry* reg,
                              u64 remains_id,
                              dom_act_time_t next_due_tick)
{
    life_remains* remains = life_remains_find(reg, remains_id);
    if (!remains) {
        return -1;
    }
    remains->next_due_tick = next_due_tick;
    return 0;
}

void life_remains_aggregate_registry_init(life_remains_aggregate_registry* reg,
                                          life_remains_aggregate* storage,
                                          u32 capacity,
                                          u64 start_id)
{
    if (!reg) {
        return;
    }
    reg->aggregates = storage;
    reg->count = 0u;
    reg->capacity = capacity;
    reg->next_id = start_id ? start_id : 1u;
    if (storage && capacity > 0u) {
        memset(storage, 0, sizeof(life_remains_aggregate) * (size_t)capacity);
    }
}

life_remains_aggregate* life_remains_aggregate_find(life_remains_aggregate_registry* reg,
                                                    u64 aggregate_id)
{
    u32 i;
    if (!reg || !reg->aggregates) {
        return 0;
    }
    for (i = 0u; i < reg->count; ++i) {
        if (reg->aggregates[i].aggregate_id == aggregate_id) {
            return &reg->aggregates[i];
        }
    }
    return 0;
}

int life_remains_aggregate_add(life_remains_aggregate_registry* reg,
                               u64 location_ref,
                               u64 ownership_rights_ref,
                               u32 state,
                               u64 provenance_hash,
                               u64 count,
                               u64* out_id)
{
    life_remains_aggregate* entry;
    if (!reg || !reg->aggregates) {
        return -1;
    }
    if (reg->count >= reg->capacity) {
        return -2;
    }
    entry = &reg->aggregates[reg->count++];
    memset(entry, 0, sizeof(*entry));
    entry->aggregate_id = reg->next_id++;
    entry->location_ref = location_ref;
    entry->ownership_rights_ref = ownership_rights_ref;
    entry->provenance_hash = provenance_hash;
    entry->count = count;
    entry->state = state;
    if (out_id) {
        *out_id = entry->aggregate_id;
    }
    return 0;
}

static u64 life_remains_provenance_hash(const life_remains* remains)
{
    u64 h = 1469598103934665603ULL;
    if (!remains) {
        return h;
    }
    h = life_hash_mix(h, remains->remains_id);
    h = life_hash_mix(h, remains->person_id);
    h = life_hash_mix(h, remains->body_id);
    h = life_hash_mix(h, remains->provenance_ref);
    return h;
}

int life_remains_collapse(life_remains_registry* reg,
                          life_remains_aggregate_registry* aggregates,
                          u64 remains_id,
                          u64* out_aggregate_id)
{
    life_remains* remains;
    life_remains_aggregate* agg;
    u64 agg_id = 0u;
    if (!reg || !aggregates) {
        return -1;
    }
    remains = life_remains_find(reg, remains_id);
    if (!remains) {
        return -2;
    }
    if (life_remains_aggregate_add(aggregates,
                                   remains->location_ref,
                                   remains->ownership_rights_ref,
                                   remains->state,
                                   life_remains_provenance_hash(remains),
                                   1u,
                                   &agg_id) != 0) {
        return -3;
    }
    agg = life_remains_aggregate_find(aggregates, agg_id);
    if (agg) {
        agg->provenance_hash = life_hash_mix(agg->provenance_hash, remains->remains_id);
    }
    remains->state = LIFE_REMAINS_COLLAPSED;
    remains->next_due_tick = DOM_TIME_ACT_MAX;
    if (out_aggregate_id) {
        *out_aggregate_id = agg_id;
    }
    return 0;
}

int life_remains_refine(life_remains_aggregate_registry* aggregates,
                        life_remains_registry* reg,
                        u64 aggregate_id,
                        u32 count,
                        dom_act_time_t created_act)
{
    u32 i;
    life_remains_aggregate* agg;
    if (!aggregates || !reg) {
        return -1;
    }
    agg = life_remains_aggregate_find(aggregates, aggregate_id);
    if (!agg) {
        return -2;
    }
    if (count == 0u || agg->count < count) {
        return -3;
    }
    for (i = 0u; i < count; ++i) {
        u64 new_id = 0u;
        if (life_remains_create(reg,
                                0u,
                                0u,
                                agg->location_ref,
                                created_act,
                                agg->ownership_rights_ref,
                                agg->provenance_hash,
                                0u,
                                &new_id) != 0) {
            return -4;
        }
        if (new_id != 0u) {
            life_remains* created = life_remains_find(reg, new_id);
            if (created) {
                created->state = agg->state;
                created->provenance_ref = agg->provenance_hash;
            }
        }
    }
    agg->count -= count;
    return 0;
}

int life_remains_epistemic_knows(const life_remains_epistemic_set* set,
                                 u64 remains_id)
{
    u32 i;
    if (!set || !set->known_remains_ids || set->count == 0u) {
        return 0;
    }
    for (i = 0u; i < set->count; ++i) {
        if (set->known_remains_ids[i] == remains_id) {
            return 1;
        }
    }
    return 0;
}
