# Dominium / Domino Identity and Determinism

## Overview
- Dominium, built on Domino, is a deterministic, integer/fixed-point simulation engine and game stack targeting retro-to-modern platforms without obsoleting prior content.
- Time-stable across decades: identical simulation outputs for identical inputs on all supported OS/architecture pairs.
- Core rule: determinism first; performance and convenience follow, never at the cost of simulation reproducibility.

## Domino Engine
- Language: ISO C89 only; no C99/C11 extensions, no host-dependent intrinsics. Dominium UI and higher-level product code uses a portable C++98 subset only; no C++11+ features.
- Responsibility: authoritative simulation loop, math, world coordinates, RNG, save/replay/net semantics.
- Numeric backbone: fixed-point types provided centrally (conceptual for now; future `fixed.h` will define):
  - Q4.12: compact storage (e.g. saves, network deltas, small ranges).
  - Q16.16 / Q24.8: main world/local geometry and simulation state.
  - Q48.16: high-range accumulators and aggregates.
- Domino owns all deterministic math; platform/UI code may convert to floats only at boundaries, never inside simulation.

## Dominium Product Suite
- Products (Game, Launcher, Setup, Tools) sit entirely atop Domino; no product may bypass Domino abstractions for simulation, IO, or rendering.
- Products are thin binaries that bind to Domino for sim, IO, and dgfx/dsys; platform/UI work lives above Domino, never replacing it.
- All product behaviors (modes, CLI, introspection) must be expressible via Domino-facing APIs and manifests.

## Determinism & Numeric Model
- Integer and fixed-point only inside simulation logic: u8/u16/u32/u64, i8/i16/i32/i64, Q4.12, Q16.16, Q24.8, Q48.16.
- Floats are forbidden in simulation, save/load, replay, and net code; floats are allowed only in platform/UI/GPU-only paths.
- World geometry: toroidal surface with circumference 2^24 meters (~16.7M m); vertical domain ±2 km, quantized to fit fixed-point choices.
- Deterministic RNG: seeded, reproducible streams; no host RNG, timers, or FP noise in simulation paths.
- Save formats use compact fixed-point (e.g. Q4.12) where possible; runtime may promote to higher resolution (Q16.16/Q24.8/Q48.16) internally without changing semantics.
- Simulation step ordering, RNG streams, save/load, replay, and net protocol semantics must produce identical outputs for identical inputs across all supported platforms.

## Platform & Architecture Matrix
Identical behavior is mandatory across all OS/architecture pairs below. Tiers describe development focus, not feature variance.

| OS family / shell            | Architectures                     | Tier            | Notes |
|------------------------------|-----------------------------------|-----------------|-------|
| WinNT (NT3→11)               | x86_32, x86_64, arm_64            | Tier 1 (primary)| |
| macOS X 10.6+ (Cocoa)        | x86_64, arm_64                    | Tier 1 (primary)| |
| Linux                        | x86_64, arm_64                    | Tier 1 (primary)| |
| BSD                          | x86_64                            | Tier 1 (primary)| |
| Web/WASM                     | wasm_32, wasm_64                  | Tier 1 (primary)| |
| Android                      | arm_32, arm_64                    | Tier 1 (primary)| |
| SDL2 shell                   | x86_32, x86_64, arm_32, arm_64    | Tier 1 (primary)| abstraction shell |
| DOS16/32                     | x86_16, x86_32                    | Tier 2 (retro)  | |
| Win3.x / Win9x               | x86_16, x86_32                    | Tier 2 (retro)  | |
| macOS Classic 7–9            | m68k_32, ppc_32                   | Tier 2 (retro)  | |
| Carbon                       | ppc_32, ppc_64                    | Tier 2 (retro)  | |
| SDL1 shell                   | x86_32, arm_32                    | Tier 2 (retro)  | abstraction shell |
| CPM80 / CPM86                | z80_8, x86_16                     | Tier 2 (retro)  | |

## Layering & Abstractions
- dsys: system abstraction for windowing, input, filesystem, processes, timing; sole path to host OS facilities.
- dgfx: graphics IR and backends; all rendering flows game → Domino → dgfx IR → backend (software/GPU/retro).
- Domino: deterministic simulation/core runtime; owns math, world state, IO semantics.
- Dominium products: Game/Launcher/Setup/Tools built strictly on Domino; they may provide UI but cannot bypass dsys/dgfx or alter sim determinism.
- Content (packs/mods/assets): data-only and scripting atop Dominium; never calls OS APIs directly; interacts via defined Domino/Dominium interfaces.
- Layer order is strict; no upward or sideways leaks (e.g., content cannot call dsys; products cannot embed platform-native drawing into simulation).

## Repository & DOMINIUM_HOME
- Single configurable root `DOMINIUM_HOME` holds repository products, packs, mods, and instances.
- Layout (conceptual): `repo/products/<product>/<product_version>/core-<core_version>/<OSFam-Arch>/bin/`, `repo/packs/<id>/<version>/`, `repo/mods/<id>/<version>/`, `instances/<instance_id>/...` (config, saves, logs).
- Multiple versions may coexist; GC removes unused versions safely.
- Detailed file/manifest schemas live in other docs (e.g., DATA_FORMATS); this spec defines the identity and invariants.

## Versioning & Compatibility Guarantees
- Distinct version domains: Domino core version, Dominium suite/game version, product version (launcher/game/setup/tools), pack/mod versions (SemVer-like).
- Compatibility profile defines: save format version, pack format version, net protocol version, replay format version, launcher↔game protocol version, tool↔game protocol version.
- Policy: never silently break old saves/packs/mods. Prefer read-compatible migrations; hard failures must be explicit and documented.
- Features unsupported on a given platform must be declared; behavior may degrade gracefully but determinism must hold.
- Any change to formats/protocols must update the compatibility profile and preserve deterministic playback of legacy data.
