/*
FILE: include/domino/core/rng.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino API / core/rng
RESPONSIBILITY: Defines the public contract for `rng` (types/constants/function signatures); does NOT provide implementation.
ALLOWED DEPENDENCIES: `include/domino/**` plus C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `source/**` private headers; keep contracts freestanding and layer-respecting.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: Determinism-critical RNG (LCG); see `docs/specs/SPEC_DETERMINISM.md`.
VERSIONING / ABI / DATA FORMAT NOTES: Public header; see `docs/specs/SPEC_ABI_TEMPLATES.md` where ABI stability matters.
EXTENSION POINTS: Extend via public headers and relevant `docs/specs/SPEC_*.md` without cross-layer coupling.
*/
/* Domino deterministic RNG interface (C89).
 * LCG: state = state * 1664525 + 1013904223 (Numerical Recipes).
 */
#ifndef DOMINO_CORE_RNG_H
#define DOMINO_CORE_RNG_H

#include "domino/core/types.h"

#ifdef __cplusplus
extern "C" {
#endif

/* d_rng_state
 * Purpose: Deterministic RNG state (LCG).
 * Notes:
 * - This RNG is not cryptographically secure.
 * - The sequence is fully determined by the 32-bit `state`.
 */
typedef struct d_rng_state {
    u32 state;
} d_rng_state;

/* d_rng_seed
 * Purpose: Initialize RNG state from a seed.
 * Parameters:
 *   rng (out): RNG state to initialize. If NULL, this is a no-op.
 *   seed (in): Seed value; 0 is remapped to 1 to avoid the degenerate 0 state.
 */
void d_rng_seed(d_rng_state* rng, u32 seed);
/* d_rng_next_u32
 * Purpose: Advance the RNG state and return the next value.
 * Parameters:
 *   rng (inout): RNG state. If NULL, returns 0.
 * Returns:
 *   Next `u32` value in the sequence.
 */
u32  d_rng_next_u32(d_rng_state* rng);
/* d_rng_next_i32
 * Purpose: Advance the RNG state and return the next value reinterpreted as `i32`.
 * Parameters:
 *   rng (inout): RNG state. If NULL, returns 0.
 * Returns:
 *   Next value cast to `i32` (two's complement is assumed by the determinism baseline).
 */
i32  d_rng_next_i32(d_rng_state* rng);
/* d_rng_peek_u32
 * Purpose: Compute the next value without updating the stored RNG state.
 * Parameters:
 *   rng (in): RNG state. If NULL, returns 0.
 * Returns:
 *   The next `u32` value that `d_rng_next_u32` would return.
 */
u32  d_rng_peek_u32(const d_rng_state* rng);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINO_CORE_RNG_H */
