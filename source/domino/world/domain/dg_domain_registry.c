#include <stdlib.h>
#include <string.h>

#include "world/domain/dg_domain_registry.h"

#include "core/dg_det_hash.h"
#include "sim/sched/dg_sched.h"

void dg_domain_registry_init(dg_domain_registry *reg) {
    if (!reg) {
        return;
    }
    reg->entries = (dg_domain_registry_entry *)0;
    reg->count = 0u;
    reg->capacity = 0u;
    reg->next_insert_index = 0u;
    reg->probe_refused = 0u;
}

void dg_domain_registry_free(dg_domain_registry *reg) {
    if (!reg) {
        return;
    }
    if (reg->entries) {
        free(reg->entries);
    }
    dg_domain_registry_init(reg);
}

int dg_domain_registry_reserve(dg_domain_registry *reg, u32 capacity) {
    dg_domain_registry_entry *new_entries;
    if (!reg) {
        return -1;
    }
    if (capacity <= reg->capacity) {
        return 0;
    }
    new_entries = (dg_domain_registry_entry *)realloc(reg->entries, sizeof(dg_domain_registry_entry) * (size_t)capacity);
    if (!new_entries) {
        return -2;
    }
    reg->entries = new_entries;
    reg->capacity = capacity;
    return 0;
}

static int dg_domain_registry_entry_cmp(const dg_domain_registry_entry *a, const dg_domain_registry_entry *b) {
    if (a->domain_id < b->domain_id) return -1;
    if (a->domain_id > b->domain_id) return 1;
    if (a->insert_index < b->insert_index) return -1;
    if (a->insert_index > b->insert_index) return 1;
    return 0;
}

static u32 dg_domain_registry_lower_bound(const dg_domain_registry *reg, const dg_domain_registry_entry *key, int *out_found) {
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
        cmp = dg_domain_registry_entry_cmp(&reg->entries[mid], key);
        if (cmp < 0) {
            lo = mid + 1u;
        } else {
            hi = mid;
        }
    }

    if (lo < reg->count) {
        if (reg->entries[lo].domain_id == key->domain_id && out_found) {
            *out_found = 1;
        }
    }
    return lo;
}

int dg_domain_registry_add(dg_domain_registry *reg, dg_domain *domain) {
    dg_domain_registry_entry e;
    u32 idx;
    int found;
    int rc;

    if (!reg || !domain) {
        return -1;
    }
    if (!dg_domain_is_valid(domain)) {
        return -2;
    }

    memset(&e, 0, sizeof(e));
    e.domain_id = domain->domain_id;
    e.domain = domain;
    e.insert_index = reg->next_insert_index++;

    idx = dg_domain_registry_lower_bound(reg, &e, &found);
    if (found) {
        return -3; /* duplicate domain_id */
    }

    if (reg->count >= reg->capacity) {
        u32 new_cap = (reg->capacity == 0u) ? 16u : (reg->capacity * 2u);
        rc = dg_domain_registry_reserve(reg, new_cap);
        if (rc != 0) {
            reg->probe_refused += 1u;
            return -4;
        }
    }

    if (idx < reg->count) {
        memmove(&reg->entries[idx + 1u], &reg->entries[idx],
                sizeof(dg_domain_registry_entry) * (size_t)(reg->count - idx));
    }
    reg->entries[idx] = e;
    reg->count += 1u;
    return 0;
}

u32 dg_domain_registry_count(const dg_domain_registry *reg) {
    return reg ? reg->count : 0u;
}

const dg_domain_registry_entry *dg_domain_registry_at(const dg_domain_registry *reg, u32 index) {
    if (!reg || !reg->entries || index >= reg->count) {
        return (const dg_domain_registry_entry *)0;
    }
    return &reg->entries[index];
}

const dg_domain_registry_entry *dg_domain_registry_find(const dg_domain_registry *reg, dg_domain_id domain_id) {
    dg_domain_registry_entry key;
    u32 idx;
    int found;

    if (!reg || !reg->entries || reg->count == 0u) {
        return (const dg_domain_registry_entry *)0;
    }

    memset(&key, 0, sizeof(key));
    key.domain_id = domain_id;
    key.insert_index = 0u;
    idx = dg_domain_registry_lower_bound(reg, &key, &found);
    if (!found || idx >= reg->count) {
        return (const dg_domain_registry_entry *)0;
    }
    return &reg->entries[idx];
}

u32 dg_domain_registry_probe_refused(const dg_domain_registry *reg) {
    return reg ? reg->probe_refused : 0u;
}

void dg_domain_registry_step_phase(dg_domain_registry *reg, dg_phase phase, dg_budget *budget) {
    u32 i;

    if (!reg) {
        return;
    }
    if (phase != DG_PH_TOPOLOGY && phase != DG_PH_SOLVE) {
        return;
    }

    for (i = 0u; i < reg->count; ++i) {
        dg_domain_registry_entry *e = &reg->entries[i];
        if (!e->domain) {
            continue;
        }
        dg_domain_step_phase(e->domain, phase, budget);
    }
}

static u64 dg_domain_registry_hash_step(u64 h, u64 v) {
    return dg_det_hash_u64(h ^ v);
}

u64 dg_domain_registry_hash_state(const dg_domain_registry *reg) {
    u64 h = 0xD06A1D0D06A1D0D1ULL;
    u32 i;

    if (!reg || !reg->entries) {
        return h;
    }

    h = dg_domain_registry_hash_step(h, (u64)reg->count);
    for (i = 0u; i < reg->count; ++i) {
        const dg_domain_registry_entry *e = &reg->entries[i];
        u64 dh = 0u;
        if (!e->domain) {
            continue;
        }
        dh = dg_domain_hash_state(e->domain);
        h = dg_domain_registry_hash_step(h, (u64)e->domain_id);
        h = dg_domain_registry_hash_step(h, dh);
    }

    return h;
}

void dg_domain_registry_phase_handler(struct dg_sched *sched, void *user_ctx) {
    dg_domain_registry *reg = (dg_domain_registry *)user_ctx;
    if (!sched || !reg) {
        return;
    }
    dg_domain_registry_step_phase(reg, sched->current_phase, &sched->budget);
}

