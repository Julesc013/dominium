/*
FILE: source/domino/sim/prop/dg_prop_registry.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / sim/prop/dg_prop_registry
RESPONSIBILITY: Implements `dg_prop_registry`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
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

#include "sim/prop/dg_prop_registry.h"

#include "core/det_invariants.h"
#include "core/dg_det_hash.h"
#include "sim/sched/dg_sched.h"

void dg_prop_registry_init(dg_prop_registry *reg) {
    if (!reg) {
        return;
    }
    reg->entries = (dg_prop_registry_entry *)0;
    reg->count = 0u;
    reg->capacity = 0u;
    reg->next_insert_index = 0u;
    reg->probe_refused = 0u;
}

void dg_prop_registry_free(dg_prop_registry *reg) {
    if (!reg) {
        return;
    }
    if (reg->entries) {
        free(reg->entries);
    }
    dg_prop_registry_init(reg);
}

int dg_prop_registry_reserve(dg_prop_registry *reg, u32 capacity) {
    dg_prop_registry_entry *new_entries;
    if (!reg) {
        return -1;
    }
    if (capacity <= reg->capacity) {
        return 0;
    }
    new_entries = (dg_prop_registry_entry *)realloc(reg->entries, sizeof(dg_prop_registry_entry) * (size_t)capacity);
    if (!new_entries) {
        return -2;
    }
    reg->entries = new_entries;
    reg->capacity = capacity;
    return 0;
}

static int dg_prop_registry_entry_cmp(const dg_prop_registry_entry *a, const dg_prop_registry_entry *b) {
    if (a->domain_id < b->domain_id) return -1;
    if (a->domain_id > b->domain_id) return 1;
    if (a->prop_id < b->prop_id) return -1;
    if (a->prop_id > b->prop_id) return 1;
    if (a->insert_index < b->insert_index) return -1;
    if (a->insert_index > b->insert_index) return 1;
    return 0;
}

static u32 dg_prop_registry_lower_bound(const dg_prop_registry *reg, const dg_prop_registry_entry *key, int *out_found) {
    u32 lo = 0u;
    u32 hi;
    u32 mid;
    int cmp;

    if (out_found) {
        *out_found = 0;
    }
    if (!reg || !reg->entries || reg->count == 0u) {
        return 0u;
    }

    hi = reg->count;
    while (lo < hi) {
        mid = lo + ((hi - lo) / 2u);
        cmp = dg_prop_registry_entry_cmp(&reg->entries[mid], key);
        if (cmp < 0) {
            lo = mid + 1u;
        } else {
            hi = mid;
        }
    }

    if (lo < reg->count) {
        if (reg->entries[lo].domain_id == key->domain_id && reg->entries[lo].prop_id == key->prop_id && out_found) {
            *out_found = 1;
        }
    }
    return lo;
}

int dg_prop_registry_add(dg_prop_registry *reg, dg_prop *prop) {
    dg_prop_registry_entry e;
    u32 idx;
    int found;
    int rc;

    if (!reg || !prop) {
        return -1;
    }
    if (!dg_prop_is_valid(prop)) {
        return -2;
    }

    memset(&e, 0, sizeof(e));
    e.domain_id = prop->domain_id;
    e.prop_id = prop->prop_id;
    e.prop = prop;
    e.insert_index = reg->next_insert_index++;

    idx = dg_prop_registry_lower_bound(reg, &e, &found);
    if (found) {
        return -3; /* duplicate (domain_id, prop_id) */
    }

    if (reg->count >= reg->capacity) {
        u32 new_cap = (reg->capacity == 0u) ? 16u : (reg->capacity * 2u);
        rc = dg_prop_registry_reserve(reg, new_cap);
        if (rc != 0) {
            reg->probe_refused += 1u;
            return -4;
        }
    }

    if (idx < reg->count) {
        memmove(&reg->entries[idx + 1u], &reg->entries[idx],
                sizeof(dg_prop_registry_entry) * (size_t)(reg->count - idx));
    }
    reg->entries[idx] = e;
    reg->count += 1u;
    return 0;
}

u32 dg_prop_registry_count(const dg_prop_registry *reg) {
    return reg ? reg->count : 0u;
}

const dg_prop_registry_entry *dg_prop_registry_at(const dg_prop_registry *reg, u32 index) {
    if (!reg || !reg->entries || index >= reg->count) {
        return (const dg_prop_registry_entry *)0;
    }
    return &reg->entries[index];
}

const dg_prop_registry_entry *dg_prop_registry_find(const dg_prop_registry *reg, dg_domain_id domain_id, dg_prop_id prop_id) {
    dg_prop_registry_entry key;
    u32 idx;
    int found;

    if (!reg || !reg->entries || reg->count == 0u) {
        return (const dg_prop_registry_entry *)0;
    }

    memset(&key, 0, sizeof(key));
    key.domain_id = domain_id;
    key.prop_id = prop_id;
    idx = dg_prop_registry_lower_bound(reg, &key, &found);
    if (!found || idx >= reg->count) {
        return (const dg_prop_registry_entry *)0;
    }
    return &reg->entries[idx];
}

u32 dg_prop_registry_probe_refused(const dg_prop_registry *reg) {
    return reg ? reg->probe_refused : 0u;
}

void dg_prop_registry_step(dg_prop_registry *reg, dg_tick tick, dg_budget *budget) {
    u32 i;
    if (!reg) return;
#ifndef NDEBUG
    for (i = 1u; i < reg->count; ++i) {
        const dg_prop_registry_entry *a = &reg->entries[i - 1u];
        const dg_prop_registry_entry *b = &reg->entries[i];
        DG_DET_GUARD_ITER_ORDER(
            (a->domain_id < b->domain_id) ||
            (a->domain_id == b->domain_id && a->prop_id < b->prop_id)
        );
    }
#endif
    for (i = 0u; i < reg->count; ++i) {
        dg_prop_registry_entry *e = &reg->entries[i];
        if (!e->prop) continue;
        dg_prop_step(e->prop, tick, budget);
    }
}

static u64 dg_prop_registry_hash_step(u64 h, u64 v) {
    return dg_det_hash_u64(h ^ v);
}

u64 dg_prop_registry_hash_state(const dg_prop_registry *reg) {
    u64 h = 0x9BADC0FFEE0DDF00ULL;
    u32 i;

    if (!reg || !reg->entries) {
        return h;
    }

#ifndef NDEBUG
    for (i = 1u; i < reg->count; ++i) {
        const dg_prop_registry_entry *a = &reg->entries[i - 1u];
        const dg_prop_registry_entry *b = &reg->entries[i];
        DG_DET_GUARD_ITER_ORDER(
            (a->domain_id < b->domain_id) ||
            (a->domain_id == b->domain_id && a->prop_id < b->prop_id)
        );
    }
#endif

    h = dg_prop_registry_hash_step(h, (u64)reg->count);
    for (i = 0u; i < reg->count; ++i) {
        const dg_prop_registry_entry *e = &reg->entries[i];
        u64 ph = 0u;
        if (!e->prop) continue;
        ph = dg_prop_hash_state(e->prop);
        h = dg_prop_registry_hash_step(h, (u64)e->domain_id);
        h = dg_prop_registry_hash_step(h, (u64)e->prop_id);
        h = dg_prop_registry_hash_step(h, ph);
    }

    return h;
}

void dg_prop_registry_solve_phase_handler(struct dg_sched *sched, void *user_ctx) {
    dg_prop_registry *reg = (dg_prop_registry *)user_ctx;
    if (!sched || !reg) {
        return;
    }
    if (sched->current_phase != DG_PH_SOLVE) {
        return;
    }
    dg_prop_registry_step(reg, sched->tick, &sched->budget);
}
