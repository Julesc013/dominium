/*
FILE: source/domino/execution/budgets/dg_budget.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / execution/budgets/dg_budget
RESPONSIBILITY: Defines internal contract for `dg_budget`; shared within its subsystem; does NOT define a public API (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (internal header).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
/* Deterministic work budgets (C89).
 *
 * Budgets are measured in integer "work units", not time.
 * Budgets are tick-driven and MUST NOT consult platform clocks.
 *
 * Budgets exist to bound per-tick work while preserving deterministic final
 * outcomes via explicit carryover queues (see dg_work_queue).
 */
#ifndef DG_BUDGET_H
#define DG_BUDGET_H

#include "sim/pkt/dg_pkt_common.h"

#ifdef __cplusplus
extern "C" {
#endif

/* Sentinel value meaning "unlimited" budget. */
#define DG_BUDGET_UNLIMITED 0xFFFFFFFFu

typedef struct dg_budget_scope {
    dg_domain_id domain_id; /* 0 means: no per-domain budget */
    dg_chunk_id  chunk_id;  /* 0 means: no per-chunk budget */
} dg_budget_scope;

dg_budget_scope dg_budget_scope_global(void);
dg_budget_scope dg_budget_scope_domain(dg_domain_id domain_id);
dg_budget_scope dg_budget_scope_chunk(dg_chunk_id chunk_id);
dg_budget_scope dg_budget_scope_domain_chunk(dg_domain_id domain_id, dg_chunk_id chunk_id);

typedef struct dg_budget_entry {
    u64 id;    /* domain_id or chunk_id */
    u32 limit; /* DG_BUDGET_UNLIMITED allowed */
    u32 used;  /* consumed this tick */
} dg_budget_entry;

typedef struct dg_budget {
    dg_tick tick;

    u32 global_limit;
    u32 global_used;

    u32 domain_default_limit;
    u32 chunk_default_limit;

    dg_budget_entry *domain_entries;
    u32              domain_count;
    u32              domain_capacity;

    dg_budget_entry *chunk_entries;
    u32              chunk_count;
    u32              chunk_capacity;

    u32 probe_domain_overflow;
    u32 probe_chunk_overflow;
} dg_budget;

void dg_budget_init(dg_budget *b);
void dg_budget_free(dg_budget *b);

/* Allocate bounded tables for domain/chunk budgets. */
int dg_budget_reserve(dg_budget *b, u32 domain_capacity, u32 chunk_capacity);

void dg_budget_begin_tick(dg_budget *b, dg_tick tick);

/* Set global and default per-domain/per-chunk limits. */
void dg_budget_set_limits(dg_budget *b, u32 global_limit, u32 domain_default_limit, u32 chunk_default_limit);

/* Optional: override limits for specific domain/chunk IDs. */
int dg_budget_set_domain_limit(dg_budget *b, dg_domain_id domain_id, u32 limit);
int dg_budget_set_chunk_limit(dg_budget *b, dg_chunk_id chunk_id, u32 limit);

/* Attempt to atomically consume from all scopes present in 'scope'.
 * Returns D_TRUE on success, D_FALSE if insufficient budget.
 */
d_bool dg_budget_try_consume(dg_budget *b, const dg_budget_scope *scope, u32 units);

/* Remaining units for the given scope (minimum across applicable budgets). */
u32 dg_budget_remaining(const dg_budget *b, const dg_budget_scope *scope);

u32 dg_budget_probe_domain_overflow(const dg_budget *b);
u32 dg_budget_probe_chunk_overflow(const dg_budget *b);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DG_BUDGET_H */
