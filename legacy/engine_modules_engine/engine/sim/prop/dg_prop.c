/*
FILE: source/domino/sim/prop/dg_prop.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / sim/prop/dg_prop
RESPONSIBILITY: Implements `dg_prop`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include <string.h>

#include "sim/prop/dg_prop.h"

void dg_prop_init(dg_prop *p, dg_domain_id domain_id, dg_prop_id prop_id, const dg_prop_vtbl *vtbl, void *user) {
    if (!p) {
        return;
    }
    memset(p, 0, sizeof(*p));
    p->domain_id = domain_id;
    p->prop_id = prop_id;
    p->vtbl = vtbl;
    p->user = user;
}

d_bool dg_prop_is_valid(const dg_prop *p) {
    if (!p) return D_FALSE;
    if (!p->vtbl) return D_FALSE;
    return D_TRUE;
}

void dg_prop_step(dg_prop *p, dg_tick tick, dg_budget *budget) {
    if (!p || !p->vtbl || !p->vtbl->step) {
        return;
    }
    p->vtbl->step(p, tick, budget);
}

int dg_prop_sample(const dg_prop *p, dg_tick tick, const void *query, void *out) {
    if (!p || !p->vtbl || !p->vtbl->sample) {
        return 0; /* stubs allowed */
    }
    return p->vtbl->sample(p, tick, query, out);
}

u32 dg_prop_serialize_state(const dg_prop *p, unsigned char *out, u32 out_cap) {
    if (!p || !p->vtbl || !p->vtbl->serialize_state) {
        return 0u;
    }
    return p->vtbl->serialize_state(p, out, out_cap);
}

u64 dg_prop_hash_state(const dg_prop *p) {
    if (!p || !p->vtbl || !p->vtbl->hash_state) {
        return 0u;
    }
    return p->vtbl->hash_state(p);
}

