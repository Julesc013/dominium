/*
FILE: source/domino/decor/compile/dg_decor_instances.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / decor/compile/dg_decor_instances
RESPONSIBILITY: Defines internal contract for `dg_decor_instances`; shared within its subsystem; does NOT define a public API (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (internal header).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
/* DECOR compiled instance lists (C89).
 *
 * Instances are neutral, renderer-agnostic records with cached evaluated poses.
 */
#ifndef DG_DECOR_INSTANCES_H
#define DG_DECOR_INSTANCES_H

#include "domino/core/types.h"

#include "core/dg_pose.h"
#include "sim/pkt/dg_pkt_common.h"
#include "world/frame/d_world_frame.h"

#include "decor/model/dg_decor_item.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct dg_decor_instance {
    dg_chunk_id     chunk_id;
    dg_decor_id      decor_id;
    dg_decor_type_id decor_type_id;
    u32              flags; /* DG_DECOR_ITEM_F_* subset */
    u32              _pad32;

    dg_decor_host host;

    dg_pose world_pose;

    dg_decor_tlv params;
} dg_decor_instance;

typedef struct dg_decor_instances {
    dg_decor_instance *items;
    u32                count;
    u32                capacity;
} dg_decor_instances;

void dg_decor_instances_init(dg_decor_instances *out);
void dg_decor_instances_free(dg_decor_instances *out);
void dg_decor_instances_clear(dg_decor_instances *out);
int  dg_decor_instances_reserve(dg_decor_instances *out, u32 capacity);

/* Build a canonical instance list by evaluating poses for each item.
 * items must already be in canonical order (dg_decor_item_cmp).
 *
 * Returns 0 on success, <0 on error (pose eval failure).
 */
int dg_decor_instances_build_from_items(
    dg_decor_instances  *out,
    const dg_decor_item *items,
    u32                  item_count,
    dg_chunk_id          chunk_id,
    const d_world_frame *frames,
    dg_tick              tick,
    dg_round_mode        round_mode
);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DG_DECOR_INSTANCES_H */

