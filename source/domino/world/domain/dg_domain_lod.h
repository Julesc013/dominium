/*
FILE: source/domino/world/domain/dg_domain_lod.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / world/domain/dg_domain_lod
RESPONSIBILITY: Implements `dg_domain_lod`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
/* Domain LOD hooks (C89).
 *
 * This module bridges domains to the representation ladder (R0–R3) via the
 * generic dg_representable interface. It does not impose semantics.
 *
 * Authoritative state MUST NOT be discarded on demotion; domain implementations
 * should use accumulators (sim/lod/dg_accum) for deferred integration.
 */
#ifndef DG_DOMAIN_LOD_H
#define DG_DOMAIN_LOD_H

#include "domino/core/types.h"

#include "sim/lod/dg_rep.h"
#include "sim/lod/dg_representable.h"
#include "sim/lod/dg_lod_index.h"

#include "world/domain/dg_domain.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct dg_domain_lod {
    dg_representable rep;
    dg_rep_state     state;
    dg_domain       *domain; /* not owned */
} dg_domain_lod;

void dg_domain_lod_init(dg_domain_lod *dl, dg_domain *domain, dg_rep_state initial_state);
d_bool dg_domain_lod_is_valid(const dg_domain_lod *dl);

dg_representable *dg_domain_lod_representable(dg_domain_lod *dl);
dg_rep_state      dg_domain_lod_get_state(const dg_domain_lod *dl);
int               dg_domain_lod_set_state(dg_domain_lod *dl, dg_rep_state new_state);

/* Convenience: default LOD key for treating a domain as a representable object. */
dg_lod_obj_key dg_domain_lod_default_key(dg_domain_id domain_id);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DG_DOMAIN_LOD_H */

