/* STRUCT incremental dirty tracking (C89). */
#include "struct/compile/dg_struct_dirty.h"

#include <stdlib.h>
#include <string.h>

static u32 dg_struct_dirty_lower_bound(const dg_struct_dirty *d, dg_struct_id struct_id) {
    u32 lo = 0u;
    u32 hi;
    u32 mid;
    if (!d) return 0u;
    hi = d->count;
    while (lo < hi) {
        mid = lo + ((hi - lo) / 2u);
        if (d->items[mid].struct_id >= struct_id) {
            hi = mid;
        } else {
            lo = mid + 1u;
        }
    }
    return lo;
}

void dg_struct_dirty_init(dg_struct_dirty *d) {
    if (!d) return;
    memset(d, 0, sizeof(*d));
}

void dg_struct_dirty_free(dg_struct_dirty *d) {
    if (!d) return;
    if (d->items) free(d->items);
    dg_struct_dirty_init(d);
}

void dg_struct_dirty_clear(dg_struct_dirty *d) {
    if (!d) return;
    d->count = 0u;
}

int dg_struct_dirty_reserve(dg_struct_dirty *d, u32 capacity) {
    dg_struct_dirty_record *arr;
    u32 new_cap;
    if (!d) return -1;
    if (capacity <= d->capacity) return 0;
    new_cap = d->capacity ? d->capacity : 8u;
    while (new_cap < capacity) {
        if (new_cap > 0x7FFFFFFFu) {
            new_cap = capacity;
            break;
        }
        new_cap *= 2u;
    }
    arr = (dg_struct_dirty_record *)realloc(d->items, sizeof(dg_struct_dirty_record) * (size_t)new_cap);
    if (!arr) return -2;
    if (new_cap > d->capacity) {
        memset(&arr[d->capacity], 0, sizeof(dg_struct_dirty_record) * (size_t)(new_cap - d->capacity));
    }
    d->items = arr;
    d->capacity = new_cap;
    return 0;
}

static dg_struct_dirty_record *dg_struct_dirty_get_or_add(dg_struct_dirty *d, dg_struct_id struct_id) {
    u32 idx;
    if (!d || struct_id == 0u) return (dg_struct_dirty_record *)0;
    idx = dg_struct_dirty_lower_bound(d, struct_id);
    if (idx < d->count && d->items[idx].struct_id == struct_id) {
        return &d->items[idx];
    }
    if (dg_struct_dirty_reserve(d, d->count + 1u) != 0) {
        return (dg_struct_dirty_record *)0;
    }
    if (idx < d->count) {
        memmove(&d->items[idx + 1u], &d->items[idx],
                sizeof(dg_struct_dirty_record) * (size_t)(d->count - idx));
    }
    memset(&d->items[idx], 0, sizeof(d->items[idx]));
    d->items[idx].struct_id = struct_id;
    d->count += 1u;
    return &d->items[idx];
}

static u32 dg_struct_dirty_expand_flags(u32 flags) {
    u32 out = flags;
    /* Dependency expansion is deterministic and conservative:
     * - footprint changes affect volume-derived artifacts and indices
     * - volume changes affect occupancy, surfaces, supports, and room bboxes
     * - enclosure changes affect enclosure graph and interior-facing surfaces
     */
    if (flags & DG_STRUCT_DIRTY_FOOTPRINT) {
        out |= (DG_STRUCT_DIRTY_VOLUME | DG_STRUCT_DIRTY_ENCLOSURE | DG_STRUCT_DIRTY_SURFACE | DG_STRUCT_DIRTY_SUPPORT);
    }
    if (flags & DG_STRUCT_DIRTY_VOLUME) {
        out |= (DG_STRUCT_DIRTY_ENCLOSURE | DG_STRUCT_DIRTY_SURFACE | DG_STRUCT_DIRTY_SUPPORT);
    }
    if (flags & DG_STRUCT_DIRTY_ENCLOSURE) {
        out |= DG_STRUCT_DIRTY_SURFACE;
    }
    return out;
}

static void dg_struct_dirty_chunk_merge(
    dg_struct_dirty_chunk_aabb *a,
    i32 cx0, i32 cy0, i32 cz0,
    i32 cx1, i32 cy1, i32 cz1
) {
    i32 t;
    if (!a) return;
    if (cx1 < cx0) { t = cx0; cx0 = cx1; cx1 = t; }
    if (cy1 < cy0) { t = cy0; cy0 = cy1; cy1 = t; }
    if (cz1 < cz0) { t = cz0; cz0 = cz1; cz1 = t; }
    if (!a->dirty) {
        a->dirty = D_TRUE;
        a->cx0 = cx0; a->cy0 = cy0; a->cz0 = cz0;
        a->cx1 = cx1; a->cy1 = cy1; a->cz1 = cz1;
        return;
    }
    if (cx0 < a->cx0) a->cx0 = cx0;
    if (cy0 < a->cy0) a->cy0 = cy0;
    if (cz0 < a->cz0) a->cz0 = cz0;
    if (cx1 > a->cx1) a->cx1 = cx1;
    if (cy1 > a->cy1) a->cy1 = cy1;
    if (cz1 > a->cz1) a->cz1 = cz1;
}

void dg_struct_dirty_mark(dg_struct_dirty *d, dg_struct_id struct_id, u32 dirty_flags) {
    dg_struct_dirty_record *r;
    if (!d || struct_id == 0u) return;
    if (dirty_flags == 0u) return;
    dirty_flags = dg_struct_dirty_expand_flags(dirty_flags);
    r = dg_struct_dirty_get_or_add(d, struct_id);
    if (!r) return;
    r->dirty_flags |= dirty_flags;
}

void dg_struct_dirty_mark_chunks(
    dg_struct_dirty *d,
    dg_struct_id     struct_id,
    u32             dirty_flags,
    i32              cx0, i32 cy0, i32 cz0,
    i32              cx1, i32 cy1, i32 cz1
) {
    dg_struct_dirty_record *r;
    if (!d || struct_id == 0u) return;
    if (dirty_flags == 0u) return;
    dirty_flags = dg_struct_dirty_expand_flags(dirty_flags);
    r = dg_struct_dirty_get_or_add(d, struct_id);
    if (!r) return;
    r->dirty_flags |= dirty_flags;
    dg_struct_dirty_chunk_merge(&r->chunks, cx0, cy0, cz0, cx1, cy1, cz1);
}

int dg_struct_dirty_get(const dg_struct_dirty *d, dg_struct_id struct_id, dg_struct_dirty_record *out) {
    u32 idx;
    if (!out) return 0;
    memset(out, 0, sizeof(*out));
    if (!d || struct_id == 0u) return 0;
    idx = dg_struct_dirty_lower_bound(d, struct_id);
    if (idx < d->count && d->items[idx].struct_id == struct_id) {
        *out = d->items[idx];
        return 1;
    }
    return 0;
}

void dg_struct_dirty_clear_flags(dg_struct_dirty *d, dg_struct_id struct_id, u32 clear_mask) {
    u32 idx;
    if (!d || struct_id == 0u) return;
    idx = dg_struct_dirty_lower_bound(d, struct_id);
    if (idx < d->count && d->items[idx].struct_id == struct_id) {
        d->items[idx].dirty_flags &= ~clear_mask;
        if (d->items[idx].dirty_flags == 0u) {
            d->items[idx].chunks.dirty = D_FALSE;
        }
    }
}
