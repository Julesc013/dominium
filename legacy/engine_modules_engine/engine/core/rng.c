/*
FILE: source/domino/core/rng.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / core/rng
RESPONSIBILITY: Implements `rng`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: Deterministic RNG (u32 LCG; unsigned overflow is modulo 2^32); see `docs/SPEC_DETERMINISM.md`.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include "domino/core/rng.h"

/* LCG constants; chosen for simple, reproducible sequences (not cryptographic). */
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
