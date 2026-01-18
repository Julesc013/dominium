/*
FILE: game/rules/war/disruption_effects.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Game / war rules
RESPONSIBILITY: Implements deterministic disruption events and effects.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Disruption application is deterministic and event-driven.
*/
#include "dominium/rules/war/disruption_effects.h"

#include <string.h>

void disruption_event_list_init(disruption_event_list* list,
                                disruption_event* storage,
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
        memset(storage, 0, sizeof(disruption_event) * (size_t)capacity);
    }
}

static u32 disruption_find_index(const disruption_event_list* list,
                                 u64 disruption_id,
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
        if (list->events[i].disruption_id == disruption_id) {
            if (out_found) {
                *out_found = 1;
            }
            return i;
        }
        if (list->events[i].disruption_id > disruption_id) {
            break;
        }
    }
    return i;
}

disruption_event* disruption_event_find(disruption_event_list* list,
                                        u64 disruption_id)
{
    int found = 0;
    u32 idx;
    if (!list || !list->events) {
        return 0;
    }
    idx = disruption_find_index(list, disruption_id, &found);
    if (!found) {
        return 0;
    }
    return &list->events[idx];
}

int disruption_event_schedule(disruption_event_list* list,
                              const disruption_event* input,
                              u64* out_id)
{
    int found = 0;
    u32 idx;
    u32 i;
    disruption_event* entry;
    u64 disruption_id;
    if (!list || !list->events || !input) {
        return -1;
    }
    if (list->count >= list->capacity) {
        return -2;
    }
    disruption_id = input->disruption_id;
    if (disruption_id == 0u) {
        disruption_id = list->next_id++;
        if (disruption_id == 0u) {
            disruption_id = list->next_id++;
        }
    }
    idx = disruption_find_index(list, disruption_id, &found);
    if (found) {
        return -3;
    }
    for (i = list->count; i > idx; --i) {
        list->events[i] = list->events[i - 1u];
    }
    entry = &list->events[idx];
    memset(entry, 0, sizeof(*entry));
    *entry = *input;
    entry->disruption_id = disruption_id;
    if (entry->status == 0u) {
        entry->status = DISRUPTION_STATUS_SCHEDULED;
    }
    if (entry->provenance_ref == 0u) {
        entry->provenance_ref = disruption_id;
    }
    list->count += 1u;
    if (out_id) {
        *out_id = disruption_id;
    }
    return 0;
}

int disruption_apply(disruption_event* event,
                     disruption_effects_context* ctx)
{
    transport_capacity* capacity;
    legitimacy_state* legit;
    u32 take = 0u;
    if (!event || !ctx) {
        return -1;
    }
    if (event->status != DISRUPTION_STATUS_SCHEDULED) {
        return 0;
    }
    if (ctx->transport && event->transport_capacity_id != 0u && event->capacity_delta > 0u) {
        capacity = transport_capacity_find(ctx->transport, event->transport_capacity_id);
        if (capacity) {
            if (capacity->available_qty <= event->capacity_delta) {
                capacity->available_qty = 0u;
            } else {
                capacity->available_qty -= event->capacity_delta;
            }
        }
    }
    if (ctx->stores && event->supply_store_ref != 0u &&
        event->supply_asset_id != 0u && event->supply_qty > 0u) {
        (void)infra_store_take(ctx->stores,
                               event->supply_store_ref,
                               event->supply_asset_id,
                               event->supply_qty,
                               &take);
    }
    if (ctx->legitimacy && event->legitimacy_id != 0u && event->legitimacy_delta != 0) {
        legit = legitimacy_find(ctx->legitimacy, event->legitimacy_id);
        if (legit) {
            (void)legitimacy_apply_delta(legit, event->legitimacy_delta);
        }
    }
    event->status = DISRUPTION_STATUS_APPLIED;
    event->scheduled_act = DOM_TIME_ACT_MAX;
    return 0;
}
