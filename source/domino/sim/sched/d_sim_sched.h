/*
FILE: source/domino/sim/sched/d_sim_sched.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / sim/sched/d_sim_sched
RESPONSIBILITY: Implements `d_sim_sched`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
/* Deterministic tick scheduler interfaces (scaffold; C89).
 * See docs/SPEC_SIM_SCHEDULER.md
 */
#ifndef D_SIM_SCHED_H
#define D_SIM_SCHED_H

#include "domino/core/types.h"

#ifdef __cplusplus
extern "C" {
#endif

/* Opaque scheduler state owned by the SIM layer. */
typedef struct d_sim_sched d_sim_sched;

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* D_SIM_SCHED_H */

