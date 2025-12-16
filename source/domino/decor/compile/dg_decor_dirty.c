/*
FILE: source/domino/decor/compile/dg_decor_dirty.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / decor/compile/dg_decor_dirty
RESPONSIBILITY: Implements `dg_decor_dirty`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
/* DECOR incremental dirty tracking (C89). */
#include "decor/compile/dg_decor_dirty.h"

#include <stdlib.h>
#include <string.h>

#include "core/det_invariants.h"

static u32 rulepack_lower_bound(const dg_decor_dirty *d, dg_decor_rulepack_id id) {
    u32 lo = 0u;
    u32 hi;
    u32 mid;
    if (!d) return 0u;
    hi = d->rulepack_count;
    while (lo < hi) {
        mid = lo + ((hi - lo) / 2u);
        if (d->rulepacks[mid].rulepack_id >= id) {
            hi = mid;
        } else {
            lo = mid + 1u;
        }
    }
    return lo;
}

static u32 chunk_lower_bound(const dg_decor_dirty *d, dg_chunk_id id) {
    u32 lo = 0u;
    u32 hi;
    u32 mid;
    if (!d) return 0u;
    hi = d->chunk_count;
    while (lo < hi) {
        mid = lo + ((hi - lo) / 2u);
        if (d->chunks[mid].chunk_id >= id) {
            hi = mid;
        } else {
            lo = mid + 1u;
        }
    }
    return lo;
}

static u32 host_lower_bound(const dg_decor_dirty *d, const dg_decor_host *host) {
    u32 lo = 0u;
    u32 hi;
    u32 mid;
    int c;
    if (!d || !host) return 0u;
    hi = d->host_count;
    while (lo < hi) {
        mid = lo + ((hi - lo) / 2u);
        c = dg_decor_host_cmp(&d->hosts[mid].host, host);
        if (c >= 0) {
            hi = mid;
        } else {
            lo = mid + 1u;
        }
    }
    return lo;
}

void dg_decor_dirty_init(dg_decor_dirty *d) {
    if (!d) return;
    memset(d, 0, sizeof(*d));
}

void dg_decor_dirty_free(dg_decor_dirty *d) {
    if (!d) return;
    if (d->rulepacks) free(d->rulepacks);
    if (d->hosts) free(d->hosts);
    if (d->chunks) free(d->chunks);
    dg_decor_dirty_init(d);
}

void dg_decor_dirty_clear(dg_decor_dirty *d) {
    if (!d) return;
    d->rulepack_count = 0u;
    d->host_count = 0u;
    d->chunk_count = 0u;
    d->overrides_dirty = D_FALSE;
}

int dg_decor_dirty_reserve_rulepacks(dg_decor_dirty *d, u32 capacity) {
    dg_decor_dirty_rulepack *arr;
    u32 new_cap;
    if (!d) return -1;
    if (capacity <= d->rulepack_capacity) return 0;
    new_cap = d->rulepack_capacity ? d->rulepack_capacity : 8u;
    while (new_cap < capacity) {
        if (new_cap > 0x7FFFFFFFu) {
            new_cap = capacity;
            break;
        }
        new_cap *= 2u;
    }
    arr = (dg_decor_dirty_rulepack *)realloc(d->rulepacks, sizeof(dg_decor_dirty_rulepack) * (size_t)new_cap);
    if (!arr) return -2;
    if (new_cap > d->rulepack_capacity) {
        memset(&arr[d->rulepack_capacity], 0, sizeof(dg_decor_dirty_rulepack) * (size_t)(new_cap - d->rulepack_capacity));
    }
    d->rulepacks = arr;
    d->rulepack_capacity = new_cap;
    return 0;
}

int dg_decor_dirty_reserve_hosts(dg_decor_dirty *d, u32 capacity) {
    dg_decor_dirty_host *arr;
    u32 new_cap;
    if (!d) return -1;
    if (capacity <= d->host_capacity) return 0;
    new_cap = d->host_capacity ? d->host_capacity : 8u;
    while (new_cap < capacity) {
        if (new_cap > 0x7FFFFFFFu) {
            new_cap = capacity;
            break;
        }
        new_cap *= 2u;
    }
    arr = (dg_decor_dirty_host *)realloc(d->hosts, sizeof(dg_decor_dirty_host) * (size_t)new_cap);
    if (!arr) return -2;
    if (new_cap > d->host_capacity) {
        memset(&arr[d->host_capacity], 0, sizeof(dg_decor_dirty_host) * (size_t)(new_cap - d->host_capacity));
    }
    d->hosts = arr;
    d->host_capacity = new_cap;
    return 0;
}

int dg_decor_dirty_reserve_chunks(dg_decor_dirty *d, u32 capacity) {
    dg_decor_dirty_chunk *arr;
    u32 new_cap;
    if (!d) return -1;
    if (capacity <= d->chunk_capacity) return 0;
    new_cap = d->chunk_capacity ? d->chunk_capacity : 8u;
    while (new_cap < capacity) {
        if (new_cap > 0x7FFFFFFFu) {
            new_cap = capacity;
            break;
        }
        new_cap *= 2u;
    }
    arr = (dg_decor_dirty_chunk *)realloc(d->chunks, sizeof(dg_decor_dirty_chunk) * (size_t)new_cap);
    if (!arr) return -2;
    if (new_cap > d->chunk_capacity) {
        memset(&arr[d->chunk_capacity], 0, sizeof(dg_decor_dirty_chunk) * (size_t)(new_cap - d->chunk_capacity));
    }
    d->chunks = arr;
    d->chunk_capacity = new_cap;
    return 0;
}

void dg_decor_dirty_mark_overrides(dg_decor_dirty *d) {
    if (!d) return;
    d->overrides_dirty = D_TRUE;
}

void dg_decor_dirty_mark_rulepack(dg_decor_dirty *d, dg_decor_rulepack_id rulepack_id) {
    u32 idx;
    if (!d || rulepack_id == 0u) return;
    idx = rulepack_lower_bound(d, rulepack_id);
    if (idx < d->rulepack_count && d->rulepacks[idx].rulepack_id == rulepack_id) {
        d->rulepacks[idx].dirty = D_TRUE;
        return;
    }
    if (dg_decor_dirty_reserve_rulepacks(d, d->rulepack_count + 1u) != 0) return;
    if (idx < d->rulepack_count) {
        memmove(&d->rulepacks[idx + 1u], &d->rulepacks[idx],
                sizeof(dg_decor_dirty_rulepack) * (size_t)(d->rulepack_count - idx));
    }
    memset(&d->rulepacks[idx], 0, sizeof(d->rulepacks[idx]));
    d->rulepacks[idx].rulepack_id = rulepack_id;
    d->rulepacks[idx].dirty = D_TRUE;
    d->rulepack_count += 1u;
}

void dg_decor_dirty_mark_chunk(dg_decor_dirty *d, dg_chunk_id chunk_id) {
    u32 idx;
    if (!d || chunk_id == 0u) return;
    idx = chunk_lower_bound(d, chunk_id);
    if (idx < d->chunk_count && d->chunks[idx].chunk_id == chunk_id) {
        d->chunks[idx].dirty = D_TRUE;
        return;
    }
    if (dg_decor_dirty_reserve_chunks(d, d->chunk_count + 1u) != 0) return;
    if (idx < d->chunk_count) {
        memmove(&d->chunks[idx + 1u], &d->chunks[idx],
                sizeof(dg_decor_dirty_chunk) * (size_t)(d->chunk_count - idx));
    }
    memset(&d->chunks[idx], 0, sizeof(d->chunks[idx]));
    d->chunks[idx].chunk_id = chunk_id;
    d->chunks[idx].dirty = D_TRUE;
    d->chunk_count += 1u;
}

void dg_decor_dirty_mark_host(dg_decor_dirty *d, const dg_decor_host *host, dg_chunk_id chunk_id) {
    u32 idx;
    if (!d || !host) return;
    if (host->kind == DG_DECOR_HOST_NONE) return;
    idx = host_lower_bound(d, host);
    if (idx < d->host_count && dg_decor_host_cmp(&d->hosts[idx].host, host) == 0) {
        d->hosts[idx].dirty = D_TRUE;
        if (d->hosts[idx].chunk_id == 0u) d->hosts[idx].chunk_id = chunk_id;
        dg_decor_dirty_mark_chunk(d, chunk_id);
        return;
    }
    if (dg_decor_dirty_reserve_hosts(d, d->host_count + 1u) != 0) return;
    if (idx < d->host_count) {
        memmove(&d->hosts[idx + 1u], &d->hosts[idx],
                sizeof(dg_decor_dirty_host) * (size_t)(d->host_count - idx));
    }
    memset(&d->hosts[idx], 0, sizeof(d->hosts[idx]));
    d->hosts[idx].host = *host;
    d->hosts[idx].chunk_id = chunk_id;
    d->hosts[idx].dirty = D_TRUE;
    d->host_count += 1u;
    dg_decor_dirty_mark_chunk(d, chunk_id);
}

int dg_decor_dirty_get_host(const dg_decor_dirty *d, const dg_decor_host *host, dg_decor_dirty_host *out) {
    u32 idx;
    if (!out) return 0;
    memset(out, 0, sizeof(*out));
    if (!d || !host) return 0;
    idx = host_lower_bound(d, host);
    if (idx < d->host_count && dg_decor_host_cmp(&d->hosts[idx].host, host) == 0) {
        *out = d->hosts[idx];
        return 1;
    }
    return 0;
}

int dg_decor_dirty_get_chunk(const dg_decor_dirty *d, dg_chunk_id chunk_id, dg_decor_dirty_chunk *out) {
    u32 idx;
    if (!out) return 0;
    memset(out, 0, sizeof(*out));
    if (!d || chunk_id == 0u) return 0;
    idx = chunk_lower_bound(d, chunk_id);
    if (idx < d->chunk_count && d->chunks[idx].chunk_id == chunk_id) {
        *out = d->chunks[idx];
        return 1;
    }
    return 0;
}

void dg_decor_dirty_clear_host(dg_decor_dirty *d, const dg_decor_host *host) {
    u32 idx;
    if (!d || !host) return;
    idx = host_lower_bound(d, host);
    if (idx < d->host_count && dg_decor_host_cmp(&d->hosts[idx].host, host) == 0) {
        d->hosts[idx].dirty = D_FALSE;
    }
}

void dg_decor_dirty_clear_chunk(dg_decor_dirty *d, dg_chunk_id chunk_id) {
    u32 idx;
    if (!d || chunk_id == 0u) return;
    idx = chunk_lower_bound(d, chunk_id);
    if (idx < d->chunk_count && d->chunks[idx].chunk_id == chunk_id) {
        d->chunks[idx].dirty = D_FALSE;
    }
}

void dg_decor_dirty_clear_rulepack(dg_decor_dirty *d, dg_decor_rulepack_id rulepack_id) {
    u32 idx;
    if (!d || rulepack_id == 0u) return;
    idx = rulepack_lower_bound(d, rulepack_id);
    if (idx < d->rulepack_count && d->rulepacks[idx].rulepack_id == rulepack_id) {
        d->rulepacks[idx].dirty = D_FALSE;
    }
}

