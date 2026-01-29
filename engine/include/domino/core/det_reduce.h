/*
FILE: include/domino/core/det_reduce.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino API / core/det_reduce
RESPONSIBILITY: Deterministic reduction helpers (sum/min/max/histogram/distribution).
ALLOWED DEPENDENCIES: `include/domino/**` plus C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: OS-specific headers; non-deterministic containers.
*/
#ifndef DOMINO_CORE_DET_REDUCE_H
#define DOMINO_CORE_DET_REDUCE_H

#include "domino/core/types.h"
#include "domino/core/det_order.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct dom_det_reduce_u64_item {
    dom_det_order_item key;
    u64 value;
} dom_det_reduce_u64_item;

typedef struct dom_det_reduce_i64_item {
    dom_det_order_item key;
    i64 value;
} dom_det_reduce_i64_item;

typedef struct dom_det_hist_bucket {
    dom_det_order_item key;
    u64 count;
} dom_det_hist_bucket;

typedef struct dom_det_dist_bucket {
    dom_det_order_item key;
    u64 weight;
    u64 count;
} dom_det_dist_bucket;

void dom_det_reduce_sort_u64(dom_det_reduce_u64_item* items, u32 count);
void dom_det_reduce_sort_i64(dom_det_reduce_i64_item* items, u32 count);
void dom_det_reduce_sort_hist(dom_det_hist_bucket* items, u32 count);
void dom_det_reduce_sort_dist(dom_det_dist_bucket* items, u32 count);

int dom_det_reduce_sum_u64(dom_det_reduce_u64_item* items, u32 count, u64* out_sum);
int dom_det_reduce_min_u64(dom_det_reduce_u64_item* items, u32 count, u64* out_min);
int dom_det_reduce_max_u64(dom_det_reduce_u64_item* items, u32 count, u64* out_max);

int dom_det_reduce_sum_i64(dom_det_reduce_i64_item* items, u32 count, i64* out_sum);
int dom_det_reduce_min_i64(dom_det_reduce_i64_item* items, u32 count, i64* out_min);
int dom_det_reduce_max_i64(dom_det_reduce_i64_item* items, u32 count, i64* out_max);

/* Merge items in-place after sorting by key; returns new count. */
u32 dom_det_reduce_hist_merge(dom_det_hist_bucket* items, u32 count);
u32 dom_det_reduce_dist_merge(dom_det_dist_bucket* items, u32 count);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINO_CORE_DET_REDUCE_H */
