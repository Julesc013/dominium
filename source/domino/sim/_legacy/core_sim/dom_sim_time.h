/*
FILE: source/domino/sim/_legacy/core_sim/dom_sim_time.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / sim/_legacy/core_sim/dom_sim_time
RESPONSIBILITY: Implements `dom_sim_time`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOM_SIM_TIME_H
#define DOM_SIM_TIME_H

#include "dom_core_types.h"

/* Deterministic tick identifier */
typedef dom_u64 DomTickId;

typedef struct DomSimTime {
    DomTickId tick;       /* current tick id */
    dom_u32   target_ups; /* configured UPS target */
    dom_u32   effective_ups; /* effective UPS (degraded under load) */
} DomSimTime;

void      dom_sim_time_init(DomSimTime *t, dom_u32 target_ups);
void      dom_sim_time_reset(DomSimTime *t, DomTickId start_tick);
void      dom_sim_time_set_effective_ups(DomSimTime *t, dom_u32 ups);
DomTickId dom_sim_time_tick(const DomSimTime *t);
dom_u32   dom_sim_time_target_ups(const DomSimTime *t);
dom_u32   dom_sim_time_effective_ups(const DomSimTime *t);

#endif /* DOM_SIM_TIME_H */
