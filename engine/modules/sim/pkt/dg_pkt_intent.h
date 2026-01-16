/*
FILE: source/domino/sim/pkt/dg_pkt_intent.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / sim/pkt/dg_pkt_intent
RESPONSIBILITY: Defines internal contract for `dg_pkt_intent`; shared within its subsystem; does NOT define a public API (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (internal header).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
/* Intent packet ABI (deterministic; C89).
 *
 * Placement/edit contract (authoritative):
 * - BUILD / TRANS / STRUCT / DECOR placement intents MUST be expressed as:
 *     - dg_anchor (parametric reference to authoring primitives)
 *     - local dg_pose offset relative to that anchor
 * - Unquantized placement commands are invalid and MUST be rejected before
 *   becoming authoritative state.
 * - Raw world-space meshes/vertex lists are forbidden in intents.
 *
 * See docs/SPEC_POSE_AND_ANCHORS.md and docs/SPEC_PACKETS.md.
 */
#ifndef DG_PKT_INTENT_H
#define DG_PKT_INTENT_H

#include "sim/pkt/dg_pkt_common.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct dg_pkt_intent {
    dg_pkt_hdr            hdr;
    const unsigned char  *payload;     /* TLV bytes; not owned */
    u32                   payload_len; /* mirrors hdr.payload_len */
} dg_pkt_intent;

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DG_PKT_INTENT_H */
