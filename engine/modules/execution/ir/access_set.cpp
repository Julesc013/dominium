/*
FILE: source/domino/execution/ir/access_set.cpp
MODULE: Domino
RESPONSIBILITY: AccessSet conflict detection and reduction validation.
*/
#include "domino/execution/access_set.h"

static d_bool ranges_overlap_index(const dom_access_range *a, const dom_access_range *b) {
    u64 a_start = a->start_id;
    u64 a_end = a->end_id;
    u64 b_start = b->start_id;
    u64 b_end = b->end_id;
    if (a->kind == DOM_RANGE_SINGLE) {
        a_end = a_start;
    }
    if (b->kind == DOM_RANGE_SINGLE) {
        b_end = b_start;
    }
    return (a_start <= b_end && b_start <= a_end) ? D_TRUE : D_FALSE;
}

d_bool dom_access_ranges_overlap(const dom_access_range *a, const dom_access_range *b) {
    if (!a || !b) {
        return D_FALSE;
    }
    if (a->component_id != b->component_id || a->field_id != b->field_id) {
        return D_FALSE;
    }
    if ((a->kind == DOM_RANGE_INDEX_RANGE || a->kind == DOM_RANGE_SINGLE) &&
        (b->kind == DOM_RANGE_INDEX_RANGE || b->kind == DOM_RANGE_SINGLE)) {
        return ranges_overlap_index(a, b);
    }
    /* Conservative: if we cannot prove disjoint, treat as overlapping. */
    return D_TRUE;
}

static d_bool op_is_allowed(u32 op) {
    switch (op) {
        case DOM_REDUCE_INT_SUM:
        case DOM_REDUCE_INT_MIN:
        case DOM_REDUCE_INT_MAX:
        case DOM_REDUCE_FIXED_SUM:
        case DOM_REDUCE_BIT_OR:
        case DOM_REDUCE_BIT_AND:
        case DOM_REDUCE_BIT_XOR:
        case DOM_REDUCE_HISTOGRAM_MERGE:
        case DOM_REDUCE_SET_UNION:
            return D_TRUE;
        default:
            break;
    }
    return D_FALSE;
}

d_bool dom_verify_reduction_rules(const dom_access_set *set) {
    if (!set) {
        return D_FALSE;
    }
    if (set->reduce_count == 0u) {
        return D_TRUE;
    }
    if (set->reduction_op == DOM_REDUCE_NONE) {
        return D_FALSE;
    }
    if (!op_is_allowed(set->reduction_op)) {
        return D_FALSE;
    }
    if (set->commutative != D_TRUE) {
        return D_FALSE;
    }
    return D_TRUE;
}

static d_bool ranges_conflict(const dom_access_range *a, u32 a_count,
                              const dom_access_range *b, u32 b_count) {
    u32 i;
    u32 j;
    if ((a_count > 0u && !a) || (b_count > 0u && !b)) {
        return D_TRUE;
    }
    for (i = 0u; i < a_count; ++i) {
        for (j = 0u; j < b_count; ++j) {
            if (dom_access_ranges_overlap(&a[i], &b[j])) {
                return D_TRUE;
            }
        }
    }
    return D_FALSE;
}

d_bool dom_detect_access_conflicts(const dom_access_set *a, const dom_access_set *b) {
    if (!a || !b) {
        return D_FALSE;
    }
    /* Write/Write conflicts. */
    if (ranges_conflict(a->write_ranges, a->write_count, b->write_ranges, b->write_count)) {
        return D_TRUE;
    }
    /* Read/Write conflicts. */
    if (ranges_conflict(a->write_ranges, a->write_count, b->read_ranges, b->read_count)) {
        return D_TRUE;
    }
    if (ranges_conflict(b->write_ranges, b->write_count, a->read_ranges, a->read_count)) {
        return D_TRUE;
    }
    /* Write/Reduce conflicts (conservative). */
    if (ranges_conflict(a->write_ranges, a->write_count, b->reduce_ranges, b->reduce_count)) {
        return D_TRUE;
    }
    if (ranges_conflict(b->write_ranges, b->write_count, a->reduce_ranges, a->reduce_count)) {
        return D_TRUE;
    }
    /* Reduce/Reduce conflicts: allowed only if same deterministic operator. */
    if (a->reduce_count > 0u || b->reduce_count > 0u) {
        if (a->reduction_op != b->reduction_op || a->reduction_op == DOM_REDUCE_NONE) {
            return D_TRUE;
        }
        if (!op_is_allowed(a->reduction_op)) {
            return D_TRUE;
        }
    }
    return D_FALSE;
}
