/*
FILE: game/rules/governance/jurisdiction_model.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Game / governance
RESPONSIBILITY: Implements jurisdiction records and deterministic registries.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Jurisdiction ordering is stable and deterministic.
*/
#include "dominium/rules/governance/jurisdiction_model.h"

#include <string.h>

void jurisdiction_registry_init(jurisdiction_registry* reg,
                                jurisdiction_record* storage,
                                u32 capacity)
{
    if (!reg) {
        return;
    }
    reg->records = storage;
    reg->count = 0u;
    reg->capacity = capacity;
    if (storage && capacity > 0u) {
        memset(storage, 0, sizeof(jurisdiction_record) * (size_t)capacity);
    }
}

static u32 jurisdiction_find_index(const jurisdiction_registry* reg,
                                   u64 jurisdiction_id,
                                   int* out_found)
{
    u32 i;
    if (out_found) {
        *out_found = 0;
    }
    if (!reg || !reg->records) {
        return 0u;
    }
    for (i = 0u; i < reg->count; ++i) {
        if (reg->records[i].jurisdiction_id == jurisdiction_id) {
            if (out_found) {
                *out_found = 1;
            }
            return i;
        }
        if (reg->records[i].jurisdiction_id > jurisdiction_id) {
            break;
        }
    }
    return i;
}

int jurisdiction_register(jurisdiction_registry* reg,
                          u64 jurisdiction_id,
                          u64 boundary_ref,
                          u64 time_standard_id,
                          u64 money_standard_id)
{
    int found = 0;
    u32 idx;
    u32 i;
    jurisdiction_record* entry;
    if (!reg || !reg->records) {
        return -1;
    }
    if (reg->count >= reg->capacity) {
        return -2;
    }
    idx = jurisdiction_find_index(reg, jurisdiction_id, &found);
    if (found) {
        return -3;
    }
    for (i = reg->count; i > idx; --i) {
        reg->records[i] = reg->records[i - 1u];
    }
    entry = &reg->records[idx];
    memset(entry, 0, sizeof(*entry));
    entry->jurisdiction_id = jurisdiction_id;
    entry->boundary_ref = boundary_ref;
    entry->default_time_standard_id = time_standard_id;
    entry->default_money_standard_id = money_standard_id;
    entry->policy_set_id = 0u;
    entry->enforcement_capacity_ref = 0u;
    entry->legitimacy_ref = 0u;
    entry->next_due_tick = DOM_TIME_ACT_MAX;
    reg->count += 1u;
    return 0;
}

jurisdiction_record* jurisdiction_find(jurisdiction_registry* reg,
                                       u64 jurisdiction_id)
{
    int found = 0;
    u32 idx;
    if (!reg || !reg->records) {
        return 0;
    }
    idx = jurisdiction_find_index(reg, jurisdiction_id, &found);
    if (!found) {
        return 0;
    }
    return &reg->records[idx];
}

int jurisdiction_set_policy(jurisdiction_registry* reg,
                            u64 jurisdiction_id,
                            u64 policy_set_id)
{
    jurisdiction_record* record = jurisdiction_find(reg, jurisdiction_id);
    if (!record) {
        return -1;
    }
    record->policy_set_id = policy_set_id;
    return 0;
}

int jurisdiction_set_refs(jurisdiction_registry* reg,
                          u64 jurisdiction_id,
                          u64 legitimacy_ref,
                          u64 enforcement_ref)
{
    jurisdiction_record* record = jurisdiction_find(reg, jurisdiction_id);
    if (!record) {
        return -1;
    }
    record->legitimacy_ref = legitimacy_ref;
    record->enforcement_capacity_ref = enforcement_ref;
    return 0;
}
