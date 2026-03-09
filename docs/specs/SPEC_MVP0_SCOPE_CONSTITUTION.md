Status: CANONICAL
Last Reviewed: 2026-03-09
Supersedes: none
Superseded By: none

# MVP-0: v0.0.0 Scope Constitution

Status: binding. Scope: Dominium v0.0.0 product boundary, baseline reality profile, exclusions, success criteria, and forward-compatibility floor.

## Purpose

This document freezes the target for Dominium v0.0.0.

It defines what is in scope, what is out of scope, and what must remain stable
for forward-compatible expansion. All v0.0.0 implementation work and all
implementation prompts targeting v0.0.0 MUST conform to this document, subject
to `docs/canon/constitution_v1.md` and `docs/canon/glossary_v1.md`.

This document does not authorize:

- weakened determinism
- narrative content
- civilization simulation
- non-minimal data expansion
- art or asset dependencies

This scope inherits the following constitutional rules and does not weaken them:

- no runtime mode flags; profiles only
- Process-only mutation
- Observer/Renderer/Truth separation
- pack-driven integration with deterministic refusal or degradation when packs
  are absent

## 1) MVP intent

Dominium v0.0.0 is:

- deterministic
- procedural
- lawful
- geometry-agnostic
- MMO-ready
- code-heavy and data-light
- replay-stable
- overlay-safe
- zero-civilization baseline universe

For v0.0.0:

- `MMO-ready` means the substrate preserves authoritative server compatibility,
  lawful authority evaluation, stable identity, and replay discipline. It does
  not imply civilization, economy, or live-service feature scope.
- `code-heavy and data-light` means the baseline relies on code, profiles,
  contracts, and minimal Packs rather than large content datasets.

Dominium v0.0.0 demonstrates:

- Milky Way procedural generation
- minimal Sol system pinning
- procedural Earth-like planet generation
- full GEO, LOGIC, PROC, and SYS infrastructure presence
- geometry editing
- `freecam` plus minimal embodiment
- deterministic overlay model

It is not a game yet.
It is a playable universe substrate.

## 2) Included systems (mandatory)

### 2.1 GEO (full)

v0.0.0 MUST include:

- `SpaceTopologyProfile`
- `MetricProfile`
- `PartitionProfile`
- `ProjectionProfile`
- stable `GeoCellKey` identity
- frame graph
- deterministic metric queries
- Field binding to GEO
- pathing substrate
- geometry editing contract
- worldgen interface
- overlay merge model
- GEO stress envelope

### 2.2 PHYS (baseline realistic)

v0.0.0 MUST include:

- quantities and units
- Fields for temperature, pollution, and gravity stubs
- energy ledger
- entropy proxy
- deterministic transforms

### 2.3 TEMP

v0.0.0 MUST include:

- canonical tick
- temporal domains
- deterministic scheduling

### 2.4 SYS

v0.0.0 MUST include:

- System templates
- collapse and expand
- capsule boundaries
- reliability and forensics

### 2.5 PROC

v0.0.0 MUST include:

- Process definitions
- yield, defect, and QC surfaces
- stabilization
- capsules
- drift detection
- software pipelines stubbed but present

### 2.6 LOGIC

v0.0.0 MUST include:

- signals, buses, and carriers
- logic elements
- network graph
- deterministic evaluation
- timing and oscillation handling
- compilation and collapse
- debug instrumentation
- fault, noise, and security hooks
- protocol layer
- stress envelope

### 2.7 EMBODIMENT (minimal)

v0.0.0 MUST include:

- body capsule collider
- first-person and third-person lenses
- `freecam`
- basic tool interface
- no art dependency

### 2.8 UX

v0.0.0 MUST include:

- CLI map view
- GUI `freecam`
- teleport tool
- inspection panels
- diegetic instrumentation

## 3) Excluded systems (non-goals for v0.0.0)

The following are explicitly out of scope for v0.0.0:

- NPC agents
- economy
- governments
- crafting trees
- real DEM or Earth data packs
- cities
- roads
- traffic systems
- combat systems
- interstellar travel mechanics
- detailed climate simulation
- biology
- AI behavior trees
- narrative or lore systems
- full rendering assets such as textures or models

The teleport tool is an observer or tooling affordance only. It is not a
diegetic travel mechanic.

## 4) Default reality profile

### 4.1 Universe

The default reality profile for v0.0.0 MUST be:

- Milky Way procedural galaxy
- realistic physical constants
- no civilization

### 4.2 Sol system

The Sol baseline MUST be a minimal pin with:

- star mass
- orbital hierarchy
- planet radii and masses
- moon orbit

The Sol baseline MUST NOT include terrain data.

### 4.3 Earth

Earth MUST be procedural and Earth-like, with:

- correct radius, tilt, and rotation
- ocean coverage target
- continental noise distribution
- polar ice caps
- climate bands stub
- day, night, and seasonal cycle

Earth MUST NOT include:

- real DEM
- cities
- borders

## 5) Determinism requirements

The following are mandatory:

- same `UniverseIdentity` produces the same outputs
- all world generation uses named RNG streams
- all authoritative IDs derive from
  `universe_seed + geo_cell_key + object_kind + local_subkey`
- no wall-clock dependence
- no unordered container iteration in authoritative paths
- deterministic ordering and deterministic reduction rules
- thread-count invariance for authoritative outcomes
- all debug paths and overrides logged through profiles and exception ledger
- replay from compaction anchors matches canonical hash partitions

## 6) Overlay safety

The following are mandatory:

- the procedural base layer is canonical
- the official Sol pin is an Overlay
- any future Earth DEM Pack overlays existing identity; it does not replace IDs
- player edits are stored as patch-layer overlays
- identity does not change without explicit migration

## 7) Performance constraints

The following are mandatory:

- on-demand generation only
- no eager galaxy instantiation
- all heavy evaluation budgeted through META-COMPUTE
- coupling relevance gates expensive updates
- compiled logic is preferred under load

## 8) Success criteria for v0.0.0

A build qualifies as v0.0.0 only when all of the following are true.

### 8.1 User-visible capability

The user can:

- launch a universe with the default profile
- teleport anywhere in the Milky Way
- refine the Sol system
- refine Earth
- observe day and night cycle
- edit terrain
- place and evaluate logic circuits
- collapse and expand Systems
- view maps and projections
- replay deterministically

### 8.2 Stress harnesses

The following stress harnesses pass:

- GEO stress
- LOGIC stress
- PROC stress
- overlay stress

### 8.3 Portability proof

Cross-platform canonical hash matches are required.

## 9) Forward compatibility guarantee

The following contracts are frozen and must not require restart of the
compatibility model:

- GEO profiles
- stable ID derivation
- overlay merge model
- worldgen `generator_version` lock
- Process capsule semantics
- logic compilation contract
- profile override architecture

Refactors are allowed.
Restarts are not.

## 10) Declaration

This document freezes the target for Dominium v0.0.0.

All implementation work must conform.
All future Packs must layer on top.
All deviations must be explicit and versioned.
