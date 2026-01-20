/*
FILE: game/rules/agents/agent_aggregation_tasks.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Game / agents
RESPONSIBILITY: Implements agent aggregation/refinement helpers.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Aggregation and refinement are deterministic.
*/
#include "dominium/rules/agents/agent_aggregation_tasks.h"

#include <string.h>

void dom_agent_cohort_buffer_init(dom_agent_cohort_buffer* buffer,
                                  dom_agent_cohort_item* storage,
                                  u32 capacity)
{
    if (!buffer) {
        return;
    }
    buffer->entries = storage;
    buffer->count = 0u;
    buffer->capacity = capacity;
    if (storage && capacity > 0u) {
        memset(storage, 0, sizeof(dom_agent_cohort_item) * (size_t)capacity);
    }
}

void dom_agent_cohort_buffer_reset(dom_agent_cohort_buffer* buffer)
{
    if (!buffer) {
        return;
    }
    buffer->count = 0u;
}

static u32 dom_agent_cohort_find_index(const dom_agent_cohort_buffer* buffer,
                                       u64 cohort_id,
                                       int* out_found)
{
    u32 i;
    if (out_found) {
        *out_found = 0;
    }
    if (!buffer || !buffer->entries) {
        return 0u;
    }
    for (i = 0u; i < buffer->count; ++i) {
        if (buffer->entries[i].cohort_id == cohort_id) {
            if (out_found) {
                *out_found = 1;
            }
            return i;
        }
        if (buffer->entries[i].cohort_id > cohort_id) {
            break;
        }
    }
    return i;
}

static dom_agent_cohort_item* dom_agent_cohort_ensure(dom_agent_cohort_buffer* buffer,
                                                      u64 cohort_id)
{
    int found = 0;
    u32 idx;
    u32 i;
    dom_agent_cohort_item* entry;
    if (!buffer || !buffer->entries) {
        return 0;
    }
    idx = dom_agent_cohort_find_index(buffer, cohort_id, &found);
    if (found) {
        return &buffer->entries[idx];
    }
    if (buffer->count >= buffer->capacity) {
        return 0;
    }
    for (i = buffer->count; i > idx; --i) {
        buffer->entries[i] = buffer->entries[i - 1u];
    }
    entry = &buffer->entries[idx];
    entry->cohort_id = cohort_id;
    entry->member_count = 0u;
    buffer->count += 1u;
    return entry;
}

u32 dom_agent_aggregate_cohorts_slice(dom_agent_population_item* population,
                                      u32 population_count,
                                      u32 start_index,
                                      u32 max_count,
                                      dom_agent_cohort_buffer* cohorts,
                                      dom_agent_audit_log* audit)
{
    u32 i;
    u32 end;
    if (!population || !cohorts || start_index >= population_count || max_count == 0u) {
        return 0u;
    }
    end = start_index + max_count;
    if (end > population_count) {
        end = population_count;
    }
    for (i = start_index; i < end; ++i) {
        dom_agent_population_item* item = &population[i];
        u64 cohort_id = item->cohort_id ? item->cohort_id : item->agent_id;
        dom_agent_cohort_item* cohort = dom_agent_cohort_ensure(cohorts, cohort_id);
        if (!cohort) {
            continue;
        }
        cohort->member_count += 1u;
        if (audit) {
            dom_agent_audit_record(audit, DOM_AGENT_AUDIT_AGGREGATE,
                                   cohort_id, (i64)cohort->member_count);
        }
    }
    return end - start_index;
}

u32 dom_agent_refine_individuals_slice(dom_agent_population_item* population,
                                       u32 population_count,
                                       u32 start_index,
                                       u32 max_count,
                                       const dom_agent_aggregation_policy* policy,
                                       dom_agent_audit_log* audit)
{
    u32 i;
    u32 end;
    u32 threshold = policy ? policy->refine_threshold : 0u;
    if (!population || start_index >= population_count || max_count == 0u) {
        return 0u;
    }
    end = start_index + max_count;
    if (end > population_count) {
        end = population_count;
    }
    for (i = start_index; i < end; ++i) {
        dom_agent_population_item* item = &population[i];
        if (item->interest_level >= threshold) {
            item->status = DOM_AGENT_POP_INDIVIDUAL;
            if (audit) {
                dom_agent_audit_record(audit, DOM_AGENT_AUDIT_REFINE,
                                       item->agent_id, (i64)item->interest_level);
            }
        }
    }
    return end - start_index;
}

u32 dom_agent_collapse_individuals_slice(dom_agent_population_item* population,
                                         u32 population_count,
                                         u32 start_index,
                                         u32 max_count,
                                         const dom_agent_aggregation_policy* policy,
                                         dom_agent_audit_log* audit)
{
    u32 i;
    u32 end;
    u32 threshold = policy ? policy->collapse_threshold : 0u;
    if (!population || start_index >= population_count || max_count == 0u) {
        return 0u;
    }
    end = start_index + max_count;
    if (end > population_count) {
        end = population_count;
    }
    for (i = start_index; i < end; ++i) {
        dom_agent_population_item* item = &population[i];
        if (item->interest_level <= threshold) {
            item->status = DOM_AGENT_POP_COHORT;
            if (audit) {
                dom_agent_audit_record(audit, DOM_AGENT_AUDIT_COLLAPSE,
                                       item->agent_id, (i64)item->interest_level);
            }
        }
    }
    return end - start_index;
}
