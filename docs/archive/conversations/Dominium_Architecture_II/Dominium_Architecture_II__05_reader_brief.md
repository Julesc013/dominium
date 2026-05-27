# Reader Brief — Dominium Architecture II

## What This Chat Was About

This chat developed the Dominium project from broad systems brainstorming into a detailed deterministic engine architecture and Codex-ready implementation plan. It covered the world model, building model, cut/fill and terrain layers, roads/rails/tunnels/bridges as vector-authored but grid-baked corridors, surface versus space domains, orbital construction/logistics, and the repository/documentation structure needed to guide Codex 5.1 Max. The chat ended with the user preparing to retire the conversation and asking for a maximum-fidelity package for future continuation.

The most immediate practical output is a set of V4 spec replacements and Codex prompts. The important current target is a playable MVP: one full-size Earth surface; all systems minimally interactable; Lua for all data; Windows/DX9/Win32/SDL2 path; 2D vector top-down and 3D vector first-person. Multiplayer, Sol/space, all other renderers/platforms, textures, sounds and music are later steps.

## Most Important Things to Know

- Dominium core must be deterministic, integer/fixed-point, C89-compatible.
- No floats in authoritative simulation.
- Renderer and platform are strictly separate from sim.
- MVP is vector-only and DX9/Windows-first.
- The world uses meters plus Q16.16 fixed substeps.
- Spatial ladder is subnano → surface, with sparse microgrids/chunks.
- Buildings use blocks/cells/faces/edges as sim truth.
- Doors/devices are explicit fixtures, never automatic tunnel features.
- Terrain uses immutable base terrain plus earthworks deltas/cavities.
- Vector splines bake into chainpoints/linear microgrids.
- Space uses on-rails logic and local bubbles, not full n-body.
- Lua data lives through `/engine/script` with Lua 5.4.4 and sandboxed APIs.
- State hash uses FNV-1a 64-bit over canonical authoritative serialization.
- Codex should use only the listed files and current docs/dev files.

## Active Plans or Workstreams

- WORKSTREAM-01: Unified documentation/source-of-truth
- WORKSTREAM-02: Deterministic core/kernel
- WORKSTREAM-03: ECS architecture
- WORKSTREAM-04: Messaging, events, jobs
- WORKSTREAM-05: Spatial hierarchy and cosmic identity
- WORKSTREAM-06: Terrain, cut/fill, and microgrids
- WORKSTREAM-07: Building system: cells, faces, edges, fixtures
- WORKSTREAM-08: Vector corridor/spline infrastructure
- WORKSTREAM-09: Utility networks: power, data, fluids, thermal
- WORKSTREAM-10: Transport systems
- WORKSTREAM-11: Pathfinding and deterministic movement
- WORKSTREAM-12: Surface vs space and orbital systems

## Decisions Already Made

- DECISION-01: Use meter-based world coordinates with fixed substeps/Q16.16.
- DECISION-02: Use strict sim/render separation.
- DECISION-03: Adopt base-16 spatial ladder from subnano to surface.
- DECISION-04: Store surfaces as sparse microgrids/chunks, not continuous dense arrays.
- DECISION-05: Default local world is Earth/Sol/Milky Way.
- DECISION-06: Support canonical surface plus multiple surface instances for shards/mirrors.
- DECISION-07: Cross-surface interactions are asynchronous external events only.
- DECISION-08: Use on-rails orbital mechanics, not full n-body.
- DECISION-09: Docking, landing and takeoff are state-machine/domain transitions.
- DECISION-10: Use blocks/modules/cells/faces/edges as building simulation truth.
- DECISION-11: Use vector shapes/splines as authoring, generation and visual layers only.
- DECISION-12: Place walls/floors/roofs on grid faces/edges including diagonals.
- DECISION-13: Buildings rigid for now but schema supports destruction/collapse later.
- DECISION-14: Doors/devices are explicit fixtures placed manually or by explicit blueprint/pattern.
- DECISION-15: Immutable base terrain plus earthworks deltas and cavities.
- DECISION-16: Vector alignments bake into deterministic ChainPoints and linear microgrids.

## Pending Tasks

- TASK-01: Apply/verify BUILDING.md V4
- TASK-02: Apply/verify SPEC_CORE.md V4
- TASK-03: Apply/verify DATA_FORMATS.md V4
- TASK-04: Apply/verify DIRECTORY_CONTEXT.md V4
- TASK-05: Verify dominium_new_addendum.txt contains renderer/platform addendum
- TASK-06: Generate CMake/build skeleton
- TASK-07: Implement core/sim/ECS shell
- TASK-08: Implement Win32 + DX9 vector shell
- TASK-09: Wire minimal client loop
- TASK-10: Implement 2D/3D vector camera/input controls
- TASK-11: Add /engine/script to DIRECTORY_CONTEXT/build
- TASK-12: Vendor Lua 5.4.4
- TASK-13: Implement script VM and sandbox
- TASK-14: Implement Lua bindings
- TASK-15: Create minimal Lua data prototypes

## Open Questions

- QUESTION-01: Have V4 docs been applied to the actual repository?
- QUESTION-02: Does the actual repo contain /engine, /game, /data etc. yet?
- QUESTION-03: Should docs root remain flat or use /docs/spec?
- QUESTION-04: How to reconcile Lua-for-all-data with JSON-oriented DATA_FORMATS sections?
- QUESTION-05: What is the final DomDrawCmd/camera API?
- QUESTION-06: Native Win32 or SDL2 first?
- QUESTION-07: Can DX9.0c reliably target Windows 2000 SP4 through Windows 11?
- QUESTION-08: Can SDL2 support Windows 2000 target?
- QUESTION-09: Can Lua 5.4.4 build with old/retro compilers?
- QUESTION-10: What exact ECS component set is MVP?

## Files / Artifacts / Prompts to Preserve

- ARTIFACT-19: User-provided current directory tree
- ARTIFACT-20: BUILDING.md V4
- ARTIFACT-21: SPEC_CORE.md V4
- ARTIFACT-22: DATA_FORMATS.md V4
- ARTIFACT-23: DIRECTORY_CONTEXT.md V4
- ARTIFACT-24: Codex consistency pass prompt
- ARTIFACT-25: Codex CMake/build skeleton prompt
- ARTIFACT-26: Codex core API skeleton prompt
- ARTIFACT-27: Codex sim/ECS shell prompt
- ARTIFACT-28: Codex platform/render shell prompt
- ARTIFACT-29: Codex minimal client loop prompt
- ARTIFACT-30: Lua clarification answer

## What to Verify Before Acting

- VERIFY-01: Actual repo file contents and whether V4 docs applied.
- VERIFY-02: Actual directory existence under /engine, /game, /data, etc.
- VERIFY-03: DX9.0c support on Windows 2000 SP4 through Windows 11+.
- VERIFY-04: SDL2 support for Windows 2000 target.
- VERIFY-05: Lua 5.4.4 portability to required compilers.
- VERIFY-06: Restrictive LICENCE.md legal enforceability.
- VERIFY-07: CMake minimum/toolchains and flags.
- VERIFY-08: JSON-vs-Lua data policy.
- VERIFY-09: Final DomDrawCmd/camera API.
- VERIFY-10: Current docs use LICENCE.md and SPEC_CORE.md names consistently.

## Best Next Step

Verify that BUILDING.md, SPEC_CORE.md, DATA_FORMATS.md, DIRECTORY_CONTEXT.md, and docs/dev/dominium_new_addendum.txt on disk match the generated/current intent, then run the Codex consistency pass before any implementation.
