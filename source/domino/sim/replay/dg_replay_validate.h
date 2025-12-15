/* Replay validation (C89).
 *
 * Validation compares two replay streams and localizes the first divergence.
 * No strings in mismatch output: IDs and hashes only.
 */
#ifndef DG_REPLAY_VALIDATE_H
#define DG_REPLAY_VALIDATE_H

#include "domino/core/types.h"

#include "sim/hash/dg_hash.h"
#include "sim/replay/dg_replay_stream.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef enum dg_replay_validate_mode {
    DG_REPLAY_VALIDATE_STRICT = 1,
    DG_REPLAY_VALIDATE_STRUCTURAL = 2,
    DG_REPLAY_VALIDATE_BEHAVIORAL = 3
} dg_replay_validate_mode;

typedef struct dg_replay_mismatch {
    d_bool            ok;
    dg_replay_validate_mode mode;

    dg_tick           tick;
    dg_hash_domain_id domain_id;

    dg_hash_value expected_hash;
    dg_hash_value actual_hash;

    u32 expected_tick_index;
    u32 actual_tick_index;
} dg_replay_mismatch;

void dg_replay_mismatch_clear(dg_replay_mismatch *m);

/* Validate two streams.
 * Returns 0 if OK, 1 if mismatch found, <0 on error.
 */
int dg_replay_validate(
    dg_replay_validate_mode mode,
    const dg_replay_stream *expected,
    const dg_replay_stream *actual,
    dg_replay_mismatch     *out_mismatch
);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DG_REPLAY_VALIDATE_H */

