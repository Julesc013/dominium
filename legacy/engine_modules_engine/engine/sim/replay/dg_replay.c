/*
FILE: source/domino/sim/replay/dg_replay.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / sim/replay/dg_replay
RESPONSIBILITY: Implements `dg_replay`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include <string.h>

#include "sim/replay/dg_replay.h"

void dg_replay_init(dg_replay *r) {
    if (!r) {
        return;
    }
    memset(r, 0, sizeof(*r));
}

void dg_replay_set_stream(dg_replay *r, dg_replay_stream *stream) {
    if (!r) {
        return;
    }
    r->stream = stream;
}

void dg_replay_begin_tick(dg_replay *r, dg_tick tick) {
    if (!r) {
        return;
    }
    r->tick = tick;
}

int dg_replay_record_hash_snapshot(dg_replay *r, const dg_hash_snapshot *snap) {
    if (!r || !r->stream) {
        return 0;
    }
    return dg_replay_stream_record_hash_snapshot(r->stream, r->tick, snap);
}

int dg_replay_record_input_pkt(dg_replay *r, const dg_pkt_hdr *hdr, const unsigned char *payload, u32 payload_len) {
    if (!r || !r->stream) {
        return 0;
    }
    return dg_replay_stream_record_input_pkt(r->stream, r->tick, hdr, payload, payload_len);
}

int dg_replay_record_probe(dg_replay *r, const dg_replay_probe_sample *p) {
    if (!r || !r->stream) {
        return 0;
    }
    return dg_replay_stream_record_probe(r->stream, p);
}

