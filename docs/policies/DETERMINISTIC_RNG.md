# Deterministic RNG Policy (DET1)

This document defines the only allowed RNG for authoritative simulation paths.
All authoritative code MUST use deterministic RNG only and pass state explicitly.
Violations are merge-blocking.

## Scope

Applies to authoritative directories:
- `engine/modules/core/**`
- `engine/modules/sim/**`
- `engine/modules/world/**`
- `game/core/**` (simulation paths only)
- `game/rules/**`
- `game/economy/**`

## Allowed APIs

Use these headers only:
- `domino/core/rng.h`
- `domino/core/rng_streams.h`

Key primitives:
- `d_rng_state`
- `d_rng_seed`, `d_rng_next_u32`, `d_rng_next_i32`, `d_rng_peek_u32`
- `d_rng_streams`, `d_rng_streams_seed`, `d_rng_stream_seed`
- `d_rng_stream`, `d_rng_stream_const`

Named streams (canonical):
- `D_RNG_STREAM_SIM`
- `D_RNG_STREAM_CONTENT`
- `D_RNG_STREAM_EFFECTS`

## Forbidden APIs

The following are FORBIDDEN in authoritative code:
- `rand()`, `srand()`, `rand_r()`, `random()`, `arc4random()`, `drand48()`
- `<random>` and `std::random_*`
- OS entropy sources: `getrandom`, `BCryptGenRandom`, `RtlGenRandom`
- Time-based seeding (`time()`, `std::chrono`, wall-clock APIs)
- Hidden global RNG state or static RNG singletons

## Required usage rules

- RNG state MUST be owned by authoritative state and passed explicitly.
- No implicit or global RNG is allowed.
- Root seeds MUST be explicit and reproducible.
- Stream usage MUST be deterministic and stable across platforms.

## Examples

Good (deterministic, explicit state):
```
#include "domino/core/rng.h"

void sim_step(d_rng_state* rng) {
    u32 r = d_rng_next_u32(rng);
    (void)r;
}
```

Good (named streams):
```
#include "domino/core/rng_streams.h"

d_rng_streams rngs;
d_rng_streams_seed(&rngs, seed);
u32 r = d_rng_next_u32(d_rng_stream(&rngs, D_RNG_STREAM_SIM));
```

Bad (non-deterministic):
```
#include <random>

std::mt19937 gen;
```

## Enforcement

CI enforces the following IDs:
- `DET-RNG-002` (non-deterministic RNG)
- `DET-TIME-001` (OS time usage)
- `DET-G5` (no float/OS time/RNG)

Violations are merge-blocking.
