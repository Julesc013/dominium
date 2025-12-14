/* Representable interface for deterministic LOD (C89).
 *
 * A "representable" is any simulation object that participates in the
 * representation ladder (entities, caches, propagators, etc.).
 *
 * This is a pure interface/vtable layer: it does not imply gameplay logic.
 */
#ifndef DG_REPRESENTABLE_H
#define DG_REPRESENTABLE_H

#include "domino/core/types.h"

#include "sim/lod/dg_rep.h"
#include "sim/sched/dg_phase.h"

#ifdef __cplusplus
extern "C" {
#endif

struct dg_representable;

typedef struct dg_representable_vtbl {
    /* Current representation state (authoritative). */
    dg_rep_state (*get_rep_state)(const struct dg_representable *self);

    /* Authoritative transition. Must be called only at scheduler phase
     * boundaries (no mid-phase switching).
     */
    int (*set_rep_state)(struct dg_representable *self, dg_rep_state new_state);

    /* Execute representation-scoped work for the current phase.
     * 'budget_units' is a caller-owned counter (decremented by callee).
     */
    void (*step_rep)(struct dg_representable *self, dg_phase phase, u32 *budget_units);

    /* Serialize rep state into deterministic bytes (for save/load + hashing).
     * Returns bytes written (0 allowed). Must not write beyond out_cap.
     */
    u32 (*serialize_rep_state)(const struct dg_representable *self, unsigned char *out, u32 out_cap);

    /* Debug-only invariants check (deterministic). Return 0 if OK. */
    int (*rep_invariants_check)(const struct dg_representable *self);
} dg_representable_vtbl;

typedef struct dg_representable {
    const dg_representable_vtbl *vtbl;
    void                        *user; /* optional owner pointer */
} dg_representable;

void dg_representable_init(dg_representable *r, const dg_representable_vtbl *vtbl, void *user);
d_bool dg_representable_is_valid(const dg_representable *r);

dg_rep_state dg_representable_get_rep_state(const dg_representable *r);
int          dg_representable_set_rep_state(dg_representable *r, dg_rep_state new_state);
void         dg_representable_step_rep(dg_representable *r, dg_phase phase, u32 *budget_units);
u32          dg_representable_serialize_rep_state(const dg_representable *r, unsigned char *out, u32 out_cap);
int          dg_representable_rep_invariants_check(const dg_representable *r);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DG_REPRESENTABLE_H */

