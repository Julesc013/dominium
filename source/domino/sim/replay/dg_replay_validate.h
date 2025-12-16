/*
FILE: source/domino/sim/replay/dg_replay_validate.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / sim/replay/dg_replay_validate
RESPONSIBILITY: Implements `dg_replay_validate`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
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

