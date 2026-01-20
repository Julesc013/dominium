/*
FILE: game/rules/war/war_tasks_engagement.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Game / war rules
RESPONSIBILITY: Implements engagement task helpers for Work IR execution.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Engagement task ordering and outputs are deterministic.
*/
#include "dominium/rules/war/war_tasks_engagement.h"

#include <string.h>

enum {
    DOM_WAR_CASUALTY_MAX = 64u,
    DOM_WAR_EQUIP_LOSS_MAX = 16u
};

void dom_war_runtime_reset(dom_war_runtime_state* state)
{
    if (!state) {
        return;
    }
    state->engagement_cursor = 0u;
    state->occupation_cursor = 0u;
    state->resistance_cursor = 0u;
    state->disruption_cursor = 0u;
    state->route_cursor = 0u;
    state->blockade_cursor = 0u;
    state->interdiction_cursor = 0u;
}

void dom_war_audit_init(dom_war_audit_log* log,
                        dom_war_audit_entry* storage,
                        u32 capacity,
                        u64 start_id)
{
    if (!log) {
        return;
    }
    log->entries = storage;
    log->count = 0u;
    log->capacity = capacity;
    log->next_event_id = start_id ? start_id : 1u;
    if (storage && capacity > 0u) {
        memset(storage, 0, sizeof(dom_war_audit_entry) * (size_t)capacity);
    }
}

int dom_war_audit_record(dom_war_audit_log* log,
                         u32 kind,
                         u64 primary_id,
                         i64 amount)
{
    dom_war_audit_entry* entry;
    if (!log || !log->entries) {
        return -1;
    }
    if (log->count >= log->capacity) {
        return -2;
    }
    entry = &log->entries[log->count++];
    entry->event_id = log->next_event_id++;
    entry->kind = kind;
    entry->primary_id = primary_id;
    entry->amount = amount;
    return 0;
}

void dom_war_outcome_list_init(dom_war_outcome_list* list,
                               dom_war_engagement_outcome* storage,
                               u32 capacity,
                               u64 start_id)
{
    if (!list) {
        return;
    }
    list->outcomes = storage;
    list->count = 0u;
    list->capacity = capacity;
    list->next_id = start_id ? start_id : 1u;
    if (storage && capacity > 0u) {
        memset(storage, 0, sizeof(dom_war_engagement_outcome) * (size_t)capacity);
    }
}

int dom_war_outcome_append(dom_war_outcome_list* list,
                           const dom_war_engagement_outcome* outcome,
                           u64* out_id)
{
    dom_war_engagement_outcome* slot;
    if (out_id) {
        *out_id = 0u;
    }
    if (!list || !list->outcomes || !outcome) {
        return -1;
    }
    if (list->count >= list->capacity) {
        return -2;
    }
    slot = &list->outcomes[list->count++];
    *slot = *outcome;
    slot->outcome_id = list->next_id++;
    if (out_id) {
        *out_id = slot->outcome_id;
    }
    return 0;
}

void dom_war_casualty_log_init(dom_war_casualty_log* log,
                               dom_war_casualty_entry* storage,
                               u32 capacity)
{
    if (!log) {
        return;
    }
    log->entries = storage;
    log->count = 0u;
    log->capacity = capacity;
    if (storage && capacity > 0u) {
        memset(storage, 0, sizeof(dom_war_casualty_entry) * (size_t)capacity);
    }
}

int dom_war_casualty_record(dom_war_casualty_log* log,
                            u64 engagement_id,
                            u32 casualty_count,
                            u64 provenance_ref)
{
    dom_war_casualty_entry* entry;
    if (!log || !log->entries) {
        return -1;
    }
    if (log->count >= log->capacity) {
        return -2;
    }
    entry = &log->entries[log->count++];
    entry->engagement_id = engagement_id;
    entry->casualty_count = casualty_count;
    entry->provenance_ref = provenance_ref;
    return 0;
}

void dom_war_equipment_log_init(dom_war_equipment_log* log,
                                dom_war_equipment_loss_entry* storage,
                                u32 capacity)
{
    if (!log) {
        return;
    }
    log->entries = storage;
    log->count = 0u;
    log->capacity = capacity;
    if (storage && capacity > 0u) {
        memset(storage, 0, sizeof(dom_war_equipment_loss_entry) * (size_t)capacity);
    }
}

int dom_war_equipment_record(dom_war_equipment_log* log,
                             u64 engagement_id,
                             u32 equipment_loss_count,
                             u64 provenance_ref)
{
    dom_war_equipment_loss_entry* entry;
    if (!log || !log->entries) {
        return -1;
    }
    if (log->count >= log->capacity) {
        return -2;
    }
    entry = &log->entries[log->count++];
    entry->engagement_id = engagement_id;
    entry->equipment_loss_count = equipment_loss_count;
    entry->provenance_ref = provenance_ref;
    return 0;
}

void dom_war_morale_state_init(dom_war_morale_state* state,
                               dom_war_force_state* storage,
                               u32 capacity)
{
    if (!state) {
        return;
    }
    state->entries = storage;
    state->count = 0u;
    state->capacity = capacity;
    if (storage && capacity > 0u) {
        memset(storage, 0, sizeof(dom_war_force_state) * (size_t)capacity);
    }
}

static u32 dom_war_morale_find_index(const dom_war_morale_state* state,
                                     u64 force_id,
                                     int* out_found)
{
    u32 i;
    if (out_found) {
        *out_found = 0;
    }
    if (!state || !state->entries) {
        return 0u;
    }
    for (i = 0u; i < state->count; ++i) {
        if (state->entries[i].force_id == force_id) {
            if (out_found) {
                *out_found = 1;
            }
            return i;
        }
        if (state->entries[i].force_id > force_id) {
            break;
        }
    }
    return i;
}

dom_war_force_state* dom_war_morale_find(dom_war_morale_state* state,
                                         u64 force_id)
{
    int found = 0;
    u32 idx;
    if (!state || !state->entries) {
        return 0;
    }
    idx = dom_war_morale_find_index(state, force_id, &found);
    if (!found) {
        return 0;
    }
    return &state->entries[idx];
}

dom_war_force_state* dom_war_morale_ensure(dom_war_morale_state* state,
                                           u64 force_id)
{
    int found = 0;
    u32 idx;
    u32 i;
    dom_war_force_state* entry;
    if (!state || !state->entries) {
        return 0;
    }
    if (state->count >= state->capacity) {
        return 0;
    }
    idx = dom_war_morale_find_index(state, force_id, &found);
    if (found) {
        return &state->entries[idx];
    }
    for (i = state->count; i > idx; --i) {
        state->entries[i] = state->entries[i - 1u];
    }
    entry = &state->entries[idx];
    entry->force_id = force_id;
    entry->morale = 0;
    entry->readiness = 0;
    state->count += 1u;
    return entry;
}

static void dom_war_apply_morale_delta(dom_war_morale_state* state,
                                       u64 force_id,
                                       i32 morale_delta,
                                       i32 readiness_delta)
{
    dom_war_force_state* entry = dom_war_morale_ensure(state, force_id);
    if (!entry) {
        return;
    }
    entry->morale += morale_delta;
    entry->readiness += readiness_delta;
}

static u32 dom_war_seed_for_engagement(const dom_war_engagement_item* item)
{
    u64 seed = 1469598103934665603ULL;
    seed ^= item ? item->engagement_id : 0u;
    seed *= 1099511628211ULL;
    seed ^= item ? item->attacker_force_id : 0u;
    seed *= 1099511628211ULL;
    seed ^= item ? item->defender_force_id : 0u;
    seed *= 1099511628211ULL;
    seed ^= item ? (u64)item->supply_qty : 0u;
    seed *= 1099511628211ULL;
    return (u32)(seed & 0xFFFFFFFFu);
}

u32 dom_war_engagement_admit_slice(dom_war_engagement_item* items,
                                   u32 item_count,
                                   u32 start_index,
                                   u32 max_count,
                                   dom_war_audit_log* audit)
{
    u32 i;
    u32 end;
    if (!items || start_index >= item_count || max_count == 0u) {
        return 0u;
    }
    end = start_index + max_count;
    if (end > item_count) {
        end = item_count;
    }
    for (i = start_index; i < end; ++i) {
        dom_war_engagement_item* item = &items[i];
        if (item->status != DOM_WAR_ENGAGEMENT_PENDING) {
            continue;
        }
        if (item->attacker_force_id == 0u || item->defender_force_id == 0u ||
            item->supply_qty == 0u) {
            item->status = DOM_WAR_ENGAGEMENT_REFUSED;
            if (audit) {
                dom_war_audit_record(audit, DOM_WAR_AUDIT_ENGAGEMENT_REFUSE,
                                     item->engagement_id, 0);
            }
        } else {
            item->status = DOM_WAR_ENGAGEMENT_ADMITTED;
            if (audit) {
                dom_war_audit_record(audit, DOM_WAR_AUDIT_ENGAGEMENT_ADMIT,
                                     item->engagement_id, 0);
            }
        }
    }
    return end - start_index;
}

u32 dom_war_engagement_resolve_slice(dom_war_engagement_item* items,
                                     u32 item_count,
                                     u32 start_index,
                                     u32 max_count,
                                     dom_war_outcome_list* outcomes,
                                     dom_war_audit_log* audit)
{
    u32 i;
    u32 end;
    if (!items || !outcomes || start_index >= item_count || max_count == 0u) {
        return 0u;
    }
    end = start_index + max_count;
    if (end > item_count) {
        end = item_count;
    }
    for (i = start_index; i < end; ++i) {
        dom_war_engagement_item* item = &items[i];
        dom_war_engagement_outcome outcome;
        u32 seed;
        u32 casualties;
        u32 equipment;
        i32 morale_delta;
        i32 readiness_delta;
        if (item->status != DOM_WAR_ENGAGEMENT_ADMITTED) {
            continue;
        }
        seed = dom_war_seed_for_engagement(item);
        casualties = (seed % 5u) + 1u;
        equipment = seed % 3u;
        if (casualties > DOM_WAR_CASUALTY_MAX) {
            casualties = DOM_WAR_CASUALTY_MAX;
        }
        if (equipment > DOM_WAR_EQUIP_LOSS_MAX) {
            equipment = DOM_WAR_EQUIP_LOSS_MAX;
        }
        morale_delta = -(i32)((seed % 25u) + 1u);
        readiness_delta = -(i32)((seed % 20u) + 1u);
        memset(&outcome, 0, sizeof(outcome));
        outcome.engagement_id = item->engagement_id;
        outcome.winner_force_id = (seed & 1u) ? item->attacker_force_id : item->defender_force_id;
        outcome.loser_force_id = (seed & 1u) ? item->defender_force_id : item->attacker_force_id;
        outcome.casualty_count = casualties;
        outcome.equipment_loss_count = equipment;
        outcome.morale_delta = morale_delta;
        outcome.readiness_delta = readiness_delta;
        outcome.provenance_ref = item->provenance_ref ? item->provenance_ref : item->engagement_id;
        if (dom_war_outcome_append(outcomes, &outcome, 0) == 0) {
            item->status = DOM_WAR_ENGAGEMENT_RESOLVED;
            if (audit) {
                dom_war_audit_record(audit, DOM_WAR_AUDIT_ENGAGEMENT_RESOLVE,
                                     item->engagement_id, (i64)casualties);
            }
        }
    }
    return end - start_index;
}

u32 dom_war_apply_casualties_slice(const dom_war_outcome_list* outcomes,
                                   u32 start_index,
                                   u32 max_count,
                                   dom_war_casualty_log* log,
                                   dom_war_audit_log* audit)
{
    u32 i;
    u32 end;
    if (!outcomes || !outcomes->outcomes || start_index >= outcomes->count || max_count == 0u) {
        return 0u;
    }
    end = start_index + max_count;
    if (end > outcomes->count) {
        end = outcomes->count;
    }
    for (i = start_index; i < end; ++i) {
        const dom_war_engagement_outcome* outcome = &outcomes->outcomes[i];
        if (log) {
            (void)dom_war_casualty_record(log, outcome->engagement_id,
                                          outcome->casualty_count,
                                          outcome->provenance_ref);
        }
        if (audit) {
            dom_war_audit_record(audit, DOM_WAR_AUDIT_CASUALTY_APPLY,
                                 outcome->engagement_id, (i64)outcome->casualty_count);
        }
    }
    return end - start_index;
}

u32 dom_war_apply_equipment_losses_slice(const dom_war_outcome_list* outcomes,
                                         u32 start_index,
                                         u32 max_count,
                                         dom_war_equipment_log* log,
                                         dom_war_audit_log* audit)
{
    u32 i;
    u32 end;
    if (!outcomes || !outcomes->outcomes || start_index >= outcomes->count || max_count == 0u) {
        return 0u;
    }
    end = start_index + max_count;
    if (end > outcomes->count) {
        end = outcomes->count;
    }
    for (i = start_index; i < end; ++i) {
        const dom_war_engagement_outcome* outcome = &outcomes->outcomes[i];
        if (log) {
            (void)dom_war_equipment_record(log, outcome->engagement_id,
                                           outcome->equipment_loss_count,
                                           outcome->provenance_ref);
        }
        if (audit) {
            dom_war_audit_record(audit, DOM_WAR_AUDIT_EQUIPMENT_APPLY,
                                 outcome->engagement_id, (i64)outcome->equipment_loss_count);
        }
    }
    return end - start_index;
}

u32 dom_war_update_morale_readiness_slice(const dom_war_outcome_list* outcomes,
                                          u32 start_index,
                                          u32 max_count,
                                          dom_war_morale_state* morale,
                                          dom_war_audit_log* audit)
{
    u32 i;
    u32 end;
    if (!outcomes || !outcomes->outcomes || start_index >= outcomes->count || max_count == 0u) {
        return 0u;
    }
    end = start_index + max_count;
    if (end > outcomes->count) {
        end = outcomes->count;
    }
    for (i = start_index; i < end; ++i) {
        const dom_war_engagement_outcome* outcome = &outcomes->outcomes[i];
        if (morale) {
            dom_war_apply_morale_delta(morale,
                                       outcome->winner_force_id,
                                       -outcome->morale_delta,
                                       -outcome->readiness_delta);
            dom_war_apply_morale_delta(morale,
                                       outcome->loser_force_id,
                                       outcome->morale_delta,
                                       outcome->readiness_delta);
        }
        if (audit) {
            dom_war_audit_record(audit, DOM_WAR_AUDIT_MORALE_UPDATE,
                                 outcome->engagement_id, (i64)outcome->morale_delta);
        }
    }
    return end - start_index;
}
