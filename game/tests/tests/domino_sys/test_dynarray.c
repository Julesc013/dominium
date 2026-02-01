/*
FILE: tests/domino_sys/test_dynarray.c
MODULE: Repository
LAYER / SUBSYSTEM: tests/domino_sys
RESPONSIBILITY: Owns documentation for this translation unit.
ALLOWED DEPENDENCIES: Project-local headers; C89/C++98 standard headers.
FORBIDDEN DEPENDENCIES: N/A.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/specs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A.
EXTENSION POINTS: Extend via public headers and relevant `docs/specs/SPEC_*.md` without cross-layer coupling.
*/
#include "dominium/dom_core.h"
#include <stdio.h>
#include <stdlib.h>

typedef struct dyn_array {
    int *data;
    size_t count;
    size_t cap;
} dyn_array;

static void dyn_init(dyn_array *a)
{
    a->data = NULL;
    a->count = 0;
    a->cap = 0;
}

static int dyn_push(dyn_array *a, int v)
{
    size_t new_cap;
    int *new_data;
    if (a->count >= a->cap) {
        new_cap = (a->cap == 0) ? 4 : (a->cap * 2);
        new_data = (int *)realloc(a->data, new_cap * sizeof(int));
        if (!new_data) return -1;
        a->data = new_data;
        a->cap = new_cap;
    }
    a->data[a->count++] = v;
    return 0;
}

static void dyn_free(dyn_array *a)
{
    if (a->data) free(a->data);
    a->data = NULL;
    a->count = a->cap = 0;
}

int main(void)
{
    dyn_array arr;
    size_t i;
    dyn_init(&arr);
    for (i = 0; i < 10; ++i) {
        if (dyn_push(&arr, (int)i) != 0) {
            dom_log(DOM_LOG_ERROR, "test_dynarray", "push failed");
            dyn_free(&arr);
            return 1;
        }
    }
    if (arr.count != 10) {
        dom_log(DOM_LOG_ERROR, "test_dynarray", "count mismatch");
        dyn_free(&arr);
        return 1;
    }
    dyn_free(&arr);
    dom_log(DOM_LOG_INFO, "test_dynarray", "ok");
    return 0;
}
