/*
FILE: source/domino/struct/model/dg_struct_enclosure.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / struct/model/dg_struct_enclosure
RESPONSIBILITY: Implements `dg_struct_enclosure`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
/* STRUCT enclosure authoring model (C89). */
#include "struct/model/dg_struct_enclosure.h"

#include <stdlib.h>
#include <string.h>

void dg_struct_enclosure_init(dg_struct_enclosure *e) {
    if (!e) return;
    memset(e, 0, sizeof(*e));
}

void dg_struct_enclosure_free(dg_struct_enclosure *e) {
    if (!e) return;
    if (e->volume_ids) free(e->volume_ids);
    if (e->apertures) free(e->apertures);
    dg_struct_enclosure_init(e);
}

int dg_struct_enclosure_reserve_volumes(dg_struct_enclosure *e, u32 capacity) {
    dg_struct_volume_id *arr;
    u32 new_cap;
    if (!e) return -1;
    if (capacity <= e->volume_capacity) return 0;
    new_cap = e->volume_capacity ? e->volume_capacity : 4u;
    while (new_cap < capacity) {
        if (new_cap > 0x7FFFFFFFu) {
            new_cap = capacity;
            break;
        }
        new_cap *= 2u;
    }
    arr = (dg_struct_volume_id *)realloc(e->volume_ids, sizeof(dg_struct_volume_id) * (size_t)new_cap);
    if (!arr) return -2;
    e->volume_ids = arr;
    e->volume_capacity = new_cap;
    return 0;
}

static u32 dg_struct_enclosure_volume_lower_bound(const dg_struct_enclosure *e, dg_struct_volume_id volume_id) {
    u32 lo = 0u;
    u32 hi;
    u32 mid;
    if (!e) return 0u;
    hi = e->volume_count;
    while (lo < hi) {
        mid = lo + ((hi - lo) / 2u);
        if (e->volume_ids[mid] >= volume_id) {
            hi = mid;
        } else {
            lo = mid + 1u;
        }
    }
    return lo;
}

int dg_struct_enclosure_add_volume(dg_struct_enclosure *e, dg_struct_volume_id volume_id) {
    u32 idx;
    if (!e) return -1;
    if (volume_id == 0u) return -2;
    idx = dg_struct_enclosure_volume_lower_bound(e, volume_id);
    if (idx < e->volume_count && e->volume_ids[idx] == volume_id) {
        return 0;
    }
    if (dg_struct_enclosure_reserve_volumes(e, e->volume_count + 1u) != 0) {
        return -3;
    }
    if (idx < e->volume_count) {
        memmove(&e->volume_ids[idx + 1u], &e->volume_ids[idx], sizeof(dg_struct_volume_id) * (size_t)(e->volume_count - idx));
    }
    e->volume_ids[idx] = volume_id;
    e->volume_count += 1u;
    return 0;
}

int dg_struct_enclosure_reserve_apertures(dg_struct_enclosure *e, u32 capacity) {
    dg_struct_aperture *arr;
    u32 new_cap;
    if (!e) return -1;
    if (capacity <= e->aperture_capacity) return 0;
    new_cap = e->aperture_capacity ? e->aperture_capacity : 4u;
    while (new_cap < capacity) {
        if (new_cap > 0x7FFFFFFFu) {
            new_cap = capacity;
            break;
        }
        new_cap *= 2u;
    }
    arr = (dg_struct_aperture *)realloc(e->apertures, sizeof(dg_struct_aperture) * (size_t)new_cap);
    if (!arr) return -2;
    if (new_cap > e->aperture_capacity) {
        memset(&arr[e->aperture_capacity], 0, sizeof(dg_struct_aperture) * (size_t)(new_cap - e->aperture_capacity));
    }
    e->apertures = arr;
    e->aperture_capacity = new_cap;
    return 0;
}

static u32 dg_struct_enclosure_aperture_lower_bound(const dg_struct_enclosure *e, u64 aperture_id) {
    u32 lo = 0u;
    u32 hi;
    u32 mid;
    if (!e) return 0u;
    hi = e->aperture_count;
    while (lo < hi) {
        mid = lo + ((hi - lo) / 2u);
        if (e->apertures[mid].aperture_id >= aperture_id) {
            hi = mid;
        } else {
            lo = mid + 1u;
        }
    }
    return lo;
}

int dg_struct_enclosure_set_aperture(dg_struct_enclosure *e, const dg_struct_aperture *ap) {
    u32 idx;
    dg_struct_aperture tmp;
    if (!e || !ap) return -1;
    if (ap->aperture_id == 0u) return -2;
    idx = dg_struct_enclosure_aperture_lower_bound(e, ap->aperture_id);
    if (idx < e->aperture_count && e->apertures[idx].aperture_id == ap->aperture_id) {
        e->apertures[idx].to_enclosure_id = ap->to_enclosure_id;
        e->apertures[idx].kind = ap->kind;
        return 0;
    }
    if (dg_struct_enclosure_reserve_apertures(e, e->aperture_count + 1u) != 0) {
        return -3;
    }
    if (idx < e->aperture_count) {
        memmove(&e->apertures[idx + 1u], &e->apertures[idx], sizeof(dg_struct_aperture) * (size_t)(e->aperture_count - idx));
    }
    memset(&tmp, 0, sizeof(tmp));
    tmp.aperture_id = ap->aperture_id;
    tmp.to_enclosure_id = ap->to_enclosure_id;
    tmp.kind = ap->kind;
    e->apertures[idx] = tmp;
    e->aperture_count += 1u;
    return 0;
}

int dg_struct_enclosure_validate(const dg_struct_enclosure *e) {
    u32 i;
    if (!e) return -1;
    if (e->id == 0u) return -2;
    if (e->volume_count == 0u) return -3;
    for (i = 0u; i < e->volume_count; ++i) {
        if (e->volume_ids[i] == 0u) return -4;
        if (i > 0u && e->volume_ids[i - 1u] >= e->volume_ids[i]) return -5;
    }
    for (i = 0u; i < e->aperture_count; ++i) {
        if (e->apertures[i].aperture_id == 0u) return -6;
        if (i > 0u && e->apertures[i - 1u].aperture_id >= e->apertures[i].aperture_id) return -7;
    }
    return 0;
}

