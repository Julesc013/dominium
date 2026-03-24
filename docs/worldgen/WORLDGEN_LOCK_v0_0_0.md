Status: DERIVED
Last Reviewed: 2026-03-24
Supersedes: none
Superseded By: none
Stability: stable
Future Series: OMEGA
Replacement Target: post-mock release worldgen lock archive and intentional lock-version bump record

# Worldgen Lock v0.0.0

Ω-1 freezes the current MVP world genesis path as the canonical lock for `v0.0.0-mock`.

This document describes the current behavior. It does not introduce new generation features or new truth semantics.

## Lock Scope

The frozen authoritative chain is:

- seed string
- locked universe identity template
- GEO root stream derivation
- L0 galaxy coarse structure
- L1 star distribution
- L2 Sol/system derivation
- L3 Earth terrain projection
- stable IDs, stage hashes, and baseline snapshot artifacts

## 1. Canonical Seed Type

- Canonical seed type: UTF-8 string
- Current authoritative field: `universe_identity.global_seed`
- MVP lock seed baseline file: `data/baselines/worldgen/baseline_seed.txt`
- Canonical seed hash for lock artifacts:
  - `canonical_sha256({"seed_text": <seed_string>})`

Canonical serialization rules:

- Seed text is stored exactly as UTF-8 without trimming or numeric coercion.
- Worldgen lock artifacts serialize via canonical JSON with sorted keys and compact separators.
- Ordered lists in the lock are semantically ordered and must not be re-sorted by downstream tooling.

Identity boundary:

- Root RNG streams derive from:
  - `global_seed`
  - `generator_version_id`
  - `realism_profile_id`
  - semantic `geo_cell_key`
  - `stream_name`
- Stable world object IDs additionally derive from `universe_identity_hash`.
- Therefore, for this lock, “same seed” means:
  - same seed string
  - same locked universe identity template inputs
  - same generator version lock
  - same realism profile lock

## 2. RNG Stream Registry

Root stream derivation rule:

- `global_seed + generator_version_id + realism_profile_id + geo_cell_key + stream_name -> stream_seed`
- Implementation surface: `src/geo/worldgen/worldgen_engine.py::worldgen_stream_seed`
- Hash primitive: `canonical_sha256(...)`

Canonical ordered stream registry for the MVP lock:

1. `rng.worldgen.galaxy`
2. `rng.worldgen.galaxy_objects`
3. `rng.worldgen.system`
4. `rng.worldgen.system.primary_star`
5. `rng.worldgen.system.planet_count`
6. `rng.worldgen.system.planet.{planet_index}`
7. `rng.worldgen.planet`
8. `rng.worldgen.surface`
9. `rng.worldgen.surface.tile`
10. `rng.worldgen.surface.generator`
11. `rng.worldgen.surface.elevation`
12. `rng.worldgen.surface.earth.elevation`

Lock rules:

- No implicit RNG is allowed in the authoritative worldgen truth path.
- New named streams require an explicit worldgen lock version bump and baseline regeneration.
- Reuse of an existing stream for a new semantic purpose is a lock break and requires a version bump.

## 3. Refinement Pipeline

Current MVP stages present in the authoritative path:

- L0: galaxy coarse structure
  - surface: `generate_mw_cell_payload`
  - outputs:
    - cell summary
    - galactocentric placement
    - density/metallicity/habitability proxies
    - `system_seed_rows`
- L1: star distribution
  - surfaces:
    - `generate_mw_cell_payload`
    - `generate_galaxy_object_stub_payload`
  - outputs:
    - `star_system_artifact_rows`
    - galaxy object stub artifacts
- L2: Sol system derivation
  - surface: `generate_mw_system_l2_payload`
  - outputs:
    - star IDs
    - planet IDs
    - moon stub IDs
    - orbit/basic artifact rows
    - system summary rows
  - Sol anchor note:
    - `sol_anchor_object_ids` is a deterministic identity projection on the anchor cell
    - it is not a separate random generator
- L3: Earth terrain projection
  - surfaces:
    - `build_planet_surface_cell_key`
    - `generate_mw_surface_l3_payload`
    - `generate_earth_surface_tile_plan`
    - climate/tide/material/hydrology evaluators
  - outputs:
    - surface tile IDs
    - elevation parameter refs
    - climate proxies
    - geometry initialization
    - field initialization

Stage order is frozen:

- L0 must complete before L1 materialization.
- L1 system artifacts feed L2 only.
- L2 system artifacts feed L3 only.
- L3 operates on requested surface tiles only and must not eagerly expand neighboring tiles.

## 4. Invariants

Under this lock, the same seed and locked universe identity template MUST produce identical:

- galaxy node IDs
- star IDs
- planet IDs
- earth tile IDs
- elevation field hashes
- initial climate proxy hashes
- refinement stage hashes

Additional lock invariants:

- `geo_object_id` derivation must remain stable for `kind.star_system`, `kind.star`, `kind.planet`, `kind.moon`, and `kind.surface_tile`.
- Root stream derivation must remain canonical and ordered.
- L3 surface routing must stay pack/registry driven.
- No float may enter the authoritative worldgen truth path.
- No unnamed RNG may enter the authoritative worldgen truth path.

Refinement idempotence rule:

- Re-running the same locked stage with identical inputs must reproduce the same normalized artifact rows and deterministic fingerprints.
- Re-running L3 for the same requested tile must not change previously derived hashes for that tile.

## 5. Explicit Non-Goals

- No astrophysical realism guarantee
- No tectonics simulation
- No erosion evolution
- No eager full-planet terrain bake
- No cross-compiler matrix guarantee in Ω-1
  - that comparison is deferred to Ω-9

## 6. Stability Marker

```text
worldgen_lock_version = 0
stability_class = stable
worldgen_lock_id = worldgen_lock.v0_0_0
```

## 7. Baseline Artifacts

The lock is enforced by:

- `data/registries/worldgen_lock_registry.json`
- `data/baselines/worldgen/baseline_seed.txt`
- `data/baselines/worldgen/baseline_worldgen_snapshot.json`
- `tools/worldgen/tool_generate_worldgen_baseline`
- `tools/worldgen/tool_verify_worldgen_lock`
- `docs/audit/WORLDGEN_LOCK_VERIFY.md`
- `docs/audit/WORLDGEN_LOCK_BASELINE.md`
