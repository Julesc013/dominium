Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

--------------------------------
OWNERSHIP & RESPONSIBILITY
--------------------------------
ENGINE:
- Deterministic primitives and invariants defined by this spec.
- Implementation lives under `engine/` (public API in `engine/include/`).

GAME:
- Rules, policy, and interpretation defined by this spec.
- Implementation lives under `game/` (rules/content/ui as applicable).

TOOLS:
- None. Tools may only consume public APIs if needed.

SCHEMA:
- None (no canonical schema formats defined here).

FORBIDDEN:
- No launcher/setup orchestration logic in engine or game.
- No engine internal headers exposed outside engine targets.
- No game rules or policy implemented inside engine primitives.

DEPENDENCIES:
- Engine -> libs/ and schema/ only (never game/launcher/setup/tools).
- Game -> engine public API and schema/ only.
- Tools -> engine public API, game public API, and schema/ only.
- Launcher/Setup (if applicable) -> libs/contracts + schema (launcher may also use engine public API).
--------------------------------
# World Coordinates and Bands

- Horizontal world is a torus: `2^24` tiles per axis (~16.7M m circumference). Tile size = 1 m.
- Vertical tile range is fixed: `z ∈ [-2048 .. +2047]` (4096 tiles, 256 chunks).
- Chunking: `DOM_CHUNK_SIZE = 16` (16×16×16 tiles); `DOM_Z_CHUNKS = 256`.

## Relationship to anchor-based placement (authoritative)
The tile/chunk lattice is an addressing and partitioning scheme used by grid-like
domains (terrain/fields/hydrology/climate) and for deterministic chunk mapping.
It is **not** an engine-wide placement constraint.

Arbitrary placement for BUILD/TRANS/STRUCT/DECOR is expressed via anchors and
fixed-point poses (`dg_anchor` + `dg_pose`) per `docs/specs/SPEC_POSE_AND_ANCHORS.md`.
Any mapping from anchor/pose world positions to tiles/chunks is a deterministic
derived operation (quantization and chunk indexing), not an authoring truth.

## Vertical bands
- Deep underworld: z < -1024 (`DOM_Z_DEEP_MIN .. DOM_Z_BUILD_MIN`) — no normal construction, special rules later.
- Buildable band: `[-1024 .. +1536]` (`DOM_Z_BUILD_MIN .. DOM_Z_BUILD_MAX`) — full terrain + construction.
- High airspace: `+1537 .. +2047` (`DOM_Z_BUILD_MAX+1 .. DOM_Z_TOP_MAX`) — no construction; aircraft/balloons only.
- Above-grid: high-atmo / lat-lon-alt handled as `ENV_HIGH_ATMO`.
- Orbit: `ENV_ORBIT` via orbit engine when transitioning out of grid.

## Coordinate structs
- `WPosTile { x, y, z }`: tile indices; x/y wrap on the torus, z clamps to bounds.
- `WPosExact { tile, dx, dy, dz }`: sub-tile offsets in Q16.16 relative to `tile`.
- `ChunkPos { cx, cy, cz }`: chunk indices (16 tiles per axis, cz = 0..255).
- `LocalPos { lx, ly, lz }`: local coordinates inside a chunk (0..15 each).
- Helpers convert tile ↔ chunk/local and wrap x/y using `dworld_wrap_tile_coord`.
- Environment helpers: `dworld_env_from_z`, `dworld_should_switch_to_high_atmo`, `dworld_should_switch_to_orbit` gate between grid/air/orbit layers (logic stubbed for now).

## Environments and mobility
- `EnvironmentKind`: `ENV_SURFACE_GRID`, `ENV_AIR_LOCAL`, `ENV_HIGH_ATMO`, `ENV_WATER_SURFACE`, `ENV_WATER_SUBMERGED`, `ENV_ORBIT`, `ENV_VACUUM_LOCAL`.
- `AggregateMobilityKind`: `AGG_STATIC`, `AGG_SURFACE`, `AGG_WATER`, `AGG_AIR`, `AGG_SPACE`.
- `dworld_env_from_z` classifies z into bands (surface grid, local air, high atmosphere stubbed for now); `dworld_z_is_buildable` gates construction to the buildable band.

## Wrapping rules
- x/y tile indices wrap modulo `DOM_WORLD_TILES` to stay on the torus; negative indices are normalised deterministically.
- z is clamped to `[DOM_Z_MIN .. DOM_Z_MAX]`.
- Coordinate conversions stay integer-only; no floating point is permitted in Domino coordinate math.