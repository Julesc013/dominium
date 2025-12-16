/*
FILE: source/domino/sim/lod/d_sim_lod.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / sim/lod/d_sim_lod
RESPONSIBILITY: Implements `d_sim_lod`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
/* Deterministic LOD interfaces (scaffold; C89).
 * See docs/SPEC_LOD.md
 */
#ifndef D_SIM_LOD_H
#define D_SIM_LOD_H

#include "domino/core/types.h"

#ifdef __cplusplus
extern "C" {
#endif

/* Opaque LOD controller state. */
typedef struct d_sim_lod d_sim_lod;

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* D_SIM_LOD_H */

