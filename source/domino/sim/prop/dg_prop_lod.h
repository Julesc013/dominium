/*
FILE: source/domino/sim/prop/dg_prop_lod.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / sim/prop/dg_prop_lod
RESPONSIBILITY: Implements `dg_prop_lod`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
/* Propagator LOD hooks (C89).
 *
 * Bridges propagators to the representation ladder via dg_representable.
 */
#ifndef DG_PROP_LOD_H
#define DG_PROP_LOD_H

#include "domino/core/types.h"

#include "sim/lod/dg_rep.h"
#include "sim/lod/dg_representable.h"
#include "sim/lod/dg_lod_index.h"

#include "sim/prop/dg_prop.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct dg_prop_lod {
    dg_representable rep;
    dg_rep_state     state;
    dg_prop         *prop; /* not owned */
} dg_prop_lod;

void dg_prop_lod_init(dg_prop_lod *pl, dg_prop *prop, dg_rep_state initial_state);
d_bool dg_prop_lod_is_valid(const dg_prop_lod *pl);

dg_representable *dg_prop_lod_representable(dg_prop_lod *pl);
dg_rep_state      dg_prop_lod_get_state(const dg_prop_lod *pl);
int               dg_prop_lod_set_state(dg_prop_lod *pl, dg_rep_state new_state);

/* Convenience: default LOD key for treating a propagator as a representable object. */
dg_lod_obj_key dg_prop_lod_default_key(dg_domain_id domain_id, dg_prop_id prop_id);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DG_PROP_LOD_H */

