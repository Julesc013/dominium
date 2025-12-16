/*
FILE: source/domino/world/frame/dg_frame_eval.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / world/frame/dg_frame_eval
RESPONSIBILITY: Implements `dg_frame_eval`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
/* Deterministic frame evaluation (C89).
 *
 * No caching in this prompt; evaluation walks the parent chain explicitly.
 */
#ifndef DG_FRAME_EVAL_H
#define DG_FRAME_EVAL_H

#include "domino/core/types.h"

#include "core/dg_pose.h"
#include "sim/pkt/dg_pkt_common.h"

#include "world/frame/dg_frame_graph.h"

#ifdef __cplusplus
extern "C" {
#endif

/* Evaluate a frame's transform to world for the given tick.
 * Rules:
 * - Traverse parent chain in canonical order (single parent chain).
 * - Apply transforms in fixed order (rootward compose).
 * - Bounded depth (DG_FRAME_MAX_DEPTH), no recursion.
 * Returns 0 on success.
 */
int dg_frame_eval(
    const dg_frame_graph *g,
    dg_frame_id           id,
    dg_tick               tick,
    dg_round_mode         round_mode,
    dg_pose              *out_transform
);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DG_FRAME_EVAL_H */

