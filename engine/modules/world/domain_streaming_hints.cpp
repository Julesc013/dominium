/*
FILE: source/domino/world/domain_streaming_hints.cpp
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / world/domain_streaming_hints
RESPONSIBILITY: Non-authoritative, deterministic domain hint emission.
ALLOWED DEPENDENCIES: `include/domino/**` and C89/C++98 headers only.
FORBIDDEN DEPENDENCIES: Engine private headers outside world.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: Budgeted, stable ordering of hints.
*/
#include "domino/world/domain_streaming_hints.h"

#include <string.h>

static d_bool dom_domain_hint_active(const dom_domain_volume* volume)
{
    if (!volume) {
        return D_FALSE;
    }
    if (volume->existence_state == DOM_DOMAIN_EXISTENCE_NONEXISTENT ||
        volume->existence_state == DOM_DOMAIN_EXISTENCE_DECLARED ||
        volume->existence_state == DOM_DOMAIN_EXISTENCE_ARCHIVED) {
        return D_FALSE;
    }
    if (volume->archival_state != DOM_DOMAIN_ARCHIVAL_LIVE) {
        return D_FALSE;
    }
    return D_TRUE;
}

void dom_domain_streaming_hint_set_init(dom_domain_streaming_hint_set* set,
                                        dom_domain_streaming_hint* storage,
                                        u32 capacity)
{
    if (!set) {
        return;
    }
    set->hints = storage;
    set->count = 0u;
    set->capacity = capacity;
    set->overflow = 0u;
    if (storage && capacity > 0u) {
        memset(storage, 0, sizeof(dom_domain_streaming_hint) * (size_t)capacity);
    }
}

void dom_domain_streaming_hint_set_clear(dom_domain_streaming_hint_set* set)
{
    if (!set) {
        return;
    }
    set->count = 0u;
    set->overflow = 0u;
}

int dom_domain_streaming_hint_set_add(dom_domain_streaming_hint_set* set,
                                      const dom_domain_streaming_hint* hint)
{
    if (!set || !hint || !set->hints) {
        return -1;
    }
    if (set->count >= set->capacity) {
        set->overflow = 1u;
        return -2;
    }
    set->hints[set->count] = *hint;
    set->count += 1u;
    return 0;
}

int dom_domain_streaming_emit_hints(const dom_domain_volume* volumes,
                                    u32 volume_count,
                                    dom_domain_budget* budget,
                                    dom_domain_streaming_hint_set* out_hints)
{
    u32 i;
    if (!volumes || !out_hints) {
        return -1;
    }
    for (i = 0u; i < volume_count; ++i) {
        const dom_domain_volume* volume = &volumes[i];
        dom_domain_streaming_hint hint;
        u32 kind;
        u32 priority;
        if (!dom_domain_hint_active(volume)) {
            continue;
        }
        if (!volume->source) {
            continue;
        }

        if (volume->existence_state == DOM_DOMAIN_EXISTENCE_REFINABLE) {
            kind = DOM_DOMAIN_HINT_REFINE_SOON;
            priority = 100u;
        } else if (volume->existence_state == DOM_DOMAIN_EXISTENCE_REALIZED) {
            kind = DOM_DOMAIN_HINT_COLLAPSE_OK;
            priority = 10u;
        } else {
            continue;
        }

        if (budget && !dom_domain_budget_consume(budget, 1u)) {
            return 0;
        }

        memset(&hint, 0, sizeof(hint));
        hint.domain_id = volume->domain_id;
        hint.tile_id = 0u;
        hint.resolution = DOM_DOMAIN_RES_ANALYTIC;
        hint.bounds = volume->source->bounds;
        hint.kind = kind;
        hint.priority = priority;
        hint.flags = DOM_DOMAIN_HINT_FLAG_ADVISORY;

        if (dom_domain_streaming_hint_set_add(out_hints, &hint) != 0) {
            return -2;
        }
    }
    return 0;
}
