Status: DERIVED
Last Reviewed: 2026-03-09
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# MW0 Retro Audit

## Scope

This audit records the repository state before MW-0 Milky Way procedural work.

Audit targets:

- GEO worldgen refinement compatibility
- named RNG stream readiness
- reusable procedural space-generation surfaces

## Existing GEO Refinement Contract

Current authoritative worldgen contracts already support an MW refinement ladder:

- `schema/geo/worldgen_request.schema`
  - binds generation to `geo_cell_key`
  - carries explicit `refinement_level`
- `schema/geo/worldgen_result.schema`
  - stores deterministic per-cell outputs
  - permits additional deterministic metadata through `extensions`
- `src/geo/worldgen/worldgen_engine.py`
  - already routes generation by cell key only
  - already locks `generator_version_id` and `realism_profile_id`
  - already emits bounded `worldgen_result` payloads

Compatibility conclusion:

- MW `L0..L3` fits the existing GEO request/result shape without reopening the base contract.
- The Milky Way layer can attach deterministic system-seed metadata through `worldgen_result.extensions`.

## Existing Named RNG Rules

Current named authoritative streams already exist in `src/geo/worldgen/worldgen_engine.py`:

- `rng.worldgen.galaxy`
- `rng.worldgen.system`
- `rng.worldgen.planet`
- `rng.worldgen.surface`

Current seed derivation surface:

- `worldgen_stream_seed(...)`
  - hashes `global_seed`
  - hashes `generator_version_id`
  - hashes `realism_profile_id`
  - hashes semantic `geo_cell_key`
  - hashes `stream_name`

Audit conclusion:

- MW-0 does not need a new RNG policy surface.
- The Milky Way generator should consume the existing named galaxy/system streams rather than introduce a parallel seed path.

## Existing Reusable Generator Surfaces

Reusable implementation surfaces already present:

- `src/geo/worldgen/worldgen_engine.py`
  - canonical generation entry point
  - cache/refusal/proof wiring already in place
- `src/geo/index/object_id_engine.py`
  - stable GEO-derived object identity derivation
- `tools/xstack/sessionx/process_runtime.py`
  - authoritative `process.worldgen_request` mutation boundary
- `tools/xstack/testx/tests/geo8_testlib.py`
  - deterministic fixtures for worldgen process execution
- `tools/geo/tool_replay_worldgen_cell.py`
  - replay/hash verification path for generated cells

Existing optional real-data content that must remain overlay-only:

- `data/worldgen/real/milky_way/`
- `data/worldgen/real/sol_system/`

## Current Gaps

Missing or incomplete MW-specific surfaces before this task:

- no `schema/worldgen/galaxy_priors.schema`
- no `data/registries/galaxy_priors_registry.json`
- no MW-specific cell generator module under `src/worldgen/mw/`
- current realism registry points the default Milky Way profile at a legacy coarse priors token
- current stub worldgen emits fixed anchor objects rather than a deterministic per-cell star-system seed list

## Implementation Constraint

MW-0 should extend the existing GEO worldgen engine, not bypass it.

Required consequence:

- `process.worldgen_request` remains the only authoritative mutation path
- `worldgen_result` remains the canonical persisted output
- Milky Way procedural base generation must stay cell-addressed, bounded, deterministic, and overlay-safe
