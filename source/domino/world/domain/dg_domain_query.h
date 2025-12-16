/*
FILE: source/domino/world/domain/dg_domain_query.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / world/domain/dg_domain_query
RESPONSIBILITY: Defines internal contract for `dg_domain_query`; shared within its subsystem; does NOT define a public API (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (internal header).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
/* Domain query scaffolding (C89).
 *
 * Queries are semantics-free: they describe "what to sample" without implying
 * gameplay meaning. Observer context is an opaque handle reserved for later
 * knowledge/visibility systems.
 *
 * Determinism rules:
 * - Query execution must be deterministic for the same inputs.
 * - Results must be sorted canonically before returning to callers.
 */
#ifndef DG_DOMAIN_QUERY_H
#define DG_DOMAIN_QUERY_H

#include "domino/core/types.h"

#include "sim/pkt/dg_pkt_common.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct dg_domain_query_desc {
    dg_type_id   query_type_id; /* semantics-free query discriminator */
    dg_domain_id domain_id;     /* 0 means: query all domains */
    dg_chunk_id  chunk_id;      /* 0 means: not chunk-scoped */
    const void  *params;        /* optional; interpretation is query_type_id-defined */
    u32          params_bytes;
} dg_domain_query_desc;

typedef struct dg_domain_query_result {
    dg_type_id   result_type_id; /* semantics-free result discriminator */
    dg_domain_id domain_id;
    dg_chunk_id  chunk_id;
    dg_entity_id entity_id;
    u64          sub_id;         /* optional sub-identifier (0 allowed) */
} dg_domain_query_result;

typedef struct dg_domain_query_results {
    dg_domain_query_result *items;    /* caller-owned storage */
    u32                     count;
    u32                     capacity;
} dg_domain_query_results;

void dg_domain_query_results_init(dg_domain_query_results *r, dg_domain_query_result *storage, u32 capacity);
void dg_domain_query_results_clear(dg_domain_query_results *r);

/* Append a result (bounded). Returns 0 on success, <0 on error. */
int dg_domain_query_results_push(dg_domain_query_results *r, const dg_domain_query_result *item);

/* Canonical total order comparator for deterministic sorting. */
int dg_domain_query_result_cmp(const dg_domain_query_result *a, const dg_domain_query_result *b);

/* Sort results canonically (deterministic). */
void dg_domain_query_results_sort(dg_domain_query_results *r);

/* Query dispatcher across a registry (stub; no semantics here).
 * - If desc->domain_id != 0, queries only that domain (if present).
 * - Otherwise queries all registered domains in canonical domain_id order.
 * Returns 0 on success.
 */
struct dg_domain_registry;
int dg_domain_query(
    const struct dg_domain_registry *reg,
    const dg_domain_query_desc      *desc,
    const void                      *observer_ctx,
    dg_domain_query_results         *out_results
);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DG_DOMAIN_QUERY_H */

