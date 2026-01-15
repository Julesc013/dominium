/*
FILE: source/domino/sim/sense/dg_sensor.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / sim/sense/dg_sensor
RESPONSIBILITY: Defines internal contract for `dg_sensor`; shared within its subsystem; does NOT define a public API (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (internal header).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
/* Sensor interface (deterministic; C89).
 *
 * Sensors are semantic-free samplers that read world state via deterministic
 * queries and emit dg_pkt_observation packets.
 *
 * Sensors MUST NOT mutate authoritative state.
 */
#ifndef DG_SENSOR_H
#define DG_SENSOR_H

#include "agent/dg_agent_ids.h"
#include "sim/lod/dg_stride.h"
#include "sim/sense/dg_observation_buffer.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct dg_sensor_desc dg_sensor_desc;

typedef struct dg_sensor_vtbl {
    /* Sample the world and push observation packets into out_obs.
     * io_seq is a caller-managed sequence source for sensor-local emission.
     */
    int (*sample)(
        dg_agent_id             agent_id,
        const void             *observer_ctx,
        dg_tick                 tick,
        u32                    *io_seq,
        dg_observation_buffer  *out_obs
    );

    /* Optional deterministic work estimate (units). */
    u32 (*estimate_cost)(dg_agent_id agent_id, const void *observer_ctx);
} dg_sensor_vtbl;

struct dg_sensor_desc {
    dg_type_id       sensor_id; /* stable taxonomy id */
    dg_sensor_vtbl   vtbl;
    u32              stride;    /* cadence decimation; 0/1 means always */
    const char      *name;      /* optional; not used for determinism */
};

/* Deterministic stride check keyed by (agent_id, sensor_id). */
d_bool dg_sensor_should_run(const dg_sensor_desc *s, dg_tick tick, dg_agent_id agent_id);

/* Estimate cost or return a default. */
u32 dg_sensor_estimate_cost(const dg_sensor_desc *s, dg_agent_id agent_id, const void *observer_ctx, u32 default_cost);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DG_SENSOR_H */

