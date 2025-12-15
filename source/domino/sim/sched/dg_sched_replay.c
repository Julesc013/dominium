#include <string.h>

#include "sim/sched/dg_sched_replay.h"

void dg_sched_replay_init(dg_sched_replay_ctx *rc) {
    if (!rc) {
        return;
    }
    memset(rc, 0, sizeof(*rc));
}

void dg_sched_replay_begin_tick(dg_sched_replay_ctx *rc, dg_tick tick) {
    u32 i;
    if (!rc) {
        return;
    }
    rc->tick = tick;
    for (i = 0u; i < (u32)DG_PH_COUNT; ++i) {
        rc->phase_begin_count[i] = 0u;
        rc->phase_end_count[i] = 0u;
    }
    rc->deltas_committed = 0u;
}

void dg_sched_replay_phase_begin(dg_sched_replay_ctx *rc, dg_phase phase) {
    if (!rc) {
        return;
    }
    if (phase < 0 || phase >= DG_PH_COUNT) {
        return;
    }
    rc->phase_begin_count[(u32)phase] += 1u;
}

void dg_sched_replay_phase_end(dg_sched_replay_ctx *rc, dg_phase phase) {
    if (!rc) {
        return;
    }
    if (phase < 0 || phase >= DG_PH_COUNT) {
        return;
    }
    rc->phase_end_count[(u32)phase] += 1u;
}

void dg_sched_replay_record_committed_delta(dg_sched_replay_ctx *rc, const dg_order_key *key, const dg_pkt_delta *delta) {
    (void)key;
    (void)delta;
    if (!rc) {
        return;
    }
    rc->deltas_committed += 1u;
}
