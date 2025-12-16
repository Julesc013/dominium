/*
FILE: source/domino/agent/group/dg_group_ctrl.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / agent/group/dg_group_ctrl
RESPONSIBILITY: Implements `dg_group_ctrl`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include "agent/group/dg_group_ctrl.h"

d_bool dg_group_ctrl_should_run(const dg_group_ctrl_desc *c, dg_tick tick, dg_group_id group_id) {
    u64 stable_id;
    if (!c) {
        return D_FALSE;
    }
    stable_id = ((u64)group_id) ^ (c->ctrl_id * 11400714819323198485ULL);
    return dg_stride_should_run(tick, stable_id, c->stride);
}

u32 dg_group_ctrl_estimate_cost(
    const dg_group_ctrl_desc    *c,
    dg_group_id                  group_id,
    const dg_group              *group,
    const dg_observation_buffer *observations,
    const void                  *internal_state,
    u32                          default_cost
) {
    if (!c) {
        return default_cost;
    }
    if (c->vtbl.estimate_cost) {
        return c->vtbl.estimate_cost(group_id, group, observations, internal_state);
    }
    return default_cost;
}

