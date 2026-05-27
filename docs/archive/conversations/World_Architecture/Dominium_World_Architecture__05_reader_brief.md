# Reader Brief — Dominium World Architecture

## What This Chat Was About

This chat designed a deterministic, fixed-point, modular world architecture for a Dominium-style game. It covered the core spatial hierarchy, coordinate system, save format, runtime memory model, continuous terrain, material/media fields, hydrology, weather, climate, gases, liquids, oil/gas reservoirs, flooding, ruptures, networks, modding, tooling, launcher architecture, and a Codex implementation prompt. The main design principle is that chunks and segments are storage/cache boundaries only, while canonical simulation state lives in deterministic global/topological systems.

The final user-confirmed world model uses a toroidal horizontal SurfaceGrid of 2^24 metres per axis, one vertical Page of 4096 metres, 16 metre cubic chunks, runtime Q16.16 coordinates with 8-bit Segment addressing, and Q4.12 chunk-local save coordinates. The core and saves must not use floats. The core target is C89; platform/renderer/runtime may use C++98 and floats only outside the deterministic core.

## Most Important Things to Know

- SurfaceGrid is toroidal 2^24m in X/Y.
- Z is one Page: 4096m total, 2km down/up.
- Chunk = 16×16×16m.
- Runtime = Segment + Q16.16.
- Save = Q4.12 local-to-chunk.
- Correct signedness bug: local X/Y and chunk-local Q4.12 should be unsigned or otherwise redesigned.
- No floats in core or saves.
- Core C89; platform/renderer C++98 and floats allowed one-way.
- Cosmic IDs: 2^8 galaxies, 2^24 systems, 2^16 planets.
- One canonical surface saved per planet for now.
- Chunks are caches, not authorities.
- Terrain is continuous φ, not blocks.
- Ground and air are abstract materials/media, not blocks.
- Use FluidSpaces, Connectors, SpatialVolumes, and Networks for environmental systems.
- content.lock and deterministic registries are required.
- Previous Codex prompt is useful but defective and must be repaired.

## Active Plans or Workstreams

- Fixed-point deterministic core.
- Sparse TLV save format.
- Chunk/segment runtime memory.
- Continuous terrain/material/media.
- Fluid/weather/hydrology systems.
- Oil/gas/flooding/rupture support.
- Network systems for pipes/electric/heat/logic.
- Mod/content registry and deterministic Lua.
- Repo-wide modular engine/runtime/launcher/tools architecture.
- Corrected Codex implementation prompt.
- Determinism and seam tests.

## Decisions Already Made

- 2^24m toroidal horizontal surface.
- One Page Z = 4096m.
- 16m chunks.
- Runtime Q16.16.
- Save Q4.12.
- 8-bit Segment addressing.
- No floats in core/saves.
- C89 core, C++98 platform/renderer.
- One canonical saved surface per planet.
- Directory names should encode high address bits.
- Chunks must not own canonical simulation state.

## Pending Tasks

- Repair Codex prompt.
- Inspect actual repo.
- Define unsigned fixed-point types.
- Define C89 portability layer.
- Correct Region bit decomposition.
- Implement world address conversions.
- Implement TLV save/load.
- Implement minimal geom_sample and chunk cache.
- Add deterministic tests.
- Specify solvers later.

## Open Questions

- How exactly to handle 64-bit integers under C89 constraints?
- Unsigned local coordinates vs centered signed representation?
- Exact endian/alignment/compression save policy?
- Exact terrain meshing algorithm and sample resolution?
- Exact weather/hydrology/hydraulic/thermal formulas?
- Exact content manifest and Lua sandbox?
- Actual repo/build system/toolchain?

## Files / Artifacts / Prompts to Preserve

- Previous Codex 5.1 implementation prompt, but only after correction.
- Original Context Transfer Packet.
- This report package and ZIP.
- Registers and YAML spec sheet.

## What to Verify Before Acting

- Fixed-point signedness corrections.
- Region bit widths.
- C89 compatibility.
- Saved rotations are 8-bit.
- Actual repo structure.
- Compiler and platform targets.

## Best Next Step

Revise the prior Codex implementation prompt using this report, then inspect the actual git repo before generating or applying code changes.
