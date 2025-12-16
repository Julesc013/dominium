/*
FILE: source/domino/sim/act/dg_action_registry.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / sim/act/dg_action_registry
RESPONSIBILITY: Implements `dg_action_registry`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
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

#include "sim/act/dg_action_registry.h"

static int dg_action_entry_cmp(const dg_action_registry_entry *a, const dg_action_registry_entry *b) {
    if (a->type_id < b->type_id) return -1;
    if (a->type_id > b->type_id) return 1;
    return 0;
}

void dg_action_registry_init(dg_action_registry *reg) {
    if (!reg) {
        return;
    }
    reg->entries = (dg_action_registry_entry *)0;
    reg->count = 0u;
    reg->capacity = 0u;
    reg->next_insert_index = 0u;
}

void dg_action_registry_free(dg_action_registry *reg) {
    if (!reg) {
        return;
    }
    if (reg->entries) {
        free(reg->entries);
    }
    dg_action_registry_init(reg);
}

int dg_action_registry_reserve(dg_action_registry *reg, u32 capacity) {
    dg_action_registry_entry *new_entries;
    if (!reg) {
        return -1;
    }
    if (capacity <= reg->capacity) {
        return 0;
    }
    new_entries = (dg_action_registry_entry *)realloc(reg->entries, sizeof(dg_action_registry_entry) * (size_t)capacity);
    if (!new_entries) {
        return -2;
    }
    reg->entries = new_entries;
    reg->capacity = capacity;
    return 0;
}

static u32 dg_action_registry_lower_bound(const dg_action_registry *reg, dg_type_id type_id, int *out_found) {
    u32 lo = 0u;
    u32 hi;
    u32 mid;
    int cmp;
    dg_action_registry_entry key;

    if (out_found) {
        *out_found = 0;
    }
    if (!reg || reg->count == 0u) {
        return 0u;
    }

    memset(&key, 0, sizeof(key));
    key.type_id = type_id;

    hi = reg->count;
    while (lo < hi) {
        mid = lo + ((hi - lo) / 2u);
        cmp = dg_action_entry_cmp(&reg->entries[mid], &key);
        if (cmp < 0) {
            lo = mid + 1u;
        } else {
            hi = mid;
        }
    }

    if (lo < reg->count) {
        cmp = dg_action_entry_cmp(&reg->entries[lo], &key);
        if (cmp == 0 && out_found) {
            *out_found = 1;
        }
    }
    return lo;
}

int dg_action_registry_add(
    dg_action_registry   *reg,
    dg_type_id            type_id,
    const dg_action_vtbl *vtbl,
    const char           *name
) {
    dg_action_registry_entry entry;
    u32 idx;
    int found;
    int rc;

    if (!reg || !vtbl || !vtbl->apply) {
        return -1;
    }
    if (type_id == 0u) {
        return -2;
    }

    memset(&entry, 0, sizeof(entry));
    entry.type_id = type_id;
    entry.vtbl = *vtbl;
    entry.name = name;
    entry.insert_index = reg->next_insert_index++;

    idx = dg_action_registry_lower_bound(reg, type_id, &found);
    if (found) {
        return -3;
    }

    if (reg->count >= reg->capacity) {
        u32 new_cap = (reg->capacity == 0u) ? 16u : (reg->capacity * 2u);
        rc = dg_action_registry_reserve(reg, new_cap);
        if (rc != 0) {
            return -4;
        }
    }

    if (idx < reg->count) {
        memmove(&reg->entries[idx + 1u], &reg->entries[idx],
                sizeof(dg_action_registry_entry) * (size_t)(reg->count - idx));
    }
    reg->entries[idx] = entry;
    reg->count += 1u;
    return 0;
}

u32 dg_action_registry_count(const dg_action_registry *reg) {
    return reg ? reg->count : 0u;
}

const dg_action_registry_entry *dg_action_registry_at(const dg_action_registry *reg, u32 index) {
    if (!reg || !reg->entries || index >= reg->count) {
        return (const dg_action_registry_entry *)0;
    }
    return &reg->entries[index];
}

const dg_action_registry_entry *dg_action_registry_find(const dg_action_registry *reg, dg_type_id type_id) {
    u32 idx;
    int found;
    if (!reg || !reg->entries || reg->count == 0u || type_id == 0u) {
        return (const dg_action_registry_entry *)0;
    }
    idx = dg_action_registry_lower_bound(reg, type_id, &found);
    if (!found) {
        return (const dg_action_registry_entry *)0;
    }
    return &reg->entries[idx];
}

