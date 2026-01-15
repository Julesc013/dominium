/*
FILE: source/dominium/setup/core/src/util/dsu_util_mem.c
MODULE: Dominium Setup
PURPOSE: Centralized allocation wrappers for Setup Core.
*/
#include "dsu_util_internal.h"

#include <stdlib.h>

void *dsu__malloc(dsu_u32 size) {
    void *p;
    if (size == 0u) {
        return NULL;
    }
    p = malloc((size_t)size);
    return p;
}

void *dsu__realloc(void *ptr, dsu_u32 size) {
    void *p;
    if (size == 0u) {
        free(ptr);
        return NULL;
    }
    p = realloc(ptr, (size_t)size);
    return p;
}

void dsu__free(void *ptr) {
    if (!ptr) {
        return;
    }
    free(ptr);
}

