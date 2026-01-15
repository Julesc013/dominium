/*
FILE: source/domino/agent/mind/dg_mind_registry.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / agent/mind/dg_mind_registry
RESPONSIBILITY: Defines internal contract for `dg_mind_registry`; shared within its subsystem; does NOT define a public API (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (internal header).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
/* Mind registry (deterministic; C89).
 *
 * Minds are registered by mind_id and iterated in canonical ascending mind_id
 * order (no hash-map iteration).
 */
#ifndef DG_MIND_REGISTRY_H
#define DG_MIND_REGISTRY_H

#include "agent/mind/dg_mind.h"
#include "agent/act/dg_intent_buffer.h"
#include "sim/sched/dg_budget.h"
#include "sim/sched/dg_work_queue.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct dg_mind_registry_entry {
    dg_mind_desc desc;
    u32          insert_index; /* stable tie-break/debug */
} dg_mind_registry_entry;

typedef struct dg_mind_registry {
    dg_mind_registry_entry *entries; /* sorted by desc.mind_id */
    u32                     count;
    u32                     capacity;
    u32                     next_insert_index;
} dg_mind_registry;

void dg_mind_registry_init(dg_mind_registry *reg);
void dg_mind_registry_free(dg_mind_registry *reg);
int dg_mind_registry_reserve(dg_mind_registry *reg, u32 capacity);

/* Register a mind. Returns 0 on success. */
int dg_mind_registry_add(dg_mind_registry *reg, const dg_mind_desc *desc);

u32 dg_mind_registry_count(const dg_mind_registry *reg);
const dg_mind_registry_entry *dg_mind_registry_at(const dg_mind_registry *reg, u32 index);
const dg_mind_registry_entry *dg_mind_registry_find(const dg_mind_registry *reg, dg_type_id mind_id);

/* Deterministically step a specific mind for one agent.
 * Returns:
 *  0: mind stepped (or skipped due to stride)
 *  1: budget exhausted; mind enqueued to defer_q (if non-NULL)
 * <0: error
 */
int dg_mind_registry_step_agent(
    const dg_mind_registry       *reg,
    dg_type_id                    mind_id,
    dg_tick                       tick,
    dg_agent_id                   agent_id,
    const dg_observation_buffer  *observations,
    void                         *internal_state,
    dg_budget                    *budget,
    const dg_budget_scope        *scope,
    dg_work_queue                *defer_q,
    dg_intent_buffer             *out_intents,
    u32                          *io_seq
);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DG_MIND_REGISTRY_H */
