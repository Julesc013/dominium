/*
FILE: source/domino/sim/sense/dg_sensor.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / sim/sense/dg_sensor
RESPONSIBILITY: Implements `dg_sensor`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include "sim/sense/dg_sensor.h"

d_bool dg_sensor_should_run(const dg_sensor_desc *s, dg_tick tick, dg_agent_id agent_id) {
    u64 stable_id;
    if (!s) {
        return D_FALSE;
    }
    /* Combine keys; dg_stride_should_run hashes stable_id internally. */
    stable_id = ((u64)agent_id) ^ (s->sensor_id * 11400714819323198485ULL);
    return dg_stride_should_run(tick, stable_id, s->stride);
}

u32 dg_sensor_estimate_cost(const dg_sensor_desc *s, dg_agent_id agent_id, const void *observer_ctx, u32 default_cost) {
    if (!s) {
        return default_cost;
    }
    if (s->vtbl.estimate_cost) {
        return s->vtbl.estimate_cost(agent_id, observer_ctx);
    }
    return default_cost;
}

