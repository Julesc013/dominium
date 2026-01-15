/*
FILE: source/domino/sim/prop/dg_prop_registry.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / sim/prop/dg_prop_registry
RESPONSIBILITY: Defines internal contract for `dg_prop_registry`; shared within its subsystem; does NOT define a public API (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (internal header).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
/* Deterministic propagator registry (C89).
 *
 * Propagators are iterated canonically by (domain_id, prop_id) ascending.
 */
#ifndef DG_PROP_REGISTRY_H
#define DG_PROP_REGISTRY_H

#include "domino/core/types.h"

#include "sim/pkt/dg_pkt_common.h"
#include "sim/sched/dg_budget.h"
#include "sim/sched/dg_phase.h"

#include "sim/prop/dg_prop.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct dg_prop_registry_entry {
    dg_domain_id domain_id;
    dg_prop_id   prop_id;
    dg_prop     *prop;         /* not owned */
    u32          insert_index; /* stable tie-break */
} dg_prop_registry_entry;

typedef struct dg_prop_registry {
    dg_prop_registry_entry *entries;
    u32                    count;
    u32                    capacity;
    u32                    next_insert_index;
    u32                    probe_refused;
} dg_prop_registry;

void dg_prop_registry_init(dg_prop_registry *reg);
void dg_prop_registry_free(dg_prop_registry *reg);
int  dg_prop_registry_reserve(dg_prop_registry *reg, u32 capacity);

/* Add a propagator (sorted by (domain_id, prop_id)). Returns 0 on success. */
int dg_prop_registry_add(dg_prop_registry *reg, dg_prop *prop);

u32 dg_prop_registry_count(const dg_prop_registry *reg);
const dg_prop_registry_entry *dg_prop_registry_at(const dg_prop_registry *reg, u32 index);
const dg_prop_registry_entry *dg_prop_registry_find(const dg_prop_registry *reg, dg_domain_id domain_id, dg_prop_id prop_id);

u32 dg_prop_registry_probe_refused(const dg_prop_registry *reg);

void dg_prop_registry_step(dg_prop_registry *reg, dg_tick tick, dg_budget *budget);
u64  dg_prop_registry_hash_state(const dg_prop_registry *reg);

/* Convenience scheduler hook for DG_PH_SOLVE.
 * user_ctx must be a dg_prop_registry*.
 */
struct dg_sched;
void dg_prop_registry_solve_phase_handler(struct dg_sched *sched, void *user_ctx);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DG_PROP_REGISTRY_H */

