/*
FILE: include/domino/core/rng.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino API / core/rng
RESPONSIBILITY: Defines the public contract for `rng` (types/constants/function signatures); does NOT provide implementation.
ALLOWED DEPENDENCIES: `include/domino/**` plus C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `source/**` private headers; keep contracts freestanding and layer-respecting.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: Public header; see `docs/SPEC_ABI_TEMPLATES.md` where ABI stability matters.
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
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

/* d_rng_state: Public type used by `rng`. */
typedef struct d_rng_state {
    u32 state;
} d_rng_state;

/* Purpose: Seed rng.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 */
void d_rng_seed(d_rng_state* rng, u32 seed);
/* Purpose: Next u32.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/CONTRACTS.md#Return Values / Errors`.
 */
u32  d_rng_next_u32(d_rng_state* rng);
/* Purpose: Next i32.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/CONTRACTS.md#Return Values / Errors`.
 */
i32  d_rng_next_i32(d_rng_state* rng);
/* Purpose: Peek u32.
 * Parameters: See `docs/CONTRACTS.md#Parameters`.
 * Returns: See `docs/CONTRACTS.md#Return Values / Errors`.
 */
u32  d_rng_peek_u32(const d_rng_state* rng);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINO_CORE_RNG_H */
