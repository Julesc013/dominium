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

