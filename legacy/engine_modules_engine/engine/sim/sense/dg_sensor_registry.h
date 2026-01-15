/*
FILE: source/domino/sim/sense/dg_sensor_registry.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / sim/sense/dg_sensor_registry
RESPONSIBILITY: Defines internal contract for `dg_sensor_registry`; shared within its subsystem; does NOT define a public API (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (internal header).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
/* Sensor registry (deterministic; C89).
 *
 * Sensors are registered by sensor_id and iterated in canonical ascending
 * sensor_id order (no hash-map iteration).
 */
#ifndef DG_SENSOR_REGISTRY_H
#define DG_SENSOR_REGISTRY_H

#include "sim/sense/dg_sensor.h"
#include "sim/sched/dg_budget.h"
#include "sim/sched/dg_work_queue.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct dg_sensor_registry_entry {
    dg_sensor_desc desc;
    u32            insert_index; /* stable tie-break/debug */
} dg_sensor_registry_entry;

typedef struct dg_sensor_registry {
    dg_sensor_registry_entry *entries; /* sorted by desc.sensor_id */
    u32                       count;
    u32                       capacity;
    u32                       next_insert_index;
} dg_sensor_registry;

void dg_sensor_registry_init(dg_sensor_registry *reg);
void dg_sensor_registry_free(dg_sensor_registry *reg);
int dg_sensor_registry_reserve(dg_sensor_registry *reg, u32 capacity);

/* Register a sensor. Returns 0 on success. */
int dg_sensor_registry_add(dg_sensor_registry *reg, const dg_sensor_desc *desc);

u32 dg_sensor_registry_count(const dg_sensor_registry *reg);
const dg_sensor_registry_entry *dg_sensor_registry_at(const dg_sensor_registry *reg, u32 index);
const dg_sensor_registry_entry *dg_sensor_registry_find(const dg_sensor_registry *reg, dg_type_id sensor_id);

/* Deterministically sample all eligible sensors for one agent.
 * Returns:
 *  0: all eligible sensors sampled
 *  1: budget exhausted; remaining eligible sensors enqueued to defer_q (if non-NULL)
 * <0: error
 */
int dg_sensor_registry_sample_agent(
    const dg_sensor_registry   *reg,
    dg_tick                     tick,
    dg_agent_id                 agent_id,
    const void                 *observer_ctx,
    dg_budget                  *budget,
    const dg_budget_scope      *scope,
    dg_work_queue              *defer_q,
    dg_observation_buffer      *out_obs,
    u32                        *io_seq
);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DG_SENSOR_REGISTRY_H */
