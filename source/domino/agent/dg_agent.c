/*
FILE: source/domino/agent/dg_agent.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / agent/dg_agent
RESPONSIBILITY: Implements `dg_agent`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
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

#include "agent/dg_agent.h"

static u32 dg_agent_db_lower_bound(const dg_agent_db *db, dg_agent_id agent_id, int *out_found) {
    u32 lo = 0u;
    u32 hi;
    u32 mid;

    if (out_found) {
        *out_found = 0;
    }
    if (!db || db->count == 0u) {
        return 0u;
    }

    hi = db->count;
    while (lo < hi) {
        mid = lo + ((hi - lo) / 2u);
        if (db->agents[mid].agent_id < agent_id) {
            lo = mid + 1u;
        } else {
            hi = mid;
        }
    }

    if (lo < db->count && db->agents[lo].agent_id == agent_id) {
        if (out_found) {
            *out_found = 1;
        }
    }
    return lo;
}

static int dg_agent_record_find_comp(const dg_agent_record *a, dg_type_id kind_id, u32 *out_index) {
    u32 i;
    if (out_index) {
        *out_index = 0u;
    }
    if (!a || kind_id == 0u) {
        return -1;
    }
    for (i = 0u; i < a->comp_count; ++i) {
        if (a->comps[i].kind_id == kind_id) {
            if (out_index) {
                *out_index = i;
            }
            return 0;
        }
    }
    return -2;
}

void dg_agent_db_init(dg_agent_db *db) {
    if (!db) {
        return;
    }
    db->agents = (dg_agent_record *)0;
    db->count = 0u;
    db->capacity = 0u;
    db->next_agent_id = 1u;
    dg_agent_comp_registry_init(&db->comp_reg);
    db->probe_refused_agents = 0u;
    db->probe_refused_components = 0u;
}

void dg_agent_db_free(dg_agent_db *db) {
    if (!db) {
        return;
    }
    if (db->agents) {
        free(db->agents);
    }
    db->agents = (dg_agent_record *)0;
    db->count = 0u;
    db->capacity = 0u;
    db->next_agent_id = 1u;
    dg_agent_comp_registry_free(&db->comp_reg);
    db->probe_refused_agents = 0u;
    db->probe_refused_components = 0u;
}

int dg_agent_db_reserve(dg_agent_db *db, u32 agent_capacity, u32 comp_kind_capacity) {
    dg_agent_record *agents;
    int rc;

    if (!db) {
        return -1;
    }

    if (agent_capacity > db->capacity) {
        agents = (dg_agent_record *)realloc(db->agents, sizeof(dg_agent_record) * (size_t)agent_capacity);
        if (!agents) {
            return -2;
        }
        db->agents = agents;
        db->capacity = agent_capacity;
    }

    rc = dg_agent_comp_registry_reserve(&db->comp_reg, comp_kind_capacity);
    if (rc != 0) {
        return -3;
    }

    return 0;
}

int dg_agent_db_register_component_kind(dg_agent_db *db, const dg_agent_comp_kind_desc *desc) {
    if (!db) {
        return -1;
    }
    return dg_agent_comp_registry_register_kind(&db->comp_reg, desc);
}

int dg_agent_db_add(dg_agent_db *db, const dg_agent_record *init, dg_agent_id *out_agent_id) {
    dg_agent_record a;
    dg_agent_id id;
    u32 idx;
    int found;

    if (out_agent_id) {
        *out_agent_id = 0u;
    }
    if (!db || !init) {
        return -1;
    }

    a = *init;
    if (!dg_rep_state_is_valid(a.lod)) {
        a.lod = DG_REP_R0_FULL;
    }
    if (a.comp_count != 0u) {
        /* Must attach via dg_agent_db_attach_component(). */
        return -2;
    }

    if (a.agent_id != 0u) {
        id = a.agent_id;
        if (id >= db->next_agent_id) {
            db->next_agent_id = id + 1u;
        }
    } else {
        id = db->next_agent_id++;
        a.agent_id = id;
    }

    idx = dg_agent_db_lower_bound(db, id, &found);
    if (found) {
        return -3;
    }

    if (db->count >= db->capacity) {
        db->probe_refused_agents += 1u;
        return -4;
    }

    if (idx < db->count) {
        memmove(&db->agents[idx + 1u], &db->agents[idx],
                sizeof(dg_agent_record) * (size_t)(db->count - idx));
    }
    db->agents[idx] = a;
    db->count += 1u;

    if (out_agent_id) {
        *out_agent_id = id;
    }
    return 0;
}

int dg_agent_db_remove(dg_agent_db *db, dg_agent_id agent_id) {
    u32 idx;
    int found;
    u32 i;
    dg_agent_record *a;

    if (!db || agent_id == 0u) {
        return -1;
    }

    idx = dg_agent_db_lower_bound(db, agent_id, &found);
    if (!found) {
        return -2;
    }

    a = &db->agents[idx];
    for (i = 0u; i < a->comp_count; ++i) {
        (void)dg_agent_comp_free(&db->comp_reg, a->comps[i].kind_id, a->comps[i].comp_id);
    }

    if (idx + 1u < db->count) {
        memmove(&db->agents[idx], &db->agents[idx + 1u],
                sizeof(dg_agent_record) * (size_t)(db->count - (idx + 1u)));
    }
    db->count -= 1u;
    return 0;
}

u32 dg_agent_db_count(const dg_agent_db *db) {
    return db ? db->count : 0u;
}

const dg_agent_record *dg_agent_db_at(const dg_agent_db *db, u32 index) {
    if (!db || !db->agents || index >= db->count) {
        return (const dg_agent_record *)0;
    }
    return &db->agents[index];
}

dg_agent_record *dg_agent_db_find_mut(dg_agent_db *db, dg_agent_id agent_id) {
    u32 idx;
    int found;
    if (!db || !db->agents || db->count == 0u || agent_id == 0u) {
        return (dg_agent_record *)0;
    }
    idx = dg_agent_db_lower_bound(db, agent_id, &found);
    if (!found) {
        return (dg_agent_record *)0;
    }
    return &db->agents[idx];
}

const dg_agent_record *dg_agent_db_find(const dg_agent_db *db, dg_agent_id agent_id) {
    u32 idx;
    int found;
    if (!db || !db->agents || db->count == 0u || agent_id == 0u) {
        return (const dg_agent_record *)0;
    }
    idx = dg_agent_db_lower_bound(db, agent_id, &found);
    if (!found) {
        return (const dg_agent_record *)0;
    }
    return &db->agents[idx];
}

int dg_agent_db_attach_component(dg_agent_db *db, dg_agent_id agent_id, dg_type_id kind_id, dg_comp_id *out_comp_id) {
    dg_agent_record *a;
    u32 existing;
    dg_comp_id cid;
    u32 i;

    if (out_comp_id) {
        *out_comp_id = 0u;
    }
    if (!db || agent_id == 0u || kind_id == 0u) {
        return -1;
    }
    a = dg_agent_db_find_mut(db, agent_id);
    if (!a) {
        return -2;
    }
    if (dg_agent_record_find_comp(a, kind_id, &existing) == 0) {
        return -3;
    }
    if (a->comp_count >= DG_AGENT_MAX_COMPONENTS) {
        db->probe_refused_components += 1u;
        return -4;
    }

    cid = dg_agent_comp_alloc(&db->comp_reg, kind_id, agent_id, a->domain_id, a->chunk_id);
    if (cid == 0u) {
        db->probe_refused_components += 1u;
        return -5;
    }

    /* Insert into per-agent component ref list in ascending kind_id order. */
    i = a->comp_count;
    while (i > 0u) {
        if (a->comps[i - 1u].kind_id <= kind_id) {
            break;
        }
        a->comps[i] = a->comps[i - 1u];
        i -= 1u;
    }
    a->comps[i].kind_id = kind_id;
    a->comps[i].comp_id = cid;
    a->comp_count += 1u;

    if (out_comp_id) {
        *out_comp_id = cid;
    }
    return 0;
}

int dg_agent_db_detach_component(dg_agent_db *db, dg_agent_id agent_id, dg_type_id kind_id) {
    dg_agent_record *a;
    u32 idx;

    if (!db || agent_id == 0u || kind_id == 0u) {
        return -1;
    }
    a = dg_agent_db_find_mut(db, agent_id);
    if (!a) {
        return -2;
    }
    if (dg_agent_record_find_comp(a, kind_id, &idx) != 0) {
        return -3;
    }

    (void)dg_agent_comp_free(&db->comp_reg, kind_id, a->comps[idx].comp_id);

    if (idx + 1u < a->comp_count) {
        memmove(&a->comps[idx], &a->comps[idx + 1u],
                sizeof(dg_agent_comp_ref) * (size_t)(a->comp_count - (idx + 1u)));
    }
    a->comp_count -= 1u;
    return 0;
}

dg_comp_id dg_agent_db_component_of(const dg_agent_db *db, dg_agent_id agent_id, dg_type_id kind_id) {
    const dg_agent_record *a;
    u32 i;

    if (!db || agent_id == 0u || kind_id == 0u) {
        return 0u;
    }
    a = dg_agent_db_find(db, agent_id);
    if (!a) {
        return 0u;
    }
    for (i = 0u; i < a->comp_count; ++i) {
        if (a->comps[i].kind_id == kind_id) {
            return a->comps[i].comp_id;
        }
    }
    return 0u;
}

u32 dg_agent_db_probe_refused_agents(const dg_agent_db *db) {
    return db ? db->probe_refused_agents : 0u;
}

u32 dg_agent_db_probe_refused_components(const dg_agent_db *db) {
    return db ? db->probe_refused_components : 0u;
}
