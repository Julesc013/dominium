/*
FILE: source/domino/sim/prop/dg_prop.h
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
/* Semantics-free propagator interface (C89).
 *
 * A propagator is any deterministic system that evolves state over time under
 * explicit budgets (integer work units). Propagators do not imply meaning
 * such as physics, combat, or rendering.
 *
 * Propagators participate in the representation ladder (R0–R3) via
 * sim/lod and must use accumulators for lossless deferral.
 */
#ifndef DG_PROP_H
#define DG_PROP_H

#include "domino/core/types.h"

#include "sim/pkt/dg_pkt_common.h"
#include "sim/sched/dg_budget.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef u64 dg_prop_id;

struct dg_prop;

typedef struct dg_prop_vtbl {
    void (*step)(struct dg_prop *self, dg_tick tick, dg_budget *budget);

    /* Semantics-free sampling interface (stub). */
    int (*sample)(const struct dg_prop *self, dg_tick tick, const void *query, void *out);

    u32 (*serialize_state)(const struct dg_prop *self, unsigned char *out, u32 out_cap);
    u64 (*hash_state)(const struct dg_prop *self);
} dg_prop_vtbl;

typedef struct dg_prop {
    dg_domain_id        domain_id; /* budget scope; 0 allowed */
    dg_prop_id          prop_id;   /* stable id within domain or globally */
    const dg_prop_vtbl *vtbl;
    void               *user;      /* optional owner pointer */
} dg_prop;

void   dg_prop_init(dg_prop *p, dg_domain_id domain_id, dg_prop_id prop_id, const dg_prop_vtbl *vtbl, void *user);
d_bool dg_prop_is_valid(const dg_prop *p);

void dg_prop_step(dg_prop *p, dg_tick tick, dg_budget *budget);
int  dg_prop_sample(const dg_prop *p, dg_tick tick, const void *query, void *out);
u32  dg_prop_serialize_state(const dg_prop *p, unsigned char *out, u32 out_cap);
u64  dg_prop_hash_state(const dg_prop *p);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DG_PROP_H */

