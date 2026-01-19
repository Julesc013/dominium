/*
FILE: source/domino/execution/scheduler/dg_sched_hash.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / execution/scheduler/dg_sched_hash
RESPONSIBILITY: Defines internal contract for `dg_sched_hash`; shared within its subsystem; does NOT define a public API (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (internal header).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
/* Deterministic hash hooks (C89).
 *
 * Scheduler-local hash hooks. This module provides hook points for recording
 * per-phase hashes and committed deltas without file IO.
 */
#ifndef DG_SCHED_HASH_H
#define DG_SCHED_HASH_H

#include "execution/scheduler/dg_phase.h"
#include "sim/pkt/pkt_hash.h"
#include "core/dg_order_key.h"
#include "sim/pkt/dg_pkt_delta.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct dg_hash_ctx {
    dg_tick tick;

    u32 phase_begin_count[DG_PH_COUNT];
    u32 phase_end_count[DG_PH_COUNT];

    u32 deltas_committed;
    dg_pkt_hash deltas_hash; /* aggregate hash over committed deltas */
} dg_hash_ctx;

typedef dg_hash_ctx dg_sched_hash_ctx;

void dg_sched_hash_init(dg_sched_hash_ctx *hc);
void dg_sched_hash_begin_tick(dg_sched_hash_ctx *hc, dg_tick tick);

void dg_sched_hash_phase_begin(dg_sched_hash_ctx *hc, dg_phase phase);
void dg_sched_hash_phase_end(dg_sched_hash_ctx *hc, dg_phase phase);

/* Record a committed delta in canonical commit order. */
void dg_sched_hash_record_committed_delta(dg_sched_hash_ctx *hc, const dg_order_key *key, const dg_pkt_delta *delta);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DG_SCHED_HASH_H */
