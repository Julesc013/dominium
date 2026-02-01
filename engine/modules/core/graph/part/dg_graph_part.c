/*
FILE: source/domino/core/graph/part/dg_graph_part.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / core/graph/part/dg_graph_part
RESPONSIBILITY: Implements `dg_graph_part`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
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

#include "core/graph/part/dg_graph_part.h"

static u32 dg_graph_part_node_map_lower_bound(const dg_graph_part *p, dg_node_id node_id) {
    u32 lo = 0u;
    u32 hi;
    u32 mid;
    if (!p || !p->node_map || p->node_map_count == 0u) {
        return 0u;
    }
    hi = p->node_map_count;
    while (lo < hi) {
        mid = lo + ((hi - lo) / 2u);
        if (p->node_map[mid].node_id < node_id) {
            lo = mid + 1u;
        } else {
            hi = mid;
        }
    }
    return lo;
}

static u32 dg_graph_part_parts_lower_bound(const dg_graph_part *p, dg_part_id part_id) {
    u32 lo = 0u;
    u32 hi;
    u32 mid;
    if (!p || !p->parts || p->part_count == 0u) {
        return 0u;
    }
    hi = p->part_count;
    while (lo < hi) {
        mid = lo + ((hi - lo) / 2u);
        if (p->parts[mid].part_id < part_id) {
            lo = mid + 1u;
        } else {
            hi = mid;
        }
    }
    return lo;
}

static int dg_graph_part_reserve_node_map(dg_graph_part *p, u32 cap) {
    dg_graph_part_node_map *nm;
    u32 old_cap;
    if (!p) {
        return -1;
    }
    if (cap <= p->node_map_capacity) {
        return 0;
    }
    old_cap = p->node_map_capacity;
    nm = (dg_graph_part_node_map *)realloc(p->node_map, sizeof(dg_graph_part_node_map) * (size_t)cap);
    if (!nm) {
        return -2;
    }
    if (cap > old_cap) {
        memset(&nm[old_cap], 0, sizeof(dg_graph_part_node_map) * (size_t)(cap - old_cap));
    }
    p->node_map = nm;
    p->node_map_capacity = cap;
    return 0;
}

static int dg_graph_part_reserve_parts(dg_graph_part *p, u32 cap) {
    dg_graph_part_entry *pe;
    u32 old_cap;
    if (!p) {
        return -1;
    }
    if (cap <= p->part_capacity) {
        return 0;
    }
    old_cap = p->part_capacity;
    pe = (dg_graph_part_entry *)realloc(p->parts, sizeof(dg_graph_part_entry) * (size_t)cap);
    if (!pe) {
        return -2;
    }
    if (cap > old_cap) {
        memset(&pe[old_cap], 0, sizeof(dg_graph_part_entry) * (size_t)(cap - old_cap));
    }
    p->parts = pe;
    p->part_capacity = cap;
    return 0;
}

static int dg_graph_part_entry_reserve_nodes(dg_graph_part_entry *e, u32 cap) {
    dg_node_id *ids;
    u32 old_cap;
    if (!e) {
        return -1;
    }
    if (cap <= e->node_capacity) {
        return 0;
    }
    old_cap = e->node_capacity;
    ids = (dg_node_id *)realloc(e->node_ids, sizeof(dg_node_id) * (size_t)cap);
    if (!ids) {
        return -2;
    }
    if (cap > old_cap) {
        memset(&ids[old_cap], 0, sizeof(dg_node_id) * (size_t)(cap - old_cap));
    }
    e->node_ids = ids;
    e->node_capacity = cap;
    return 0;
}

static int dg_graph_part_entry_insert_node(dg_graph_part_entry *e, dg_node_id node_id) {
    u32 lo = 0u;
    u32 hi;
    u32 mid;
    u32 idx;
    if (!e) {
        return -1;
    }
    hi = e->node_count;
    while (lo < hi) {
        mid = lo + ((hi - lo) / 2u);
        if (e->node_ids[mid] < node_id) {
            lo = mid + 1u;
        } else {
            hi = mid;
        }
    }
    idx = lo;
    if (idx < e->node_count && e->node_ids[idx] == node_id) {
        return 1; /* duplicate */
    }
    if (e->node_count >= e->node_capacity) {
        u32 new_cap = (e->node_capacity == 0u) ? 16u : (e->node_capacity * 2u);
        if (new_cap < (e->node_count + 1u)) {
            new_cap = e->node_count + 1u;
        }
        if (dg_graph_part_entry_reserve_nodes(e, new_cap) != 0) {
            return -2;
        }
    }
    if (idx < e->node_count) {
        memmove(&e->node_ids[idx + 1u], &e->node_ids[idx],
                sizeof(dg_node_id) * (size_t)(e->node_count - idx));
    }
    e->node_ids[idx] = node_id;
    e->node_count += 1u;
    return 0;
}

static int dg_graph_part_entry_remove_node(dg_graph_part_entry *e, dg_node_id node_id) {
    u32 lo = 0u;
    u32 hi;
    u32 mid;
    u32 idx;
    if (!e || e->node_count == 0u) {
        return 1;
    }
    hi = e->node_count;
    while (lo < hi) {
        mid = lo + ((hi - lo) / 2u);
        if (e->node_ids[mid] < node_id) {
            lo = mid + 1u;
        } else {
            hi = mid;
        }
    }
    idx = lo;
    if (idx >= e->node_count || e->node_ids[idx] != node_id) {
        return 1;
    }
    if ((idx + 1u) < e->node_count) {
        memmove(&e->node_ids[idx], &e->node_ids[idx + 1u],
                sizeof(dg_node_id) * (size_t)(e->node_count - (idx + 1u)));
    }
    e->node_count -= 1u;
    return 0;
}

void dg_graph_part_init(dg_graph_part *p) {
    if (!p) {
        return;
    }
    p->node_map = (dg_graph_part_node_map *)0;
    p->node_map_count = 0u;
    p->node_map_capacity = 0u;
    p->parts = (dg_graph_part_entry *)0;
    p->part_count = 0u;
    p->part_capacity = 0u;
}

void dg_graph_part_free(dg_graph_part *p) {
    u32 i;
    if (!p) {
        return;
    }
    if (p->parts) {
        for (i = 0u; i < p->part_count; ++i) {
            if (p->parts[i].node_ids) {
                free(p->parts[i].node_ids);
            }
            p->parts[i].node_ids = (dg_node_id *)0;
            p->parts[i].node_count = 0u;
            p->parts[i].node_capacity = 0u;
            p->parts[i].part_id = DG_PART_ID_INVALID;
        }
        free(p->parts);
    }
    if (p->node_map) {
        free(p->node_map);
    }
    dg_graph_part_init(p);
}

void dg_graph_part_clear(dg_graph_part *p) {
    u32 i;
    if (!p) {
        return;
    }
    /* Keep allocated storage but clear counts. */
    p->node_map_count = 0u;
    if (p->parts) {
        for (i = 0u; i < p->part_count; ++i) {
            p->parts[i].node_count = 0u;
        }
    }
    p->part_count = 0u;
}

int dg_graph_part_reserve(dg_graph_part *p, u32 node_map_capacity, u32 part_capacity) {
    int rc;
    if (!p) {
        return -1;
    }
    rc = dg_graph_part_reserve_node_map(p, node_map_capacity);
    if (rc != 0) {
        return -2;
    }
    rc = dg_graph_part_reserve_parts(p, part_capacity);
    if (rc != 0) {
        return -3;
    }
    return 0;
}

dg_part_id dg_graph_part_get_node_partition(const dg_graph_part *p, dg_node_id node_id) {
    u32 idx;
    if (!p || node_id == DG_NODE_ID_INVALID) {
        return DG_PART_ID_INVALID;
    }
    idx = dg_graph_part_node_map_lower_bound(p, node_id);
    if (idx < p->node_map_count && p->node_map[idx].node_id == node_id) {
        return p->node_map[idx].part_id;
    }
    return DG_PART_ID_INVALID;
}

u32 dg_graph_part_count(const dg_graph_part *p) {
    return p ? p->part_count : 0u;
}

const dg_graph_part_entry *dg_graph_part_at(const dg_graph_part *p, u32 index) {
    if (!p || !p->parts || index >= p->part_count) {
        return (const dg_graph_part_entry *)0;
    }
    return &p->parts[index];
}

const dg_graph_part_entry *dg_graph_part_find(const dg_graph_part *p, dg_part_id part_id) {
    u32 idx;
    if (!p || !p->parts || p->part_count == 0u) {
        return (const dg_graph_part_entry *)0;
    }
    idx = dg_graph_part_parts_lower_bound(p, part_id);
    if (idx < p->part_count && p->parts[idx].part_id == part_id) {
        return &p->parts[idx];
    }
    return (const dg_graph_part_entry *)0;
}

static dg_graph_part_entry *dg_graph_part_find_mut(dg_graph_part *p, dg_part_id part_id) {
    u32 idx;
    if (!p || !p->parts || p->part_count == 0u) {
        return (dg_graph_part_entry *)0;
    }
    idx = dg_graph_part_parts_lower_bound(p, part_id);
    if (idx < p->part_count && p->parts[idx].part_id == part_id) {
        return &p->parts[idx];
    }
    return (dg_graph_part_entry *)0;
}

static dg_graph_part_entry *dg_graph_part_ensure_part(dg_graph_part *p, dg_part_id part_id) {
    u32 idx;
    int rc;
    if (!p || part_id == DG_PART_ID_INVALID) {
        return (dg_graph_part_entry *)0;
    }
    if (p->part_count >= p->part_capacity) {
        u32 new_cap = (p->part_capacity == 0u) ? 8u : (p->part_capacity * 2u);
        if (new_cap < (p->part_count + 1u)) {
            new_cap = p->part_count + 1u;
        }
        rc = dg_graph_part_reserve_parts(p, new_cap);
        if (rc != 0) {
            return (dg_graph_part_entry *)0;
        }
    }
    idx = dg_graph_part_parts_lower_bound(p, part_id);
    if (idx < p->part_count && p->parts[idx].part_id == part_id) {
        return &p->parts[idx];
    }
    if (idx < p->part_count) {
        memmove(&p->parts[idx + 1u], &p->parts[idx],
                sizeof(dg_graph_part_entry) * (size_t)(p->part_count - idx));
    }
    memset(&p->parts[idx], 0, sizeof(dg_graph_part_entry));
    p->parts[idx].part_id = part_id;
    p->parts[idx].node_ids = (dg_node_id *)0;
    p->parts[idx].node_count = 0u;
    p->parts[idx].node_capacity = 0u;
    p->part_count += 1u;
    return &p->parts[idx];
}

int dg_graph_part_set_node(dg_graph_part *p, dg_node_id node_id, dg_part_id part_id) {
    u32 map_idx;
    d_bool has_old = D_FALSE;
    dg_part_id old_part = DG_PART_ID_INVALID;

    if (!p || node_id == DG_NODE_ID_INVALID) {
        return -1;
    }

    map_idx = dg_graph_part_node_map_lower_bound(p, node_id);
    if (map_idx < p->node_map_count && p->node_map[map_idx].node_id == node_id) {
        has_old = D_TRUE;
        old_part = p->node_map[map_idx].part_id;
    }

    if (has_old && old_part == part_id) {
        return 0;
    }

    /* Pre-reserve storage for inserts so we can fail without partial state. */
    if (!has_old && part_id != DG_PART_ID_INVALID) {
        if (p->node_map_count >= p->node_map_capacity) {
            u32 new_cap = (p->node_map_capacity == 0u) ? 32u : (p->node_map_capacity * 2u);
            if (new_cap < (p->node_map_count + 1u)) {
                new_cap = p->node_map_count + 1u;
            }
            if (dg_graph_part_reserve_node_map(p, new_cap) != 0) {
                return -2;
            }
        }
    }
    if (part_id != DG_PART_ID_INVALID) {
        dg_graph_part_entry *ne = dg_graph_part_find_mut(p, part_id);
        if (!ne) {
            ne = dg_graph_part_ensure_part(p, part_id);
            if (!ne) {
                return -3;
            }
        }
        /* Reserve in the new partition node list if needed. */
        if (ne->node_count >= ne->node_capacity) {
            u32 new_cap = (ne->node_capacity == 0u) ? 16u : (ne->node_capacity * 2u);
            if (new_cap < (ne->node_count + 1u)) {
                new_cap = ne->node_count + 1u;
            }
            if (dg_graph_part_entry_reserve_nodes(ne, new_cap) != 0) {
                return -4;
            }
        }
    }

    /* Remove from old partition list (if any). */
    if (has_old && old_part != DG_PART_ID_INVALID) {
        dg_graph_part_entry *oe = dg_graph_part_find_mut(p, old_part);
        if (oe) {
            (void)dg_graph_part_entry_remove_node(oe, node_id);
        }
    }

    if (part_id == DG_PART_ID_INVALID) {
        /* Unassign: remove from node_map. */
        if (has_old) {
            if ((map_idx + 1u) < p->node_map_count) {
                memmove(&p->node_map[map_idx], &p->node_map[map_idx + 1u],
                        sizeof(dg_graph_part_node_map) * (size_t)(p->node_map_count - (map_idx + 1u)));
            }
            p->node_map_count -= 1u;
        }
        return 0;
    }

    /* Insert into new partition list (canonical by node_id). */
    {
        dg_graph_part_entry *ne = dg_graph_part_find_mut(p, part_id);
        int rc;
        if (!ne) {
            return -5;
        }
        rc = dg_graph_part_entry_insert_node(ne, node_id);
        if (rc != 0 && rc != 1) {
            return -6;
        }
    }

    /* Update/insert node_map entry. */
    if (has_old) {
        p->node_map[map_idx].part_id = part_id;
        return 0;
    }
    if (map_idx < p->node_map_count) {
        memmove(&p->node_map[map_idx + 1u], &p->node_map[map_idx],
                sizeof(dg_graph_part_node_map) * (size_t)(p->node_map_count - map_idx));
    }
    p->node_map[map_idx].node_id = node_id;
    p->node_map[map_idx].part_id = part_id;
    p->node_map_count += 1u;
    return 0;
}

