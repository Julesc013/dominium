/*
FILE: source/domino/sim/d_sim_hash.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / sim/d_sim_hash
RESPONSIBILITY: Implements `d_sim_hash`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
/* Deterministic world hashing helpers (C89). */
#ifndef D_SIM_HASH_H
#define D_SIM_HASH_H


#include "world/d_world.h"
#include "domino/core/types.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef u64 d_world_hash;

/* Compute bit-stable hash of all active world state. */
d_world_hash d_sim_hash_world(const d_world *w);

/* Optional chunk-level hashing. */
d_world_hash d_sim_hash_chunk(const d_chunk *chunk);

#ifdef __cplusplus
}
#endif

#endif
