/*
FILE: game/rules/war/engagement.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Game / war rules
RESPONSIBILITY: Implements engagement registries and outcome storage.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Engagement ordering and outcomes are deterministic.
*/
#include "dominium/rules/war/engagement.h"

#include <string.h>

const char* engagement_refusal_to_string(engagement_refusal_code code)
{
    switch (code) {
        case ENGAGEMENT_REFUSAL_NONE: return "none";
        case ENGAGEMENT_REFUSAL_ALREADY_RESOLVED: return "engagement_already_resolved";
        case ENGAGEMENT_REFUSAL_PARTICIPANT_NOT_READY: return "participant_not_ready";
        case ENGAGEMENT_REFUSAL_INSUFFICIENT_SUPPLY: return "insufficient_supply";
        case ENGAGEMENT_REFUSAL_OBJECTIVE_INVALID: return "objective_invalid";
        case ENGAGEMENT_REFUSAL_OUT_OF_DOMAIN: return "out_of_domain";
        default: return "unknown";
    }
}

void engagement_registry_init(engagement_registry* reg,
                              engagement* storage,
                              u32 capacity,
                              u64 start_id)
{
    if (!reg) {
        return;
    }
    reg->engagements = storage;
    reg->count = 0u;
    reg->capacity = capacity;
    reg->next_id = start_id ? start_id : 1u;
    if (storage && capacity > 0u) {
        memset(storage, 0, sizeof(engagement) * (size_t)capacity);
    }
}

static u32 engagement_find_index(const engagement_registry* reg,
                                 u64 engagement_id,
                                 int* out_found)
{
    u32 i;
    if (out_found) {
        *out_found = 0;
    }
    if (!reg || !reg->engagements) {
        return 0u;
    }
    for (i = 0u; i < reg->count; ++i) {
        if (reg->engagements[i].engagement_id == engagement_id) {
            if (out_found) {
                *out_found = 1;
            }
            return i;
        }
        if (reg->engagements[i].engagement_id > engagement_id) {
            break;
        }
    }
    return i;
}

static void engagement_sort_participants(engagement* entry)
{
    u32 i;
    u32 j;
    if (!entry || entry->participant_count < 2u) {
        return;
    }
    for (i = 0u; i + 1u < entry->participant_count; ++i) {
        for (j = i + 1u; j < entry->participant_count; ++j) {
            if (entry->participants[j].force_id < entry->participants[i].force_id) {
                engagement_participant tmp = entry->participants[i];
                entry->participants[i] = entry->participants[j];
                entry->participants[j] = tmp;
            }
        }
    }
}

engagement* engagement_find(engagement_registry* reg,
                            u64 engagement_id)
{
    int found = 0;
    u32 idx;
    if (!reg || !reg->engagements) {
        return 0;
    }
    idx = engagement_find_index(reg, engagement_id, &found);
    if (!found) {
        return 0;
    }
    return &reg->engagements[idx];
}

int engagement_register(engagement_registry* reg,
                        const engagement* input,
                        u64* out_id)
{
    int found = 0;
    u32 idx;
    u32 i;
    engagement* entry;
    u64 engagement_id;
    if (out_id) {
        *out_id = 0u;
    }
    if (!reg || !reg->engagements || !input) {
        return -1;
    }
    if (input->participant_count > ENGAGEMENT_MAX_PARTICIPANTS ||
        input->environment_modifier_count > ENGAGEMENT_MAX_ENV_MODIFIERS) {
        return -4;
    }
    if (reg->count >= reg->capacity) {
        return -2;
    }
    engagement_id = input->engagement_id ? input->engagement_id : reg->next_id++;
    idx = engagement_find_index(reg, engagement_id, &found);
    if (found) {
        return -3;
    }
    for (i = reg->count; i > idx; --i) {
        reg->engagements[i] = reg->engagements[i - 1u];
    }
    entry = &reg->engagements[idx];
    *entry = *input;
    entry->engagement_id = engagement_id;
    entry->status = ENGAGEMENT_STATUS_SCHEDULED;
    entry->next_due_tick = entry->resolution_act;
    engagement_sort_participants(entry);
    reg->count += 1u;
    if (out_id) {
        *out_id = engagement_id;
    }
    return 0;
}

void engagement_outcome_list_init(engagement_outcome_list* list,
                                  engagement_outcome* storage,
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
        memset(storage, 0, sizeof(engagement_outcome) * (size_t)capacity);
    }
}

int engagement_outcome_append(engagement_outcome_list* list,
                              const engagement_outcome* outcome,
                              u64* out_id)
{
    engagement_outcome* slot;
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

const engagement_outcome* engagement_outcome_find(const engagement_outcome_list* list,
                                                  u64 outcome_id)
{
    u32 i;
    if (!list || !list->outcomes) {
        return 0;
    }
    for (i = 0u; i < list->count; ++i) {
        if (list->outcomes[i].outcome_id == outcome_id) {
            return &list->outcomes[i];
        }
    }
    return 0;
}
