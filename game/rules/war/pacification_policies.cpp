/*
FILE: game/rules/war/pacification_policies.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Game / war rules
RESPONSIBILITY: Implements deterministic pacification policies and scheduled effects.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Pacification policy application is deterministic.
*/
#include "dominium/rules/war/pacification_policies.h"

#include <string.h>

void pacification_policy_registry_init(pacification_policy_registry* reg,
                                       pacification_policy* storage,
                                       u32 capacity,
                                       u64 start_id)
{
    if (!reg) {
        return;
    }
    reg->policies = storage;
    reg->count = 0u;
    reg->capacity = capacity;
    reg->next_id = start_id ? start_id : 1u;
    if (storage && capacity > 0u) {
        memset(storage, 0, sizeof(pacification_policy) * (size_t)capacity);
    }
}

static u32 pacification_policy_find_index(const pacification_policy_registry* reg,
                                          u64 policy_id,
                                          int* out_found)
{
    u32 i;
    if (out_found) {
        *out_found = 0;
    }
    if (!reg || !reg->policies) {
        return 0u;
    }
    for (i = 0u; i < reg->count; ++i) {
        if (reg->policies[i].policy_id == policy_id) {
            if (out_found) {
                *out_found = 1;
            }
            return i;
        }
        if (reg->policies[i].policy_id > policy_id) {
            break;
        }
    }
    return i;
}

pacification_policy* pacification_policy_find(pacification_policy_registry* reg,
                                              u64 policy_id)
{
    int found = 0;
    u32 idx;
    if (!reg || !reg->policies) {
        return 0;
    }
    idx = pacification_policy_find_index(reg, policy_id, &found);
    if (!found) {
        return 0;
    }
    return &reg->policies[idx];
}

int pacification_policy_register(pacification_policy_registry* reg,
                                 const pacification_policy* input,
                                 u64* out_id)
{
    int found = 0;
    u32 idx;
    u32 i;
    pacification_policy* entry;
    u64 policy_id;
    if (!reg || !reg->policies || !input) {
        return -1;
    }
    if (reg->count >= reg->capacity) {
        return -2;
    }
    policy_id = input->policy_id;
    if (policy_id == 0u) {
        policy_id = reg->next_id++;
        if (policy_id == 0u) {
            policy_id = reg->next_id++;
        }
    }
    idx = pacification_policy_find_index(reg, policy_id, &found);
    if (found) {
        return -3;
    }
    for (i = reg->count; i > idx; --i) {
        reg->policies[i] = reg->policies[i - 1u];
    }
    entry = &reg->policies[idx];
    memset(entry, 0, sizeof(*entry));
    *entry = *input;
    entry->policy_id = policy_id;
    if (entry->provenance_ref == 0u) {
        entry->provenance_ref = policy_id;
    }
    reg->count += 1u;
    if (out_id) {
        *out_id = policy_id;
    }
    return 0;
}

void pacification_policy_event_list_init(pacification_policy_event_list* list,
                                         pacification_policy_event* storage,
                                         u32 capacity,
                                         u64 start_id)
{
    if (!list) {
        return;
    }
    list->events = storage;
    list->count = 0u;
    list->capacity = capacity;
    list->next_id = start_id ? start_id : 1u;
    if (storage && capacity > 0u) {
        memset(storage, 0, sizeof(pacification_policy_event) * (size_t)capacity);
    }
}

static u32 pacification_event_find_index(const pacification_policy_event_list* list,
                                         u64 event_id,
                                         int* out_found)
{
    u32 i;
    if (out_found) {
        *out_found = 0;
    }
    if (!list || !list->events) {
        return 0u;
    }
    for (i = 0u; i < list->count; ++i) {
        if (list->events[i].event_id == event_id) {
            if (out_found) {
                *out_found = 1;
            }
            return i;
        }
        if (list->events[i].event_id > event_id) {
            break;
        }
    }
    return i;
}

pacification_policy_event* pacification_policy_event_find(pacification_policy_event_list* list,
                                                          u64 event_id)
{
    int found = 0;
    u32 idx;
    if (!list || !list->events) {
        return 0;
    }
    idx = pacification_event_find_index(list, event_id, &found);
    if (!found) {
        return 0;
    }
    return &list->events[idx];
}

int pacification_policy_event_schedule(pacification_policy_event_list* list,
                                       const pacification_policy_event* input,
                                       u64* out_id)
{
    int found = 0;
    u32 idx;
    u32 i;
    pacification_policy_event* entry;
    u64 event_id;
    if (!list || !list->events || !input) {
        return -1;
    }
    if (list->count >= list->capacity) {
        return -2;
    }
    event_id = input->event_id;
    if (event_id == 0u) {
        event_id = list->next_id++;
        if (event_id == 0u) {
            event_id = list->next_id++;
        }
    }
    idx = pacification_event_find_index(list, event_id, &found);
    if (found) {
        return -3;
    }
    for (i = list->count; i > idx; --i) {
        list->events[i] = list->events[i - 1u];
    }
    entry = &list->events[idx];
    memset(entry, 0, sizeof(*entry));
    *entry = *input;
    entry->event_id = event_id;
    if (entry->status == 0u) {
        entry->status = PACIFICATION_EVENT_SCHEDULED;
    }
    if (entry->provenance_ref == 0u) {
        entry->provenance_ref = event_id;
    }
    list->count += 1u;
    if (out_id) {
        *out_id = event_id;
    }
    return 0;
}

static int pacification_policy_costs_available(const pacification_policy* policy,
                                               infra_store_registry* stores,
                                               u64 store_ref)
{
    u32 i;
    if (!policy) {
        return 0;
    }
    if (policy->cost_count == 0u) {
        return 1;
    }
    if (!stores || store_ref == 0u) {
        return 0;
    }
    for (i = 0u; i < policy->cost_count; ++i) {
        u32 qty = 0u;
        if (policy->cost_asset_ids[i] == 0u || policy->cost_qtys[i] == 0u) {
            continue;
        }
        if (infra_store_get_qty(stores, store_ref,
                                policy->cost_asset_ids[i], &qty) != 0) {
            return 0;
        }
        if (qty < policy->cost_qtys[i]) {
            return 0;
        }
    }
    return 1;
}

static void pacification_policy_consume_costs(const pacification_policy* policy,
                                              infra_store_registry* stores,
                                              u64 store_ref)
{
    u32 i;
    if (!policy || !stores || store_ref == 0u || policy->cost_count == 0u) {
        return;
    }
    for (i = 0u; i < policy->cost_count; ++i) {
        if (policy->cost_asset_ids[i] == 0u || policy->cost_qtys[i] == 0u) {
            continue;
        }
        (void)infra_store_consume(stores, store_ref,
                                  policy->cost_asset_ids[i],
                                  policy->cost_qtys[i]);
    }
}

int pacification_policy_apply(pacification_policy_event* event,
                              pacification_apply_context* ctx,
                              occupation_refusal_code* out_refusal)
{
    pacification_policy* policy;
    occupation_state* occupation;
    resistance_state* resistance;
    territory_control* territory;
    legitimacy_state* legit;
    if (out_refusal) {
        *out_refusal = OCCUPATION_REFUSAL_NONE;
    }
    if (!event || !ctx || !ctx->policies) {
        return -1;
    }
    if (event->status != PACIFICATION_EVENT_SCHEDULED) {
        return 0;
    }
    policy = pacification_policy_find(ctx->policies, event->policy_id);
    if (!policy || policy->allowed == 0u) {
        if (out_refusal) {
            *out_refusal = OCCUPATION_REFUSAL_POLICY_NOT_ALLOWED;
        }
        return -2;
    }
    occupation = 0;
    if (ctx->occupations && event->occupation_id != 0u) {
        occupation = occupation_find(ctx->occupations, event->occupation_id);
    }
    if (!occupation && ctx->occupations && event->territory_id != 0u) {
        occupation = occupation_find_by_territory(ctx->occupations, event->territory_id);
    }
    territory = 0;
    if (ctx->territory && event->territory_id != 0u) {
        territory = territory_control_find(ctx->territory, event->territory_id);
    }
    if (!occupation) {
        if (out_refusal) {
            *out_refusal = OCCUPATION_REFUSAL_TERRITORY_NOT_CONTROLLED;
        }
        return -4;
    }
    if (!territory && ctx->territory && occupation->territory_id != 0u) {
        territory = territory_control_find(ctx->territory, occupation->territory_id);
    }
    if (!territory) {
        if (out_refusal) {
            *out_refusal = OCCUPATION_REFUSAL_UNKNOWN_TERRITORY;
        }
        return -3;
    }
    if (occupation->occupier_org_id != 0u &&
        territory->current_controller != occupation->occupier_org_id) {
        if (out_refusal) {
            *out_refusal = OCCUPATION_REFUSAL_TERRITORY_NOT_CONTROLLED;
        }
        return -5;
    }
    if (!pacification_policy_costs_available(policy, ctx->stores, event->supply_store_ref)) {
        if (out_refusal) {
            *out_refusal = OCCUPATION_REFUSAL_INSUFFICIENT_SUPPLY;
        }
        return -6;
    }
    pacification_policy_consume_costs(policy, ctx->stores, event->supply_store_ref);

    if (ctx->legitimacy && occupation->legitimacy_id != 0u &&
        policy->legitimacy_delta != 0) {
        legit = legitimacy_find(ctx->legitimacy, occupation->legitimacy_id);
        if (legit) {
            (void)legitimacy_apply_delta(legit, policy->legitimacy_delta);
        }
    }
    if (policy->coercion_delta != 0) {
        i32 next = (i32)occupation->coercion_level + policy->coercion_delta;
        if (next < 0) {
            next = 0;
        }
        if ((u32)next < policy->coercion_floor) {
            next = (i32)policy->coercion_floor;
        }
        if ((u32)next > RESISTANCE_SCALE) {
            next = (i32)RESISTANCE_SCALE;
        }
        occupation->coercion_level = (u32)next;
    }
    resistance = 0;
    if (ctx->resistances && event->resistance_id != 0u) {
        resistance = resistance_find(ctx->resistances, event->resistance_id);
    }
    if (!resistance && ctx->resistances && event->territory_id != 0u) {
        resistance = resistance_find_by_territory(ctx->resistances, event->territory_id);
    }
    if (resistance && policy->resistance_pressure_delta != 0) {
        i32 next = (i32)resistance->resistance_pressure + policy->resistance_pressure_delta;
        if (next < 0) {
            next = 0;
        }
        if ((u32)next > RESISTANCE_SCALE) {
            next = (i32)RESISTANCE_SCALE;
        }
        resistance->resistance_pressure = (u32)next;
    }
    event->status = PACIFICATION_EVENT_APPLIED;
    event->scheduled_act = DOM_TIME_ACT_MAX;
    return 0;
}
