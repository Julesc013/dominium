/*
FILE: game/rules/population/migration_model.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Game / population rules
RESPONSIBILITY: Implements migration flow registry and deterministic application.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Flow ordering and application are deterministic.
*/
#include "dominium/rules/population/migration_model.h"

#include "dominium/rules/population/demographics.h"

#include <string.h>

static u64 population_flow_id_from_input(const population_migration_input* input,
                                         u64 seed)
{
    u64 h = seed ? seed : 0x9e3779b9u;
    if (!input) {
        return h;
    }
    h ^= input->src_key.body_id + 0x9e3779b97f4a7c15ULL + (h << 6) + (h >> 2);
    h ^= input->src_key.region_id + 0x9e3779b97f4a7c15ULL + (h << 6) + (h >> 2);
    h ^= input->src_key.org_id + 0x9e3779b97f4a7c15ULL + (h << 6) + (h >> 2);
    h ^= input->dst_key.body_id + 0x9e3779b97f4a7c15ULL + (h << 6) + (h >> 2);
    h ^= input->dst_key.region_id + 0x9e3779b97f4a7c15ULL + (h << 6) + (h >> 2);
    h ^= input->dst_key.org_id + 0x9e3779b97f4a7c15ULL + (h << 6) + (h >> 2);
    h ^= (u64)input->count_delta + (h << 6) + (h >> 2);
    h ^= (u64)input->arrival_act + (h << 6) + (h >> 2);
    h ^= (u64)input->cause_code + (h << 6) + (h >> 2);
    if (h == 0u) {
        h = 1u;
    }
    return h;
}

void population_migration_registry_init(population_migration_registry* reg,
                                        population_migration_flow* storage,
                                        u32 capacity,
                                        u64 start_flow_id)
{
    if (!reg) {
        return;
    }
    reg->flows = storage;
    reg->count = 0u;
    reg->capacity = capacity;
    reg->next_flow_id = start_flow_id ? start_flow_id : 1u;
    if (storage && capacity > 0u) {
        memset(storage, 0, sizeof(population_migration_flow) * (size_t)capacity);
    }
}

static u32 population_migration_find_index(const population_migration_registry* reg,
                                           u64 flow_id,
                                           int* out_found)
{
    u32 i;
    if (out_found) {
        *out_found = 0;
    }
    if (!reg || !reg->flows) {
        return 0u;
    }
    for (i = 0u; i < reg->count; ++i) {
        if (reg->flows[i].flow_id == flow_id) {
            if (out_found) {
                *out_found = 1;
            }
            return i;
        }
        if (reg->flows[i].flow_id > flow_id) {
            break;
        }
    }
    return i;
}

population_migration_flow* population_migration_find(population_migration_registry* reg,
                                                     u64 flow_id)
{
    int found = 0;
    u32 idx;
    if (!reg || !reg->flows) {
        return 0;
    }
    idx = population_migration_find_index(reg, flow_id, &found);
    if (!found) {
        return 0;
    }
    return &reg->flows[idx];
}

int population_migration_schedule(population_migration_registry* reg,
                                  const population_migration_input* input,
                                  population_refusal_code* out_refusal)
{
    int found = 0;
    u32 idx;
    u32 i;
    population_migration_flow* entry;
    u64 flow_id;

    if (out_refusal) {
        *out_refusal = POP_REFUSAL_NONE;
    }
    if (!reg || !reg->flows || !input) {
        return -1;
    }
    if (reg->count >= reg->capacity) {
        return -2;
    }
    flow_id = input->flow_id ? input->flow_id : population_flow_id_from_input(input, reg->next_flow_id++);
    idx = population_migration_find_index(reg, flow_id, &found);
    if (found) {
        return -3;
    }
    for (i = reg->count; i > idx; --i) {
        reg->flows[i] = reg->flows[i - 1u];
    }
    entry = &reg->flows[idx];
    memset(entry, 0, sizeof(*entry));
    entry->flow_id = flow_id;
    entry->src_key = input->src_key;
    entry->dst_key = input->dst_key;
    entry->src_cohort_id = population_cohort_id_from_key(&input->src_key);
    entry->dst_cohort_id = population_cohort_id_from_key(&input->dst_key);
    entry->count_delta = input->count_delta;
    entry->start_act = input->start_act;
    entry->arrival_act = input->arrival_act;
    entry->cause_code = input->cause_code;
    entry->provenance_mix = input->provenance_mix ? input->provenance_mix : flow_id;
    entry->status = POP_MIGRATION_ACTIVE;
    reg->count += 1u;
    return 0;
}

int population_migration_apply(population_migration_flow* flow,
                               population_cohort_registry* cohorts,
                               population_refusal_code* out_refusal)
{
    population_cohort_state* src;
    population_cohort_state* dst;
    population_refusal_code refusal = POP_REFUSAL_NONE;
    if (out_refusal) {
        *out_refusal = POP_REFUSAL_NONE;
    }
    if (!flow || !cohorts) {
        return -1;
    }
    if (flow->status != POP_MIGRATION_ACTIVE) {
        return 0;
    }
    src = population_cohort_find(cohorts, flow->src_cohort_id);
    dst = population_cohort_find(cohorts, flow->dst_cohort_id);
    if (!src || !dst) {
        if (out_refusal) {
            *out_refusal = POP_REFUSAL_COHORT_NOT_FOUND;
        }
        return -2;
    }
    if (flow->count_delta > src->count) {
        if (out_refusal) {
            *out_refusal = POP_REFUSAL_MIGRATION_INSUFFICIENT_RESOURCES;
        }
        return -3;
    }
    if (population_demographics_apply_delta(src, -(i32)flow->count_delta,
                                            flow->provenance_mix, &refusal) != 0) {
        if (out_refusal) {
            *out_refusal = refusal;
        }
        return -4;
    }
    if (population_demographics_apply_delta(dst, (i32)flow->count_delta,
                                            flow->provenance_mix, &refusal) != 0) {
        if (out_refusal) {
            *out_refusal = refusal;
        }
        return -5;
    }
    flow->status = POP_MIGRATION_COMPLETED;
    return 0;
}
