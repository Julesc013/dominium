/* Deterministic scheduler phases (C89).
 *
 * This header defines the authoritative phase list for SIM tick scheduling.
 * Phase ordering MUST remain stable across platforms and builds.
 *
 * See: docs/SPEC_SIM_SCHEDULER.md
 */
#ifndef DG_PHASE_H
#define DG_PHASE_H

#include "domino/core/types.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef enum dg_phase {
    DG_PH_INPUT = 0,
    DG_PH_TOPOLOGY = 1,
    DG_PH_SENSE = 2,
    DG_PH_MIND = 3,
    DG_PH_ACTION = 4,
    DG_PH_SOLVE = 5,
    DG_PH_COMMIT = 6,
    DG_PH_HASH = 7,
    DG_PH_COUNT = 8
} dg_phase;

typedef struct dg_phase_meta {
    dg_phase    phase;
    const char *name; /* debug/telemetry only; not used for determinism */
} dg_phase_meta;

d_bool dg_phase_is_valid(dg_phase phase);
u32 dg_phase_count(void);
const dg_phase_meta *dg_phase_meta_get(dg_phase phase);
const char *dg_phase_name(dg_phase phase);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DG_PHASE_H */

