/*
FILE: source/domino/decor/compile/dg_decor_tiles.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino impl / decor/compile/dg_decor_tiles
RESPONSIBILITY: Defines internal contract for `dg_decor_tiles`; shared within its subsystem; does NOT define a public API (see `include/**`).
ALLOWED DEPENDENCIES: `include/domino/**`, `source/domino/**`, and C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `include/dominium/**`, `source/dominium/**` (engine must not depend on product layer).
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: N/A (internal header).
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
/* DECOR compiled tiles (C89).
 *
 * Tiles are chunk-aligned render-only batches, grouped by decor_type_id.
 * No rendering backend is referenced here.
 */
#ifndef DG_DECOR_TILES_H
#define DG_DECOR_TILES_H

#include "domino/core/types.h"

#include "sim/pkt/dg_pkt_common.h"

#include "decor/model/dg_decor_ids.h"
#include "decor/compile/dg_decor_instances.h"

#ifdef __cplusplus
extern "C" {
#endif

typedef struct dg_decor_tile {
    dg_chunk_id     chunk_id;
    dg_decor_type_id decor_type_id;
    u32             index_offset; /* into dg_decor_tiles.indices */
    u32             index_count;
} dg_decor_tile;

typedef struct dg_decor_tiles {
    dg_decor_tile *tiles;
    u32           tile_count;
    u32           tile_capacity;

    u32          *indices; /* instance indices (u32) */
    u32           index_count;
    u32           index_capacity;
} dg_decor_tiles;

void dg_decor_tiles_init(dg_decor_tiles *t);
void dg_decor_tiles_free(dg_decor_tiles *t);
void dg_decor_tiles_clear(dg_decor_tiles *t);
int  dg_decor_tiles_reserve(dg_decor_tiles *t, u32 tile_capacity, u32 index_capacity);

/* Build tiles grouped by decor_type_id (ascending).
 * Within each tile, indices follow the canonical instance order.
 *
 * Returns 0 on success.
 */
int dg_decor_tiles_build_from_instances(dg_decor_tiles *out, const dg_decor_instances *instances);

#ifdef __cplusplus
} /* extern "C" */
#endif

#endif /* DG_DECOR_TILES_H */

