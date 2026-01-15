/*
FILE: source/domino/sim/_legacy/core_sim/dom_sim_time.c
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
#include "dom_sim_time.h"

void dom_sim_time_init(DomSimTime *t, dom_u32 target_ups)
{
    if (!t) return;
    t->tick = 0;
    t->target_ups = target_ups;
    t->effective_ups = target_ups;
}

void dom_sim_time_reset(DomSimTime *t, DomTickId start_tick)
{
    if (!t) return;
    t->tick = start_tick;
}

void dom_sim_time_set_effective_ups(DomSimTime *t, dom_u32 ups)
{
    if (!t) return;
    t->effective_ups = ups;
}

DomTickId dom_sim_time_tick(const DomSimTime *t)
{
    return t ? t->tick : 0;
}

dom_u32 dom_sim_time_target_ups(const DomSimTime *t)
{
    return t ? t->target_ups : 0;
}

dom_u32 dom_sim_time_effective_ups(const DomSimTime *t)
{
    return t ? t->effective_ups : 0;
}
