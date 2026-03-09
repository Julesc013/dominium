Status: DERIVED
Last Reviewed: 2026-03-09
Supersedes: none
Superseded By: none

# MW2 Retro Audit

## Scope

This audit records the repository state before MW-2 star and orbital priors work.

Audit targets:

- realism-profile prior references
- named RNG stream readiness for system/star/planet derivation
- reusable runtime or test surfaces for L2 refinement

## Existing Realism Profile Prior Hooks

The current realism contract already exposes the hooks MW-2 needs.

Relevant surfaces:

- `schema/geo/realism_profile.schema`
  - requires `galaxy_priors_ref`
  - requires `system_priors_ref`
  - requires `planet_priors_ref`
  - requires `surface_priors_ref`
- `data/registries/realism_profile_registry.json`
  - default MVP realism profile already carries system and planet prior references

Current gap:

- no `system_priors_registry.json`
- no `planet_priors_registry.json`
- no star/planet model schemas for refinement `L2`

Audit conclusion:

- MW-2 can remain profile-driven without reopening the realism-profile contract.
- The missing work is to materialize the declared prior references into registries and runtime use.

## Existing Named RNG Stream Rules

Current GEO worldgen already defines the authoritative named stream roots:

- `rng.worldgen.galaxy`
- `rng.worldgen.system`
- `rng.worldgen.planet`
- `rng.worldgen.surface`

Relevant runtime surface:

- `src/geo/worldgen/worldgen_engine.py`
  - `worldgen_rng_stream_policy(...)`
  - deterministic seed derivation from universe lineage, cell key, generator version, realism profile, and stream name

MW-1 consequence:

- each `StarSystemSeed` already carries deterministic `system_seed_value`
- MW-2 can derive star/body substreams from that stable system seed under named salts

Audit conclusion:

- MW-2 does not need a second RNG policy layer.
- Star and orbital priors should derive substreams from `system_seed_value` using named stream tokens, not global or wall-clock randomness.

## Existing Reusable Runtime Surfaces

Current insertion points already exist:

- `src/geo/worldgen/worldgen_engine.py`
  - canonical refinement dispatch
  - cache, refusal, and result wiring
  - current `L2` object expansion is only a placeholder count expander
- `src/worldgen/mw/mw_cell_generator.py`
  - stable system-seed generation
  - star-system artifact metadata including metallicity and habitability bias
- `tools/xstack/sessionx/process_runtime.py`
  - authoritative `process.worldgen_request` mutation boundary
  - idempotent persistence for spawned objects and MW-1 star-system artifacts

Current placeholder before MW-2:

- `_generated_object_rows(...)` in `src/geo/worldgen/worldgen_engine.py`
  - derives `kind.star`, `kind.planet`, and `kind.moon` counts directly from hashes
  - does not emit star/planet artifact models
  - does not apply orbital-spacing or stability constraints

Audit conclusion:

- MW-2 should replace the current placeholder `L2` expansion with a dedicated system refiner, not add a parallel object-generation path.

## Existing Reusable Planet/Orbit Code

Search results show no existing runtime planet-prior generator to reuse.

Notable findings:

- `src/meta/reference/geo_small_reference.py`
  - contains only reference fixtures and overlay examples involving `kind.planet`
  - not a runtime worldgen surface
- specs/docs describe orbital fields and body concepts
  - useful for terminology and coarse field naming
  - not an implemented deterministic generator

Audit conclusion:

- MW-2 must introduce the first runtime star/orbital prior generator module.
- Reuse should come from existing GEO identity, worldgen, and TestX fixture surfaces rather than from a pre-existing planet generator.

## Existing Verification Surfaces

Reusable verification surfaces already present:

- `tools/xstack/testx/tests/geo8_testlib.py`
  - deterministic worldgen process fixture
- `tools/worldgen/tool_replay_system_instantiation.py`
  - MW-1 replay/hash proof pattern
- existing MW-0 and MW-1 TestX fixtures
  - deterministic hash and idempotence coverage patterns

Audit conclusion:

- MW-2 can extend the established replay/tool/test pattern without introducing a new verification stack.
