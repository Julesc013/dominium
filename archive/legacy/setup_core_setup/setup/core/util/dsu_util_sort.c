/*
FILE: source/dominium/setup/core/src/util/dsu_util_sort.c
MODULE: Dominium Setup
PURPOSE: Deterministic stable sorting helpers (no qsort dependence).
*/
#include "dsu_util_internal.h"

void dsu__sort_str_ptrs(char **items, dsu_u32 count) {
    dsu_u32 i;
    if (!items || count < 2u) {
        return;
    }

    /* Stable insertion sort. */
    for (i = 1u; i < count; ++i) {
        char *key = items[i];
        dsu_u32 j = i;
        while (j > 0u && dsu__strcmp_bytes(items[j - 1u], key) > 0) {
            items[j] = items[j - 1u];
            --j;
        }
        items[j] = key;
    }
}

