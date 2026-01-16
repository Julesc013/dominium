/*
FILE: source/domino/sim/lod/dg_rep.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / sim/lod/dg_rep
RESPONSIBILITY: Defines internal contract for `dg_rep`; shared within its subsystem; does NOT define a public API (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (internal header).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
/* Representation ladder (R0/R1/R2/R3) for deterministic LOD (C89).
 *
 * The ladder is engine-wide and used for entities, caches, propagators, etc.
 * Promotion/demotion MUST be driven only by lockstep state and scheduler
 * phase boundaries (see docs/SPEC_LOD.md).
 */
#ifndef DG_REP_H
#define DG_REP_H

#include "domino/core/types.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef enum dg_rep_state {
    DG_REP_R0_FULL = 0,
    DG_REP_R1_LITE = 1,
    DG_REP_R2_AGG = 2,
    DG_REP_R3_DORMANT = 3,
    DG_REP_COUNT = 4
} dg_rep_state;

d_bool dg_rep_state_is_valid(dg_rep_state s);
const char *dg_rep_state_name(dg_rep_state s); /* debug/telemetry only */

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DG_REP_H */

