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
