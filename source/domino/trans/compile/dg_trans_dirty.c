/* TRANS incremental dirty tracking (C89). */
#include "trans/compile/dg_trans_dirty.h"

#include <stdlib.h>
#include <string.h>

#include "core/det_invariants.h"

static u32 dg_trans_dirty_alignment_lower_bound(const dg_trans_dirty *d, dg_trans_alignment_id id) {
    u32 lo = 0u;
    u32 hi;
    u32 mid;
    if (!d) return 0u;
    hi = d->alignment_count;
    while (lo < hi) {
        mid = lo + ((hi - lo) / 2u);
        if (d->alignments[mid].alignment_id >= id) {
            hi = mid;
        } else {
            lo = mid + 1u;
        }
    }
    return lo;
}

static u32 dg_trans_dirty_junction_lower_bound(const dg_trans_dirty *d, dg_trans_junction_id id) {
    u32 lo = 0u;
    u32 hi;
    u32 mid;
    if (!d) return 0u;
    hi = d->junction_count;
    while (lo < hi) {
        mid = lo + ((hi - lo) / 2u);
        if (d->junctions[mid].junction_id >= id) {
            hi = mid;
        } else {
            lo = mid + 1u;
        }
    }
    return lo;
}

void dg_trans_dirty_init(dg_trans_dirty *d) {
    if (!d) return;
    memset(d, 0, sizeof(*d));
}

void dg_trans_dirty_free(dg_trans_dirty *d) {
    if (!d) return;
    if (d->alignments) free(d->alignments);
    if (d->junctions) free(d->junctions);
    dg_trans_dirty_init(d);
}

void dg_trans_dirty_clear(dg_trans_dirty *d) {
    if (!d) return;
    d->alignment_count = 0u;
    d->junction_count = 0u;
}

int dg_trans_dirty_reserve_alignments(dg_trans_dirty *d, u32 capacity) {
    dg_trans_dirty_alignment *a;
    u32 new_cap;
    if (!d) return -1;
    if (capacity <= d->alignment_capacity) return 0;
    new_cap = d->alignment_capacity ? d->alignment_capacity : 8u;
    while (new_cap < capacity) {
        if (new_cap > 0x7FFFFFFFu) {
            new_cap = capacity;
            break;
        }
        new_cap *= 2u;
    }
    a = (dg_trans_dirty_alignment *)realloc(d->alignments, sizeof(dg_trans_dirty_alignment) * (size_t)new_cap);
    if (!a) return -2;
    if (new_cap > d->alignment_capacity) {
        memset(&a[d->alignment_capacity], 0, sizeof(dg_trans_dirty_alignment) * (size_t)(new_cap - d->alignment_capacity));
    }
    d->alignments = a;
    d->alignment_capacity = new_cap;
    return 0;
}

int dg_trans_dirty_reserve_junctions(dg_trans_dirty *d, u32 capacity) {
    dg_trans_dirty_junction *j;
    u32 new_cap;
    if (!d) return -1;
    if (capacity <= d->junction_capacity) return 0;
    new_cap = d->junction_capacity ? d->junction_capacity : 8u;
    while (new_cap < capacity) {
        if (new_cap > 0x7FFFFFFFu) {
            new_cap = capacity;
            break;
        }
        new_cap *= 2u;
    }
    j = (dg_trans_dirty_junction *)realloc(d->junctions, sizeof(dg_trans_dirty_junction) * (size_t)new_cap);
    if (!j) return -2;
    if (new_cap > d->junction_capacity) {
        memset(&j[d->junction_capacity], 0, sizeof(dg_trans_dirty_junction) * (size_t)(new_cap - d->junction_capacity));
    }
    d->junctions = j;
    d->junction_capacity = new_cap;
    return 0;
}

static void dg_trans_dirty_range_merge(dg_trans_dirty_range *r, dg_q s0, dg_q s1) {
    dg_q lo;
    dg_q hi;
    if (!r) return;
    lo = s0;
    hi = s1;
    if (hi < lo) {
        dg_q t = lo;
        lo = hi;
        hi = t;
    }
    if (!r->dirty) {
        r->dirty = D_TRUE;
        r->s0 = lo;
        r->s1 = hi;
        return;
    }
    if (lo < r->s0) r->s0 = lo;
    if (hi > r->s1) r->s1 = hi;
}

static dg_trans_dirty_alignment *dg_trans_dirty_get_or_add_alignment(dg_trans_dirty *d, dg_trans_alignment_id alignment_id) {
    u32 idx;
    if (!d || alignment_id == 0u) return (dg_trans_dirty_alignment *)0;
    idx = dg_trans_dirty_alignment_lower_bound(d, alignment_id);
    if (idx < d->alignment_count && d->alignments[idx].alignment_id == alignment_id) {
        return &d->alignments[idx];
    }
    if (dg_trans_dirty_reserve_alignments(d, d->alignment_count + 1u) != 0) {
        return (dg_trans_dirty_alignment *)0;
    }
    if (idx < d->alignment_count) {
        memmove(&d->alignments[idx + 1u], &d->alignments[idx],
                sizeof(dg_trans_dirty_alignment) * (size_t)(d->alignment_count - idx));
    }
    memset(&d->alignments[idx], 0, sizeof(d->alignments[idx]));
    d->alignments[idx].alignment_id = alignment_id;
    d->alignment_count += 1u;
    return &d->alignments[idx];
}

static dg_trans_dirty_junction *dg_trans_dirty_get_or_add_junction(dg_trans_dirty *d, dg_trans_junction_id junction_id) {
    u32 idx;
    if (!d || junction_id == 0u) return (dg_trans_dirty_junction *)0;
    idx = dg_trans_dirty_junction_lower_bound(d, junction_id);
    if (idx < d->junction_count && d->junctions[idx].junction_id == junction_id) {
        return &d->junctions[idx];
    }
    if (dg_trans_dirty_reserve_junctions(d, d->junction_count + 1u) != 0) {
        return (dg_trans_dirty_junction *)0;
    }
    if (idx < d->junction_count) {
        memmove(&d->junctions[idx + 1u], &d->junctions[idx],
                sizeof(dg_trans_dirty_junction) * (size_t)(d->junction_count - idx));
    }
    memset(&d->junctions[idx], 0, sizeof(d->junctions[idx]));
    d->junctions[idx].junction_id = junction_id;
    d->junction_count += 1u;
    return &d->junctions[idx];
}

void dg_trans_dirty_mark_alignment_microseg(dg_trans_dirty *d, dg_trans_alignment_id alignment_id, dg_q s0, dg_q s1) {
    dg_trans_dirty_alignment *a = dg_trans_dirty_get_or_add_alignment(d, alignment_id);
    if (!a) return;
    dg_trans_dirty_range_merge(&a->microseg, s0, s1);
}

void dg_trans_dirty_mark_alignment_slotmap(dg_trans_dirty *d, dg_trans_alignment_id alignment_id, dg_q s0, dg_q s1) {
    dg_trans_dirty_alignment *a = dg_trans_dirty_get_or_add_alignment(d, alignment_id);
    if (!a) return;
    dg_trans_dirty_range_merge(&a->slotmap, s0, s1);
}

void dg_trans_dirty_mark_junction(dg_trans_dirty *d, dg_trans_junction_id junction_id) {
    dg_trans_dirty_junction *j = dg_trans_dirty_get_or_add_junction(d, junction_id);
    if (!j) return;
    j->dirty = D_TRUE;
}

int dg_trans_dirty_get_alignment(const dg_trans_dirty *d, dg_trans_alignment_id alignment_id, dg_trans_dirty_alignment *out) {
    u32 idx;
    if (!out) return 0;
    memset(out, 0, sizeof(*out));
    if (!d || alignment_id == 0u) return 0;
    idx = dg_trans_dirty_alignment_lower_bound(d, alignment_id);
    if (idx < d->alignment_count && d->alignments[idx].alignment_id == alignment_id) {
        *out = d->alignments[idx];
        return 1;
    }
    return 0;
}

int dg_trans_dirty_get_junction(const dg_trans_dirty *d, dg_trans_junction_id junction_id, dg_trans_dirty_junction *out) {
    u32 idx;
    if (!out) return 0;
    memset(out, 0, sizeof(*out));
    if (!d || junction_id == 0u) return 0;
    idx = dg_trans_dirty_junction_lower_bound(d, junction_id);
    if (idx < d->junction_count && d->junctions[idx].junction_id == junction_id) {
        *out = d->junctions[idx];
        return 1;
    }
    return 0;
}

void dg_trans_dirty_clear_alignment(dg_trans_dirty *d, dg_trans_alignment_id alignment_id) {
    u32 idx;
    if (!d || alignment_id == 0u) return;
    idx = dg_trans_dirty_alignment_lower_bound(d, alignment_id);
    if (idx < d->alignment_count && d->alignments[idx].alignment_id == alignment_id) {
        d->alignments[idx].microseg.dirty = D_FALSE;
        d->alignments[idx].slotmap.dirty = D_FALSE;
    }
}

void dg_trans_dirty_clear_junction(dg_trans_dirty *d, dg_trans_junction_id junction_id) {
    u32 idx;
    if (!d || junction_id == 0u) return;
    idx = dg_trans_dirty_junction_lower_bound(d, junction_id);
    if (idx < d->junction_count && d->junctions[idx].junction_id == junction_id) {
        d->junctions[idx].dirty = D_FALSE;
    }
}

int dg_trans_dirty_range_to_seg_span(dg_q s0, dg_q s1, dg_q microseg_max_len_q, u32 *out_seg0, u32 *out_seg1) {
    dg_q lo;
    dg_q hi;
    u64 max_len_raw;
    u64 lo_raw;
    u64 hi_raw;
    u64 hi_adj;
    u64 seg0;
    u64 seg1;

    if (!out_seg0 || !out_seg1) return -1;
    *out_seg0 = 0u;
    *out_seg1 = 0u;
    if (microseg_max_len_q <= 0) return -2;

    lo = s0;
    hi = s1;
    if (hi < lo) {
        dg_q t = lo;
        lo = hi;
        hi = t;
    }

    if (lo < 0) lo = 0;
    if (hi < 0) hi = 0;

    max_len_raw = (u64)(i64)microseg_max_len_q;
    lo_raw = (u64)(i64)lo;
    hi_raw = (u64)(i64)hi;

    if (max_len_raw == 0u) return -3;

    /* Treat dirty ranges as half-open [lo, hi) when hi>lo to avoid boundary over-marking. */
    if (hi_raw > lo_raw && hi_raw > 0u) {
        hi_adj = hi_raw - 1u;
    } else {
        hi_adj = hi_raw;
    }

    seg0 = lo_raw / max_len_raw;
    seg1 = hi_adj / max_len_raw;

    if (seg0 > 0xFFFFFFFFULL) seg0 = 0xFFFFFFFFULL;
    if (seg1 > 0xFFFFFFFFULL) seg1 = 0xFFFFFFFFULL;

    *out_seg0 = (u32)seg0;
    *out_seg1 = (u32)seg1;
    return 0;
}

