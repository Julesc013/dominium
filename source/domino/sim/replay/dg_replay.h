/*
FILE: source/domino/sim/replay/dg_replay.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / sim/replay/dg_replay
RESPONSIBILITY: Defines internal contract for `dg_replay`; shared within its subsystem; does NOT define a public API (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (internal header).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
/* Replay recorder wrapper (C89).
 *
 * This is a small helper for feeding a dg_replay_stream from simulation code.
 * It does not perform any IO and does not add semantics.
 */
#ifndef DG_REPLAY_H
#define DG_REPLAY_H

#include "domino/core/types.h"

#include "sim/pkt/dg_pkt_common.h"
#include "sim/hash/dg_hash.h"

#include "sim/replay/dg_replay_stream.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct dg_replay {
    dg_replay_stream *stream; /* not owned; may be NULL */
    dg_tick           tick;
} dg_replay;

void dg_replay_init(dg_replay *r);
void dg_replay_set_stream(dg_replay *r, dg_replay_stream *stream);

void dg_replay_begin_tick(dg_replay *r, dg_tick tick);

int dg_replay_record_hash_snapshot(dg_replay *r, const dg_hash_snapshot *snap);
int dg_replay_record_input_pkt(dg_replay *r, const dg_pkt_hdr *hdr, const unsigned char *payload, u32 payload_len);
int dg_replay_record_probe(dg_replay *r, const dg_replay_probe_sample *p);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DG_REPLAY_H */

