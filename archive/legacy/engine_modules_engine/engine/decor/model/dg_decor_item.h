/*
FILE: source/domino/decor/model/dg_decor_item.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / decor/model/dg_decor_item
RESPONSIBILITY: Defines internal contract for `dg_decor_item`; shared within its subsystem; does NOT define a public API (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (internal header).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
/* DECOR items (C89).
 *
 * Decor items are derived placement instances. Authoring is source-of-truth
 * via rulepacks + overrides + anchors.
 */
#ifndef DG_DECOR_ITEM_H
#define DG_DECOR_ITEM_H

#include "domino/core/types.h"

#include "core/dg_pose.h"
#include "world/frame/dg_anchor.h"

#include "decor/model/dg_decor_ids.h"
#include "decor/model/dg_decor_host.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct dg_decor_tlv {
    const unsigned char *ptr; /* TLV bytes (tag:u32_le,len:u32_le,payload...) */
    u32                  len;
} dg_decor_tlv;

/* Decor item flags (authoring/compile metadata only). */
#define DG_DECOR_ITEM_F_NONE       0u
#define DG_DECOR_ITEM_F_PROMOTABLE ((u32)0x00000001u)
#define DG_DECOR_ITEM_F_PINNED     ((u32)0x00000002u) /* internal: pinned by override */

typedef struct dg_decor_item {
    dg_decor_id      decor_id;
    dg_decor_type_id decor_type_id;
    u32              flags;
    u32              _pad32; /* reserved; must be zero */

    dg_decor_host host;   /* host binding (authoring IDs only) */
    dg_anchor     anchor; /* authoritative anchor parameters (quantized) */
    dg_pose       local_offset;

    dg_decor_tlv params;
} dg_decor_item;

void dg_decor_item_clear(dg_decor_item *it);

/* Canonical comparator for final item/instance ordering:
 * (host kind, host id, decor_type_id, decor_id).
 */
int dg_decor_item_cmp(const dg_decor_item *a, const dg_decor_item *b);

/* Evaluate item anchor + local offset into a world-space pose. */
int dg_decor_item_eval_pose(
    const dg_decor_item *it,
    const d_world_frame *frames,
    dg_tick              tick,
    dg_round_mode        round_mode,
    dg_pose             *out_pose
);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DG_DECOR_ITEM_H */

