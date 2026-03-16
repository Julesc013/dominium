Status: CANONICAL
Last Reviewed: 2026-03-13
Supersedes: none
Superseded By: none
Scope: v0.0.0 convergence boundary for Dominium.
Stability: provisional
Future Series: DOC-ARCHIVE
Replacement Target: legacy reference surface retained without current binding authority

# MVP Scope Lock

This document freezes the scope of `v0.0.0`.
After this lock, work is limited to consolidation, validation, portability, platform hardening, UI harmonization, and release preparation.
It does not authorize new simulation domains, new gameplay systems, new material chemistry, new economy layers, or semantic contract drift.

## Engine Core Included

- Deterministic simulation kernel: Assemblies, Fields, Processes, and Law.
- GEO topology, frame, metric, partition, and projection layers.
- MW galaxy refinement pipeline and system seed generation.
- SOL illumination geometry and orbital proxy layers.
- EARTH terrain, hydrology, climate, wind, and tide proxy layers.
- Material, surface, and albedo proxies as EARTH stub surfaces.
- Embodiment movement plus jump stub support.
- Logic L1 evaluation and L2 compile path.
- SYS and PROC composition frameworks.
- Pollution advection with bounded deterministic updates.
- Server authority and headless execution.
- Capability negotiation and explicit degrade ladders.
- Pack compatibility validation and pack lock generation.
- LIB content-store, install, and instance flows.
- AppShell CLI, TUI, rendered, and native-selection surfaces.
- IPC attach and detach flows.
- Supervisor-managed process topology.
- Deterministic repro bundles and replay proof verification.
- Proof anchors and epoch anchors.
- Stability tagging and replacement-plan discipline.

## Explicitly Excluded From v0.0.0

- Real fluid volume simulation.
- Periodic table, molecules, and chemistry semantics.
- Crafting and inventory systems.
- Vehicles and transport simulation.
- Tectonics and erosion simulation.
- Ecology and vegetation dynamics.
- Economy, institutions, and governance simulation.
- Combat and damage systems.
- Stellar lifecycle and supernova simulation.
- Real ephemerides and N-body physics.
- OS-native GUIs beyond the basic launcher and setup shell surfaces.

## Provisional Stub Systems

- Earth material proxy:
  future_series=`MAT`
  replacement_target=`Replace EARTH-10 proxy rows with MAT-authored surface material semantics.`
- Earth albedo proxy:
  future_series=`SOL/EARTH`
  replacement_target=`Replace EARTH-10 albedo stubs with calibrated SOL/EARTH illumination-aware surface response models.`
- Galaxy density, metallicity, and radiation proxies:
  future_series=`GAL+/ASTRO`
  replacement_target=`Replace GAL-0 proxy fields with dynamic galaxy domain pack semantics.`
- Compact object stubs:
  future_series=`ASTRO-DOMAIN`
  replacement_target=`Replace static compact-object stubs with dynamic lifecycle and gas-dynamics domain systems.`
- Orbit proxy:
  future_series=`SOL/GAL`
  replacement_target=`Replace the MVP Kepler proxy with pack-selected N-body or real ephemeris providers without refactoring GEO lens consumers.`
- Sky gradient model:
  future_series=`SOL/EARTH`
  replacement_target=`Replace sky stubs with calibrated SOL/EARTH sky models.`
- Wind proxy model:
  future_series=`EARTH`
  replacement_target=`Replace wind stubs with calibrated EARTH wind parameter sets.`
- Tide proxy model:
  future_series=`EARTH/SOL`
  replacement_target=`Replace tide stubs with calibrated EARTH/SOL tide parameter sets.`

## Convergence Rule

From this lock forward:

- no new simulation domain families
- no new gameplay systems
- no semantic changes to frozen contracts
- no directory restructures
- no regression lock changes without the explicitly required update tag for that lock
