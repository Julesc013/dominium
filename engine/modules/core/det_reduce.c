/*
FILE: source/domino/core/det_reduce.c
MODULE: Domino
RESPONSIBILITY: Deterministic reduction helpers (sum/min/max/histogram/distribution).
*/
#include "domino/core/det_reduce.h"

static int dom_det_reduce_key_cmp(const dom_det_order_item* a, const dom_det_order_item* b)
{
    return dom_det_order_item_cmp(a, b);
}

void dom_det_reduce_sort_u64(dom_det_reduce_u64_item* items, u32 count)
{
    u32 i;
    if (!items || count <= 1u) {
        return;
    }
    for (i = 1u; i < count; ++i) {
        dom_det_reduce_u64_item key = items[i];
        u32 j = i;
        while (j > 0u && dom_det_reduce_key_cmp(&items[j - 1u].key, &key.key) > 0) {
            items[j] = items[j - 1u];
            --j;
        }
        items[j] = key;
    }
}

void dom_det_reduce_sort_i64(dom_det_reduce_i64_item* items, u32 count)
{
    u32 i;
    if (!items || count <= 1u) {
        return;
    }
    for (i = 1u; i < count; ++i) {
        dom_det_reduce_i64_item key = items[i];
        u32 j = i;
        while (j > 0u && dom_det_reduce_key_cmp(&items[j - 1u].key, &key.key) > 0) {
            items[j] = items[j - 1u];
            --j;
        }
        items[j] = key;
    }
}

void dom_det_reduce_sort_hist(dom_det_hist_bucket* items, u32 count)
{
    u32 i;
    if (!items || count <= 1u) {
        return;
    }
    for (i = 1u; i < count; ++i) {
        dom_det_hist_bucket key = items[i];
        u32 j = i;
        while (j > 0u && dom_det_reduce_key_cmp(&items[j - 1u].key, &key.key) > 0) {
            items[j] = items[j - 1u];
            --j;
        }
        items[j] = key;
    }
}

void dom_det_reduce_sort_dist(dom_det_dist_bucket* items, u32 count)
{
    u32 i;
    if (!items || count <= 1u) {
        return;
    }
    for (i = 1u; i < count; ++i) {
        dom_det_dist_bucket key = items[i];
        u32 j = i;
        while (j > 0u && dom_det_reduce_key_cmp(&items[j - 1u].key, &key.key) > 0) {
            items[j] = items[j - 1u];
            --j;
        }
        items[j] = key;
    }
}

int dom_det_reduce_sum_u64(dom_det_reduce_u64_item* items, u32 count, u64* out_sum)
{
    u32 i;
    u64 sum = 0u;
    if (!out_sum) {
        return DOM_DET_INVALID;
    }
    if (!items || count == 0u) {
        *out_sum = 0u;
        return DOM_DET_OK;
    }
    dom_det_reduce_sort_u64(items, count);
    for (i = 0u; i < count; ++i) {
        sum += items[i].value;
    }
    *out_sum = sum;
    return DOM_DET_OK;
}

int dom_det_reduce_min_u64(dom_det_reduce_u64_item* items, u32 count, u64* out_min)
{
    u32 i;
    u64 min_val = 0u;
    if (!out_min) {
        return DOM_DET_INVALID;
    }
    if (!items || count == 0u) {
        return DOM_DET_EMPTY;
    }
    dom_det_reduce_sort_u64(items, count);
    min_val = items[0u].value;
    for (i = 1u; i < count; ++i) {
        if (items[i].value < min_val) {
            min_val = items[i].value;
        }
    }
    *out_min = min_val;
    return DOM_DET_OK;
}

int dom_det_reduce_max_u64(dom_det_reduce_u64_item* items, u32 count, u64* out_max)
{
    u32 i;
    u64 max_val = 0u;
    if (!out_max) {
        return DOM_DET_INVALID;
    }
    if (!items || count == 0u) {
        return DOM_DET_EMPTY;
    }
    dom_det_reduce_sort_u64(items, count);
    max_val = items[0u].value;
    for (i = 1u; i < count; ++i) {
        if (items[i].value > max_val) {
            max_val = items[i].value;
        }
    }
    *out_max = max_val;
    return DOM_DET_OK;
}

int dom_det_reduce_sum_i64(dom_det_reduce_i64_item* items, u32 count, i64* out_sum)
{
    u32 i;
    i64 sum = 0;
    if (!out_sum) {
        return DOM_DET_INVALID;
    }
    if (!items || count == 0u) {
        *out_sum = 0;
        return DOM_DET_OK;
    }
    dom_det_reduce_sort_i64(items, count);
    for (i = 0u; i < count; ++i) {
        sum += items[i].value;
    }
    *out_sum = sum;
    return DOM_DET_OK;
}

int dom_det_reduce_min_i64(dom_det_reduce_i64_item* items, u32 count, i64* out_min)
{
    u32 i;
    i64 min_val = 0;
    if (!out_min) {
        return DOM_DET_INVALID;
    }
    if (!items || count == 0u) {
        return DOM_DET_EMPTY;
    }
    dom_det_reduce_sort_i64(items, count);
    min_val = items[0u].value;
    for (i = 1u; i < count; ++i) {
        if (items[i].value < min_val) {
            min_val = items[i].value;
        }
    }
    *out_min = min_val;
    return DOM_DET_OK;
}

int dom_det_reduce_max_i64(dom_det_reduce_i64_item* items, u32 count, i64* out_max)
{
    u32 i;
    i64 max_val = 0;
    if (!out_max) {
        return DOM_DET_INVALID;
    }
    if (!items || count == 0u) {
        return DOM_DET_EMPTY;
    }
    dom_det_reduce_sort_i64(items, count);
    max_val = items[0u].value;
    for (i = 1u; i < count; ++i) {
        if (items[i].value > max_val) {
            max_val = items[i].value;
        }
    }
    *out_max = max_val;
    return DOM_DET_OK;
}

u32 dom_det_reduce_hist_merge(dom_det_hist_bucket* items, u32 count)
{
    u32 i;
    u32 out = 0u;
    if (!items || count == 0u) {
        return 0u;
    }
    dom_det_reduce_sort_hist(items, count);
    for (i = 0u; i < count; ++i) {
        if (out == 0u ||
            dom_det_reduce_key_cmp(&items[out - 1u].key, &items[i].key) != 0) {
            items[out] = items[i];
            out += 1u;
        } else {
            items[out - 1u].count += items[i].count;
        }
    }
    return out;
}

u32 dom_det_reduce_dist_merge(dom_det_dist_bucket* items, u32 count)
{
    u32 i;
    u32 out = 0u;
    if (!items || count == 0u) {
        return 0u;
    }
    dom_det_reduce_sort_dist(items, count);
    for (i = 0u; i < count; ++i) {
        if (out == 0u ||
            dom_det_reduce_key_cmp(&items[out - 1u].key, &items[i].key) != 0) {
            items[out] = items[i];
            out += 1u;
        } else {
            items[out - 1u].weight += items[i].weight;
            items[out - 1u].count += items[i].count;
        }
    }
    return out;
}
