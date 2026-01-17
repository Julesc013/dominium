/*
FILE: game/core/dom_epistemic.c
MODULE: Dominium
LAYER / SUBSYSTEM: Dominium core / epistemic
RESPONSIBILITY: Implements deterministic Epistemic Interface Layer snapshots.
ALLOWED DEPENDENCIES: `game/include/**`, `engine/include/**` public headers, and C89 headers only.
FORBIDDEN DEPENDENCIES: engine internal headers; product-layer runtime code.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes; no exceptions.
DETERMINISM: Snapshot ordering and queries are deterministic.
*/
#include "dominium/epistemic.h"

#include <string.h>

static int dom_capability_entry_cmp(const dom_capability_entry* a,
                                    const dom_capability_entry* b)
{
    if (!a || !b) {
        return a ? 1 : (b ? -1 : 0);
    }
    if (a->capability_id < b->capability_id) return -1;
    if (a->capability_id > b->capability_id) return 1;
    if (a->subject_kind < b->subject_kind) return -1;
    if (a->subject_kind > b->subject_kind) return 1;
    if (a->subject_id < b->subject_id) return -1;
    if (a->subject_id > b->subject_id) return 1;
    return 0;
}

void dom_capability_snapshot_init(dom_capability_snapshot* snap,
                                  dom_capability_entry* storage,
                                  u32 capacity)
{
    if (!snap) {
        return;
    }
    snap->entries = storage;
    snap->count = 0u;
    snap->capacity = capacity;
    snap->snapshot_tick = 0;
    if (storage && capacity > 0u) {
        memset(storage, 0, sizeof(dom_capability_entry) * (size_t)capacity);
    }
}

void dom_capability_snapshot_clear(dom_capability_snapshot* snap)
{
    if (!snap) {
        return;
    }
    snap->count = 0u;
}

int dom_capability_snapshot_add(dom_capability_snapshot* snap,
                                const dom_capability_entry* entry)
{
    if (!snap || !entry || !snap->entries) {
        return -1;
    }
    if (entry->capability_id == 0u) {
        return -2;
    }
    if (snap->count >= snap->capacity) {
        return -3;
    }
    snap->entries[snap->count++] = *entry;
    return 0;
}

void dom_capability_snapshot_finalize(dom_capability_snapshot* snap)
{
    u32 i;
    if (!snap || !snap->entries || snap->count < 2u) {
        return;
    }
    for (i = 1u; i < snap->count; ++i) {
        dom_capability_entry key = snap->entries[i];
        u32 j = i;
        while (j > 0u && dom_capability_entry_cmp(&snap->entries[j - 1u], &key) > 0) {
            snap->entries[j] = snap->entries[j - 1u];
            --j;
        }
        snap->entries[j] = key;
    }
}

const dom_capability_entry* dom_capability_snapshot_find(
    const dom_capability_snapshot* snap,
    u32 capability_id,
    u32 subject_kind,
    u64 subject_id
) {
    u32 i;
    if (!snap || !snap->entries) {
        return (const dom_capability_entry*)0;
    }
    for (i = 0u; i < snap->count; ++i) {
        const dom_capability_entry* e = &snap->entries[i];
        if (e->capability_id == capability_id &&
            e->subject_kind == subject_kind &&
            e->subject_id == subject_id) {
            return e;
        }
    }
    return (const dom_capability_entry*)0;
}

dom_epistemic_view dom_epistemic_query(
    const dom_capability_snapshot* snap,
    u32 capability_id,
    u32 subject_kind,
    u64 subject_id,
    dom_act_time_t now_tick
) {
    dom_epistemic_view view;
    const dom_capability_entry* entry = dom_capability_snapshot_find(
        snap, capability_id, subject_kind, subject_id);

    view.state = DOM_EPI_UNKNOWN;
    view.uncertainty_q16 = 0u;
    view.observed_tick = 0;
    view.latency_ticks = 0u;
    view.is_stale = 0;
    view.is_uncertain = 0;

    if (!entry) {
        return view;
    }

    if (entry->expires_tick != DOM_EPISTEMIC_EXPIRES_NEVER &&
        entry->expires_tick <= now_tick) {
        return view;
    }

    view.state = entry->state;
    view.uncertainty_q16 = entry->uncertainty_q16;
    view.observed_tick = entry->observed_tick;
    view.latency_ticks = entry->latency_ticks;
    view.is_uncertain = (entry->uncertainty_q16 != 0u);
    if (entry->latency_ticks > 0u) {
        dom_act_time_t age = now_tick - entry->observed_tick;
        if (age > (dom_act_time_t)entry->latency_ticks) {
            view.is_stale = 1;
        }
    }
    return view;
}
