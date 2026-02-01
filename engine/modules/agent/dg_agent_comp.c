/*
FILE: source/domino/agent/dg_agent_comp.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / agent/dg_agent_comp
RESPONSIBILITY: Implements `dg_agent_comp`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
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

#include "agent/dg_agent_comp.h"

static int dg_agent_comp_kind_cmp(const dg_agent_comp_kind *a, const dg_agent_comp_kind *b) {
    if (a->desc.kind_id < b->desc.kind_id) return -1;
    if (a->desc.kind_id > b->desc.kind_id) return 1;
    return 0;
}

static u32 dg_agent_comp_kind_lower_bound(const dg_agent_comp_registry *reg, dg_type_id kind_id, int *out_found) {
    u32 lo = 0u;
    u32 hi;
    u32 mid;
    int cmp;
    dg_agent_comp_kind key;

    if (out_found) {
        *out_found = 0;
    }
    if (!reg || reg->count == 0u) {
        return 0u;
    }

    memset(&key, 0, sizeof(key));
    key.desc.kind_id = kind_id;

    hi = reg->count;
    while (lo < hi) {
        mid = lo + ((hi - lo) / 2u);
        cmp = dg_agent_comp_kind_cmp(&reg->kinds[mid], &key);
        if (cmp < 0) {
            lo = mid + 1u;
        } else {
            hi = mid;
        }
    }

    if (lo < reg->count) {
        cmp = dg_agent_comp_kind_cmp(&reg->kinds[lo], &key);
        if (cmp == 0 && out_found) {
            *out_found = 1;
        }
    }
    return lo;
}

static int dg_agent_comp_id_cmp_for_kind(const dg_agent_comp_kind *k, dg_comp_id a, dg_comp_id b) {
    u32 ia;
    u32 ib;
    dg_domain_id da, db;
    dg_chunk_id ca, cb;
    dg_agent_id oa, ob;

    if (!k || a == 0u || b == 0u) {
        return 0;
    }

    ia = (u32)(a - 1u);
    ib = (u32)(b - 1u);

    da = k->domain_id[ia];
    db = k->domain_id[ib];
    if (da < db) return -1;
    if (da > db) return 1;

    ca = k->chunk_id[ia];
    cb = k->chunk_id[ib];
    if (ca < cb) return -1;
    if (ca > cb) return 1;

    oa = k->owner_agent[ia];
    ob = k->owner_agent[ib];
    if (oa < ob) return -1;
    if (oa > ob) return 1;

    if (a < b) return -1;
    if (a > b) return 1;
    return 0;
}

static void dg_agent_comp_kind_storage_free(dg_agent_comp_kind *k) {
    if (!k) {
        return;
    }
    if (k->data) free(k->data);
    if (k->owner_agent) free(k->owner_agent);
    if (k->domain_id) free(k->domain_id);
    if (k->chunk_id) free(k->chunk_id);
    if (k->active_ids) free(k->active_ids);
    if (k->free_ids) free(k->free_ids);
    memset(k, 0, sizeof(*k));
}

static int dg_agent_comp_kind_storage_alloc(dg_agent_comp_kind *k) {
    size_t data_bytes;
    u32 i;

    if (!k) {
        return -1;
    }

    if (k->desc.capacity == 0u) {
        k->data = (unsigned char *)0;
        k->owner_agent = (dg_agent_id *)0;
        k->domain_id = (dg_domain_id *)0;
        k->chunk_id = (dg_chunk_id *)0;
        k->active_ids = (dg_comp_id *)0;
        k->free_ids = (dg_comp_id *)0;
        k->active_count = 0u;
        k->free_count = 0u;
        return 0;
    }

    data_bytes = (size_t)k->desc.elem_size * (size_t)k->desc.capacity;
    if (data_bytes != 0u) {
        k->data = (unsigned char *)malloc(data_bytes);
        if (!k->data) {
            return -2;
        }
        memset(k->data, 0, data_bytes);
    } else {
        k->data = (unsigned char *)0;
    }

    k->owner_agent = (dg_agent_id *)malloc(sizeof(dg_agent_id) * (size_t)k->desc.capacity);
    k->domain_id = (dg_domain_id *)malloc(sizeof(dg_domain_id) * (size_t)k->desc.capacity);
    k->chunk_id = (dg_chunk_id *)malloc(sizeof(dg_chunk_id) * (size_t)k->desc.capacity);
    k->active_ids = (dg_comp_id *)malloc(sizeof(dg_comp_id) * (size_t)k->desc.capacity);
    k->free_ids = (dg_comp_id *)malloc(sizeof(dg_comp_id) * (size_t)k->desc.capacity);

    if (!k->owner_agent || !k->domain_id || !k->chunk_id || !k->active_ids || !k->free_ids) {
        return -3;
    }

    memset(k->owner_agent, 0, sizeof(dg_agent_id) * (size_t)k->desc.capacity);
    memset(k->domain_id, 0, sizeof(dg_domain_id) * (size_t)k->desc.capacity);
    memset(k->chunk_id, 0, sizeof(dg_chunk_id) * (size_t)k->desc.capacity);
    memset(k->active_ids, 0, sizeof(dg_comp_id) * (size_t)k->desc.capacity);
    memset(k->free_ids, 0, sizeof(dg_comp_id) * (size_t)k->desc.capacity);

    k->active_count = 0u;
    k->free_count = k->desc.capacity;
    for (i = 0u; i < k->desc.capacity; ++i) {
        k->free_ids[i] = (dg_comp_id)(i + 1u);
    }

    return 0;
}

void dg_agent_comp_registry_init(dg_agent_comp_registry *reg) {
    if (!reg) {
        return;
    }
    reg->kinds = (dg_agent_comp_kind *)0;
    reg->count = 0u;
    reg->capacity = 0u;
}

void dg_agent_comp_registry_free(dg_agent_comp_registry *reg) {
    u32 i;
    if (!reg) {
        return;
    }
    if (reg->kinds) {
        for (i = 0u; i < reg->count; ++i) {
            dg_agent_comp_kind_storage_free(&reg->kinds[i]);
        }
        free(reg->kinds);
    }
    dg_agent_comp_registry_init(reg);
}

int dg_agent_comp_registry_reserve(dg_agent_comp_registry *reg, u32 kind_capacity) {
    dg_agent_comp_kind *kinds;
    if (!reg) {
        return -1;
    }
    if (kind_capacity <= reg->capacity) {
        return 0;
    }
    kinds = (dg_agent_comp_kind *)realloc(reg->kinds, sizeof(dg_agent_comp_kind) * (size_t)kind_capacity);
    if (!kinds) {
        return -2;
    }
    reg->kinds = kinds;
    reg->capacity = kind_capacity;
    return 0;
}

int dg_agent_comp_registry_register_kind(dg_agent_comp_registry *reg, const dg_agent_comp_kind_desc *desc) {
    dg_agent_comp_kind k;
    u32 idx;
    int found;
    int rc;

    if (!reg || !desc) {
        return -1;
    }
    if (desc->kind_id == 0u) {
        return -2;
    }

    memset(&k, 0, sizeof(k));
    k.desc = *desc;
    k.probe_refused_alloc = 0u;

    idx = dg_agent_comp_kind_lower_bound(reg, desc->kind_id, &found);
    if (found) {
        return -3;
    }

    if (reg->count >= reg->capacity) {
        u32 new_cap = (reg->capacity == 0u) ? 8u : (reg->capacity * 2u);
        rc = dg_agent_comp_registry_reserve(reg, new_cap);
        if (rc != 0) {
            return -4;
        }
    }

    rc = dg_agent_comp_kind_storage_alloc(&k);
    if (rc != 0) {
        dg_agent_comp_kind_storage_free(&k);
        return -5;
    }

    if (idx < reg->count) {
        memmove(&reg->kinds[idx + 1u], &reg->kinds[idx],
                sizeof(dg_agent_comp_kind) * (size_t)(reg->count - idx));
    }
    reg->kinds[idx] = k;
    reg->count += 1u;
    return 0;
}

u32 dg_agent_comp_registry_count(const dg_agent_comp_registry *reg) {
    return reg ? reg->count : 0u;
}

const dg_agent_comp_kind *dg_agent_comp_registry_at(const dg_agent_comp_registry *reg, u32 index) {
    if (!reg || !reg->kinds || index >= reg->count) {
        return (const dg_agent_comp_kind *)0;
    }
    return &reg->kinds[index];
}

dg_agent_comp_kind *dg_agent_comp_registry_find_mut(dg_agent_comp_registry *reg, dg_type_id kind_id) {
    u32 idx;
    int found;
    if (!reg || !reg->kinds || reg->count == 0u) {
        return (dg_agent_comp_kind *)0;
    }
    idx = dg_agent_comp_kind_lower_bound(reg, kind_id, &found);
    if (!found) {
        return (dg_agent_comp_kind *)0;
    }
    return &reg->kinds[idx];
}

const dg_agent_comp_kind *dg_agent_comp_registry_find(const dg_agent_comp_registry *reg, dg_type_id kind_id) {
    u32 idx;
    int found;
    if (!reg || !reg->kinds || reg->count == 0u) {
        return (const dg_agent_comp_kind *)0;
    }
    idx = dg_agent_comp_kind_lower_bound(reg, kind_id, &found);
    if (!found) {
        return (const dg_agent_comp_kind *)0;
    }
    return &reg->kinds[idx];
}

dg_comp_id dg_agent_comp_alloc(
    dg_agent_comp_registry *reg,
    dg_type_id              kind_id,
    dg_agent_id             owner_agent,
    dg_domain_id            domain_id,
    dg_chunk_id             chunk_id
) {
    dg_agent_comp_kind *k;
    dg_comp_id cid;
    u32 slot;
    u32 ins;

    if (!reg || kind_id == 0u || owner_agent == 0u) {
        return 0u;
    }
    k = dg_agent_comp_registry_find_mut(reg, kind_id);
    if (!k || k->desc.capacity == 0u) {
        return 0u;
    }
    if (k->free_count == 0u) {
        k->probe_refused_alloc += 1u;
        return 0u;
    }

    /* Deterministic: pop from end of prefilled free-id stack. */
    k->free_count -= 1u;
    cid = k->free_ids[k->free_count];
    slot = (u32)(cid - 1u);

    k->owner_agent[slot] = owner_agent;
    k->domain_id[slot] = domain_id;
    k->chunk_id[slot] = chunk_id;

    /* Deterministic insertion by canonical (domain,chunk,owner,id). */
    ins = k->active_count;
    while (ins > 0u) {
        dg_comp_id prev = k->active_ids[ins - 1u];
        if (dg_agent_comp_id_cmp_for_kind(k, prev, cid) <= 0) {
            break;
        }
        k->active_ids[ins] = prev;
        ins -= 1u;
    }
    k->active_ids[ins] = cid;
    k->active_count += 1u;

    return cid;
}

int dg_agent_comp_free(dg_agent_comp_registry *reg, dg_type_id kind_id, dg_comp_id comp_id) {
    dg_agent_comp_kind *k;
    u32 slot;
    u32 i;
    size_t data_bytes;

    if (!reg || kind_id == 0u || comp_id == 0u) {
        return -1;
    }
    k = dg_agent_comp_registry_find_mut(reg, kind_id);
    if (!k || k->desc.capacity == 0u) {
        return -2;
    }
    if (comp_id < 1u || comp_id > k->desc.capacity) {
        return -3;
    }
    slot = (u32)(comp_id - 1u);
    if (k->owner_agent[slot] == 0u) {
        return -4;
    }

    /* Remove from active list (bounded linear scan). */
    for (i = 0u; i < k->active_count; ++i) {
        if (k->active_ids[i] == comp_id) {
            break;
        }
    }
    if (i >= k->active_count) {
        return -5;
    }
    if (i + 1u < k->active_count) {
        memmove(&k->active_ids[i], &k->active_ids[i + 1u], sizeof(dg_comp_id) * (size_t)(k->active_count - (i + 1u)));
    }
    k->active_count -= 1u;

    /* Clear slot for determinism and safety. */
    k->owner_agent[slot] = 0u;
    k->domain_id[slot] = 0u;
    k->chunk_id[slot] = 0u;
    data_bytes = (size_t)k->desc.elem_size;
    if (k->data && data_bytes != 0u) {
        memset(k->data + (data_bytes * (size_t)slot), 0, data_bytes);
    }

    /* Push back onto free stack (bounded). */
    if (k->free_count < k->desc.capacity) {
        k->free_ids[k->free_count] = comp_id;
        k->free_count += 1u;
    }

    return 0;
}

void *dg_agent_comp_data(dg_agent_comp_registry *reg, dg_type_id kind_id, dg_comp_id comp_id) {
    dg_agent_comp_kind *k;
    u32 slot;
    size_t stride;
    if (!reg || kind_id == 0u || comp_id == 0u) {
        return (void *)0;
    }
    k = dg_agent_comp_registry_find_mut(reg, kind_id);
    if (!k || !k->data || k->desc.elem_size == 0u) {
        return (void *)0;
    }
    if (comp_id < 1u || comp_id > k->desc.capacity) {
        return (void *)0;
    }
    slot = (u32)(comp_id - 1u);
    if (k->owner_agent[slot] == 0u) {
        return (void *)0;
    }
    stride = (size_t)k->desc.elem_size;
    return (void *)(k->data + (stride * (size_t)slot));
}

const void *dg_agent_comp_data_const(const dg_agent_comp_registry *reg, dg_type_id kind_id, dg_comp_id comp_id) {
    const dg_agent_comp_kind *k;
    u32 slot;
    size_t stride;
    if (!reg || kind_id == 0u || comp_id == 0u) {
        return (const void *)0;
    }
    k = dg_agent_comp_registry_find(reg, kind_id);
    if (!k || !k->data || k->desc.elem_size == 0u) {
        return (const void *)0;
    }
    if (comp_id < 1u || comp_id > k->desc.capacity) {
        return (const void *)0;
    }
    slot = (u32)(comp_id - 1u);
    if (k->owner_agent[slot] == 0u) {
        return (const void *)0;
    }
    stride = (size_t)k->desc.elem_size;
    return (const void *)(k->data + (stride * (size_t)slot));
}

dg_agent_id dg_agent_comp_owner(const dg_agent_comp_registry *reg, dg_type_id kind_id, dg_comp_id comp_id) {
    const dg_agent_comp_kind *k;
    u32 slot;
    if (!reg || kind_id == 0u || comp_id == 0u) {
        return 0u;
    }
    k = dg_agent_comp_registry_find(reg, kind_id);
    if (!k || !k->owner_agent) {
        return 0u;
    }
    if (comp_id < 1u || comp_id > k->desc.capacity) {
        return 0u;
    }
    slot = (u32)(comp_id - 1u);
    return k->owner_agent[slot];
}

dg_domain_id dg_agent_comp_domain(const dg_agent_comp_registry *reg, dg_type_id kind_id, dg_comp_id comp_id) {
    const dg_agent_comp_kind *k;
    u32 slot;
    if (!reg || kind_id == 0u || comp_id == 0u) {
        return 0u;
    }
    k = dg_agent_comp_registry_find(reg, kind_id);
    if (!k || !k->domain_id) {
        return 0u;
    }
    if (comp_id < 1u || comp_id > k->desc.capacity) {
        return 0u;
    }
    slot = (u32)(comp_id - 1u);
    return k->domain_id[slot];
}

dg_chunk_id dg_agent_comp_chunk(const dg_agent_comp_registry *reg, dg_type_id kind_id, dg_comp_id comp_id) {
    const dg_agent_comp_kind *k;
    u32 slot;
    if (!reg || kind_id == 0u || comp_id == 0u) {
        return 0u;
    }
    k = dg_agent_comp_registry_find(reg, kind_id);
    if (!k || !k->chunk_id) {
        return 0u;
    }
    if (comp_id < 1u || comp_id > k->desc.capacity) {
        return 0u;
    }
    slot = (u32)(comp_id - 1u);
    return k->chunk_id[slot];
}

u32 dg_agent_comp_active_count(const dg_agent_comp_registry *reg, dg_type_id kind_id) {
    const dg_agent_comp_kind *k;
    if (!reg || kind_id == 0u) {
        return 0u;
    }
    k = dg_agent_comp_registry_find(reg, kind_id);
    return k ? k->active_count : 0u;
}

dg_comp_id dg_agent_comp_active_at(const dg_agent_comp_registry *reg, dg_type_id kind_id, u32 index) {
    const dg_agent_comp_kind *k;
    if (!reg || kind_id == 0u) {
        return 0u;
    }
    k = dg_agent_comp_registry_find(reg, kind_id);
    if (!k || !k->active_ids || index >= k->active_count) {
        return 0u;
    }
    return k->active_ids[index];
}

u32 dg_agent_comp_probe_refused_alloc(const dg_agent_comp_registry *reg, dg_type_id kind_id) {
    const dg_agent_comp_kind *k;
    if (!reg || kind_id == 0u) {
        return 0u;
    }
    k = dg_agent_comp_registry_find(reg, kind_id);
    return k ? k->probe_refused_alloc : 0u;
}

