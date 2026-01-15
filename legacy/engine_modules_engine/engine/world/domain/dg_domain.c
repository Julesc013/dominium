/*
FILE: source/domino/world/domain/dg_domain.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / world/domain/dg_domain
RESPONSIBILITY: Implements `dg_domain`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include <string.h>

#include "world/domain/dg_domain.h"

void dg_domain_init(dg_domain *d, dg_domain_id domain_id, const dg_domain_vtbl *vtbl, void *user) {
    if (!d) {
        return;
    }
    memset(d, 0, sizeof(*d));
    d->domain_id = domain_id;
    d->vtbl = vtbl;
    d->user = user;
}

d_bool dg_domain_is_valid(const dg_domain *d) {
    if (!d) {
        return D_FALSE;
    }
    if (!d->vtbl) {
        return D_FALSE;
    }
    return D_TRUE;
}

void dg_domain_step_phase(dg_domain *d, dg_phase phase, dg_budget *budget) {
    if (!d || !d->vtbl || !d->vtbl->step_phase) {
        return;
    }
    d->vtbl->step_phase(d, phase, budget);
}

int dg_domain_query_domain(
    const dg_domain            *d,
    const dg_domain_query_desc *desc,
    const void                 *observer_ctx,
    dg_domain_query_results    *out_results
) {
    if (!d || !d->vtbl || !d->vtbl->query) {
        return 0; /* stubs allowed */
    }
    return d->vtbl->query(d, desc, observer_ctx, out_results);
}

u32 dg_domain_serialize_state(const dg_domain *d, unsigned char *out, u32 out_cap) {
    if (!d || !d->vtbl || !d->vtbl->serialize_state) {
        return 0u;
    }
    return d->vtbl->serialize_state(d, out, out_cap);
}

u64 dg_domain_hash_state(const dg_domain *d) {
    if (!d || !d->vtbl || !d->vtbl->hash_state) {
        return 0u;
    }
    return d->vtbl->hash_state(d);
}

void dg_domain_spatial_index_init(dg_domain_spatial_index *idx, const dg_domain_spatial_index_vtbl *vtbl, void *user) {
    if (!idx) {
        return;
    }
    idx->vtbl = vtbl;
    idx->user = user;
}

d_bool dg_domain_spatial_index_is_valid(const dg_domain_spatial_index *idx) {
    if (!idx || !idx->vtbl) {
        return D_FALSE;
    }
    return D_TRUE;
}

void dg_domain_spatial_index_step_topology(dg_domain_spatial_index *idx, dg_tick tick, dg_budget *budget) {
    if (!idx || !idx->vtbl || !idx->vtbl->step_topology) {
        return;
    }
    idx->vtbl->step_topology(idx->user, tick, budget);
}

int dg_domain_spatial_index_query(
    dg_domain_spatial_index    *idx,
    const dg_domain_query_desc *desc,
    const void                 *observer_ctx,
    dg_domain_query_results    *out_results
) {
    if (!idx || !idx->vtbl || !idx->vtbl->query) {
        return 0; /* optional */
    }
    return idx->vtbl->query(idx->user, desc, observer_ctx, out_results);
}

