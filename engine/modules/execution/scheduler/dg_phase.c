/*
FILE: source/domino/execution/scheduler/dg_phase.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / execution/scheduler/dg_phase
RESPONSIBILITY: Implements `dg_phase`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/specs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/specs/SPEC_*.md` without cross-layer coupling.
*/
#include "execution/scheduler/dg_phase.h"

static const dg_phase_meta g_dg_phase_meta[DG_PH_COUNT] = {
    { DG_PH_INPUT,    "PH_INPUT" },
    { DG_PH_TOPOLOGY, "PH_TOPOLOGY" },
    { DG_PH_SENSE,    "PH_SENSE" },
    { DG_PH_MIND,     "PH_MIND" },
    { DG_PH_ACTION,   "PH_ACTION" },
    { DG_PH_SOLVE,    "PH_SOLVE" },
    { DG_PH_COMMIT,   "PH_COMMIT" },
    { DG_PH_HASH,     "PH_HASH" }
};

d_bool dg_phase_is_valid(dg_phase phase) {
    return (phase >= (dg_phase)0) && (phase < DG_PH_COUNT) ? D_TRUE : D_FALSE;
}

u32 dg_phase_count(void) {
    return (u32)DG_PH_COUNT;
}

const dg_phase_meta *dg_phase_meta_get(dg_phase phase) {
    if (!dg_phase_is_valid(phase)) {
        return (const dg_phase_meta *)0;
    }
    return &g_dg_phase_meta[(u32)phase];
}

const char *dg_phase_name(dg_phase phase) {
    const dg_phase_meta *m = dg_phase_meta_get(phase);
    return m ? m->name : "PH_INVALID";
}
