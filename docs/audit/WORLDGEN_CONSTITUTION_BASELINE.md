# GEO-8 Worldgen Constitution Baseline

Status: Baseline complete for GEO-8.

## Scope

This report summarizes the implemented GEO-8 worldgen contract:

- deterministic, on-demand generation by `geo_cell_key`
- version-locked `UniverseIdentity` worldgen lineage
- data-driven `RealismProfile` scaffolds
- canonical process-owned `worldgen_result` emission
- replay/proof surfaces for generated cells

## Relevant Invariants

- `docs/canon/constitution_v1.md` `A1` Determinism is primary
- `docs/canon/constitution_v1.md` `A2` Process-only mutation
- `docs/canon/constitution_v1.md` `A4` No runtime mode flags
- `docs/canon/constitution_v1.md` `A6` Provenance is mandatory
- `docs/canon/constitution_v1.md` `A9` Pack-driven integration
- `docs/canon/constitution_v1.md` `E4` Named RNG streams
- `docs/canon/constitution_v1.md` `E6` Replay equivalence
- `docs/canon/constitution_v1.md` `C3` CompatX obligations

## Realism Profile Scaffolds

Registered baseline realism profiles:

- `realism.realistic_default_milkyway_stub`
- `realism.flat_world_stub`
- `realism.torus_world_stub`
- `realism.fantasy_stub`

These profiles remain data-only priors. They do not mutate truth directly and do not bypass generator version locking.

## Generator Version Locking

`UniverseIdentity` now carries:

- `generator_version_id`
- `realism_profile_id`

Runtime behavior:

- `process.worldgen_request` refuses generator-version overrides that conflict with the locked universe lineage
- realism profile drift is refused through the same lineage guard
- session creation, resume metadata, and proof surfaces now surface these lock values explicitly

## On-Demand Generation Behavior

Authoritative generation is routed through `process.worldgen_request`.

Deterministic behavior:

- generation is addressed by `geo_cell_key`
- generation never scans unbounded space
- named RNG stream seeds derive from `global_seed`, generator version, realism profile, cell key, and stream name
- refinement levels `0..3` emit bounded anchor content only
- generated object identities use GEO-1 stable ID derivation

Canonical output surfaces per cell:

- spawned object IDs
- initial field values
- initial macro geometry state when surface refinement is requested

## Cache and Replay

Implemented cache behavior:

- cache key is derived from `universe_seed`, `geo_cell_key`, `refinement_level`, `generator_version_id`, and `realism_profile_id`
- cache eviction does not change regenerated outputs
- request IDs do not alter canonical worldgen results

Proof and replay surfaces:

- `generator_version_registry_hash`
- `realism_profile_registry_hash`
- `worldgen_request_hash_chain`
- `worldgen_result_hash_chain`
- `worldgen_spawned_object_hash_chain`

Replay tooling:

- `tools/geo/tool_replay_worldgen_cell.py`

## Integration Status

Minimal deterministic request builders are integrated for:

- projection/view extent cell requests
- ROI cell requests
- explicit process-backed cell requests

This remains a contract-first integration:

- no eager galaxy generation
- no real-data overlays
- no deep orbital or climate simulation

## GEO-9 Readiness

The repository is ready for GEO-9 overlay composition.

Stable prerequisites now exist for:

- canonical procedural base generation
- version-locked universe lineage
- replay-stable generated object identities
- later official/mod/save overlays layered above the base contract
