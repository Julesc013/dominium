/*
FILE: source/domino/sim/lod/dg_stride.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / sim/lod/dg_stride
RESPONSIBILITY: Defines internal contract for `dg_stride`; shared within its subsystem; does NOT define a public API (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/specs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (internal header).
EXTENSION POINTS: Extend via public headers and relevant `docs/specs/SPEC_*.md` without cross-layer coupling.
*/
/* Deterministic cadence decimation helpers (C89).
 *
 * Used to run low-frequency updates in a stable way without RNG/time sources.
 */
#ifndef DG_STRIDE_H
#define DG_STRIDE_H

#include "sim/pkt/dg_pkt_common.h"

#ifdef __cplusplus
extern "C" {
#endif

/* Returns D_TRUE if a stride-based update should run at 'tick' for 'stable_id'.
 *
 * Rule:
 *   (tick + hash(stable_id)) % stride == 0
 *
 * Notes:
 * - 'stride' of 0 or 1 means "always run".
 * - hash() is deterministic and platform-stable (see core/dg_det_hash.h).
 */
d_bool dg_stride_should_run(dg_tick tick, u64 stable_id, u32 stride);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DG_STRIDE_H */

