#include "domino/core/rng.h"

#define D_RNG_A 1664525u
#define D_RNG_C 1013904223u

static u32 d_rng_step(u32 s) {
    return s * D_RNG_A + D_RNG_C;
}

void d_rng_seed(d_rng_state* rng, u32 seed) {
    if (!rng) {
        return;
    }
    rng->state = (seed != 0u) ? seed : 1u;
}

u32 d_rng_next_u32(d_rng_state* rng) {
    if (!rng) {
        return 0u;
    }
    rng->state = d_rng_step(rng->state);
    return rng->state;
}

i32 d_rng_next_i32(d_rng_state* rng) {
    return (i32)d_rng_next_u32(rng);
}

u32 d_rng_peek_u32(const d_rng_state* rng) {
    if (!rng) {
        return 0u;
    }
    return d_rng_step(rng->state);
}
