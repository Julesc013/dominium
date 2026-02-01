Status: DERIVED
Last Reviewed: 2026-02-01
Supersedes: none
Superseded By: none

--------------------------------
OWNERSHIP & RESPONSIBILITY
--------------------------------
ENGINE:
- None. Engine provides generic primitives only if referenced.

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
# SPEC_CONSTRUCTIONS_V0 - Construction Model v0 (Local Bubble Only)

This spec defines the v0 construction model: deterministic placement of small
structures inside active local bubbles. It is authoritative for runtime
behavior and persistence, and does not describe rendering or gameplay loops.

## 1. Construction instances
Each construction instance includes:
- `instance_id`: stable, deterministic id (u64).
- `construction_type_id`: deterministic type id (u32).
- `body_id`: owning celestial body id (u64).
- `surface_chunk_key`: deterministic surface chunk key (see
  `docs/specs/SPEC_SURFACE_STREAMING.md`).
- `local_position`: fixed-point meters in a local tangent frame anchored at the
  chunk origin.
- `orientation`: axis-aligned rotation (0, 90, 180, 270 degrees), stored as a
  0..3 enum.

Local tangent frame origin is defined by the chunk's origin lat/long. The
orientation is in that frame and never uses floats.

## 2. Construction types (v0)
Type ids are fixed for v0:
- `1`: HABITAT
- `2`: STORAGE
- `3`: GENERIC_PLATFORM

Type ids must remain deterministic across platforms and releases.

## 3. Placement rules
Placement is command-driven and deterministic:
- Placement MUST be inside an active activation bubble.
- `body_id` MUST match the active bubble body.
- Height is sampled via the deterministic height sampler.
- The grid is 1 meter. Overlap is forbidden (grid-cell occupancy).
- Invalid placements are refused with explicit codes.

Placement and removal occur only at tick boundaries. Missing derived data must
never block placement; fidelity may degrade instead.

## 4. Commands
Two commands are authoritative inputs:
- `CMD_PLACE_CONSTRUCTION_V1`
  - `construction_type_id` (u32)
  - `body_id` (u64)
  - `lat_turns` (q16.16)
  - `lon_turns` (q16.16)
  - `orientation` (u32)
- `CMD_REMOVE_CONSTRUCTION_V1`
  - `instance_id` (u64)

Commands are applied in deterministic order (peer id, command id).

## 5. Persistence
Constructions are stored in:
- Universe bundles: `CNST` chunk (versioned).
- Saves: `CNST` chunk (versioned).
- Replays: recorded as commands.

Unknown fields/chunks are skipped and preserved per container rules.

## 6. Related specs
- `docs/specs/SPEC_LANES_AND_BUBBLES.md`
- `docs/specs/SPEC_SURFACE_STREAMING.md`
- `docs/specs/SPEC_SURFACE_TOPOLOGY.md`
- `docs/specs/SPEC_DETERMINISM.md`