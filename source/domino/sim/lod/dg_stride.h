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

