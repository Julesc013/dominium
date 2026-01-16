/*
FILE: include/domino/core/rng_streams.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino API / core/rng_streams
RESPONSIBILITY: Deterministic RNG stream bundle for authoritative code paths.
ALLOWED DEPENDENCIES: `include/domino/**` plus C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: OS entropy sources; platform time APIs.
*/
#ifndef DOMINO_CORE_RNG_STREAMS_H
#define DOMINO_CORE_RNG_STREAMS_H

#include "domino/core/rng.h"

#ifdef __cplusplus
extern "C" {
#endif

/* d_rng_stream_id
 * Purpose: Named RNG streams for deterministic separation of concerns.
 * Notes:
 * - Streams are deterministic given the same root seed.
 */
typedef enum d_rng_stream_id {
    D_RNG_STREAM_SIM = 0,
    D_RNG_STREAM_CONTENT = 1,
    D_RNG_STREAM_EFFECTS = 2,
    D_RNG_STREAM_MAX = 3
} d_rng_stream_id;

/* d_rng_streams
 * Purpose: Bundle of deterministic RNG states, one per stream.
 */
typedef struct d_rng_streams {
    d_rng_state streams[D_RNG_STREAM_MAX];
} d_rng_streams;

/* d_rng_streams_seed
 * Purpose: Seed all streams from a single root seed.
 * Parameters:
 *   rngs (out): Stream bundle to seed. If NULL, this is a no-op.
 *   seed (in): Root seed value.
 */
void d_rng_streams_seed(d_rng_streams* rngs, u32 seed);

/* d_rng_stream_seed
 * Purpose: Seed a single stream explicitly.
 * Parameters:
 *   rngs (inout): Stream bundle. If NULL, this is a no-op.
 *   id (in): Stream identifier.
 *   seed (in): Seed value.
 */
void d_rng_stream_seed(d_rng_streams* rngs, d_rng_stream_id id, u32 seed);

/* d_rng_stream
 * Purpose: Get a mutable RNG state for a stream.
 * Returns: Pointer to the stream state, or NULL for invalid inputs.
 */
d_rng_state* d_rng_stream(d_rng_streams* rngs, d_rng_stream_id id);

/* d_rng_stream_const
 * Purpose: Get a read-only RNG state for a stream.
 * Returns: Pointer to the stream state, or NULL for invalid inputs.
 */
const d_rng_state* d_rng_stream_const(const d_rng_streams* rngs, d_rng_stream_id id);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DOMINO_CORE_RNG_STREAMS_H */
