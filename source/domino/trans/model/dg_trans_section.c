/*
FILE: source/domino/trans/model/dg_trans_section.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / trans/model/dg_trans_section
RESPONSIBILITY: Implements `dg_trans_section`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
/* TRANS cross-section archetypes (slot packing) (C89). */
#include "trans/model/dg_trans_section.h"

#include <stdlib.h>
#include <string.h>

#include "core/det_invariants.h"

static void dg_trans_slot_free_fields(dg_trans_slot *slot) {
    if (!slot) return;
    if (slot->allowed_types) {
        free(slot->allowed_types);
    }
    slot->allowed_types = (dg_trans_occupant_type_id *)0;
    slot->allowed_type_count = 0u;
    slot->allowed_type_capacity = 0u;
}

void dg_trans_section_init(dg_trans_section_archetype *sec) {
    if (!sec) return;
    memset(sec, 0, sizeof(*sec));
}

void dg_trans_section_free(dg_trans_section_archetype *sec) {
    u32 i;
    if (!sec) return;
    if (sec->slots) {
        for (i = 0u; i < sec->slot_count; ++i) {
            dg_trans_slot_free_fields(&sec->slots[i]);
        }
        free(sec->slots);
    }
    dg_trans_section_init(sec);
}

int dg_trans_section_reserve_slots(dg_trans_section_archetype *sec, u32 capacity) {
    dg_trans_slot *new_slots;
    u32 new_cap;
    if (!sec) return -1;
    if (capacity <= sec->slot_capacity) return 0;
    new_cap = sec->slot_capacity ? sec->slot_capacity : 8u;
    while (new_cap < capacity) {
        if (new_cap > 0x7FFFFFFFu) {
            new_cap = capacity;
            break;
        }
        new_cap *= 2u;
    }
    new_slots = (dg_trans_slot *)realloc(sec->slots, sizeof(dg_trans_slot) * (size_t)new_cap);
    if (!new_slots) return -2;
    if (new_cap > sec->slot_capacity) {
        memset(&new_slots[sec->slot_capacity], 0, sizeof(dg_trans_slot) * (size_t)(new_cap - sec->slot_capacity));
    }
    sec->slots = new_slots;
    sec->slot_capacity = new_cap;
    return 0;
}

static u32 dg_trans_section_slot_lower_bound(const dg_trans_section_archetype *sec, dg_trans_slot_id slot_id) {
    u32 lo = 0u;
    u32 hi;
    u32 mid;
    if (!sec) return 0u;
    hi = sec->slot_count;
    while (lo < hi) {
        mid = lo + ((hi - lo) / 2u);
        if (sec->slots[mid].slot_id >= slot_id) {
            hi = mid;
        } else {
            lo = mid + 1u;
        }
    }
    return lo;
}

static void dg_trans_sort_u64_insertion(u64 *v, u32 count) {
    u32 i;
    if (!v || count < 2u) return;
    for (i = 1u; i < count; ++i) {
        u64 key = v[i];
        u32 j = i;
        while (j > 0u && v[j - 1u] > key) {
            v[j] = v[j - 1u];
            j -= 1u;
        }
        v[j] = key;
    }
}

int dg_trans_section_slot_set_allowed_types(dg_trans_slot *slot, const dg_trans_occupant_type_id *types, u32 type_count) {
    dg_trans_occupant_type_id *buf;
    u32 i;
    u32 out_count;
    if (!slot) return -1;

    dg_trans_slot_free_fields(slot);
    if (!types || type_count == 0u) {
        return 0;
    }

    buf = (dg_trans_occupant_type_id *)malloc(sizeof(dg_trans_occupant_type_id) * (size_t)type_count);
    if (!buf) return -2;
    for (i = 0u; i < type_count; ++i) {
        buf[i] = types[i];
    }
    dg_trans_sort_u64_insertion((u64 *)buf, type_count);

    /* Dedup in place. */
    out_count = 0u;
    for (i = 0u; i < type_count; ++i) {
        if (i == 0u || buf[i] != buf[i - 1u]) {
            buf[out_count++] = buf[i];
        }
    }

    if (out_count == 0u) {
        free(buf);
        return 0;
    }

    slot->allowed_types = buf;
    slot->allowed_type_count = out_count;
    slot->allowed_type_capacity = out_count;
    return 0;
}

int dg_trans_section_set_slot(dg_trans_section_archetype *sec, const dg_trans_slot *slot) {
    u32 idx;
    dg_trans_slot tmp;
    if (!sec || !slot) return -1;
    if (slot->slot_id == 0u) return -2;

    idx = dg_trans_section_slot_lower_bound(sec, slot->slot_id);
    if (idx < sec->slot_count && sec->slots[idx].slot_id == slot->slot_id) {
        /* Update in place (free old allowed list first). */
        dg_trans_slot_free_fields(&sec->slots[idx]);
        sec->slots[idx].offset_t = slot->offset_t;
        sec->slots[idx].offset_h = slot->offset_h;
        sec->slots[idx].width = slot->width;
        sec->slots[idx].height = slot->height;
        sec->slots[idx].rail_id = slot->rail_id;
        return dg_trans_section_slot_set_allowed_types(&sec->slots[idx], slot->allowed_types, slot->allowed_type_count);
    }

    if (dg_trans_section_reserve_slots(sec, sec->slot_count + 1u) != 0) {
        return -3;
    }

    if (idx < sec->slot_count) {
        memmove(&sec->slots[idx + 1u], &sec->slots[idx], sizeof(dg_trans_slot) * (size_t)(sec->slot_count - idx));
    }

    memset(&tmp, 0, sizeof(tmp));
    tmp.slot_id = slot->slot_id;
    tmp.offset_t = slot->offset_t;
    tmp.offset_h = slot->offset_h;
    tmp.width = slot->width;
    tmp.height = slot->height;
    tmp.rail_id = slot->rail_id;
    sec->slots[idx] = tmp;
    sec->slot_count += 1u;

    return dg_trans_section_slot_set_allowed_types(&sec->slots[idx], slot->allowed_types, slot->allowed_type_count);
}

dg_trans_slot *dg_trans_section_find_slot(dg_trans_section_archetype *sec, dg_trans_slot_id slot_id) {
    u32 idx;
    if (!sec || slot_id == 0u) return (dg_trans_slot *)0;
    idx = dg_trans_section_slot_lower_bound(sec, slot_id);
    if (idx < sec->slot_count && sec->slots[idx].slot_id == slot_id) {
        return &sec->slots[idx];
    }
    return (dg_trans_slot *)0;
}

const dg_trans_slot *dg_trans_section_find_slot_const(const dg_trans_section_archetype *sec, dg_trans_slot_id slot_id) {
    u32 idx;
    if (!sec || slot_id == 0u) return (const dg_trans_slot *)0;
    idx = dg_trans_section_slot_lower_bound(sec, slot_id);
    if (idx < sec->slot_count && sec->slots[idx].slot_id == slot_id) {
        return &sec->slots[idx];
    }
    return (const dg_trans_slot *)0;
}

int dg_trans_slot_allows_type(const dg_trans_slot *slot, dg_trans_occupant_type_id occupant_type_id) {
    u32 lo;
    u32 hi;
    u32 mid;
    if (!slot) return 0;
    if (slot->allowed_type_count == 0u) {
        /* Empty list means "no restriction" (caller-defined). */
        return 1;
    }
    lo = 0u;
    hi = slot->allowed_type_count;
    while (lo < hi) {
        mid = lo + ((hi - lo) / 2u);
        if (slot->allowed_types[mid] >= occupant_type_id) {
            hi = mid;
        } else {
            lo = mid + 1u;
        }
    }
    if (lo < slot->allowed_type_count && slot->allowed_types[lo] == occupant_type_id) {
        return 1;
    }
    return 0;
}

