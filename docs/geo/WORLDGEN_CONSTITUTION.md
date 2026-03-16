Status: DERIVED
Last Reviewed: 2026-03-16
Supersedes: none
Superseded By: none
Stability: provisional
Future Series: DOC-CONVERGENCE
Replacement Target: canon-aligned documentation set for convergence and release preparation

# Worldgen Constitution

Status: Canonical GEO-8 doctrine for deterministic on-demand procedural generation.

## Scope

This document defines the authoritative GEO-8 worldgen contract.

It governs:

- deterministic on-demand generation by `geo_cell_key`
- version-locked procedural base generation
- `RealismProfile` control of priors and constraints
- stable GEO-derived object identities
- deterministic cache/replay/proof behavior

This document does not:

- add real-world data packs
- require eager universe generation
- authorize nondeterministic randomness
- authorize direct truth mutation outside processes

## Relevant Invariants

- `docs/canon/constitution_v1.md` `A1` Determinism is primary
- `docs/canon/constitution_v1.md` `A2` Process-only mutation
- `docs/canon/constitution_v1.md` `A4` No runtime mode flags
- `docs/canon/constitution_v1.md` `A6` Provenance is mandatory
- `docs/canon/constitution_v1.md` `A9` Pack-driven integration
- `docs/canon/constitution_v1.md` `E4` Named RNG streams
- `docs/canon/constitution_v1.md` `E6` Replay equivalence
- `docs/canon/constitution_v1.md` `C3` CompatX obligations

## 1. Worldgen Inputs

Authoritative worldgen is a pure function of:

- `UniverseIdentity`
- `geo_cell_key`
- requested `refinement_level`
- deterministic reason code

The required effective identity inputs are:

- `universe_id`
- `global_seed`
- `generator_version_id`
- `realism_profile_id`
- `topology_profile_id`
- `metric_profile_id`
- `partition_profile_id`

If `generator_version_id` or `realism_profile_id` are absent from older identities, runtime may resolve them to canonical defaults, but the resolved values become the locked values for that session/save lineage and must be logged explicitly.

## 2. Generation Addressing

Worldgen must target space only through `geo_cell_key`.

Required properties:

- generation is partition-based
- generation never scans infinite space
- generation requests are local and bounded
- all cache keys and replay checks are cell-addressed

Forbidden:

- float-position-only generation without `geo_cell_key`
- whole-universe enumeration
- implicit neighborhood expansion outside declared request bounds

## 3. Canonical Base Layer Outputs

For a given request, the canonical base layer output is a deterministic `worldgen_result`.

It may contain:

1. spawned object identities
2. initial field values for the requested cell
3. initial macro geometry state for the requested cell
4. optional template spawn descriptors for later SYS/PROC materialization

Each output must be derivable solely from:

- the request
- the locked universe identity
- the active realism profile
- the locked generator version

No hidden mutable state may influence procedural output.

## 4. RealismProfile

`RealismProfile` provides data-driven priors and constraints. It does not directly mutate truth.

Supported domains:

- galaxy priors
  - star density
  - IMF bias
  - metallicity gradient
- system priors
  - star multiplicity
  - planet occurrence
- planet priors
  - density class
  - atmosphere tendency
  - moon tendency
- surface priors
  - terrain tendency
  - fill/void tendency
  - macro temperature tendency

Rules:

- profiles are data-only
- profiles are pack-extensible
- profiles do not override generator version lock
- profile changes across sessions are explicit profile changes, not hidden mode switches

## 5. Generator Version Lock

`generator_version_id` is immutable for a universe lineage unless an explicit CompatX migration is invoked.

Required behavior:

- a universe save created under one generator version must not silently regenerate under another
- requests that attempt to override the locked generator version must be refused
- proof bundles must surface the active generator version registry hash and result hash chain

Changing worldgen algorithm semantics without a version bump is forbidden.

## 6. Stable Identity

Every procedurally generated object must use GEO-1 identity derivation:

`object_id = H(universe_identity_hash, topology_profile_id, partition_profile_id, geo_cell_key, object_kind_id, local_subkey)`

Rules:

- `local_subkey` ordering must be deterministic
- refinement must not reorder previously emitted local subkeys for the same generator version
- overlay layers may add or override content later, but the procedural base identity contract remains stable

## 7. Refinement Model

Generation is refinement-driven and bounded.

Reference refinement tiers:

- `0`: macro cell anchors
- `1`: system-scale anchors
- `2`: planet/body anchors
- `3`: surface macro state

The exact content emitted at each refinement level is generator-version-defined.

Rules:

- higher refinement is explicit
- lower refinement does not imply full deep generation
- regeneration of the same refinement level must be bit-identical
- refinement may emit additional objects, but previously emitted identities for the same request must remain stable

## 8. RNG Stream Policy

Authoritative worldgen randomness must use named deterministic streams only:

- `rng.worldgen.galaxy`
- `rng.worldgen.system`
- `rng.worldgen.planet`
- `rng.worldgen.surface`

Seed derivation rule:

`seed = H(global_seed, generator_version_id, realism_profile_id, geo_cell_key, stream_name)`

Rules:

- no wall-clock
- no global random module state
- no unnamed stream use
- all stochastic branching must be reproducible from the declared seed rule

## 9. Process Boundary

Authoritative worldgen mutation must occur only through `process.worldgen_request`.

The process may:

- check deterministic caches
- produce a canonical `worldgen_result`
- seed field cells through GEO/FIELD helpers
- seed geometry state through GEO-7 helpers
- register generated object identities in canonical runtime state

The process must not:

- mutate truth from viewer/lens/render paths
- bypass the process runtime commit boundary
- silently rewrite generator locks

## 10. On-Demand Request Sources

Worldgen requests may be created by:

- view/projection extent interest
- ROI/system interest
- explicit query
- explicit teleport target
- simulation/pathing/system expansion interest

Rules:

- request creation is deterministic
- reason codes are explicit
- requests are loggable and replayable
- request batching must preserve deterministic cell ordering

## 11. Caching and Eviction

Worldgen results may be cached by:

`H(geo_cell_key, refinement_level, generator_version_id, realism_profile_id, global_seed)`

Rules:

- cache lookup is pure
- cache hits and misses do not change canonical outputs
- eviction must not change regenerated outputs
- derived cache metadata may be dropped; canonical `worldgen_result` semantics may not drift

## 12. Overlay Separation

GEO-8 defines only the canonical procedural base layer.

Separate layers:

- procedural base layer
- official overlay layer
- mod overlay layer
- save/edit overlay layer

Rules:

- overlays do not redefine the meaning of the base layer retroactively
- player edits and later real-data overlays must compose above the base layer through explicit contracts
- GEO-9 owns overlay semantics

## 13. Proof and Replay

Proof bundles must include:

- `generator_version_registry_hash`
- `realism_profile_registry_hash`
- `worldgen_request_hash_chain`
- `worldgen_result_hash_chain`

Replay requirement:

- rerunning the same cell request with the same locked universe identity must reproduce identical result fingerprints and object IDs

## 14. Refusal Conditions

Worldgen must refuse explicitly when:

- `geo_cell_key` is invalid
- generator version is undeclared
- realism profile is undeclared
- an override conflicts with the locked universe generator version
- an override conflicts with the locked universe realism profile where policy forbids drift
- request bounds are invalid

Silent fallback is forbidden.

## 15. GEO-8 Readiness Outcome

This contract establishes:

- deterministic cell-key world generation
- version-locked procedural base generation
- stable GEO object identity generation
- bounded, replayable, proof-carrying on-demand generation

It intentionally leaves to later phases:

- overlay composition and authored real-data merge
- full orbital integration
- rich domain-specific simulation activation beyond initial conditions
