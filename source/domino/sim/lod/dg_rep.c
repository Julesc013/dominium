/*
FILE: source/domino/sim/lod/dg_rep.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / sim/lod/dg_rep
RESPONSIBILITY: Implements `dg_rep`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include "sim/lod/dg_rep.h"

d_bool dg_rep_state_is_valid(dg_rep_state s) {
    return (s >= DG_REP_R0_FULL && s < DG_REP_COUNT) ? D_TRUE : D_FALSE;
}

const char *dg_rep_state_name(dg_rep_state s) {
    switch (s) {
        case DG_REP_R0_FULL: return "R0_FULL";
        case DG_REP_R1_LITE: return "R1_LITE";
        case DG_REP_R2_AGG: return "R2_AGG";
        case DG_REP_R3_DORMANT: return "R3_DORMANT";
        default: break;
    }
    return "R?_INVALID";
}

