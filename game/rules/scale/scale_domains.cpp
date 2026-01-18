/*
FILE: game/rules/scale/scale_domains.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Game / scale
RESPONSIBILITY: Implements scale domains and deterministic registries.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Domain ordering and lookups are deterministic.
*/
#include "dominium/rules/scale/scale_domains.h"

#include <string.h>

void scale_domain_registry_init(scale_domain_registry* reg,
                                scale_domain_record* storage,
                                u32 capacity)
{
    if (!reg) {
        return;
    }
    reg->records = storage;
    reg->count = 0u;
    reg->capacity = capacity;
    if (storage && capacity > 0u) {
        memset(storage, 0, sizeof(scale_domain_record) * (size_t)capacity);
    }
}

static u32 scale_domain_find_index(const scale_domain_registry* reg,
                                   u64 domain_id,
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
        if (reg->records[i].domain_id == domain_id) {
            if (out_found) {
                *out_found = 1;
            }
            return i;
        }
        if (reg->records[i].domain_id > domain_id) {
            break;
        }
    }
    return i;
}

int scale_domain_register(scale_domain_registry* reg,
                          u64 domain_id,
                          scale_domain_type type,
                          u32 min_warp,
                          u32 max_warp,
                          u32 default_step_act,
                          scale_fidelity_limit fidelity_limit)
{
    int found = 0;
    u32 idx;
    u32 i;
    scale_domain_record* entry;
    if (!reg || !reg->records) {
        return -1;
    }
    if (reg->count >= reg->capacity) {
        return -2;
    }
    idx = scale_domain_find_index(reg, domain_id, &found);
    if (found) {
        return -3;
    }
    for (i = reg->count; i > idx; --i) {
        reg->records[i] = reg->records[i - 1u];
    }
    entry = &reg->records[idx];
    memset(entry, 0, sizeof(*entry));
    entry->domain_id = domain_id;
    entry->type = type;
    entry->min_warp = min_warp;
    entry->max_warp = max_warp;
    entry->default_step_act = default_step_act;
    entry->fidelity_limit = fidelity_limit;
    reg->count += 1u;
    return 0;
}

scale_domain_record* scale_domain_find(scale_domain_registry* reg,
                                       u64 domain_id)
{
    int found = 0;
    u32 idx;
    if (!reg || !reg->records) {
        return 0;
    }
    idx = scale_domain_find_index(reg, domain_id, &found);
    if (!found) {
        return 0;
    }
    return &reg->records[idx];
}
