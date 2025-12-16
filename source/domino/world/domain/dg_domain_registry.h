/*
FILE: source/domino/world/domain/dg_domain_registry.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / world/domain/dg_domain_registry
RESPONSIBILITY: Defines internal contract for `dg_domain_registry`; shared within its subsystem; does NOT define a public API (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (internal header).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
/* Deterministic domain registry (C89).
 *
 * Domains are iterated canonically in ascending domain_id order.
 */
#ifndef DG_DOMAIN_REGISTRY_H
#define DG_DOMAIN_REGISTRY_H

#include "domino/core/types.h"

#include "sim/pkt/dg_pkt_common.h"
#include "sim/sched/dg_phase.h"
#include "sim/sched/dg_budget.h"

#include "world/domain/dg_domain.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct dg_domain_registry_entry {
    dg_domain_id domain_id;
    dg_domain   *domain;       /* not owned */
    u32          insert_index; /* stable tie-break for identical IDs (should not happen) */
} dg_domain_registry_entry;

typedef struct dg_domain_registry {
    dg_domain_registry_entry *entries;
    u32                      count;
    u32                      capacity;
    u32                      next_insert_index;
    u32                      probe_refused;
} dg_domain_registry;

void dg_domain_registry_init(dg_domain_registry *reg);
void dg_domain_registry_free(dg_domain_registry *reg);
int  dg_domain_registry_reserve(dg_domain_registry *reg, u32 capacity);

/* Add a domain (sorted by domain_id). Returns 0 on success. */
int dg_domain_registry_add(dg_domain_registry *reg, dg_domain *domain);

u32 dg_domain_registry_count(const dg_domain_registry *reg);
const dg_domain_registry_entry *dg_domain_registry_at(const dg_domain_registry *reg, u32 index);
const dg_domain_registry_entry *dg_domain_registry_find(const dg_domain_registry *reg, dg_domain_id domain_id);

u32 dg_domain_registry_probe_refused(const dg_domain_registry *reg);

/* Canonical phase stepping under scheduler budgets. Only DG_PH_TOPOLOGY and
 * DG_PH_SOLVE are acted on in this prompt.
 */
void dg_domain_registry_step_phase(dg_domain_registry *reg, dg_phase phase, dg_budget *budget);

/* Deterministic aggregate hash across all domains (canonical order). */
u64 dg_domain_registry_hash_state(const dg_domain_registry *reg);

/* Convenience scheduler hook for DG_PH_TOPOLOGY / DG_PH_SOLVE.
 * user_ctx must be a dg_domain_registry*.
 */
struct dg_sched;
void dg_domain_registry_phase_handler(struct dg_sched *sched, void *user_ctx);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DG_DOMAIN_REGISTRY_H */

