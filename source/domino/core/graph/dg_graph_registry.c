/*
FILE: source/domino/core/graph/dg_graph_registry.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / core/graph/dg_graph_registry
RESPONSIBILITY: Implements `dg_graph_registry`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
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

#include "core/graph/dg_graph_registry.h"

static u32 dg_graph_registry_type_lower_bound(const dg_graph_registry *r, dg_graph_type_id type_id) {
    u32 lo = 0u;
    u32 hi;
    u32 mid;
    if (!r || !r->types || r->type_count == 0u) {
        return 0u;
    }
    hi = r->type_count;
    while (lo < hi) {
        mid = lo + ((hi - lo) / 2u);
        if (r->types[mid].graph_type_id < type_id) {
            lo = mid + 1u;
        } else {
            hi = mid;
        }
    }
    return lo;
}

static int dg_graph_registry_instance_cmp_key(dg_graph_type_id ta, dg_graph_instance_id ia, dg_graph_type_id tb, dg_graph_instance_id ib) {
    if (ta < tb) return -1;
    if (ta > tb) return 1;
    if (ia < ib) return -1;
    if (ia > ib) return 1;
    return 0;
}

static u32 dg_graph_registry_instance_lower_bound(const dg_graph_registry *r, dg_graph_type_id type_id, dg_graph_instance_id inst_id) {
    u32 lo = 0u;
    u32 hi;
    u32 mid;
    if (!r || !r->instances || r->instance_count == 0u) {
        return 0u;
    }
    hi = r->instance_count;
    while (lo < hi) {
        int cmp;
        mid = lo + ((hi - lo) / 2u);
        cmp = dg_graph_registry_instance_cmp_key(
            r->instances[mid].graph_type_id, r->instances[mid].graph_instance_id,
            type_id, inst_id
        );
        if (cmp < 0) {
            lo = mid + 1u;
        } else {
            hi = mid;
        }
    }
    return lo;
}

static int dg_graph_registry_reserve_types(dg_graph_registry *r, u32 cap) {
    dg_graph_registry_type *t;
    if (!r) {
        return -1;
    }
    if (cap <= r->type_capacity) {
        return 0;
    }
    t = (dg_graph_registry_type *)realloc(r->types, sizeof(dg_graph_registry_type) * (size_t)cap);
    if (!t) {
        return -2;
    }
    if (cap > r->type_capacity) {
        memset(&t[r->type_capacity], 0, sizeof(dg_graph_registry_type) * (size_t)(cap - r->type_capacity));
    }
    r->types = t;
    r->type_capacity = cap;
    return 0;
}

static int dg_graph_registry_reserve_instances(dg_graph_registry *r, u32 cap) {
    dg_graph_registry_instance *it;
    if (!r) {
        return -1;
    }
    if (cap <= r->instance_capacity) {
        return 0;
    }
    it = (dg_graph_registry_instance *)realloc(r->instances, sizeof(dg_graph_registry_instance) * (size_t)cap);
    if (!it) {
        return -2;
    }
    if (cap > r->instance_capacity) {
        memset(&it[r->instance_capacity], 0, sizeof(dg_graph_registry_instance) * (size_t)(cap - r->instance_capacity));
    }
    r->instances = it;
    r->instance_capacity = cap;
    return 0;
}

void dg_graph_registry_init(dg_graph_registry *r) {
    if (!r) {
        return;
    }
    r->types = (dg_graph_registry_type *)0;
    r->type_count = 0u;
    r->type_capacity = 0u;
    r->next_type_insert_index = 0u;
    r->instances = (dg_graph_registry_instance *)0;
    r->instance_count = 0u;
    r->instance_capacity = 0u;
    r->next_instance_insert_index = 0u;
}

void dg_graph_registry_free(dg_graph_registry *r) {
    if (!r) {
        return;
    }
    if (r->types) {
        free(r->types);
    }
    if (r->instances) {
        free(r->instances);
    }
    dg_graph_registry_init(r);
}

int dg_graph_registry_reserve(dg_graph_registry *r, u32 type_capacity, u32 instance_capacity) {
    int rc;
    if (!r) {
        return -1;
    }
    rc = dg_graph_registry_reserve_types(r, type_capacity);
    if (rc != 0) {
        return -2;
    }
    rc = dg_graph_registry_reserve_instances(r, instance_capacity);
    if (rc != 0) {
        return -3;
    }
    return 0;
}

int dg_graph_registry_add_type(
    dg_graph_registry          *r,
    dg_graph_type_id            graph_type_id,
    dg_schema_id                node_schema_id,
    dg_schema_id                edge_schema_id,
    const dg_graph_rebuild_vtbl *rebuild_vtbl
) {
    dg_graph_registry_type t;
    u32 idx;
    int rc;

    if (!r || graph_type_id == 0u) {
        return -1;
    }

    idx = dg_graph_registry_type_lower_bound(r, graph_type_id);
    if (idx < r->type_count && r->types[idx].graph_type_id == graph_type_id) {
        return 1; /* already present */
    }

    if (r->type_count >= r->type_capacity) {
        u32 new_cap = (r->type_capacity == 0u) ? 32u : (r->type_capacity * 2u);
        if (new_cap < (r->type_count + 1u)) {
            new_cap = r->type_count + 1u;
        }
        rc = dg_graph_registry_reserve_types(r, new_cap);
        if (rc != 0) {
            return -2;
        }
    }

    memset(&t, 0, sizeof(t));
    t.graph_type_id = graph_type_id;
    t.node_schema_id = node_schema_id;
    t.edge_schema_id = edge_schema_id;
    if (rebuild_vtbl) {
        t.has_rebuild_vtbl = D_TRUE;
        t.rebuild_vtbl = *rebuild_vtbl;
    } else {
        t.has_rebuild_vtbl = D_FALSE;
        memset(&t.rebuild_vtbl, 0, sizeof(t.rebuild_vtbl));
    }
    t.insert_index = r->next_type_insert_index++;

    if (idx < r->type_count) {
        memmove(&r->types[idx + 1u], &r->types[idx],
                sizeof(dg_graph_registry_type) * (size_t)(r->type_count - idx));
    }
    r->types[idx] = t;
    r->type_count += 1u;
    return 0;
}

int dg_graph_registry_add_instance(
    dg_graph_registry     *r,
    dg_graph_type_id       graph_type_id,
    dg_graph_instance_id   graph_instance_id,
    dg_graph             *graph,
    void                 *user_ctx
) {
    dg_graph_registry_instance it;
    u32 idx;
    int rc;

    if (!r || graph_type_id == 0u || graph_instance_id == 0u) {
        return -1;
    }

    /* Require type registration (schema/vtbl). */
    if (!dg_graph_registry_find_type(r, graph_type_id)) {
        return -2;
    }

    idx = dg_graph_registry_instance_lower_bound(r, graph_type_id, graph_instance_id);
    if (idx < r->instance_count &&
        r->instances[idx].graph_type_id == graph_type_id &&
        r->instances[idx].graph_instance_id == graph_instance_id) {
        return 1; /* already present */
    }

    if (r->instance_count >= r->instance_capacity) {
        u32 new_cap = (r->instance_capacity == 0u) ? 64u : (r->instance_capacity * 2u);
        if (new_cap < (r->instance_count + 1u)) {
            new_cap = r->instance_count + 1u;
        }
        rc = dg_graph_registry_reserve_instances(r, new_cap);
        if (rc != 0) {
            return -3;
        }
    }

    memset(&it, 0, sizeof(it));
    it.graph_type_id = graph_type_id;
    it.graph_instance_id = graph_instance_id;
    it.graph = graph;
    it.user_ctx = user_ctx;
    it.insert_index = r->next_instance_insert_index++;

    if (idx < r->instance_count) {
        memmove(&r->instances[idx + 1u], &r->instances[idx],
                sizeof(dg_graph_registry_instance) * (size_t)(r->instance_count - idx));
    }
    r->instances[idx] = it;
    r->instance_count += 1u;
    return 0;
}

u32 dg_graph_registry_type_count(const dg_graph_registry *r) {
    return r ? r->type_count : 0u;
}

u32 dg_graph_registry_instance_count(const dg_graph_registry *r) {
    return r ? r->instance_count : 0u;
}

const dg_graph_registry_type *dg_graph_registry_type_at(const dg_graph_registry *r, u32 index) {
    if (!r || !r->types || index >= r->type_count) {
        return (const dg_graph_registry_type *)0;
    }
    return &r->types[index];
}

const dg_graph_registry_instance *dg_graph_registry_instance_at(const dg_graph_registry *r, u32 index) {
    if (!r || !r->instances || index >= r->instance_count) {
        return (const dg_graph_registry_instance *)0;
    }
    return &r->instances[index];
}

const dg_graph_registry_type *dg_graph_registry_find_type(const dg_graph_registry *r, dg_graph_type_id graph_type_id) {
    u32 idx;
    if (!r || !r->types || r->type_count == 0u) {
        return (const dg_graph_registry_type *)0;
    }
    idx = dg_graph_registry_type_lower_bound(r, graph_type_id);
    if (idx < r->type_count && r->types[idx].graph_type_id == graph_type_id) {
        return &r->types[idx];
    }
    return (const dg_graph_registry_type *)0;
}

const dg_graph_registry_instance *dg_graph_registry_find_instance(
    const dg_graph_registry *r,
    dg_graph_type_id         graph_type_id,
    dg_graph_instance_id     graph_instance_id
) {
    u32 idx;
    if (!r || !r->instances || r->instance_count == 0u) {
        return (const dg_graph_registry_instance *)0;
    }
    idx = dg_graph_registry_instance_lower_bound(r, graph_type_id, graph_instance_id);
    if (idx < r->instance_count &&
        r->instances[idx].graph_type_id == graph_type_id &&
        r->instances[idx].graph_instance_id == graph_instance_id) {
        return &r->instances[idx];
    }
    return (const dg_graph_registry_instance *)0;
}

