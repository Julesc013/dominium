/* Domino deterministic RNG interface (C89).
 * LCG: state = state * 1664525 + 1013904223 (Numerical Recipes).
 */
#ifndef DOMINO_CORE_RNG_H
#define DOMINO_CORE_RNG_H

#include "domino/core/types.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct d_rng_state {
    u32 state;
} d_rng_state;

void d_rng_seed(d_rng_state* rng, u32 seed);
u32  d_rng_next_u32(d_rng_state* rng);
i32  d_rng_next_i32(d_rng_state* rng);
u32  d_rng_peek_u32(const d_rng_state* rng);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINO_CORE_RNG_H */
