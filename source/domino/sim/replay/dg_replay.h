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

