/*
FILE: include/domino/dworld.h
MODULE: Domino
LAYER / SUBSYSTEM: Domino API / dworld
RESPONSIBILITY: Defines the public contract for `dworld` (types/constants/function signatures); does NOT provide implementation.
ALLOWED DEPENDENCIES: `include/domino/**` plus C89/C++98 standard headers as needed.
FORBIDDEN DEPENDENCIES: `source/**` private headers; keep contracts freestanding and layer-respecting.
THREADING MODEL: No internal synchronization; callers must serialize access unless stated otherwise.
ERROR MODEL: Return codes/NULL pointers; no exceptions.
DETERMINISM: See `docs/SPEC_DETERMINISM.md` for deterministic subsystems; otherwise N/A.
VERSIONING / ABI / DATA FORMAT NOTES: Public header; see `docs/SPEC_ABI_TEMPLATES.md` where ABI stability matters.
EXTENSION POINTS: Extend via public headers and relevant `docs/SPEC_*.md` without cross-layer coupling.
*/
#ifndef DOMINO_DWORLD_H
#define DOMINO_DWORLD_H

#include "dnumeric.h"

#ifdef __cplusplus
extern "C" {
#endif

/* Horizontal torus: 2^24 tiles circumference (~16.7M m) */
#define DOM_WORLD_TILES_LOG2 24
#define DOM_WORLD_TILES      (1u << DOM_WORLD_TILES_LOG2)

/* Chunk dimensions */
#define DOM_CHUNK_SIZE  16          /* 16x16x16 tiles per chunk */
#define DOM_Z_CHUNKS    256         /* 256 chunks vertically => 4096 tiles */

/* Vertical tile bounds: [-2048 .. +2047] */
#define DOM_Z_MIN       (-2048)
#define DOM_Z_MAX       ( 2047)

/* Vertical bands (semantic) */
#define DOM_Z_DEEP_MIN  (-2048)     /* Deep underworld low bound */
#define DOM_Z_BUILD_MIN (-1024)     /* Minimum z for normal construction */
#define DOM_Z_BUILD_MAX ( 1536)     /* Maximum z for construction */
#define DOM_Z_TOP_MAX   ( 2047)     /* Maximum z of world grid */

/* Kármán-line-ish logical alt for orbit transitions handled later */

/* Purpose: Horizontal tile coordinate (x/y) on the world torus.
 *
 * Notes:
 * - Canonical range after wrapping is `[0, DOM_WORLD_TILES)`.
 */
typedef int32_t TileCoord;
/* Purpose: Vertical tile coordinate (z) in the bounded world grid.
 * Range: `DOM_Z_MIN .. DOM_Z_MAX`.
 */
typedef int16_t TileHeight;

/* Purpose: Tile-space world position (x/y wrap on the horizontal torus). */
typedef struct {
    TileCoord  x;
    TileCoord  y;
    TileHeight z;
} WPosTile;

/* Purpose: Sub-tile exact position with Q16.16 offsets within tile coordinates (POD). */
typedef struct {
    WPosTile tile;
    PosUnit  dx;
    PosUnit  dy;
    PosUnit  dz;
} WPosExact;

/* Purpose: Chunk coordinate (cx/cy) in chunk-space. */
typedef int32_t ChunkCoord;
/* Purpose: Chunk height coordinate (cz) in chunk-space.
 * Range: 0..`DOM_Z_CHUNKS - 1` in current layouts.
 */
typedef int16_t ChunkHeight;

/* Purpose: Chunk-space world position (cx/cy/cz) (POD). */
typedef struct {
    ChunkCoord  cx;
    ChunkCoord  cy;
    ChunkHeight cz;   /* 0..255 */
} ChunkPos;

/* Purpose: Local coordinate within a chunk axis. Range: 0..`DOM_CHUNK_SIZE - 1`. */
typedef uint8_t LocalCoord;

/* Purpose: Local position within a chunk (lx/ly/lz) (POD). */
typedef struct {
    LocalCoord lx;
    LocalCoord ly;
    LocalCoord lz;
} LocalPos;

/* Purpose: High-level embedding for an actor/aggregate in the world model. */
typedef enum {
    ENV_SURFACE_GRID,    /* inside voxel world grid (terrain, buildings) */
    ENV_AIR_LOCAL,       /* low-altitude airspace, still referencing grid */
    ENV_HIGH_ATMO,       /* high atmosphere/near-space, no terrain construction */
    ENV_WATER_SURFACE,   /* ocean/lake surface */
    ENV_WATER_SUBMERGED, /* underwater */
    ENV_ORBIT,           /* analytic Kepler orbit around a body */
    ENV_VACUUM_LOCAL     /* local inertial bubble near station/ship in space */
} EnvironmentKind;

/* Purpose: Aggregate mobility classification for environment constraints. */
typedef enum {
    AGG_STATIC,    /* anchored to terrain, buildings, fixed installations */
    AGG_SURFACE,   /* moves on/near surface: cars, trucks, ground robots */
    AGG_WATER,     /* boats, ships, submarines */
    AGG_AIR,       /* aircraft, VTOL, drones in atmosphere */
    AGG_SPACE      /* spacecraft, stations, orbital platforms */
} AggregateMobilityKind;

/* Coordinate helpers */

/* Wraps a horizontal tile coordinate into the canonical [0, DOM_WORLD_TILES) range. */
TileCoord dworld_wrap_tile_coord(TileCoord t);

/* Converts a tile position into chunk + local coordinates.
 *
 * Purpose: Convert from tile-space to chunk-space + local-space addressing.
 *
 * Parameters:
 *   - tile: Input tile position (required).
 *   - out_chunk/out_local: Optional outputs; may be NULL.
 */
void dworld_tile_to_chunk_local(const WPosTile *tile, ChunkPos *out_chunk, LocalPos *out_local);

/* Converts chunk + local coordinates back into a tile position.
 *
 * Purpose: Convert from chunk-space + local-space addressing back to tile-space.
 *
 * Preconditions:
 *   - chunk/local/out_tile must be non-NULL; otherwise the function is a no-op.
 */
void dworld_chunk_local_to_tile(const ChunkPos *chunk, const LocalPos *local, WPosTile *out_tile);

/* Purpose: Initialize an exact position from a tile position with zero sub-tile offsets. */
void dworld_init_exact_from_tile(const WPosTile *tile, WPosExact *out_pos);

/* Environment helpers */
/* Purpose: Map a clamped z tile height to a coarse environment kind. */
EnvironmentKind dworld_env_from_z(TileHeight z);
/* Purpose: Return whether `z` falls within the buildable vertical band. */
bool            dworld_z_is_buildable(TileHeight z);
/* Purpose: Return whether an exact position should transition from grid/airspace to high atmosphere. */
bool            dworld_should_switch_to_high_atmo(const WPosExact *pos);
/* Purpose: Return whether an exact position should transition from high atmosphere to orbit. */
bool            dworld_should_switch_to_orbit(const WPosExact *pos);

#ifdef __cplusplus
}
#endif

#endif /* DOMINO_DWORLD_H */
