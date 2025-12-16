/*
FILE: source/domino/world/frame/dg_frame.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / world/frame/dg_frame
RESPONSIBILITY: Defines internal contract for `dg_frame`; shared within its subsystem; does NOT define a public API (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (internal header).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
/* Generic frame identifiers (C89).
 *
 * Frames form a directed acyclic parent graph (forest) used for deterministic
 * coordinate transforms. No semantics are implied by "frame".
 */
#ifndef DG_FRAME_H
#define DG_FRAME_H

#include "domino/core/types.h"

#include "sim/pkt/dg_pkt_common.h"

#ifdef __cplusplus
extern "C" {
#endif

/* Stable frame identifier used by packets and authoritative state. */
typedef u64 dg_frame_id;

/* Reserved world/root frame id. */
#define DG_FRAME_ID_WORLD ((dg_frame_id)0u)

/* Fixed bound for parent traversal (no unbounded recursion). */
#define DG_FRAME_MAX_DEPTH 16u

d_bool dg_frame_id_is_world(dg_frame_id id);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DG_FRAME_H */

