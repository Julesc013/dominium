# Dominium — Core Deterministic Contract (Engine v0)

This document is the binding description for the deterministic core that now lives in `/engine/`. It aligns code, runtime stubs, and tools with the fixed-point, C89-only model required for replayable simulation.

## 1. Language and determinism
- Core engine (`/engine/*.c`) is **C89** only. No C99, no `//` comments, no VLAs.
- Authoritative simulation state and save data use **integers and fixed-point only**. No floats/doubles anywhere inside `/engine/` or any save format.
- Runtime/frontends (`/runtime`, `/launcher`, `/tools`) use **C++98** max and must not feed floating-point values back into engine state.
- Iteration order is deterministic; ECS and chunk tables are stable and sorted/hashed deterministically. RNG state is explicit and saved.
- Fixed tick step (`fix32 dt`) is required; multi-rate scheduling is stubbed but order is fixed for future systems.

## 2. Numeric model
- Base types in `engine/core_types.h`: `u8/u16/u32/u64`, signed variants, and `b32` (`TRUE`/`FALSE` macros).
- Fixed-point:
  - `fix32` = **Q16.16** (`FIX32_ONE`, `FIX32_HALF`, helpers for mul/div).
  - `fix16` = **Q4.12** for chunk-local save positions.
- Angles use discrete integers: yaw/pitch/roll as `u16` (0..65535 → 0..360°).
- All IDs are 64-bit: `EntityId`, `VolumeId`, `FluidSpaceId`, `ThermalSpaceId`, `NetNodeId`, `NetEdgeId`, `RNGId`, `RecipeId`.

## 3. Coordinates and world shape
- Surfaces are toroidal: **2²⁴ m × 2²⁴ m** in X/Y. Z range is fixed to **[-2048 m, +2048 m)**.
- Segment grid: 256×256 segments. Each segment spans **65,536 m** per axis.
- Chunking: chunks are **16×16×16 m**. There are 4096 chunks per segment axis and 256 chunks vertically.
- Runtime coordinate (`SimPos`, in `engine/world_addr.h`):
  - `sx/sy`: `u8` segment indices.
  - `x/y/z`: `fix32` local position inside the segment (wrapped modulo 65,536 m; z clamped to [-2048,+2048)).
- Chunk key (`ChunkKey3D`) holds global chunk indices; `SaveLocalPos` uses `fix16` for 0..16 m offsets inside a chunk.
- Mapping helpers (`engine/world_addr.c`) convert `SimPos` ↔ chunk key + local offsets and normalise/wrap coordinates deterministically.

## 4. RNG rules
- Deterministic xoroshiro128+ variant (`engine/core_rng.*`) with explicit seed/state.
- Registry map from `RNGId` → `RNGState` is fixed-size and never implicit.
- Procedural sampling uses stateless coordinate hashing; time-varying systems use saved `RNGState` only. No dependence on load order or wallclock.

## 5. World model and services
- Surfaces own:
  - Chunk hash table (fixed size) of `ChunkRuntime` caches (terrain samples, entity/volume refs, dirty flags).
  - Registry pointers (materials, volumes, recipes).
  - RNG states for weather/hydro/misc.
  - ECS storage (sorted by `EntityId`).
- Geometry sampling (`geom_sample`) is pure and reconstructable from seeds/recipes + edits/volumes; caches are optional accelerators.
- Fields sampling (`field_sample_scalar/vector`) exposes deterministic scalar/vector fields (elevation stubbed, temperature stubbed).
- `WorldServices` (in `engine/sim_world.h`) is the read-only gateway for runtime/game code: raycast/overlap stubs, geometry sampling, medium/field sampling.

## 6. Simulation order (stubbed but fixed)
Per-surface tick (`sim_tick_surface`):
1. Input/commands (stubbed).
2. ECS movement/kinematics (normalises positions).
3. Networks (electrical/hydraulic) — stub.
4. Fluid spaces — stub.
5. Climate/atmo/hydro — stub.
6. Thermal — stub.
7. Apply edit ops, mark chunk dirty — stub.
Order is fixed now to keep determinism as systems fill in later.

## 7. Save/IO contract (summary)
- `UniverseMeta` (`universe.meta`) stores version + universe seed.
- `SurfaceMeta` (`surface_XXX.meta`) stores version, surface id, seed, recipe id, and all core RNG states.
- Region files (`regions/surface_XXX_region.bin`) contain chunk blobs as TLV sections (`ChunkSectionHeader`), with reserved types 1–6 for engine and 1000+ for mods. Unknown sections are skipped.
- Chunk caches are non-authoritative; canonical state is seeds + edits + deterministic rules.

## 8. Layering
- `/engine/`: deterministic core, C89, fixed-point only.
- `/runtime/`: game-facing binaries, C++98, may use floats internally for rendering/UI but never feed them into engine state.
- `/launcher/`: C++98 stub that orchestrates runtimes; reads metadata only.
- `/tools/`: offline inspectors/validators; reuse engine IO and do not reinvent formats.

These rules are binding for all current code and any future expansion. Conflicts elsewhere must be resolved in favour of this file.
