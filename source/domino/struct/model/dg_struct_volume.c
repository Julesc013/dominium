/* STRUCT volume authoring model (C89). */
#include "struct/model/dg_struct_volume.h"

#include <stdlib.h>
#include <string.h>

static void dg_struct_volume_free_kind_fields(dg_struct_volume *v) {
    if (!v) return;
    if (v->kind == DG_STRUCT_VOLUME_BOOL) {
        if (v->u.boolean.terms) free(v->u.boolean.terms);
        v->u.boolean.terms = (dg_struct_volume_bool_term *)0;
        v->u.boolean.term_count = 0u;
        v->u.boolean.term_capacity = 0u;
    }
    memset(&v->u, 0, sizeof(v->u));
}

void dg_struct_volume_init(dg_struct_volume *v) {
    if (!v) return;
    memset(v, 0, sizeof(*v));
}

void dg_struct_volume_free(dg_struct_volume *v) {
    if (!v) return;
    dg_struct_volume_free_kind_fields(v);
    dg_struct_volume_init(v);
}

int dg_struct_volume_set_extrude(dg_struct_volume *v, dg_struct_footprint_id footprint_id, dg_q base_z, dg_q height, d_bool is_void) {
    if (!v) return -1;
    dg_struct_volume_free_kind_fields(v);
    v->kind = DG_STRUCT_VOLUME_EXTRUDE;
    v->is_void = is_void ? D_TRUE : D_FALSE;
    v->u.extrude.footprint_id = footprint_id;
    v->u.extrude.base_z = base_z;
    v->u.extrude.height = height;
    return 0;
}

int dg_struct_volume_set_sweep(dg_struct_volume *v, dg_struct_footprint_id footprint_id, dg_q length, dg_q height, d_bool is_void) {
    if (!v) return -1;
    dg_struct_volume_free_kind_fields(v);
    v->kind = DG_STRUCT_VOLUME_SWEEP;
    v->is_void = is_void ? D_TRUE : D_FALSE;
    v->u.sweep.footprint_id = footprint_id;
    v->u.sweep.length = length;
    v->u.sweep.height = height;
    return 0;
}

int dg_struct_volume_set_boolean(dg_struct_volume *v, d_bool is_void) {
    if (!v) return -1;
    dg_struct_volume_free_kind_fields(v);
    v->kind = DG_STRUCT_VOLUME_BOOL;
    v->is_void = is_void ? D_TRUE : D_FALSE;
    return 0;
}

int dg_struct_volume_bool_reserve_terms(dg_struct_volume *v, u32 capacity) {
    dg_struct_volume_bool_term *arr;
    u32 new_cap;
    if (!v) return -1;
    if (v->kind != DG_STRUCT_VOLUME_BOOL) return -2;
    if (capacity <= v->u.boolean.term_capacity) return 0;
    new_cap = v->u.boolean.term_capacity ? v->u.boolean.term_capacity : 4u;
    while (new_cap < capacity) {
        if (new_cap > 0x7FFFFFFFu) {
            new_cap = capacity;
            break;
        }
        new_cap *= 2u;
    }
    arr = (dg_struct_volume_bool_term *)realloc(v->u.boolean.terms, sizeof(dg_struct_volume_bool_term) * (size_t)new_cap);
    if (!arr) return -3;
    if (new_cap > v->u.boolean.term_capacity) {
        memset(&arr[v->u.boolean.term_capacity], 0, sizeof(dg_struct_volume_bool_term) * (size_t)(new_cap - v->u.boolean.term_capacity));
    }
    v->u.boolean.terms = arr;
    v->u.boolean.term_capacity = new_cap;
    return 0;
}

static u32 dg_struct_volume_bool_term_lower_bound(const dg_struct_volume *v, u32 term_index) {
    u32 lo = 0u;
    u32 hi;
    u32 mid;
    if (!v || v->kind != DG_STRUCT_VOLUME_BOOL) return 0u;
    hi = v->u.boolean.term_count;
    while (lo < hi) {
        mid = lo + ((hi - lo) / 2u);
        if (v->u.boolean.terms[mid].term_index >= term_index) {
            hi = mid;
        } else {
            lo = mid + 1u;
        }
    }
    return lo;
}

int dg_struct_volume_bool_set_term(dg_struct_volume *v, u32 term_index, dg_struct_volume_id volume_id, dg_struct_bool_op op) {
    u32 idx;
    dg_struct_volume_bool_term tmp;
    if (!v) return -1;
    if (v->kind != DG_STRUCT_VOLUME_BOOL) return -2;
    if (volume_id == 0u) return -3;

    idx = dg_struct_volume_bool_term_lower_bound(v, term_index);
    if (idx < v->u.boolean.term_count && v->u.boolean.terms[idx].term_index == term_index) {
        v->u.boolean.terms[idx].volume_id = volume_id;
        v->u.boolean.terms[idx].op = op;
        return 0;
    }

    if (dg_struct_volume_bool_reserve_terms(v, v->u.boolean.term_count + 1u) != 0) {
        return -4;
    }

    if (idx < v->u.boolean.term_count) {
        memmove(&v->u.boolean.terms[idx + 1u], &v->u.boolean.terms[idx],
                sizeof(dg_struct_volume_bool_term) * (size_t)(v->u.boolean.term_count - idx));
    }
    memset(&tmp, 0, sizeof(tmp));
    tmp.term_index = term_index;
    tmp.volume_id = volume_id;
    tmp.op = op;
    v->u.boolean.terms[idx] = tmp;
    v->u.boolean.term_count += 1u;
    return 0;
}

int dg_struct_volume_validate(const dg_struct_volume *v) {
    u32 i;
    if (!v) return -1;
    if (v->id == 0u) return -2;
    switch (v->kind) {
    case DG_STRUCT_VOLUME_EXTRUDE:
        if (v->u.extrude.footprint_id == 0u) return -10;
        if (v->u.extrude.height < 0) return -11;
        return 0;
    case DG_STRUCT_VOLUME_SWEEP:
        if (v->u.sweep.footprint_id == 0u) return -20;
        if (v->u.sweep.length < 0) return -21;
        if (v->u.sweep.height < 0) return -22;
        return 0;
    case DG_STRUCT_VOLUME_BOOL:
        for (i = 0u; i < v->u.boolean.term_count; ++i) {
            const dg_struct_volume_bool_term *t = &v->u.boolean.terms[i];
            if (t->volume_id == 0u) return -30;
            if (t->op != DG_STRUCT_BOOL_UNION &&
                t->op != DG_STRUCT_BOOL_SUBTRACT &&
                t->op != DG_STRUCT_BOOL_INTERSECT) return -31;
        }
        return 0;
    default:
        return -3;
    }
}

