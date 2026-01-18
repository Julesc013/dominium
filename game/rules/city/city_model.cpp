/*
FILE: game/rules/city/city_model.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Game / city rules
RESPONSIBILITY: Implements city registries and macro summaries.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: City ordering is stable and deterministic.
*/
#include "dominium/rules/city/city_model.h"

#include <string.h>

void city_registry_init(city_registry* reg,
                        city_record* storage,
                        u32 capacity)
{
    if (!reg) {
        return;
    }
    reg->cities = storage;
    reg->count = 0u;
    reg->capacity = capacity;
    if (storage && capacity > 0u) {
        memset(storage, 0, sizeof(city_record) * (size_t)capacity);
    }
}

static u32 city_find_index(const city_registry* reg,
                           u64 city_id,
                           int* out_found)
{
    u32 i;
    if (out_found) {
        *out_found = 0;
    }
    if (!reg || !reg->cities) {
        return 0u;
    }
    for (i = 0u; i < reg->count; ++i) {
        if (reg->cities[i].city_id == city_id) {
            if (out_found) {
                *out_found = 1;
            }
            return i;
        }
        if (reg->cities[i].city_id > city_id) {
            break;
        }
    }
    return i;
}

int city_register(city_registry* reg,
                  u64 city_id,
                  u64 location_ref,
                  u64 governance_context_ref)
{
    int found = 0;
    u32 idx;
    u32 i;
    city_record* entry;
    if (!reg || !reg->cities) {
        return -1;
    }
    if (reg->count >= reg->capacity) {
        return -2;
    }
    idx = city_find_index(reg, city_id, &found);
    if (found) {
        return -3;
    }
    for (i = reg->count; i > idx; --i) {
        reg->cities[i] = reg->cities[i - 1u];
    }
    entry = &reg->cities[idx];
    memset(entry, 0, sizeof(*entry));
    entry->city_id = city_id;
    entry->location_ref = location_ref;
    entry->governance_context_ref = governance_context_ref;
    entry->boundary_ref = 0u;
    entry->building_count = 0u;
    entry->cohort_count = 0u;
    entry->next_due_tick = DOM_TIME_ACT_MAX;
    reg->count += 1u;
    return 0;
}

city_record* city_find(city_registry* reg, u64 city_id)
{
    int found = 0;
    u32 idx;
    if (!reg || !reg->cities) {
        return 0;
    }
    idx = city_find_index(reg, city_id, &found);
    if (!found) {
        return 0;
    }
    return &reg->cities[idx];
}

static int city_insert_id_sorted(u64* ids, u32* count, u32 max_count, u64 id)
{
    u32 i;
    if (!ids || !count) {
        return -1;
    }
    if (*count >= max_count) {
        return -2;
    }
    for (i = 0u; i < *count; ++i) {
        if (ids[i] == id) {
            return 0;
        }
        if (ids[i] > id) {
            break;
        }
    }
    if (i < *count) {
        u32 j;
        for (j = *count; j > i; --j) {
            ids[j] = ids[j - 1u];
        }
    }
    ids[i] = id;
    *count += 1u;
    return 0;
}

int city_add_building(city_registry* reg,
                      u64 city_id,
                      u64 building_id,
                      civ1_refusal_code* out_refusal)
{
    city_record* city = city_find(reg, city_id);
    if (out_refusal) {
        *out_refusal = CIV1_REFUSAL_NONE;
    }
    if (!city) {
        if (out_refusal) {
            *out_refusal = CIV1_REFUSAL_CITY_NOT_FOUND;
        }
        return -1;
    }
    return city_insert_id_sorted(city->building_ids, &city->building_count,
                                 CITY_MAX_BUILDINGS, building_id);
}

int city_add_population_cohort(city_registry* reg,
                               u64 city_id,
                               u64 cohort_id,
                               civ1_refusal_code* out_refusal)
{
    city_record* city = city_find(reg, city_id);
    if (out_refusal) {
        *out_refusal = CIV1_REFUSAL_NONE;
    }
    if (!city) {
        if (out_refusal) {
            *out_refusal = CIV1_REFUSAL_CITY_NOT_FOUND;
        }
        return -1;
    }
    return city_insert_id_sorted(city->population_cohort_refs, &city->cohort_count,
                                 CITY_MAX_COHORT_REFS, cohort_id);
}

static int city_summary_add(city_macro_summary* summary, u64 asset_id, u32 qty)
{
    u32 i;
    if (!summary || qty == 0u) {
        return 0;
    }
    for (i = 0u; i < summary->total_count; ++i) {
        if (summary->totals[i].asset_id == asset_id) {
            summary->totals[i].qty += qty;
            return 0;
        }
        if (summary->totals[i].asset_id > asset_id) {
            break;
        }
    }
    if (summary->total_count >= CITY_MAX_SUMMARY_ASSETS) {
        return -1;
    }
    if (i < summary->total_count) {
        u32 j;
        for (j = summary->total_count; j > i; --j) {
            summary->totals[j] = summary->totals[j - 1u];
        }
    }
    summary->totals[i].asset_id = asset_id;
    summary->totals[i].qty = qty;
    summary->total_count += 1u;
    return 0;
}

int city_collect_macro_summary(const city_record* city,
                               const building_machine_registry* machines,
                               const infra_store_registry* stores,
                               city_macro_summary* out_summary)
{
    u32 i;
    if (!out_summary) {
        return -1;
    }
    memset(out_summary, 0, sizeof(*out_summary));
    if (!city || !machines || !stores) {
        return -2;
    }
    for (i = 0u; i < city->building_count; ++i) {
        const building_machine* machine = building_machine_find((building_machine_registry*)machines,
                                                                city->building_ids[i]);
        const infra_store* store;
        u32 a;
        if (!machine || machine->output_store_count == 0u) {
            continue;
        }
        store = infra_store_find_const(stores, machine->output_stores[0]);
        if (!store) {
            continue;
        }
        for (a = 0u; a < store->asset_count; ++a) {
            (void)city_summary_add(out_summary, store->assets[a].asset_id, store->assets[a].quantity);
        }
    }
    return 0;
}

int city_apply_macro_summary(const city_record* city,
                             const building_machine_registry* machines,
                             infra_store_registry* stores,
                             const city_macro_summary* summary)
{
    u32 i;
    if (!summary) {
        return -1;
    }
    if (!city || !machines || !stores) {
        return -2;
    }
    for (i = 0u; i < city->building_count; ++i) {
        const building_machine* machine = building_machine_find((building_machine_registry*)machines,
                                                                city->building_ids[i]);
        if (!machine || machine->output_store_count == 0u) {
            continue;
        }
        (void)infra_store_clear(stores, machine->output_stores[0]);
    }
    if (city->building_count == 0u) {
        return 0;
    }
    for (i = 0u; i < summary->total_count; ++i) {
        const building_machine* machine = building_machine_find((building_machine_registry*)machines,
                                                                city->building_ids[0]);
        if (!machine || machine->output_store_count == 0u) {
            return -3;
        }
        (void)infra_store_add(stores,
                              machine->output_stores[0],
                              summary->totals[i].asset_id,
                              summary->totals[i].qty);
    }
    return 0;
}
