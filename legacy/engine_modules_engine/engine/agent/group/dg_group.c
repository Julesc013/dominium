/*
FILE: source/domino/agent/group/dg_group.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / agent/group/dg_group
RESPONSIBILITY: Implements `dg_group`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
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

#include "agent/group/dg_group.h"

static u32 dg_group_lower_bound(const dg_group *g, dg_agent_id agent_id, int *out_found) {
    u32 lo = 0u;
    u32 hi;
    u32 mid;

    if (out_found) {
        *out_found = 0;
    }
    if (!g || g->count == 0u) {
        return 0u;
    }

    hi = g->count;
    while (lo < hi) {
        mid = lo + ((hi - lo) / 2u);
        if (g->members[mid] < agent_id) {
            lo = mid + 1u;
        } else {
            hi = mid;
        }
    }
    if (lo < g->count && g->members[lo] == agent_id) {
        if (out_found) {
            *out_found = 1;
        }
    }
    return lo;
}

void dg_group_init(dg_group *g) {
    if (!g) {
        return;
    }
    g->group_id = 0u;
    g->members = (dg_agent_id *)0;
    g->count = 0u;
    g->capacity = 0u;
    g->owns_storage = D_FALSE;
    g->probe_refused_members = 0u;
}

void dg_group_free(dg_group *g) {
    if (!g) {
        return;
    }
    if (g->owns_storage && g->members) {
        free(g->members);
    }
    dg_group_init(g);
}

int dg_group_reserve(dg_group *g, u32 capacity) {
    dg_agent_id *members;
    if (!g) {
        return -1;
    }
    dg_group_free(g);
    if (capacity == 0u) {
        return 0;
    }
    members = (dg_agent_id *)malloc(sizeof(dg_agent_id) * (size_t)capacity);
    if (!members) {
        return -2;
    }
    memset(members, 0, sizeof(dg_agent_id) * (size_t)capacity);
    g->members = members;
    g->capacity = capacity;
    g->count = 0u;
    g->owns_storage = D_TRUE;
    g->probe_refused_members = 0u;
    return 0;
}

void dg_group_set_id(dg_group *g, dg_group_id group_id) {
    if (!g) {
        return;
    }
    g->group_id = group_id;
}

int dg_group_add_member(dg_group *g, dg_agent_id agent_id) {
    u32 idx;
    int found;

    if (!g || agent_id == 0u) {
        return -1;
    }
    if (!g->members || g->capacity == 0u) {
        g->probe_refused_members += 1u;
        return -2;
    }

    idx = dg_group_lower_bound(g, agent_id, &found);
    if (found) {
        return 0;
    }
    if (g->count >= g->capacity) {
        g->probe_refused_members += 1u;
        return -3;
    }

    if (idx < g->count) {
        memmove(&g->members[idx + 1u], &g->members[idx], sizeof(dg_agent_id) * (size_t)(g->count - idx));
    }
    g->members[idx] = agent_id;
    g->count += 1u;
    return 0;
}

int dg_group_remove_member(dg_group *g, dg_agent_id agent_id) {
    u32 idx;
    int found;

    if (!g || agent_id == 0u) {
        return -1;
    }
    if (!g->members || g->count == 0u) {
        return -2;
    }

    idx = dg_group_lower_bound(g, agent_id, &found);
    if (!found) {
        return -3;
    }

    if (idx + 1u < g->count) {
        memmove(&g->members[idx], &g->members[idx + 1u], sizeof(dg_agent_id) * (size_t)(g->count - (idx + 1u)));
    }
    g->count -= 1u;
    return 0;
}

d_bool dg_group_contains(const dg_group *g, dg_agent_id agent_id) {
    u32 idx;
    int found;
    if (!g || !g->members || g->count == 0u || agent_id == 0u) {
        return D_FALSE;
    }
    idx = dg_group_lower_bound(g, agent_id, &found);
    return found ? D_TRUE : D_FALSE;
}

u32 dg_group_member_count(const dg_group *g) {
    return g ? g->count : 0u;
}

dg_agent_id dg_group_member_at(const dg_group *g, u32 index) {
    if (!g || !g->members || index >= g->count) {
        return 0u;
    }
    return g->members[index];
}

u32 dg_group_probe_refused_members(const dg_group *g) {
    return g ? g->probe_refused_members : 0u;
}

