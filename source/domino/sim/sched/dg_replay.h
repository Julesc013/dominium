/* Deterministic replay hooks (C89).
 *
 * This module defines hook points for building replay traces. No file IO is
 * implemented here; storage is in-memory scaffolding only.
 */
#ifndef DG_REPLAY_H
#define DG_REPLAY_H

#include "sim/sched/dg_phase.h"
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

void dg_replay_init(dg_replay_ctx *rc);
void dg_replay_begin_tick(dg_replay_ctx *rc, dg_tick tick);
void dg_replay_phase_begin(dg_replay_ctx *rc, dg_phase phase);
void dg_replay_phase_end(dg_replay_ctx *rc, dg_phase phase);

/* Stub hook: in later prompts, this will append to a trace buffer. */
void dg_replay_record_committed_delta(dg_replay_ctx *rc, const dg_order_key *key, const dg_pkt_delta *delta);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DG_REPLAY_H */

