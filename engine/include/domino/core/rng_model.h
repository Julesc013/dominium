/*
FILE: include/domino/core/rng_model.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino API / core/rng_model
RESPONSIBILITY: Deterministic RNG derivation and named stream validation.
ALLOWED DEPENDENCIES: `include/domino/**` plus C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: OS entropy sources; platform time APIs.
DETERMINISM: Named RNG streams with stable derivation; see docs/architecture/RNG_MODEL.md.
*/
#ifndef DOMINO_CORE_RNG_MODEL_H
#define DOMINO_CORE_RNG_MODEL_H

#include "domino/core/types.h"
#include "domino/core/rng.h"

#ifdef __cplusplus
extern "C" {
#endif

enum d_rng_mix_flags {
    D_RNG_MIX_NONE   = 0u,
    D_RNG_MIX_DOMAIN = 1u << 0u,
    D_RNG_MIX_PROCESS = 1u << 1u,
    D_RNG_MIX_TICK   = 1u << 2u,
    D_RNG_MIX_STREAM = 1u << 3u,
    D_RNG_MIX_ALL = D_RNG_MIX_DOMAIN | D_RNG_MIX_PROCESS | D_RNG_MIX_TICK | D_RNG_MIX_STREAM
};

/* d_rng_fold_u64
 * Purpose: Fold a 64-bit value into 32 bits deterministically.
 */
u32 d_rng_fold_u64(u64 value);

/* d_rng_hash_str32
 * Purpose: Hash a string into a 32-bit deterministic value (FNV-1a).
 */
u32 d_rng_hash_str32(const char* text);

/* d_rng_stream_name_valid
 * Purpose: Validate a named RNG stream ID.
 * Required format: noise.stream.<domain>.<subsystem>.<purpose>
 */
int d_rng_stream_name_valid(const char* name);

/* d_rng_seed_from_context
 * Purpose: Derive a deterministic seed from context and stream name.
 * Notes: Caller selects which components to mix using `mix_flags`.
 */
u32 d_rng_seed_from_context(u64 world_seed,
                            u64 domain_id,
                            u64 process_id,
                            u64 tick_index,
                            const char* stream_name,
                            u32 mix_flags);

/* d_rng_state_from_context
 * Purpose: Initialize RNG state from context and stream name.
 */
void d_rng_state_from_context(d_rng_state* rng,
                              u64 world_seed,
                              u64 domain_id,
                              u64 process_id,
                              u64 tick_index,
                              const char* stream_name,
                              u32 mix_flags);

/* d_rng_state_from_seed
 * Purpose: Initialize RNG state from an already-derived seed, while enforcing
 * named stream validation.
 */
void d_rng_state_from_seed(d_rng_state* rng, u32 seed, const char* stream_name);

#ifndef NDEBUG
#include <assert.h>
#define D_DET_GUARD_RNG_STREAM_NAME(name) assert(d_rng_stream_name_valid(name))
#else
#define D_DET_GUARD_RNG_STREAM_NAME(name) ((void)0)
#endif

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINO_CORE_RNG_MODEL_H */
