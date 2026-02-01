/*
FILE: source/domino/execution/scheduler/dg_sched_replay.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / execution/scheduler/dg_sched_replay
RESPONSIBILITY: Defines internal contract for `dg_sched_replay`; shared within its subsystem; does NOT define a public API (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/specs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (internal header).
EXTENSION POINTS: Extend via public headers and relevant `docs/specs/SPEC_*.md` without cross-layer coupling.
*/
/* Deterministic replay hooks (C89).
 *
 * Scheduler-local replay hooks. This module defines hook points for building
 * replay traces. No file IO is implemented here; storage is in-memory
 * scaffolding only.
 */
#ifndef DG_SCHED_REPLAY_H
#define DG_SCHED_REPLAY_H

#include "execution/scheduler/dg_phase.h"
#include "core/dg_order_key.h"
#include "sim/pkt/dg_pkt_delta.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct dg_replay_ctx {
    dg_tick tick;
    u32     phase_begin_count[DG_PH_COUNT];
    u32     phase_end_count[DG_PH_COUNT];
    u32     deltas_committed;
} dg_replay_ctx;

typedef dg_replay_ctx dg_sched_replay_ctx;

void dg_sched_replay_init(dg_sched_replay_ctx *rc);
void dg_sched_replay_begin_tick(dg_sched_replay_ctx *rc, dg_tick tick);
void dg_sched_replay_phase_begin(dg_sched_replay_ctx *rc, dg_phase phase);
void dg_sched_replay_phase_end(dg_sched_replay_ctx *rc, dg_phase phase);

/* Stub hook: in later prompts, this will append to a trace buffer. */
void dg_sched_replay_record_committed_delta(dg_sched_replay_ctx *rc, const dg_order_key *key, const dg_pkt_delta *delta);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DG_SCHED_REPLAY_H */
