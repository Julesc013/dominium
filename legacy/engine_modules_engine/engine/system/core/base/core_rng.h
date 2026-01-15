/*
FILE: source/domino/system/core/base/core_rng.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / system/core/base/core_rng
RESPONSIBILITY: Defines internal contract for `core_rng`; shared within its subsystem; does NOT define a public API (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (internal header).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
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
