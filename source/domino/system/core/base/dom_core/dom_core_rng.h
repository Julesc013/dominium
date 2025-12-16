/*
FILE: source/domino/system/core/base/dom_core/dom_core_rng.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / system/core/base/dom_core/dom_core_rng
RESPONSIBILITY: Implements `dom_core_rng`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
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
