/*
FILE: source/domino/struct/model/dg_struct_ids.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / struct/model/dg_struct_ids
RESPONSIBILITY: Defines internal contract for `dg_struct_ids`; shared within its subsystem; does NOT define a public API (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (internal header).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
/* STRUCT stable identifiers and canonical ordering helpers (C89).
 *
 * STRUCT authoring objects and compiled artifacts are referenced by stable
 * numeric IDs and MUST define total ordering for all deterministic iteration
 * and compilation.
 */
#ifndef DG_STRUCT_IDS_H
#define DG_STRUCT_IDS_H

#include "domino/core/types.h"

#include "core/det_invariants.h"

#ifdef __cplusplus
extern "C" {
#endif

/* Authoring IDs (stable). */
typedef u64 dg_struct_id;
typedef u64 dg_struct_footprint_id;
typedef u64 dg_struct_volume_id;
typedef u64 dg_struct_enclosure_id;
typedef u64 dg_struct_surface_template_id;
typedef u64 dg_struct_socket_id;
typedef u64 dg_struct_carrier_intent_id;

/* Compiled artifact IDs (stable). */
typedef u64 dg_struct_occ_region_id;
typedef u64 dg_struct_room_id;
typedef u64 dg_struct_surface_id;
typedef u64 dg_struct_support_node_id;
typedef u64 dg_struct_support_edge_id;
typedef u64 dg_struct_carrier_artifact_id;

/* Surface key used for stable ordering/lookup in compiled graphs. */
typedef struct dg_struct_surface_key {
    dg_struct_id        struct_id;
    dg_struct_surface_id surface_id;
} dg_struct_surface_key;

static int dg_struct_surface_key_cmp(const dg_struct_surface_key *a, const dg_struct_surface_key *b) {
    int c;
    if (a == b) return 0;
    if (!a) return -1;
    if (!b) return 1;
    c = D_DET_CMP_U64(a->struct_id, b->struct_id);
    if (c) return c;
    c = D_DET_CMP_U64(a->surface_id, b->surface_id);
    if (c) return c;
    return 0;
}

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DG_STRUCT_IDS_H */

