/*
FILE: game/core/dom_interest_set.c
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium core / interest_set
RESPONSIBILITY: Implements InterestSet ordering, deduplication, and relevance transitions.
ALLOWED DEPENDENCIES: `game/include/**`, `engine/include/**` public headers, and C89 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; product-layer runtime code.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Deterministic ordering and membership are mandatory.
*/
#include "dominium/interest_set.h"

#include <stdlib.h>
#include <string.h>

void dom_interest_set_init(dom_interest_set* set)
{
    if (!set) {
        return;
    }
    set->entries = NULL;
    set->count = 0u;
    set->capacity = 0u;
    set->overflow = 0u;
}

void dom_interest_set_free(dom_interest_set* set)
{
    if (!set) {
        return;
    }
    if (set->entries) {
        free(set->entries);
    }
    dom_interest_set_init(set);
}

int dom_interest_set_reserve(dom_interest_set* set, u32 capacity)
{
    dom_interest_entry* entries;
    if (!set) {
        return -1;
    }
    dom_interest_set_free(set);
    if (capacity == 0u) {
        return 0;
    }
    entries = (dom_interest_entry*)malloc(sizeof(dom_interest_entry) * (size_t)capacity);
    if (!entries) {
        return -2;
    }
    memset(entries, 0, sizeof(dom_interest_entry) * (size_t)capacity);
    set->entries = entries;
    set->capacity = capacity;
    return 0;
}

void dom_interest_set_clear(dom_interest_set* set)
{
    if (!set) {
        return;
    }
    set->count = 0u;
    set->overflow = 0u;
}

int dom_interest_set_add(dom_interest_set* set,
                         u32 target_kind,
                         u64 target_id,
                         dom_interest_reason reason,
                         u32 strength,
                         dom_act_time_t expiry_tick)
{
    dom_interest_entry* entry;
    if (!set || !set->entries) {
        return -1;
    }
    if (set->count >= set->capacity) {
        set->overflow += 1u;
        return -2;
    }
    entry = &set->entries[set->count++];
    entry->target_id = target_id;
    entry->target_kind = target_kind;
    entry->reason = (u32)reason;
    entry->strength = strength;
    entry->expiry_tick = expiry_tick;
    return 0;
}

u32 dom_interest_set_overflow(const dom_interest_set* set)
{
    return set ? set->overflow : 0u;
}

static int dom_interest_entry_cmp(const dom_interest_entry* a, const dom_interest_entry* b)
{
    if (!a || !b) {
        return a ? 1 : (b ? -1 : 0);
    }
    if (a->target_kind < b->target_kind) return -1;
    if (a->target_kind > b->target_kind) return 1;
    if (a->target_id < b->target_id) return -1;
    if (a->target_id > b->target_id) return 1;
    if (a->reason < b->reason) return -1;
    if (a->reason > b->reason) return 1;
    if (a->strength < b->strength) return -1;
    if (a->strength > b->strength) return 1;
    if (a->expiry_tick < b->expiry_tick) return -1;
    if (a->expiry_tick > b->expiry_tick) return 1;
    return 0;
}

static int dom_interest_entry_same_key(const dom_interest_entry* a, const dom_interest_entry* b)
{
    if (!a || !b) {
        return 0;
    }
    return (a->target_kind == b->target_kind &&
            a->target_id == b->target_id &&
            a->reason == b->reason);
}

static void dom_interest_insertion_sort(dom_interest_entry* entries, u32 count)
{
    u32 i;
    if (!entries) {
        return;
    }
    for (i = 1u; i < count; ++i) {
        dom_interest_entry key = entries[i];
        u32 j = i;
        while (j > 0u && dom_interest_entry_cmp(&entries[j - 1u], &key) > 0) {
            entries[j] = entries[j - 1u];
            --j;
        }
        entries[j] = key;
    }
}

void dom_interest_set_finalize(dom_interest_set* set)
{
    u32 i;
    u32 write = 0u;
    if (!set || !set->entries || set->count == 0u) {
        return;
    }

    dom_interest_insertion_sort(set->entries, set->count);

    for (i = 0u; i < set->count; ++i) {
        if (write == 0u || !dom_interest_entry_same_key(&set->entries[write - 1u], &set->entries[i])) {
            set->entries[write++] = set->entries[i];
        } else {
            dom_interest_entry* cur = &set->entries[write - 1u];
            const dom_interest_entry* incoming = &set->entries[i];
            if (incoming->strength > cur->strength) {
                cur->strength = incoming->strength;
            }
            if (incoming->expiry_tick > cur->expiry_tick) {
                cur->expiry_tick = incoming->expiry_tick;
            }
        }
    }
    set->count = write;
}

u32 dom_interest_set_strength(const dom_interest_set* set,
                              u32 target_kind,
                              u64 target_id,
                              dom_act_time_t now,
                              dom_act_time_t* out_expiry)
{
    u32 i;
    u32 best_strength = 0u;
    dom_act_time_t best_expiry = 0;
    if (!set || !set->entries) {
        if (out_expiry) {
            *out_expiry = 0;
        }
        return 0u;
    }
    for (i = 0u; i < set->count; ++i) {
        const dom_interest_entry* entry = &set->entries[i];
        if (entry->target_kind != target_kind || entry->target_id != target_id) {
            continue;
        }
        if (entry->expiry_tick != DOM_INTEREST_PERSISTENT && entry->expiry_tick <= now) {
            continue;
        }
        if (entry->strength > best_strength) {
            best_strength = entry->strength;
        }
        if (entry->expiry_tick > best_expiry) {
            best_expiry = entry->expiry_tick;
        }
    }
    if (out_expiry) {
        *out_expiry = best_expiry;
    }
    return best_strength;
}

void dom_interest_state_init(dom_interest_state* states, u32 state_count)
{
    u32 i;
    if (!states) {
        return;
    }
    for (i = 0u; i < state_count; ++i) {
        states[i].state = DOM_REL_LATENT;
        states[i].last_change_tick = 0;
    }
}

static dom_relevance_state dom_interest_desired_state(u32 strength, const dom_interest_policy* policy)
{
    if (!policy) {
        if (strength > 0u) {
            return DOM_REL_COLD;
        }
        return DOM_REL_LATENT;
    }
    if (strength >= policy->enter_hot) {
        return DOM_REL_HOT;
    }
    if (strength >= policy->enter_warm) {
        return DOM_REL_WARM;
    }
    if (strength > 0u) {
        return DOM_REL_COLD;
    }
    return DOM_REL_LATENT;
}

static dom_relevance_state dom_interest_apply_hysteresis(dom_relevance_state current,
                                                        u32 strength,
                                                        const dom_interest_policy* policy)
{
    if (!policy) {
        return dom_interest_desired_state(strength, policy);
    }
    if (current == DOM_REL_HOT) {
        if (strength >= policy->exit_hot) {
            return DOM_REL_HOT;
        }
        if (strength >= policy->enter_warm) {
            return DOM_REL_WARM;
        }
        return (strength > 0u) ? DOM_REL_COLD : DOM_REL_LATENT;
    }
    if (current == DOM_REL_WARM) {
        if (strength >= policy->exit_warm) {
            return DOM_REL_WARM;
        }
        return (strength > 0u) ? DOM_REL_COLD : DOM_REL_LATENT;
    }
    return dom_interest_desired_state(strength, policy);
}

u32 dom_interest_state_apply(const dom_interest_set* set,
                             dom_interest_state* states,
                             u32 state_count,
                             const dom_interest_policy* policy,
                             dom_act_time_t now_tick,
                             dom_interest_transition* out_transitions,
                             u32* in_out_count)
{
    u32 i;
    u32 written = 0u;
    u32 max_out = in_out_count ? *in_out_count : 0u;
    dom_interest_policy local_policy;

    if (!states || state_count == 0u) {
        return 0u;
    }

    if (!policy) {
        local_policy.enter_warm = DOM_INTEREST_STRENGTH_LOW;
        local_policy.exit_warm = 0u;
        local_policy.enter_hot = DOM_INTEREST_STRENGTH_HIGH;
        local_policy.exit_hot = DOM_INTEREST_STRENGTH_MED;
        local_policy.min_dwell_ticks = 0;
        policy = &local_policy;
    }

    for (i = 0u; i < state_count; ++i) {
        dom_interest_state* state = &states[i];
        dom_relevance_state desired;
        u32 strength = dom_interest_set_strength(set, state->target_kind, state->target_id, now_tick, NULL);
        desired = dom_interest_apply_hysteresis(state->state, strength, policy);

        if (desired != state->state) {
            dom_act_time_t elapsed = now_tick - state->last_change_tick;
            if (elapsed < 0) {
                elapsed = 0;
            }
            if (elapsed < policy->min_dwell_ticks) {
                continue;
            }
            if (out_transitions && written < max_out) {
                out_transitions[written].target_id = state->target_id;
                out_transitions[written].target_kind = state->target_kind;
                out_transitions[written].from_state = state->state;
                out_transitions[written].to_state = desired;
            }
            written += 1u;
            state->state = desired;
            state->last_change_tick = now_tick;
        }
    }

    if (in_out_count) {
        *in_out_count = written > max_out ? max_out : written;
    }
    return written;
}
