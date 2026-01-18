/*
FILE: game/rules/war/security_force.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Game / war rules
RESPONSIBILITY: Implements security force registries and epistemic estimates.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Force ordering and estimates are deterministic.
*/
#include "dominium/rules/war/security_force.h"

#include <string.h>

static u32 security_force_bucket_u32(u32 value, u32 bucket)
{
    if (bucket == 0u) {
        return value;
    }
    return (value / bucket) * bucket;
}

const char* war_refusal_to_string(war_refusal_code code)
{
    switch (code) {
        case WAR_REFUSAL_NONE: return "none";
        case WAR_REFUSAL_INSUFFICIENT_POPULATION: return "insufficient_population";
        case WAR_REFUSAL_INSUFFICIENT_EQUIPMENT: return "insufficient_equipment";
        case WAR_REFUSAL_INSUFFICIENT_LOGISTICS: return "insufficient_logistics";
        case WAR_REFUSAL_INSUFFICIENT_AUTHORITY: return "insufficient_authority";
        case WAR_REFUSAL_INSUFFICIENT_LEGITIMACY: return "insufficient_legitimacy";
        default: return "unknown";
    }
}

void security_force_registry_init(security_force_registry* reg,
                                  security_force* storage,
                                  u32 capacity,
                                  u64 start_force_id)
{
    if (!reg) {
        return;
    }
    reg->forces = storage;
    reg->count = 0u;
    reg->capacity = capacity;
    reg->next_force_id = start_force_id ? start_force_id : 1u;
    if (storage && capacity > 0u) {
        memset(storage, 0, sizeof(security_force) * (size_t)capacity);
    }
}

static u32 security_force_find_index(const security_force_registry* reg,
                                     u64 force_id,
                                     int* out_found)
{
    u32 i;
    if (out_found) {
        *out_found = 0;
    }
    if (!reg || !reg->forces) {
        return 0u;
    }
    for (i = 0u; i < reg->count; ++i) {
        if (reg->forces[i].force_id == force_id) {
            if (out_found) {
                *out_found = 1;
            }
            return i;
        }
        if (reg->forces[i].force_id > force_id) {
            break;
        }
    }
    return i;
}

security_force* security_force_find(security_force_registry* reg,
                                    u64 force_id)
{
    int found = 0;
    u32 idx;
    if (!reg || !reg->forces) {
        return 0;
    }
    idx = security_force_find_index(reg, force_id, &found);
    if (!found) {
        return 0;
    }
    return &reg->forces[idx];
}

int security_force_register(security_force_registry* reg,
                            u64 force_id,
                            u64 owning_org_or_jurisdiction,
                            u32 domain_scope,
                            u64 cohort_ref,
                            u64 provenance_ref)
{
    int found = 0;
    u32 idx;
    u32 i;
    security_force* entry;
    if (!reg || !reg->forces) {
        return -1;
    }
    if (reg->count >= reg->capacity) {
        return -2;
    }
    if (force_id == 0u) {
        force_id = reg->next_force_id++;
        if (force_id == 0u) {
            force_id = reg->next_force_id++;
        }
    }
    idx = security_force_find_index(reg, force_id, &found);
    if (found) {
        return -3;
    }
    for (i = reg->count; i > idx; --i) {
        reg->forces[i] = reg->forces[i - 1u];
    }
    entry = &reg->forces[idx];
    memset(entry, 0, sizeof(*entry));
    entry->force_id = force_id;
    entry->owning_org_or_jurisdiction = owning_org_or_jurisdiction;
    entry->domain_scope = domain_scope;
    entry->cohort_ref = cohort_ref;
    entry->next_due_tick = DOM_TIME_ACT_MAX;
    entry->provenance_ref = provenance_ref ? provenance_ref : force_id;
    entry->status = SECURITY_FORCE_INACTIVE;
    reg->count += 1u;
    return 0;
}

int security_force_add_equipment(security_force_registry* reg,
                                 u64 force_id,
                                 u64 equipment_id,
                                 u32 qty)
{
    u32 i;
    u32 insert_at;
    security_force* force;
    if (!reg || !equipment_id || qty == 0u) {
        return -1;
    }
    force = security_force_find(reg, force_id);
    if (!force) {
        return -2;
    }
    for (i = 0u; i < force->equipment_count; ++i) {
        if (force->equipment_refs[i] == equipment_id) {
            force->equipment_qtys[i] += qty;
            return 0;
        }
        if (force->equipment_refs[i] > equipment_id) {
            break;
        }
    }
    if (force->equipment_count >= SECURITY_FORCE_MAX_EQUIPMENT) {
        return -3;
    }
    insert_at = i;
    for (i = force->equipment_count; i > insert_at; --i) {
        force->equipment_refs[i] = force->equipment_refs[i - 1u];
        force->equipment_qtys[i] = force->equipment_qtys[i - 1u];
    }
    force->equipment_refs[insert_at] = equipment_id;
    force->equipment_qtys[insert_at] = qty;
    force->equipment_count += 1u;
    return 0;
}

int security_force_add_logistics_dependency(security_force_registry* reg,
                                            u64 force_id,
                                            u64 dependency_ref)
{
    u32 i;
    u32 insert_at;
    security_force* force;
    if (!reg || !dependency_ref) {
        return -1;
    }
    force = security_force_find(reg, force_id);
    if (!force) {
        return -2;
    }
    for (i = 0u; i < force->logistics_dependency_count; ++i) {
        if (force->logistics_dependency_refs[i] == dependency_ref) {
            return 0;
        }
        if (force->logistics_dependency_refs[i] > dependency_ref) {
            break;
        }
    }
    if (force->logistics_dependency_count >= SECURITY_FORCE_MAX_LOGISTICS) {
        return -3;
    }
    insert_at = i;
    for (i = force->logistics_dependency_count; i > insert_at; --i) {
        force->logistics_dependency_refs[i] = force->logistics_dependency_refs[i - 1u];
    }
    force->logistics_dependency_refs[insert_at] = dependency_ref;
    force->logistics_dependency_count += 1u;
    return 0;
}

int security_force_set_states(security_force_registry* reg,
                              u64 force_id,
                              u64 readiness_state_ref,
                              u64 morale_state_ref)
{
    security_force* force = security_force_find(reg, force_id);
    if (!force) {
        return -1;
    }
    force->readiness_state_ref = readiness_state_ref;
    force->morale_state_ref = morale_state_ref;
    return 0;
}

int security_force_set_status(security_force_registry* reg,
                              u64 force_id,
                              u32 status)
{
    security_force* force = security_force_find(reg, force_id);
    if (!force) {
        return -1;
    }
    force->status = status;
    return 0;
}

int security_force_estimate_from_view(const dom_epistemic_view* view,
                                      u32 actual_count,
                                      u32 readiness_level,
                                      u32 morale_level,
                                      security_force_estimate* out)
{
    int is_known = 0;
    if (!out) {
        return -1;
    }
    if (view && view->state == DOM_EPI_KNOWN && !view->is_uncertain) {
        is_known = 1;
    }
    if (is_known) {
        out->estimated_count = actual_count;
        out->estimated_readiness = readiness_level;
        out->estimated_morale = morale_level;
        out->uncertainty_q16 = view ? view->uncertainty_q16 : 0u;
        out->is_exact = 1;
        return 0;
    }
    out->estimated_count = security_force_bucket_u32(actual_count, 10u);
    out->estimated_readiness = security_force_bucket_u32(readiness_level, 50u);
    out->estimated_morale = security_force_bucket_u32(morale_level, 50u);
    out->uncertainty_q16 = view ? view->uncertainty_q16 : 0xFFFFu;
    out->is_exact = 0;
    return 0;
}
