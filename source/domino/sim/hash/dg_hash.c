#include <string.h>

#include "sim/hash/dg_hash.h"

void dg_hash_snapshot_init(dg_hash_snapshot *s, dg_hash_snapshot_entry *storage, u32 capacity) {
    if (!s) {
        return;
    }
    s->entries = storage;
    s->count = 0u;
    s->capacity = capacity;
}

void dg_hash_snapshot_clear(dg_hash_snapshot *s) {
    if (!s) {
        return;
    }
    s->count = 0u;
}

const dg_hash_snapshot_entry *dg_hash_snapshot_at(const dg_hash_snapshot *s, u32 index) {
    if (!s || !s->entries || index >= s->count) {
        return (const dg_hash_snapshot_entry *)0;
    }
    return &s->entries[index];
}

const dg_hash_snapshot_entry *dg_hash_snapshot_find(const dg_hash_snapshot *s, dg_hash_domain_id domain_id) {
    u32 lo;
    u32 hi;
    u32 mid;

    if (!s || !s->entries || s->count == 0u) {
        return (const dg_hash_snapshot_entry *)0;
    }

    lo = 0u;
    hi = s->count;
    while (lo < hi) {
        mid = lo + ((hi - lo) / 2u);
        if (s->entries[mid].domain_id < domain_id) {
            lo = mid + 1u;
        } else {
            hi = mid;
        }
    }
    if (lo < s->count && s->entries[lo].domain_id == domain_id) {
        return &s->entries[lo];
    }
    return (const dg_hash_snapshot_entry *)0;
}

