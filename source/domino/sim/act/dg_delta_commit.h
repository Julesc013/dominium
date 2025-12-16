/*
FILE: source/domino/sim/act/dg_delta_commit.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / sim/act/dg_delta_commit
RESPONSIBILITY: Implements `dg_delta_commit`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
/* Sorted delta commit (deterministic; C89).
 *
 * Commit is the sole authorized mutation point for authoritative simulation
 * state. All deltas buffered for the tick are applied in canonical order.
 */
#ifndef DG_DELTA_COMMIT_H
#define DG_DELTA_COMMIT_H

#include "sim/act/dg_delta_buffer.h"
#include "sim/act/dg_delta_registry.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct dg_delta_commit_stats {
    u32 deltas_applied;
    u32 deltas_rejected;    /* unknown handler */
    u64 ordering_checksum;  /* optional; 0 if none */
} dg_delta_commit_stats;

/* Sort deltas by canonical dg_order_key and apply them via registry handlers. */
int dg_delta_commit_apply(
    void                   *world,
    const dg_delta_registry *registry,
    dg_delta_buffer        *buffer,
    dg_delta_commit_stats  *out_stats
);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DG_DELTA_COMMIT_H */

