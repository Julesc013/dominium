/*
FILE: game/rules/population/cohort_types.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Game / population rules
RESPONSIBILITY: Implements cohort registries and deterministic cohort IDs.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Cohort IDs and ordering are deterministic.
*/
#include "dominium/rules/population/cohort_types.h"

#include "dominium/rules/population/demographics.h"

#include <string.h>

static u64 population_hash_mix(u64 h, u64 v)
{
    h ^= v + 0x9e3779b97f4a7c15ULL + (h << 6) + (h >> 2);
    return h;
}

u64 population_cohort_id_from_key(const population_cohort_key* key)
{
    u64 h = 0xC0D1C0D1u;
    if (!key) {
        return 0u;
    }
    h = population_hash_mix(h, key->body_id);
    h = population_hash_mix(h, key->region_id);
    h = population_hash_mix(h, key->org_id);
    if (h == 0u) {
        h = 1u;
    }
    return h;
}

void population_cohort_registry_init(population_cohort_registry* reg,
                                     population_cohort_state* storage,
                                     u32 capacity)
{
    if (!reg) {
        return;
    }
    reg->cohorts = storage;
    reg->count = 0u;
    reg->capacity = capacity;
    if (storage && capacity > 0u) {
        memset(storage, 0, sizeof(population_cohort_state) * (size_t)capacity);
    }
}

static u32 population_cohort_find_index(const population_cohort_registry* reg,
                                        u64 cohort_id,
                                        int* out_found)
{
    u32 i;
    if (out_found) {
        *out_found = 0;
    }
    if (!reg || !reg->cohorts) {
        return 0u;
    }
    for (i = 0u; i < reg->count; ++i) {
        if (reg->cohorts[i].cohort_id == cohort_id) {
            if (out_found) {
                *out_found = 1;
            }
            return i;
        }
        if (reg->cohorts[i].cohort_id > cohort_id) {
            break;
        }
    }
    return i;
}

int population_cohort_register(population_cohort_registry* reg,
                               const population_cohort_key* key,
                               u32 count,
                               u64 needs_state_ref)
{
    int found = 0;
    u32 idx;
    u32 i;
    population_cohort_state* entry;
    u64 cohort_id;

    if (!reg || !reg->cohorts || !key) {
        return -1;
    }
    if (reg->count >= reg->capacity) {
        return -2;
    }
    cohort_id = population_cohort_id_from_key(key);
    idx = population_cohort_find_index(reg, cohort_id, &found);
    if (found) {
        return -3;
    }
    for (i = reg->count; i > idx; --i) {
        reg->cohorts[i] = reg->cohorts[i - 1u];
    }
    entry = &reg->cohorts[idx];
    memset(entry, 0, sizeof(*entry));
    entry->cohort_id = cohort_id;
    entry->key = *key;
    entry->count = count;
    entry->needs_state_ref = needs_state_ref;
    entry->next_due_tick = DOM_TIME_ACT_MAX;
    entry->provenance_summary_hash = population_hash_mix(cohort_id, (u64)count);
    (void)population_demographics_init(entry);
    reg->count += 1u;
    return 0;
}

population_cohort_state* population_cohort_find(population_cohort_registry* reg,
                                                u64 cohort_id)
{
    int found = 0;
    u32 idx;
    if (!reg || !reg->cohorts) {
        return 0;
    }
    idx = population_cohort_find_index(reg, cohort_id, &found);
    if (!found) {
        return 0;
    }
    return &reg->cohorts[idx];
}

population_cohort_state* population_cohort_find_by_key(population_cohort_registry* reg,
                                                       const population_cohort_key* key)
{
    if (!key) {
        return 0;
    }
    return population_cohort_find(reg, population_cohort_id_from_key(key));
}

int population_cohort_adjust_count(population_cohort_registry* reg,
                                   u64 cohort_id,
                                   i32 delta,
                                   u32* out_count)
{
    population_cohort_state* cohort = population_cohort_find(reg, cohort_id);
    if (!cohort) {
        return -1;
    }
    if (population_demographics_apply_delta(cohort, delta, (u64)cohort_id, 0) != 0) {
        return -2;
    }
    if (out_count) {
        *out_count = cohort->count;
    }
    if (cohort->count == 0u) {
        cohort->next_due_tick = DOM_TIME_ACT_MAX;
    }
    return 0;
}

int population_cohort_set_next_due(population_cohort_registry* reg,
                                   u64 cohort_id,
                                   dom_act_time_t next_due_tick)
{
    population_cohort_state* cohort = population_cohort_find(reg, cohort_id);
    if (!cohort) {
        return -1;
    }
    cohort->next_due_tick = next_due_tick;
    return 0;
}

int population_cohort_set_provenance(population_cohort_registry* reg,
                                     u64 cohort_id,
                                     u64 provenance_hash)
{
    population_cohort_state* cohort = population_cohort_find(reg, cohort_id);
    if (!cohort) {
        return -1;
    }
    cohort->provenance_summary_hash = provenance_hash;
    return 0;
}

int population_cohort_mix_provenance(population_cohort_registry* reg,
                                     u64 cohort_id,
                                     u64 provenance_mix)
{
    population_cohort_state* cohort = population_cohort_find(reg, cohort_id);
    if (!cohort) {
        return -1;
    }
    cohort->provenance_summary_hash =
        population_hash_mix(cohort->provenance_summary_hash, provenance_mix);
    return 0;
}
