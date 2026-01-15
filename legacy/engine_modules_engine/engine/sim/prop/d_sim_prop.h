/*
FILE: source/domino/sim/prop/d_sim_prop.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / sim/prop/d_sim_prop
RESPONSIBILITY: Defines internal contract for `d_sim_prop`; shared within its subsystem; does NOT define a public API (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (internal header).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
/* Deterministic propagation interfaces (scaffold; C89).
 * See docs/SPEC_DOMAINS_FRAMES_PROP.md
 */
#ifndef D_SIM_PROP_H
#define D_SIM_PROP_H

#include "domino/core/types.h"

#ifdef __cplusplus
extern "C" {
#endif

/* Opaque propagator state. */
typedef struct d_sim_prop d_sim_prop;

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* D_SIM_PROP_H */

