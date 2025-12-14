/* STRUCT footprint authoring model (C89). */
#include "struct/model/dg_struct_footprint.h"

#include <stdlib.h>
#include <string.h>

#include "core/det_invariants.h"

static void dg_struct_footprint_ring_free_fields(dg_struct_footprint_ring *r) {
    if (!r) return;
    if (r->verts) free(r->verts);
    r->verts = (dg_struct_footprint_vertex *)0;
    r->vert_count = 0u;
    r->vert_capacity = 0u;
}

void dg_struct_footprint_init(dg_struct_footprint *fp) {
    if (!fp) return;
    memset(fp, 0, sizeof(*fp));
}

void dg_struct_footprint_free(dg_struct_footprint *fp) {
    u32 i;
    if (!fp) return;
    if (fp->rings) {
        for (i = 0u; i < fp->ring_count; ++i) {
            dg_struct_footprint_ring_free_fields(&fp->rings[i]);
        }
        free(fp->rings);
    }
    dg_struct_footprint_init(fp);
}

int dg_struct_footprint_reserve_rings(dg_struct_footprint *fp, u32 capacity) {
    dg_struct_footprint_ring *arr;
    u32 new_cap;
    if (!fp) return -1;
    if (capacity <= fp->ring_capacity) return 0;
    new_cap = fp->ring_capacity ? fp->ring_capacity : 4u;
    while (new_cap < capacity) {
        if (new_cap > 0x7FFFFFFFu) {
            new_cap = capacity;
            break;
        }
        new_cap *= 2u;
    }
    arr = (dg_struct_footprint_ring *)realloc(fp->rings, sizeof(dg_struct_footprint_ring) * (size_t)new_cap);
    if (!arr) return -2;
    if (new_cap > fp->ring_capacity) {
        memset(&arr[fp->ring_capacity], 0, sizeof(dg_struct_footprint_ring) * (size_t)(new_cap - fp->ring_capacity));
    }
    fp->rings = arr;
    fp->ring_capacity = new_cap;
    return 0;
}

static u32 dg_struct_footprint_ring_lower_bound(const dg_struct_footprint *fp, u32 ring_index) {
    u32 lo = 0u;
    u32 hi;
    u32 mid;
    if (!fp) return 0u;
    hi = fp->ring_count;
    while (lo < hi) {
        mid = lo + ((hi - lo) / 2u);
        if (fp->rings[mid].ring_index >= ring_index) {
            hi = mid;
        } else {
            lo = mid + 1u;
        }
    }
    return lo;
}

static dg_struct_footprint_ring *dg_struct_footprint_get_or_add_ring(dg_struct_footprint *fp, u32 ring_index) {
    u32 idx;
    if (!fp) return (dg_struct_footprint_ring *)0;

    idx = dg_struct_footprint_ring_lower_bound(fp, ring_index);
    if (idx < fp->ring_count && fp->rings[idx].ring_index == ring_index) {
        return &fp->rings[idx];
    }

    if (dg_struct_footprint_reserve_rings(fp, fp->ring_count + 1u) != 0) {
        return (dg_struct_footprint_ring *)0;
    }

    if (idx < fp->ring_count) {
        memmove(&fp->rings[idx + 1u], &fp->rings[idx],
                sizeof(dg_struct_footprint_ring) * (size_t)(fp->ring_count - idx));
    }
    memset(&fp->rings[idx], 0, sizeof(fp->rings[idx]));
    fp->rings[idx].ring_index = ring_index;
    fp->rings[idx].is_hole = (ring_index == 0u) ? D_FALSE : D_TRUE;
    fp->ring_count += 1u;
    return &fp->rings[idx];
}

int dg_struct_footprint_set_ring(dg_struct_footprint *fp, u32 ring_index, d_bool is_hole) {
    dg_struct_footprint_ring *r;
    if (!fp) return -1;
    r = dg_struct_footprint_get_or_add_ring(fp, ring_index);
    if (!r) return -2;
    r->is_hole = is_hole ? D_TRUE : D_FALSE;
    return 0;
}

int dg_struct_footprint_reserve_ring_verts(dg_struct_footprint *fp, u32 ring_index, u32 capacity) {
    dg_struct_footprint_ring *r;
    dg_struct_footprint_vertex *arr;
    u32 new_cap;
    if (!fp) return -1;
    r = dg_struct_footprint_get_or_add_ring(fp, ring_index);
    if (!r) return -2;
    if (capacity <= r->vert_capacity) return 0;
    new_cap = r->vert_capacity ? r->vert_capacity : 8u;
    while (new_cap < capacity) {
        if (new_cap > 0x7FFFFFFFu) {
            new_cap = capacity;
            break;
        }
        new_cap *= 2u;
    }
    arr = (dg_struct_footprint_vertex *)realloc(r->verts, sizeof(dg_struct_footprint_vertex) * (size_t)new_cap);
    if (!arr) return -3;
    if (new_cap > r->vert_capacity) {
        memset(&arr[r->vert_capacity], 0, sizeof(dg_struct_footprint_vertex) * (size_t)(new_cap - r->vert_capacity));
    }
    r->verts = arr;
    r->vert_capacity = new_cap;
    return 0;
}

static u32 dg_struct_footprint_vertex_lower_bound(const dg_struct_footprint_ring *r, u32 vertex_index) {
    u32 lo = 0u;
    u32 hi;
    u32 mid;
    if (!r) return 0u;
    hi = r->vert_count;
    while (lo < hi) {
        mid = lo + ((hi - lo) / 2u);
        if (r->verts[mid].vertex_index >= vertex_index) {
            hi = mid;
        } else {
            lo = mid + 1u;
        }
    }
    return lo;
}

int dg_struct_footprint_set_vertex(dg_struct_footprint *fp, u32 ring_index, u32 vertex_index, dg_q x, dg_q y) {
    dg_struct_footprint_ring *r;
    u32 idx;
    dg_struct_footprint_vertex tmp;
    if (!fp) return -1;

    r = dg_struct_footprint_get_or_add_ring(fp, ring_index);
    if (!r) return -2;

    idx = dg_struct_footprint_vertex_lower_bound(r, vertex_index);
    if (idx < r->vert_count && r->verts[idx].vertex_index == vertex_index) {
        r->verts[idx].x = x;
        r->verts[idx].y = y;
        return 0;
    }

    if (dg_struct_footprint_reserve_ring_verts(fp, ring_index, r->vert_count + 1u) != 0) {
        return -3;
    }

    if (idx < r->vert_count) {
        memmove(&r->verts[idx + 1u], &r->verts[idx],
                sizeof(dg_struct_footprint_vertex) * (size_t)(r->vert_count - idx));
    }

    memset(&tmp, 0, sizeof(tmp));
    tmp.vertex_index = vertex_index;
    tmp.x = x;
    tmp.y = y;
    r->verts[idx] = tmp;
    r->vert_count += 1u;
    return 0;
}

dg_struct_footprint_ring *dg_struct_footprint_find_ring(dg_struct_footprint *fp, u32 ring_index) {
    u32 idx;
    if (!fp) return (dg_struct_footprint_ring *)0;
    idx = dg_struct_footprint_ring_lower_bound(fp, ring_index);
    if (idx < fp->ring_count && fp->rings[idx].ring_index == ring_index) {
        return &fp->rings[idx];
    }
    return (dg_struct_footprint_ring *)0;
}

const dg_struct_footprint_ring *dg_struct_footprint_find_ring_const(const dg_struct_footprint *fp, u32 ring_index) {
    u32 idx;
    if (!fp) return (const dg_struct_footprint_ring *)0;
    idx = dg_struct_footprint_ring_lower_bound(fp, ring_index);
    if (idx < fp->ring_count && fp->rings[idx].ring_index == ring_index) {
        return &fp->rings[idx];
    }
    return (const dg_struct_footprint_ring *)0;
}

/* Approximate signed area in integer meters (Q0) to avoid overflow.
 * Positive means CCW in (x,y) plane.
 */
static i64 dg_struct_footprint_ring_signed_area_i64(const dg_struct_footprint_ring *r) {
    i64 acc = 0;
    u32 i;
    u32 n;
    if (!r) return 0;
    n = r->vert_count;
    if (n < 3u) return 0;
    for (i = 0u; i < n; ++i) {
        const dg_struct_footprint_vertex *a = &r->verts[i];
        const dg_struct_footprint_vertex *b = &r->verts[(i + 1u) % n];
        i64 ax = D_DET_RSHIFT_FLOOR_I64((i64)a->x, 16);
        i64 ay = D_DET_RSHIFT_FLOOR_I64((i64)a->y, 16);
        i64 bx = D_DET_RSHIFT_FLOOR_I64((i64)b->x, 16);
        i64 by = D_DET_RSHIFT_FLOOR_I64((i64)b->y, 16);
        acc += (ax * by) - (bx * ay);
    }
    return acc;
}

static void dg_struct_footprint_ring_reverse_xy(dg_struct_footprint_ring *r) {
    u32 i;
    u32 n;
    if (!r) return;
    n = r->vert_count;
    for (i = 0u; i < (n / 2u); ++i) {
        u32 j = n - 1u - i;
        dg_q tx = r->verts[i].x;
        dg_q ty = r->verts[i].y;
        r->verts[i].x = r->verts[j].x;
        r->verts[i].y = r->verts[j].y;
        r->verts[j].x = tx;
        r->verts[j].y = ty;
    }
}

int dg_struct_footprint_canon_winding(dg_struct_footprint *fp) {
    u32 ri;
    if (!fp) return -1;
    for (ri = 0u; ri < fp->ring_count; ++ri) {
        dg_struct_footprint_ring *r = &fp->rings[ri];
        i64 area = dg_struct_footprint_ring_signed_area_i64(r);
        if (area == 0) continue;
        if (!r->is_hole) {
            if (area < 0) dg_struct_footprint_ring_reverse_xy(r);
        } else {
            if (area > 0) dg_struct_footprint_ring_reverse_xy(r);
        }
    }
    return 0;
}

int dg_struct_footprint_validate(const dg_struct_footprint *fp) {
    u32 ri;
    const dg_struct_footprint_ring *outer;
    if (!fp) return -1;
    if (fp->id == 0u) return -2;
    outer = dg_struct_footprint_find_ring_const(fp, 0u);
    if (!outer) return -3;
    if (outer->vert_count < 3u) return -4;

    for (ri = 0u; ri < fp->ring_count; ++ri) {
        const dg_struct_footprint_ring *r = &fp->rings[ri];
        i64 area;
        if (r->vert_count < 3u) return -5;
        area = dg_struct_footprint_ring_signed_area_i64(r);
        if (area == 0) continue;
        if (!r->is_hole) {
            if (area < 0) return -6;
        } else {
            if (area > 0) return -7;
        }
    }

    return 0;
}

int dg_struct_footprint_get_aabb2(const dg_struct_footprint *fp, dg_struct_footprint_aabb2 *out) {
    u32 ri;
    u32 vi;
    d_bool have = D_FALSE;
    dg_struct_footprint_aabb2 aabb;
    if (!out) return -1;
    out->min_x = 0; out->min_y = 0; out->max_x = 0; out->max_y = 0;
    if (!fp) return -2;

    memset(&aabb, 0, sizeof(aabb));
    for (ri = 0u; ri < fp->ring_count; ++ri) {
        const dg_struct_footprint_ring *r = &fp->rings[ri];
        for (vi = 0u; vi < r->vert_count; ++vi) {
            const dg_struct_footprint_vertex *v = &r->verts[vi];
            if (!have) {
                aabb.min_x = v->x; aabb.max_x = v->x;
                aabb.min_y = v->y; aabb.max_y = v->y;
                have = D_TRUE;
            } else {
                if (v->x < aabb.min_x) aabb.min_x = v->x;
                if (v->x > aabb.max_x) aabb.max_x = v->x;
                if (v->y < aabb.min_y) aabb.min_y = v->y;
                if (v->y > aabb.max_y) aabb.max_y = v->y;
            }
        }
    }

    if (!have) return -3;
    *out = aabb;
    return 0;
}
