/*
FILE: source/domino/sim/act/dg_action.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / sim/act/dg_action
RESPONSIBILITY: Implements `dg_action`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/specs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/specs/SPEC_*.md` without cross-layer coupling.
*/
#include "sim/act/dg_action.h"

u32 dg_action_estimate_cost(
    const dg_action_vtbl *vtbl,
    dg_agent_id           agent_id,
    const dg_pkt_intent  *intent,
    const void           *world_state,
    u32                   default_cost
) {
    if (!vtbl) {
        return default_cost;
    }
    if (vtbl->estimate_cost) {
        return vtbl->estimate_cost(agent_id, intent, world_state);
    }
    return default_cost;
}

