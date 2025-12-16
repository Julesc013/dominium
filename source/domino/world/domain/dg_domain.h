/*
FILE: source/domino/world/domain/dg_domain.h
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
/* Semantics-free world domain interface (C89).
 *
 * A domain is a container for authoritative world state with:
 * - its own spatial partitioning model (domain-owned)
 * - its own field layers (bus integration)
 * - its own compiled caches (derived; regenerable)
 * - LOD policy hooks via the representation ladder (see sim/lod)
 *
 * Domains MUST remain semantics-free: no hardcoded meaning such as "planet" or
 * "battlefield" belongs here.
 *
 * Determinism rules:
 * - Domain iteration is canonical: ascending domain_id.
 * - All work is bounded by deterministic budgets (no clocks).
 */
#ifndef DG_DOMAIN_H
#define DG_DOMAIN_H

#include "domino/core/types.h"

#include "sim/pkt/dg_pkt_common.h"
#include "sim/sched/dg_phase.h"
#include "sim/sched/dg_budget.h"

#include "world/domain/dg_domain_query.h"

#ifdef __cplusplus
extern "C" {
#endif

struct dg_domain;

typedef struct dg_domain_vtbl {
    void (*step_phase)(struct dg_domain *self, dg_phase phase, dg_budget *budget);

    int (*query)(
        const struct dg_domain      *self,
        const dg_domain_query_desc  *desc,
        const void                  *observer_ctx,
        dg_domain_query_results     *out_results
    );

    u32 (*serialize_state)(const struct dg_domain *self, unsigned char *out, u32 out_cap);
    u64 (*hash_state)(const struct dg_domain *self);
} dg_domain_vtbl;

typedef struct dg_domain {
    dg_domain_id          domain_id;
    const dg_domain_vtbl *vtbl;
    void                 *user; /* optional owner pointer */
} dg_domain;

void   dg_domain_init(dg_domain *d, dg_domain_id domain_id, const dg_domain_vtbl *vtbl, void *user);
d_bool dg_domain_is_valid(const dg_domain *d);

void dg_domain_step_phase(dg_domain *d, dg_phase phase, dg_budget *budget);
int  dg_domain_query_domain(
    const dg_domain            *d,
    const dg_domain_query_desc *desc,
    const void                 *observer_ctx,
    dg_domain_query_results    *out_results
);
u32 dg_domain_serialize_state(const dg_domain *d, unsigned char *out, u32 out_cap);
u64 dg_domain_hash_state(const dg_domain *d);

/* Domain-owned spatial index interface (stub; no concrete indices here).
 * Spatial indices must be chunk/partition aligned and rebuildable under budget.
 */
typedef struct dg_domain_spatial_index_vtbl {
    /* Incremental rebuild step for DG_PH_TOPOLOGY (may schedule work). */
    void (*step_topology)(void *self, dg_tick tick, dg_budget *budget);

    /* Optional query interface (deterministic). */
    int (*query)(
        void                       *self,
        const dg_domain_query_desc *desc,
        const void                 *observer_ctx,
        dg_domain_query_results    *out_results
    );
} dg_domain_spatial_index_vtbl;

typedef struct dg_domain_spatial_index {
    const dg_domain_spatial_index_vtbl *vtbl;
    void                               *user;
} dg_domain_spatial_index;

void   dg_domain_spatial_index_init(dg_domain_spatial_index *idx, const dg_domain_spatial_index_vtbl *vtbl, void *user);
d_bool dg_domain_spatial_index_is_valid(const dg_domain_spatial_index *idx);
void   dg_domain_spatial_index_step_topology(dg_domain_spatial_index *idx, dg_tick tick, dg_budget *budget);
int    dg_domain_spatial_index_query(
    dg_domain_spatial_index      *idx,
    const dg_domain_query_desc   *desc,
    const void                   *observer_ctx,
    dg_domain_query_results      *out_results
);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DG_DOMAIN_H */

