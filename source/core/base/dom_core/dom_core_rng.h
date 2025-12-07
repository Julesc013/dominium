#ifndef DOM_CORE_RNG_H
#define DOM_CORE_RNG_H

#include "dom_core_types.h"

typedef struct dom_rng {
    dom_u64 s0;
    dom_u64 s1;
} dom_rng;

void   dom_rng_seed(dom_rng *rng, dom_u64 seed);
dom_u32 dom_rng_u32(dom_rng *rng);
dom_u64 dom_rng_u64(dom_rng *rng);
dom_i32 dom_rng_i32_range(dom_rng *rng, dom_i32 lo, dom_i32 hi);

#endif /* DOM_CORE_RNG_H */
