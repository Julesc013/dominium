/*
FILE: game/agents/agent_belief_update.cpp
MODULE: Dominium
LAYER / SUBSYSTEM: Game / agents
RESPONSIBILITY: Implements deterministic belief updates for agents.
ALLOWED DEPENDENCIES: game/include/**, engine/include/** public headers, and C++98 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; OS/platform headers.
THREADING MODEL: No internal synchronization; callers must serialize access.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Belief deltas clamp to fixed bounds and apply in-order.
*/
#include "dominium/agents/agent_belief_update.h"

#include <string.h>

static u32 agent_clamp_confidence(i32 value)
{
    if (value < 0) {
        return 0u;
    }
    if ((u32)value > AGENT_CONFIDENCE_MAX) {
        return AGENT_CONFIDENCE_MAX;
    }
    return (u32)value;
}

static u32 agent_clamp_need(i32 value)
{
    if (value < 0) {
        return 0u;
    }
    if ((u32)value > AGENT_NEED_SCALE) {
        return AGENT_NEED_SCALE;
    }
    return (u32)value;
}

static u32 agent_belief_find_index(const agent_belief_store* store,
                                   u64 agent_id,
                                   u64 knowledge_ref,
                                   int* out_found)
{
    u32 i;
    if (out_found) {
        *out_found = 0;
    }
    if (!store || !store->entries) {
        return 0u;
    }
    for (i = 0u; i < store->count; ++i) {
        const agent_belief_entry* e = &store->entries[i];
        if (e->agent_id == agent_id && e->knowledge_ref == knowledge_ref) {
            if (out_found) {
                *out_found = 1;
            }
            return i;
        }
        if (e->agent_id > agent_id ||
            (e->agent_id == agent_id && e->knowledge_ref > knowledge_ref)) {
            break;
        }
    }
    return i;
}

static void agent_belief_remove_at(agent_belief_store* store, u32 idx)
{
    u32 i;
    if (!store || !store->entries || idx >= store->count) {
        return;
    }
    for (i = idx; i + 1u < store->count; ++i) {
        store->entries[i] = store->entries[i + 1u];
    }
    store->count -= 1u;
}

void agent_belief_store_init(agent_belief_store* store,
                             agent_belief_entry* storage,
                             u32 capacity,
                             u64 start_id,
                             u32 decay_q16_per_act,
                             u32 min_confidence_q16)
{
    if (!store) {
        return;
    }
    store->entries = storage;
    store->count = 0u;
    store->capacity = capacity;
    store->next_id = start_id ? start_id : 1u;
    store->decay_q16_per_act = decay_q16_per_act;
    store->min_confidence_q16 = (min_confidence_q16 > AGENT_CONFIDENCE_MAX)
        ? AGENT_CONFIDENCE_MAX : min_confidence_q16;
    store->last_decay_act = 0u;
    if (storage && capacity > 0u) {
        memset(storage, 0, sizeof(agent_belief_entry) * (size_t)capacity);
    }
}

int agent_belief_store_apply_event(agent_belief_store* store,
                                   const agent_belief_event* event,
                                   dom_act_time_t now_act)
{
    int found = 0;
    u32 idx;
    u32 i;
    agent_belief_entry* entry;
    u32 confidence;
    if (!store || !store->entries || !event || event->agent_id == 0u) {
        return -1;
    }
    idx = agent_belief_find_index(store, event->agent_id, event->knowledge_ref, &found);
    if (event->kind == AGENT_BELIEF_EVENT_FORGET) {
        if (!found) {
            return 0;
        }
        entry = &store->entries[idx];
        confidence = entry->confidence_q16;
        if (event->confidence_delta_q16 != 0) {
            confidence = agent_clamp_confidence((i32)confidence + event->confidence_delta_q16);
        } else {
            confidence = 0u;
        }
        entry->confidence_q16 = confidence;
        entry->flags |= AGENT_BELIEF_FLAG_DISTORTED;
        if (confidence <= store->min_confidence_q16) {
            agent_belief_remove_at(store, idx);
        }
        return 0;
    }

    if (!found) {
        if (store->count >= store->capacity) {
            u32 lowest_idx = 0u;
            u32 lowest_conf = AGENT_CONFIDENCE_MAX;
            for (i = 0u; i < store->count; ++i) {
                if (store->entries[i].confidence_q16 < lowest_conf) {
                    lowest_conf = store->entries[i].confidence_q16;
                    lowest_idx = i;
                }
            }
            agent_belief_remove_at(store, lowest_idx);
            if (idx > lowest_idx) {
                idx -= 1u;
            }
        }
        if (store->count >= store->capacity) {
            return -2;
        }
        for (i = store->count; i > idx; --i) {
            store->entries[i] = store->entries[i - 1u];
        }
        entry = &store->entries[idx];
        memset(entry, 0, sizeof(*entry));
        entry->belief_id = store->next_id++;
        entry->agent_id = event->agent_id;
        entry->knowledge_ref = event->knowledge_ref;
        entry->topic_id = event->topic_id;
        store->count += 1u;
    } else {
        entry = &store->entries[idx];
    }

    confidence = entry->confidence_q16;
    if (event->confidence_q16 != 0u) {
        confidence = event->confidence_q16;
    } else if (event->confidence_delta_q16 != 0) {
        confidence = agent_clamp_confidence((i32)confidence + event->confidence_delta_q16);
    }
    if (confidence == 0u) {
        confidence = AGENT_CONFIDENCE_MAX / 2u;
    }
    entry->confidence_q16 = confidence;
    entry->topic_id = event->topic_id ? event->topic_id : entry->topic_id;
    entry->observed_act = (event->observed_act != 0u) ? event->observed_act : now_act;
    entry->expires_act = event->expires_act;
    entry->flags |= event->flags_set;
    entry->flags &= ~event->flags_clear;
    if (event->kind == AGENT_BELIEF_EVENT_HEAR) {
        entry->flags |= AGENT_BELIEF_FLAG_HEARSAY;
    }
    if (event->kind == AGENT_BELIEF_EVENT_DISTORT) {
        entry->flags |= AGENT_BELIEF_FLAG_DISTORTED;
    }
    return 0;
}

void agent_belief_store_decay(agent_belief_store* store,
                              dom_act_time_t now_act)
{
    u32 i = 0u;
    u32 decay_q16;
    if (!store || !store->entries) {
        return;
    }
    if (store->decay_q16_per_act == 0u || store->count == 0u) {
        store->last_decay_act = now_act;
        return;
    }
    if (store->last_decay_act == 0u) {
        store->last_decay_act = now_act;
        return;
    }
    if (now_act <= store->last_decay_act) {
        return;
    }
    decay_q16 = (u32)((u64)store->decay_q16_per_act * (u64)(now_act - store->last_decay_act));
    while (i < store->count) {
        agent_belief_entry* entry = &store->entries[i];
        if (entry->expires_act != 0u && entry->expires_act <= now_act) {
            agent_belief_remove_at(store, i);
            continue;
        }
        if (decay_q16 > 0u) {
            u32 next_conf = agent_clamp_confidence((i32)entry->confidence_q16 - (i32)decay_q16);
            entry->confidence_q16 = next_conf;
            if (next_conf <= store->min_confidence_q16) {
                agent_belief_remove_at(store, i);
                continue;
            }
        }
        i += 1u;
    }
    store->last_decay_act = now_act;
}

const agent_belief_entry* agent_belief_store_best_topic(const agent_belief_store* store,
                                                        u64 agent_id,
                                                        u32 topic_id)
{
    const agent_belief_entry* best = 0;
    u32 i;
    if (!store || !store->entries) {
        return 0;
    }
    for (i = 0u; i < store->count; ++i) {
        const agent_belief_entry* entry = &store->entries[i];
        if (entry->agent_id != agent_id || entry->topic_id != topic_id) {
            continue;
        }
        if (!best || entry->confidence_q16 > best->confidence_q16 ||
            (entry->confidence_q16 == best->confidence_q16 && entry->belief_id < best->belief_id)) {
            best = entry;
        }
    }
    return best;
}

u32 agent_belief_store_mask(const agent_belief_store* store,
                            u64 agent_id)
{
    u32 mask = 0u;
    u32 i;
    if (!store || !store->entries) {
        return 0u;
    }
    for (i = 0u; i < store->count; ++i) {
        const agent_belief_entry* entry = &store->entries[i];
        if (entry->agent_id != agent_id) {
            continue;
        }
        switch (entry->topic_id) {
            case AGENT_BELIEF_TOPIC_RESOURCE:
                mask |= AGENT_KNOW_RESOURCE;
                break;
            case AGENT_BELIEF_TOPIC_SAFE_ROUTE:
                mask |= AGENT_KNOW_SAFE_ROUTE;
                break;
            case AGENT_BELIEF_TOPIC_THREAT:
                mask |= AGENT_KNOW_THREAT;
                break;
            default:
                break;
        }
    }
    return mask;
}

void agent_belief_init(agent_belief_state* state,
                       u64 agent_id,
                       u32 knowledge_mask,
                       u32 hunger_level,
                       u32 threat_level,
                       dom_act_time_t now_act)
{
    if (!state) {
        return;
    }
    state->agent_id = agent_id;
    state->knowledge_mask = knowledge_mask;
    state->hunger_level = (hunger_level > AGENT_NEED_SCALE) ? AGENT_NEED_SCALE : hunger_level;
    state->threat_level = (threat_level > AGENT_NEED_SCALE) ? AGENT_NEED_SCALE : threat_level;
    state->last_update_act = now_act;
}

int agent_belief_apply_observation(agent_belief_state* state,
                                   const agent_observation_event* obs,
                                   dom_act_time_t now_act)
{
    i32 next;
    if (!state || !obs) {
        return -1;
    }
    state->knowledge_mask |= obs->knowledge_grant_mask;
    state->knowledge_mask &= ~obs->knowledge_clear_mask;

    next = (i32)state->hunger_level + obs->hunger_delta;
    state->hunger_level = agent_clamp_need(next);

    next = (i32)state->threat_level + obs->threat_delta;
    state->threat_level = agent_clamp_need(next);

    state->last_update_act = now_act;
    return 0;
}

int agent_belief_apply_command_outcome(agent_belief_state* state,
                                       const agent_command_outcome* outcome,
                                       dom_act_time_t now_act)
{
    i32 next;
    if (!state || !outcome) {
        return -1;
    }
    state->knowledge_mask &= ~outcome->knowledge_clear_mask;
    if (!outcome->success && outcome->refusal == AGENT_REFUSAL_INSUFFICIENT_KNOWLEDGE &&
        outcome->knowledge_clear_mask == 0u) {
        state->knowledge_mask &= ~AGENT_KNOW_RESOURCE;
    }

    next = (i32)state->hunger_level + outcome->hunger_delta;
    state->hunger_level = agent_clamp_need(next);

    next = (i32)state->threat_level + outcome->threat_delta;
    state->threat_level = agent_clamp_need(next);

    state->last_update_act = now_act;
    return 0;
}
