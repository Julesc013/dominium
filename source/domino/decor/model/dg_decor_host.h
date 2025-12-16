/*
FILE: source/domino/decor/model/dg_decor_host.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / decor/model/dg_decor_host
RESPONSIBILITY: Implements `dg_decor_host`; owns translation-unit-local helpers/state; does NOT define the public contract (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (implementation file).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
/* DECOR host bindings (C89).
 *
 * Host bindings are host-agnostic references to authoring IDs. They MUST NOT
 * reference compiled geometry or rendering artifacts.
 */
#ifndef DG_DECOR_HOST_H
#define DG_DECOR_HOST_H

#include "domino/core/types.h"

#include "core/det_invariants.h"
#include "sim/pkt/dg_pkt_common.h"

#include "trans/model/dg_trans_ids.h"
#include "struct/model/dg_struct_ids.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef enum dg_decor_host_kind {
    DG_DECOR_HOST_NONE = 0,
    DG_DECOR_HOST_TERRAIN_PATCH = 1,
    DG_DECOR_HOST_TRANS_SLOT_SURFACE = 2,
    DG_DECOR_HOST_STRUCT_SURFACE = 3,
    DG_DECOR_HOST_ROOM_SURFACE = 4,
    DG_DECOR_HOST_SOCKET = 5
} dg_decor_host_kind;

typedef struct dg_decor_host_terrain_patch {
    dg_chunk_id chunk_id; /* terrain patch host is chunk-aligned */
} dg_decor_host_terrain_patch;

typedef struct dg_decor_host_trans_slot_surface {
    dg_trans_alignment_id alignment_id;
    u32                   segment_index; /* microsegment index (0-based) */
    dg_trans_slot_id       slot_id;       /* slot/surface identifier (0 means invalid) */
} dg_decor_host_trans_slot_surface;

typedef struct dg_decor_host_struct_surface {
    dg_struct_id         struct_id;
    dg_struct_surface_id surface_id;
} dg_decor_host_struct_surface;

typedef struct dg_decor_host_room_surface {
    dg_struct_room_id    room_id;
    dg_struct_surface_id surface_id;
} dg_decor_host_room_surface;

typedef struct dg_decor_host_socket {
    u64 socket_id; /* host-specific; stable within its subsystem */
} dg_decor_host_socket;

typedef union dg_decor_host_u {
    dg_decor_host_terrain_patch     terrain_patch;
    dg_decor_host_trans_slot_surface trans_slot_surface;
    dg_decor_host_struct_surface    struct_surface;
    dg_decor_host_room_surface      room_surface;
    dg_decor_host_socket            socket;
} dg_decor_host_u;

typedef struct dg_decor_host {
    dg_decor_host_kind kind;
    u32                _pad32; /* reserved; must be zero */
    dg_decor_host_u    u;
} dg_decor_host;

void dg_decor_host_clear(dg_decor_host *h);

/* Canonical total-order comparator for host bindings. */
int dg_decor_host_cmp(const dg_decor_host *a, const dg_decor_host *b);

/* Stable numeric host id used for deterministic seeding. */
u64 dg_decor_host_stable_id_u64(const dg_decor_host *h);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DG_DECOR_HOST_H */

