/*
FILE: source/dominium/setup/core/src/util/dsu_util_blob.c
MODULE: Dominium Setup
PURPOSE: Growable byte buffer for deterministic serialization.
*/
#include "dsu_util_internal.h"

#include <string.h>

void dsu__blob_init(dsu_blob_t *b) {
    if (!b) {
        return;
    }
    b->data = NULL;
    b->size = 0u;
    b->cap = 0u;
}

void dsu__blob_free(dsu_blob_t *b) {
    if (!b) {
        return;
    }
    dsu__free(b->data);
    b->data = NULL;
    b->size = 0u;
    b->cap = 0u;
}

static dsu_status_t dsu__blob_grow_to(dsu_blob_t *b, dsu_u32 needed_cap) {
    dsu_u32 new_cap;
    dsu_u8 *p;
    if (needed_cap <= b->cap) {
        return DSU_STATUS_SUCCESS;
    }
    new_cap = (b->cap == 0u) ? 64u : b->cap;
    while (new_cap < needed_cap) {
        if (new_cap > 0x7FFFFFFFu) {
            new_cap = needed_cap;
            break;
        }
        new_cap *= 2u;
    }
    p = (dsu_u8 *)dsu__realloc(b->data, new_cap);
    if (!p) {
        return DSU_STATUS_IO_ERROR;
    }
    b->data = p;
    b->cap = new_cap;
    return DSU_STATUS_SUCCESS;
}

dsu_status_t dsu__blob_reserve(dsu_blob_t *b, dsu_u32 additional) {
    dsu_u32 needed;
    if (!b) {
        return DSU_STATUS_INVALID_ARGS;
    }
    if (additional == 0u) {
        return DSU_STATUS_SUCCESS;
    }
    if (b->size > 0xFFFFFFFFu - additional) {
        return DSU_STATUS_INTERNAL_ERROR;
    }
    needed = b->size + additional;
    return dsu__blob_grow_to(b, needed);
}

dsu_status_t dsu__blob_append(dsu_blob_t *b, const void *bytes, dsu_u32 len) {
    dsu_status_t st;
    if (!b) {
        return DSU_STATUS_INVALID_ARGS;
    }
    if (len == 0u) {
        return DSU_STATUS_SUCCESS;
    }
    if (!bytes) {
        return DSU_STATUS_INVALID_ARGS;
    }
    st = dsu__blob_reserve(b, len);
    if (st != DSU_STATUS_SUCCESS) {
        return st;
    }
    memcpy(b->data + b->size, bytes, (size_t)len);
    b->size += len;
    return DSU_STATUS_SUCCESS;
}

