#ifndef DOM_CORE_RNG_H
#define DOM_CORE_RNG_H

#include "core_types.h"
#include "core_ids.h"

typedef struct RNGState {
    u64 s0;
    u64 s1;
} RNGState;

typedef struct RNGRegistryEntry {
    RNGId id;
    RNGState state;
    b32 used;
} RNGRegistryEntry;

#define RNG_REGISTRY_CAPACITY 64

typedef struct RNGRegistry {
    RNGRegistryEntry entries[RNG_REGISTRY_CAPACITY];
} RNGRegistry;

void rng_seed(RNGState *rng, u64 seed);
u64  rng_next_u64(RNGState *rng);
u32  rng_next_u32(RNGState *rng);

void rng_registry_init(RNGRegistry *reg);
RNGState *rng_registry_get(RNGRegistry *reg, RNGId id, b32 create_if_missing);

#endif /* DOM_CORE_RNG_H */
