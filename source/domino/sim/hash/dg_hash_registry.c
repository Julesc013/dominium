/*
FILE: source/domino/sim/hash/dg_hash_registry.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / sim/hash/dg_hash_registry
RESPONSIBILITY: Implements `dg_hash_registry`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include <stdlib.h>
#include <string.h>

#include "sim/hash/dg_hash_registry.h"

void dg_hash_registry_init(dg_hash_registry *r) {
    if (!r) {
        return;
    }
    r->entries = (dg_hash_registry_entry *)0;
    r->count = 0u;
    r->capacity = 0u;
    r->next_insert_index = 0u;
    r->probe_refused = 0u;
}

void dg_hash_registry_free(dg_hash_registry *r) {
    if (!r) {
        return;
    }
    if (r->entries) {
        free(r->entries);
    }
    dg_hash_registry_init(r);
}

int dg_hash_registry_reserve(dg_hash_registry *r, u32 capacity) {
    dg_hash_registry_entry *e;
    if (!r) {
        return -1;
    }
    if (capacity <= r->capacity) {
        return 0;
    }
    e = (dg_hash_registry_entry *)realloc(r->entries, sizeof(dg_hash_registry_entry) * (size_t)capacity);
    if (!e) {
        return -2;
    }
    r->entries = e;
    r->capacity = capacity;
    return 0;
}

static int dg_hash_registry_entry_cmp(const dg_hash_registry_entry *a, const dg_hash_registry_entry *b) {
    if (a->domain_id < b->domain_id) return -1;
    if (a->domain_id > b->domain_id) return 1;
    if (a->insert_index < b->insert_index) return -1;
    if (a->insert_index > b->insert_index) return 1;
    return 0;
}

static u32 dg_hash_registry_lower_bound(const dg_hash_registry *r, const dg_hash_registry_entry *key, int *out_found) {
    u32 lo = 0u;
    u32 hi;
    u32 mid;
    int cmp;

    if (out_found) {
        *out_found = 0;
    }
    if (!r || !r->entries || r->count == 0u) {
        return 0u;
    }

    hi = r->count;
    while (lo < hi) {
        mid = lo + ((hi - lo) / 2u);
        cmp = dg_hash_registry_entry_cmp(&r->entries[mid], key);
        if (cmp < 0) {
            lo = mid + 1u;
        } else {
            hi = mid;
        }
    }

    if (lo < r->count) {
        if (r->entries[lo].domain_id == key->domain_id && out_found) {
            *out_found = 1;
        }
    }
    return lo;
}

int dg_hash_registry_add_domain(
    dg_hash_registry   *r,
    dg_hash_domain_id   domain_id,
    u32                 flags,
    dg_hash_domain_fn   fn,
    void               *user_ctx
) {
    dg_hash_registry_entry e;
    u32 idx;
    int found;
    int rc;

    if (!r || domain_id == 0u || !fn) {
        return -1;
    }

    memset(&e, 0, sizeof(e));
    e.domain_id = domain_id;
    e.flags = flags;
    e.fn = fn;
    e.user_ctx = user_ctx;
    e.insert_index = r->next_insert_index++;

    idx = dg_hash_registry_lower_bound(r, &e, &found);
    if (found) {
        return -2;
    }

    if (r->count >= r->capacity) {
        u32 new_cap = (r->capacity == 0u) ? 16u : (r->capacity * 2u);
        rc = dg_hash_registry_reserve(r, new_cap);
        if (rc != 0) {
            r->probe_refused += 1u;
            return -3;
        }
    }

    if (idx < r->count) {
        memmove(&r->entries[idx + 1u], &r->entries[idx],
                sizeof(dg_hash_registry_entry) * (size_t)(r->count - idx));
    }
    r->entries[idx] = e;
    r->count += 1u;
    return 0;
}

u32 dg_hash_registry_count(const dg_hash_registry *r) {
    return r ? r->count : 0u;
}

const dg_hash_registry_entry *dg_hash_registry_at(const dg_hash_registry *r, u32 index) {
    if (!r || !r->entries || index >= r->count) {
        return (const dg_hash_registry_entry *)0;
    }
    return &r->entries[index];
}

const dg_hash_registry_entry *dg_hash_registry_find(const dg_hash_registry *r, dg_hash_domain_id domain_id) {
    dg_hash_registry_entry key;
    u32 idx;
    int found;

    if (!r || !r->entries || r->count == 0u) {
        return (const dg_hash_registry_entry *)0;
    }

    memset(&key, 0, sizeof(key));
    key.domain_id = domain_id;
    key.insert_index = 0u;
    idx = dg_hash_registry_lower_bound(r, &key, &found);
    if (!found || idx >= r->count) {
        return (const dg_hash_registry_entry *)0;
    }
    return &r->entries[idx];
}

u32 dg_hash_registry_probe_refused(const dg_hash_registry *r) {
    return r ? r->probe_refused : 0u;
}

int dg_hash_registry_compute_tick(
    const dg_hash_registry *r,
    dg_tick                 tick,
    dg_hash_snapshot       *out_snapshot
) {
    dg_hash_stream s;
    u32 i;
    u32 max_out;

    if (!out_snapshot) {
        return -1;
    }
    dg_hash_snapshot_clear(out_snapshot);

    if (!r || !r->entries) {
        return 0;
    }
    if (!out_snapshot->entries || out_snapshot->capacity == 0u) {
        return -2;
    }

    max_out = (out_snapshot->capacity < r->count) ? out_snapshot->capacity : r->count;

    dg_hash_stream_init(&s);
    for (i = 0u; i < max_out; ++i) {
        const dg_hash_registry_entry *e = &r->entries[i];
        dg_hash_snapshot_entry *dst = &out_snapshot->entries[i];
        dg_hash_stream_begin_domain(&s, e->domain_id, tick);
        e->fn(&s, tick, e->user_ctx);
        dst->domain_id = e->domain_id;
        dst->value = dg_hash_stream_finalize(&s);
    }
    out_snapshot->count = max_out;

    if (max_out < r->count) {
        return 1;
    }
    return 0;
}

