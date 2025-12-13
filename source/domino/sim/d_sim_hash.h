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
