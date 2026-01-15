/*
FILE: source/domino/system/core/base/core_rng.c
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / system/core/base/core_rng
RESPONSIBILITY: Implements `core_rng`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#include "core_rng.h"

#include <string.h>

static u64 rotl64(u64 x, int k)
{
    return (x << k) | (x >> (64 - k));
}

static u64 splitmix64_next(u64 *state)
{
    u64 z;
    *state += 0x9E3779B97F4A7C15ULL;
    z = *state;
    z = (z ^ (z >> 30)) * 0xBF58476D1CE4E5B9ULL;
    z = (z ^ (z >> 27)) * 0x94D049BB133111EBULL;
    return z ^ (z >> 31);
}

void rng_seed(RNGState *rng, u64 seed)
{
    u64 sm_state = seed;
    if (!rng) return;
    rng->s0 = splitmix64_next(&sm_state);
    rng->s1 = splitmix64_next(&sm_state);
    if (rng->s0 == 0 && rng->s1 == 0) {
        rng->s1 = 1; /* Avoid zero state */
    }
}

u64 rng_next_u64(RNGState *rng)
{
    u64 s0;
    u64 s1;
    u64 result;
    if (!rng) return 0;
    s0 = rng->s0;
    s1 = rng->s1;
    result = s0 + s1;
    s1 ^= s0;
    rng->s0 = rotl64(s0, 55) ^ s1 ^ (s1 << 14);
    rng->s1 = rotl64(s1, 36);
    return result;
}

u32 rng_next_u32(RNGState *rng)
{
    return (u32)rng_next_u64(rng);
}

void rng_registry_init(RNGRegistry *reg)
{
    if (!reg) return;
    memset(reg, 0, sizeof(*reg));
}

RNGState *rng_registry_get(RNGRegistry *reg, RNGId id, b32 create_if_missing)
{
    u32 i;
    if (!reg) return NULL;
    for (i = 0; i < RNG_REGISTRY_CAPACITY; ++i) {
        if (reg->entries[i].used && reg->entries[i].id == id) {
            return &reg->entries[i].state;
        }
    }
    if (!create_if_missing) {
        return NULL;
    }
    for (i = 0; i < RNG_REGISTRY_CAPACITY; ++i) {
        if (!reg->entries[i].used) {
            reg->entries[i].used = TRUE;
            reg->entries[i].id = id;
            rng_seed(&reg->entries[i].state, id);
            return &reg->entries[i].state;
        }
    }
    return NULL;
}
