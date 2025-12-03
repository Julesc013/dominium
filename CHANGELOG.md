# Dominium — Change History and Compatibility Contract

This file documents **all user-visible and engine-visible changes** to Dominium.

It serves three purposes:

1. Track **features, fixes, and refactors** per version  
2. Document **determinism and save-compatibility guarantees**  
3. Provide a stable reference for **mod authors** and **port maintainers**

All entries must follow the rules below.

---

# 0. FORMAT AND RULES

## 0.1 Versioning

Dominium uses **semantic versioning with determinism qualifiers**:

- `MAJOR.MINOR.PATCH`  
- Optional suffixes:
  - `-dev`   — development / unstable  
  - `-exp`   — experimental branches  
  - `-rcN`   — release candidate  

Examples:

- `0.1.0-dev`
- `1.0.0`
- `1.1.3-rc1`

### MAJOR

Increment when:

- Determinism guarantees change fundamentally  
- Savefile format changes in a **non-migratable** way  
- Network protocol becomes incompatible with prior versions  

### MINOR

Increment when:

- Features are added  
- Savefiles remain **loadable** (with possible migration)  
- Determinism is preserved for matching version pairs  
- Network protocol remains compatible inside same MAJOR  

### PATCH

Increment when:

- Only bug fixes, internal refactors, and minor changes  
- No change in data formats that break saves or replays  

---

## 0.2 Entry Structure

Each version section:

```markdown
## [X.Y.Z] - YYYY-MM-DD

### Added
- …

### Changed
- …

### Fixed
- …

### Removed
- …

### Determinism & Compatibility
- Determinism: [Unchanged | Strengthened | Risky Change]
- Savefiles: [Fully compatible | Compatible via migration | Incompatible]
- Replays: [Compatible | Broken | N/A]
- Network: [Compatible | Incompatible | N/A]
Sections may be omitted if empty.
Every determinism-relevant change must be explicitly documented under Determinism & Compatibility.

0.3 Determinism Rules in Changelog
Any change that touches:
• engine/sim
• engine/core fixed-point math
• engine/net protocol
• Savefile structure
• Job system, tick order, or lanes
must:
1. Note whether old replays still produce identical results
2. Mark whether old saves load to a state equivalent under the new spec
3. Specify whether multiplayer clients with mismatched minor/patch versions can participate
If behaviour changes but is still deterministic, document that explicitly.

0.4 “Unreleased” Section
The top of this file always contains:
## [Unreleased]

### Added
- …

### Changed
- …

### Fixed
- …

### Removed
- …

### Determinism & Compatibility
- Determinism:
- Savefiles:
- Replays:
- Network:
Entries accumulate during development.
When a release is cut, the section is renamed to the version and a fresh [Unreleased] section is created above.

1. RELEASE HISTORY
[Unreleased]
Added
• Root repository structure (/docs, /engine, /game, /data, /mods, /tools, /tests, /external, /build, /package, /scripts, /ports).
• Project meta files:
o README.md
o LICENSE.md (strict, personal-use-only)
o SECURITY.md (determinism-focused security model)
o CODE_OF_CONDUCT.md
o .gitignore
o Root CMakeLists.txt
• Initial deterministic engine specification documents (V3 series, Volumes 1A–1B):
o Determinism kernel
o Tick pipeline
o ECS architecture
o Messaging and job systems
o Serialization, chunking, spatial indexing, prefabs, mod injection
Changed
• N/A (first tracked iteration)
Fixed
• N/A
Removed
• N/A
Determinism & Compatibility
• Determinism: Baseline model defined; no behaviour yet to change.
• Savefiles: Save format specified, but no stable on-disk format shipped.
• Replays: Replay model specified; no backwards compatibility constraints yet.
• Network: Lockstep protocol and invariants specified; no public compatibility expectations.

[0.1.0] - YYYY-MM-DD (FIRST PUBLIC SPEC SNAPSHOT)
Replace YYYY-MM-DD with actual release date.
Added
• Formalised deterministic kernel:
o Integer/fixed-point only simulation
o 7-phase tick pipeline
o Virtual lanes and merge rules
o Strict event ordering and backpressure model
• ECS core:
o Stable entity IDs with generation
o Dense component storage
o Strict sorted iteration by entity_id
• Messaging and jobs:
o Local/lane/cross-lane/global event buses
o Deterministic command buffers
o Job queues and worker assignment rules
o Interrupt model and task routing
• Persistence:
o Savefile block layout
o Chunk/subchunk/voxel metadata
o Network graph persistence
o Replay-log architecture
• Spatial & physics:
o Meter-based integer grid
o Chunk/subchunk hierarchy
o BVH and wide uniform grid
o Integer-based collision and raycasting
• Prefabs & mods:
o Prefab format
o Deterministic prefab instantiation
o Strict mod capabilities and prohibitions
• Build system:
o Root CMake with:
• DOM_BUILD_ENGINE_ONLY
• DOM_BUILD_CLIENT
• DOM_BUILD_SERVER
• DOM_BUILD_TOOLS
• DOM_BUILD_TESTS
• Backend feature flags (GL1/GL2/DX9/DX11/software)
• Determinism checks (DOM_STRICT_DETERMINISM)
Changed
• N/A (first tagged spec release)
Fixed
• N/A
Removed
• N/A
Determinism & Compatibility
• Determinism:
o Defined as core invariant of the project.
o All simulation design is constrained by deterministic architecture.
• Savefiles:
o Canonical format defined; initial version = 0x00030000.
o No prior versions to support.
• Replays:
o Replay records defined; semantics stable for 0.1.x line.
• Network:
o Lockstep protocol defined; 0.1.x line expected to remain internally compatible unless explicitly broken.

2. FUTURE ENTRY TEMPLATE
For future releases, copy and fill:
## [X.Y.Z] - YYYY-MM-DD

### Added
- New features…

### Changed
- Behaviour changes…

### Fixed
- Bug fixes…

### Removed
- Deprecated or removed features…

### Determinism & Compatibility
- Determinism:
  - [e.g.] Tick ordering unchanged; modifications scoped to UI only.
- Savefiles:
  - [e.g.] Old saves auto-migrated via migration step M3 → M4.
- Replays:
  - [e.g.] Replays from 0.1.x no longer valid due to changed job routing.
- Network:
  - [e.g.] Network protocol remains compatible within MAJOR 1.
All determinism-impacting changes must be evaluated and documented here.