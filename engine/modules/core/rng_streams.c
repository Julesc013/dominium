/*
FILE: source/domino/core/rng_streams.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / core/rng_streams
RESPONSIBILITY: Implements deterministic RNG stream bundles (no global state).
*/
#include "domino/core/rng_streams.h"

#include <stddef.h>

static void d_rng_streams_seed_internal(d_rng_streams* rngs, u32 seed) {
    d_rng_state tmp;
    u32 i;

    d_rng_seed(&tmp, seed);
    for (i = 0u; i < (u32)D_RNG_STREAM_MAX; ++i) {
        const u32 stream_seed = d_rng_next_u32(&tmp);
        d_rng_seed(&rngs->streams[i], stream_seed);
    }
}

void d_rng_streams_seed(d_rng_streams* rngs, u32 seed) {
    if (!rngs) {
        return;
    }
    d_rng_streams_seed_internal(rngs, seed);
}

void d_rng_stream_seed(d_rng_streams* rngs, d_rng_stream_id id, u32 seed) {
    if (!rngs || id < 0 || id >= D_RNG_STREAM_MAX) {
        return;
    }
    d_rng_seed(&rngs->streams[id], seed);
}

d_rng_state* d_rng_stream(d_rng_streams* rngs, d_rng_stream_id id) {
    if (!rngs || id < 0 || id >= D_RNG_STREAM_MAX) {
        return (d_rng_state*)0;
    }
    return &rngs->streams[id];
}

const d_rng_state* d_rng_stream_const(const d_rng_streams* rngs, d_rng_stream_id id) {
    if (!rngs || id < 0 || id >= D_RNG_STREAM_MAX) {
        return (const d_rng_state*)0;
    }
    return &rngs->streams[id];
}
