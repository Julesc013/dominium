/*
FILE: source/domino/sim/act/dg_capability.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / sim/act/dg_capability
RESPONSIBILITY: Implements `dg_capability`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/specs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/specs/SPEC_*.md` without cross-layer coupling.
*/
#include <stdlib.h>
#include <string.h>

#include "sim/act/dg_capability.h"

void dg_capability_set_init(dg_capability_set *s) {
    if (!s) {
        return;
    }
    s->action_type_ids = (dg_type_id *)0;
    s->count = 0u;
    s->capacity = 0u;
}

void dg_capability_set_free(dg_capability_set *s) {
    if (!s) {
        return;
    }
    if (s->action_type_ids) {
        free(s->action_type_ids);
    }
    dg_capability_set_init(s);
}

int dg_capability_set_reserve(dg_capability_set *s, u32 capacity) {
    dg_type_id *ids;
    if (!s) {
        return -1;
    }
    dg_capability_set_free(s);
    if (capacity == 0u) {
        return 0;
    }
    ids = (dg_type_id *)malloc(sizeof(dg_type_id) * (size_t)capacity);
    if (!ids) {
        return -2;
    }
    memset(ids, 0, sizeof(dg_type_id) * (size_t)capacity);
    s->action_type_ids = ids;
    s->count = 0u;
    s->capacity = capacity;
    return 0;
}

static u32 dg_capability_lower_bound(const dg_capability_set *s, dg_type_id id, int *out_found) {
    u32 lo = 0u;
    u32 hi;
    u32 mid;

    if (out_found) {
        *out_found = 0;
    }
    if (!s || s->count == 0u) {
        return 0u;
    }

    hi = s->count;
    while (lo < hi) {
        mid = lo + ((hi - lo) / 2u);
        if (s->action_type_ids[mid] < id) {
            lo = mid + 1u;
        } else {
            hi = mid;
        }
    }
    if (lo < s->count && s->action_type_ids[lo] == id) {
        if (out_found) {
            *out_found = 1;
        }
    }
    return lo;
}

int dg_capability_set_add(dg_capability_set *s, dg_type_id action_type_id) {
    u32 idx;
    int found;

    if (!s || action_type_id == 0u) {
        return -1;
    }
    if (!s->action_type_ids || s->capacity == 0u) {
        return -2;
    }

    idx = dg_capability_lower_bound(s, action_type_id, &found);
    if (found) {
        return 0; /* already present */
    }
    if (s->count >= s->capacity) {
        return -3;
    }

    if (idx < s->count) {
        memmove(&s->action_type_ids[idx + 1u], &s->action_type_ids[idx],
                sizeof(dg_type_id) * (size_t)(s->count - idx));
    }
    s->action_type_ids[idx] = action_type_id;
    s->count += 1u;
    return 0;
}

d_bool dg_capability_set_contains(const dg_capability_set *s, dg_type_id action_type_id) {
    u32 idx;
    int found;
    if (!s || !s->action_type_ids || s->count == 0u || action_type_id == 0u) {
        return D_FALSE;
    }
    idx = dg_capability_lower_bound(s, action_type_id, &found);
    return found ? D_TRUE : D_FALSE;
}

u32 dg_capability_set_count(const dg_capability_set *s) {
    return s ? s->count : 0u;
}

dg_type_id dg_capability_set_at(const dg_capability_set *s, u32 index) {
    if (!s || !s->action_type_ids || index >= s->count) {
        return 0u;
    }
    return s->action_type_ids[index];
}

